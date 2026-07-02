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
# [569] Unknown Intrusion Traffic Detection Method Based on Unsupervised Learning and Open-set Recognition
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
编号：569
题名：Unknown Intrusion Traffic Detection Method Based on Unsupervised Learning and Open-set Recognition
年份：2025
DOI：10.21203/rs.3.rs-6201348/v1
来源：Research Square preprint
PDF：paper/10.21203_rs.3.rs-6201348_v1.pdf
已有粗分类：加密流量分类与应用识别
二级关联：无
相关性：强相关，分数 14
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\569.txt
- 原始字符数：114896
- 本次发送字符数：114896
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Unknown Intrusion Tra c Detection Method Based
on Unsupervised Learning and Open-set
Recognition
Jun Fang
Naval Aviation University
Cunxiang Xie

Naval Aviation University

Article
Keywords:
Posted Date: March 27th, 2025
DOI: https://doi.org/10.21203/rs.3.rs-6201348/v1
License:   This work is licensed under a Creative Commons Attribution 4.0 International License.
Read Full License
Additional Declarations: No competing interests reported.

1

Unknown Intrusion Traffic Detection Method Based on Unsupervised

2

Learning and Open-set Recognition

3

Jun Fang 1, Cunxiang Xie 1,*

4

1 Naval Aviation University, Yantai 264001, China;

5

maidifj@163.com; xiecunxiang1996@163.com; 932304145@qq.com

6

*Correspondence: xiecunxiang1996@163.com

7
8

Abstract

9
10
11
12
13
14
15
16
17
18

Intrusion traffic detection technology is an important network protection technology to ensure network communication
security and protect users' information privacy. To address problems relating to the low classification accuracy of current
intrusion traffic detection algorithms and that most of the current research focus on closed set detection, this paper
proposes a detection and classification model for open set traffic based on information maximization generative
adversarial network and OpenMax algorithm. Firstly, the intrusion traffic classification model under the closed set
condition is trained, and the sample activation vector is recalculated in the penultimate layer of the model by using the
OpenMax algorithm. According to the activation vector of the known category, the estimated probability of the unknown
category is then calculated to identify unknown traffic. Results show that the model's classification accuracy for
CICIDS2017 open set traffic in the misuse and anomaly detection experiments is above 88.5% and 88.2%, respectively.
The model can effectively detect various types of unknown traffic with high detection accuracy and robustness.

1 Introduction
Intrusion detection refers to a particular type of security monitoring, and protection for computers and data networks
whilst they operate normally and openly [1]. Intrusion detection is an important means to protect the security of network
communication. The network intrusion methods can generally be divided as follows: non-administrator users inside the
system access files or data without permission; attackers outside the system illegally access or destroy system data; or
finally, user rights management within the system is chaotic [2]. The goal of intrusion detection system (IDS) is to detect
and identify the above intrusion methods in real-time. At present, the Internet technology is developing rapidly, and its
application fields cover most areas of social life. Its technological development has shown phenomena such as
diversification of terminal forms, dynamic protocol ports, and a significant increase in the number of users, which has
led to an explosive increase in the amount of information processed by the Internet. While the amount of network
information and the number of users are growing rapidly, malicious attacks, network viruses, and traffic intrusions have
also appeared, posing a significant threat to the users' information security. Therefore, the importance of network
intrusion detection technology for protecting information security is increasingly important and has been highlighted
recently. Compared with traditional network defense technologies such as firewalls, Network Intrusion Detection System
(NIDS) can better detect and identify abnormal network traffic and classify the attack mode of intrusion traffic, thereby
preventing the network from being attacked by possible threats, thereby ensuring the confidentiality, integrity and
availability of the network [3].
There are three ways for NIDS to analyze network traffic: misuse detection, anomaly detection and hybrid detection
[4]. The technology based on misuse detection performs intrusion detection through the characteristics of known types
of intrusion traffic, and realizes the detection and classification of attack traffic through feature comparison. Misuse
1

detection-based algorithms usually use methods such as expert knowledge base and pattern matching for model
construction, which are characterized by the need to build a knowledge base containing the characteristics of known
intrusion traffic in advance. This method has a low false alarm rate, but cannot detect unknown types of attack traffic
(i.e., zero-day attack traffic), meaning that the database needs to be updated manually. The algorithm based on anomaly
detection only records normal network traffic and system behaviors, and detects intrusion traffic by the deviation
between anomaly traffic and normal traffic. When the deviation value between abnormal traffic and normal traffic
exceeds a pre-set threshold, the traffic will be classified as intrusion traffic. This method does not need to build the
intrusion traffic feature base in advance, but it may misclassify normal traffic as abnormal when there is a change in
system traffic, so it has the drawback of high false alarm probability [5]. Anomaly detection-based algorithms have the
ability to detect new and unknown attack traffic [6], and it is widely used for early warning of intrusion traffic because
of its low computational complexity and less reliance on recorded traffic. However, in order to apply appropriate
measures to prevent the problem from worsening or to return the system to normal mode, the identification results of the
IDS need to be presented to the Intrusion Response System (IRS). For the IRS, screening out abnormal traffic cannot
provide sufficient alert information. In a manual response system, there are several pre-configured sets of responses
based on the type of attack [7]. When a problem occurs, the administrator needs to select and apply a set of pre-configured
actions based on the type of attack traffic output from the IDS. In an automated response system, the IDS needs to
provide alerts that contain more information, such as attack description, attack time, source IP, user account, etc.
Anomaly detection algorithms only distinguish traffic as normal or anomalous, which may result in the IRS performing
inappropriate responses or failing to ensure that the response is sufficient to offset the attack. Therefore, for IDSs, both
misuse detection and anomaly detection have important implications, and hybrid detection algorithms can combine the
advantages of both detection algorithms.
The early intrusion traffic detection relies on the rule-based detection method [8], i.e., the intrusion rules are set in
advance through prior knowledge, and then the corresponding state parameters of the network environment are captured
and compared with the set rules to achieve intrusion detection. Denning D E [9] proposed a remote intrusion detection
expert system (IDES), which uses anomaly catchers to collect network status in the deployed network environment. The
expert system then analyses and processes the collected information to determine the traffic flow. The methods based on
rules and expert systems can detect and identify intrusion traffic types within the constraints of rules. However, they
cannot effectively identify unknown intrusion traffic outside the established rules. The establishment of an expert
knowledge base requires a lot of prior knowledge and time, which is not applicable under the modern conditions of large
Internet information traffic.
At present, intrusion traffic detection methods based on machine learning have been widely used [10-11]. Compared
with traditional rule-based and expert system detection methods, the workload of manually setting detection rules can
be avoided. Safaldin M et al. [12] proposed an improved binary gray wolf optimization support vector machine model,
which is used to eliminate redundant feature quantities in the model and reduce the false alarm rate of the algorithm. The
reduced feature set is trained and tested through the Support Vector Machine (SVM), and the accuracy of the binary
classification on the KDD99 dataset reached 96%; Al-Qatf M et al. [13] proposed a self-learning intrusion detection
system (STL-IDS) to perform feature learning and dimensionality reduction on the data set, which improves the
prediction accuracy of SVM for attacks. The multi-classification accuracy rate reached 80.48%; Ahmim A et al. [14]
proposed an intrusion traffic classification algorithm based on the decision tree and rule model. By using three classifiers,
REP-Tree, RIPPER and Forest PA, the multi-classification task of the CICIDS2017 intrusion traffic data set was realized,
and the multi-classification accuracy rate reached 96.67%. The above three machine learning algorithms have effectively
improved SVM, decision tree, random forest and other models. However, there are several problems, such as low
classification and recognition rate of some datasets and weak model generalization.
Compared with other types of machine learning algorithms, intrusion detection algorithms based on deep learning
can directly perform feature representation learning from the data set, and the feature layer parameters can be gradually
adjusted through the training process [15], thus eliminating the need for manual feature extraction and processing steps
and possessing a greater advantage in processing large amounts of data.
The application of deep learning methods in the intrusion detection classification model can be divided into
supervised learning algorithms and unsupervised learning algorithms [16]. Among them, the supervised learning
algorithm is mainly used in the design of intrusion detection and classification algorithms, which can effectively improve
the detection and classification accuracy. Most of the current deep learning research on NIDS is based on supervised
learning algorithms [17]. Vinayakumar R et al. [18] proposed a hybrid intrusion detection and alarm system based on
Deep Neural Network (DNN), which realizes binary and multi-classification of intrusion traffic data sets such as
CICIDS2017 data set. The accuracy of multi-classification and binary classification on the CICIDS2017 dataset is very
high, reaching 93.1% and 95.6%, respectively. However, the classification effect for other types of datasets is not good.
Ma W G et al. [19] proposed an abnormal traffic detection method based on Long Short-Term Memory (LSTM) and an

improved residual network, which improves the feature adaptability of the LSTM layer. The accuracy rates of the upper
two-class and multi-class are 92.3% and 89.3%, respectively. Tang X B et al [20]. performed sampling optimization on
the NSL-KDD training set through adaptive synthesis (ADASYN) sampling, which effectively improves the feature
extraction ability of the improved residual network model for small samples, and the accuracy rates of multiclassification and binary classification of intrusion traffic are 89.40% and 91.88%, respectively.
The above methods have improved the classification accuracy of intrusion traffic but are prone to problems such as
overfitting and gradient disappearance during training. The disadvantage of supervised learning is that the training of the
model and the establishment of data patterns needs be carried out by identifying the relevant features and categories of
the labeled data. Therefore, the range of data sets that can be used for training is inherently limited, and the expansion
of the training set requires labeling first.
In the practical network environment, it is challenging to obtain the labels of traffic data [21], with the analysis of
network traffic and log records being time-consuming and labor-intensive, often with only a small amount of available
data to label. In contrast, unsupervised learning algorithms can obtain feature information from data without category
labels, and automatically divide the data into different classes according to a small number of prior conditions, which
can solve the problems of supervised learning algorithms. However, the performance of current intrusion detection and
classification models designed using unsupervised learning algorithms is usually lower than that of supervised learning
algorithms, and the accuracy of some algorithms is not ideal [22]. Zhang X et al [23]. achieved intrusion detection on
the NSL-KDD dataset through Bidirectional Generative Adversarial Networks (BiGAN) and compared the detection
performance with the original GAN. The results show that the detection performance of intrusion traffic binary
classification using the BiGAN model is better than the original GAN, and the detection accuracy rate reaches 71.72%.
In [24], the loss function of BiGAN is improved, and the algorithm realizes the classification and identification of 10%
of the KDD-99 intrusion traffic data set. The results show that the detection precision and recall are 93.24% and 94.73%,
respectively. However, the article does not give the detection accuracy of the algorithm.
The comparison shows that the classification accuracy and other performances of the above algorithms are lower
than the supervised learning algorithms trained on the same dataset. Therefore, in intrusion detection, numerous studies
have used unsupervised learning algorithms to expand training data sets to improve the classification and recognition
performance of intrusion detection models. Vu L et al. [25] used an ACGAN-SVM algorithm to achieve the purpose of
synthesizing attack traffic data and expanding the data set. The algorithm carried out classification tests on four intrusion
traffic data sets. The results show that the algorithm's performance using the expanded dataset improved in terms of
classification precision and recall. Lee J H et al. [26] proposed a GAN-RF algorithm that uses generative adversarial
networks for data augmentation of the CICIDS2017 dataset and then uses a random forest model for intrusion traffic
detection and classification. The results show that compared to using the RF model alone, the classification accuracy is
improved from 99.19% to 99.83%.
The above algorithm can effectively improve the performance of the intrusion detection model through data
expansion, but it does not have the function of processing unlabeled training data. The detection and identification
performed by the above-mentioned algorithms are all performed in a closed data set, i.e., all types of intrusion traffic are
known, and the types that can be identified by the algorithm are limited to known types. There are usually a large number
of unknown types of intrusion traffic in the actual network environment and the above detection algorithm cannot classify
the unknown traffic, meaning that it is difficult to adapt to the actual network environment. Therefore, it is necessary to
detect unknown intrusion traffic in the open space. The two main concepts of open set identification are: (1) A binary
discriminator for learning open and closed sets by using some anomaly data as open sets. (2) Unsupervised learning of
closed-set data distributions with the use of GAN and using the discriminators as open-set likelihood functions [27]. Due
to the limitation of data types, anomaly data cannot include all cases of open sets. Due to the training instability of GAN,
the latter is usually poor for open-set identification. Therefore, there is a high demand for the performance of GAN
models. In addition, more models are used to perform open set recognition. Zhang H et al. [28] proposed an OpenHybrid
framework. This framework solves the open set recognition problem by combining a generative flow-based model with
a discriminative classifier. Chen G et al. [29] proposed a Reciprocal Learning Point (RPL) framework. The framework
introduces unknown information through reciprocal points, and the neural network can learn a more compact and robust
feature space and efficiently separate the known space from the unknown space. Perera P et al. [30] proposed an
algorithm based on generative-discriminative feature representations for open-set identification. The best closed-set
features are first used to train the classifier, and then the classifier is used to evaluate the difference between the known
set and open-set samples produced by the generator. Yang H M et al. [31] proposed a deep learning framework called
convolutional prototype network (CPN), which uses open-world oriented and human-like prototype model to replace
SoftMax. CPN is able to improve the robustness of convolutional neural networks in open-set recognition while
maintaining the high accuracy of closed-set recognition. Tang R et al. [32] proposed an unsupervised method of
ZeroWall, which uses an auto-encoder and recurrent neural network (RNN) to capture the semantic features of normal

traffic and classify traffic that cannot understand semantics as unknown attack traffic. This approach has a good detection
rate for zero-day attacks missed by Web application firewalls (WAFs), with an F1-score of 0.98, however, the algorithm
does not consider the classification of known attack traffic. Zhang Y et al. [33] introduced the OpenMax layer to replace
the SoftMax layer in the convolutional neural network and realized the detection of unknown attack traffic. However,
when the unknown class traffic is multi-class intrusion traffic, the OpenMax layer cannot further classify the unknown
class. Zhang Z et al. [34] proposed an unknown traffic classification method based on sparse auto-encoder and
established the mapping of traffic features to semantic space through reconstruction error to detect unknown attack
traffic. The algorithm claims to achieve 88.3% accuracy in attack traffic detection on the NSL-KDD dataset. However,
it only considers the detection performance of unknown traffic and does not verify the algorithm's ability to classify
known normal traffic.
Based on the problems and challenges of the above researches, this paper proposes an intrusion traffic detection
algorithm based on unsupervised learning algorithm and open set identification method and combines the advantages of
the two algorithms. The main innovations of this paper are as follows:
1)
2)

3)

4)

Construct an unsupervised learning intrusion traffic classification algorithm based on Information Maximizing
Generative Adversarial Nets (Info GAN) to reduce the dependence on label data and improve the model
classification performance.
Based on the OpenMax layer structure, an unknown class detection algorithm based on misuse detection is
proposed to improve the detection performance of the model for open set intrusion traffic samples. Combining
the closed set classification model and the open set detection model, an O-S (OpenMax-SoftMax) open set
intrusion traffic classification model is proposed, which is capable of detecting and classifying unknown traffic
and maintaining the known intrusion traffic high-precision classification.
Combining the fine-grained classification method, Info GAN and OpenMax algorithm, a detection and
analysis system for abnormal traffic is proposed. The system only needs to record the characteristics and
behavior patterns of normal traffic. It is suitable for network environments with various unknown traffic, and
has the ability to update and expand the data types that can be recognized by the algorithm in real time. It
implements automatic and efficient anomaly detection analysis in cyberspace.
Various experimental results of the proposed algorithm are presented. First, we verify the loss function value,
classification accuracy and other indicators of the closed-set intrusion traffic algorithm based on Info GAN
under different training epochs, so as to determine the best epochs for the intrusion traffic classification
algorithm. Then, for the O-S open set intrusion traffic classification model, we control the values of the
hyperparameters alpha rank, tail size and distance type respectively. We test the open set identification and
classification of the model for various types of intrusion traffic under different hyperparameter values. For the
abnormal traffic detection model based on fine-grained classification, we control the hyperparameters alpha
rank, tail size and the number of normal traffic classifications respectively, and test the detection and
identification performance of the abnormal traffic detection model for intrusion traffic under different
parameter values. The experimental results show that the proposed algorithm has good performance in the
detection and identification of intrusion traffic under the condition of open set.

2 Preparation Knowledge
2.1 Generative Adversarial Network
Generative Adversarial Network (GAN) is an unsupervised generative model algorithm proposed by Ian J.
Goodfellow et al [35]. The algorithm trains both the generator (Generator, G) and discriminator (Discriminator, D)
models at the same time. The generator is used to synthesize the data and fit the input data distribution, and the
discriminator is used to calculate the probability that the sample comes from the input data instead of the generator. In
the process of model training, the purpose of the generator is to maximize the probability of misjudgment by the
discriminator, and the discriminator continuously improves the discrimination ability according to the input data during
the training process. The two form a minmax game framework. The working process of the original GAN is shown in
Figure 1.

Random
noise z

When nash
equilibrium

Fake data

Output data

z

G(z)

Train the
generator

Labeling
（Label=0）

Generator

G(z), y=0

G_loss

Loss
function

binary_cross
entropy

D_loss

D[G(z)]
D(x)

Train the discriminator

x, y=1

Labeling
（Label=1）

x

Input data

Result
Output：0/1

Discriminator

Figure 1. Working process of generative adversarial network.

The specific workflow is as follows:
(1) In each round of training, firstly perform k cycles: input the real data set x , and set the label of the data (label=1),



input random noise z = z (1) , z ( 2) ,..., z ( m)

 to the generator to generate fitting fake data G ( z ) , set the label (label=0),

input the real data and fake data into the discriminator, calculate the loss function, and train the discriminator.
(2) After the cycle is completed, the parameters of the discriminator are fixed, and the generator generates fake data
G ( z ) , which is input to the discriminator to update the parameters of the generator by reducing the stochastic gradient.
(3) Steps (1) and (2) are executed in a loop until the algorithm converges, and the training is completed. The purpose
of the algorithm is to match the distribution of the generated data PG ( x ) with the real data distribution Pdata ( x ) , and
the minimax game between the generator and the discriminator can be expressed by Eq.(1).
min max V ( D, G ) =  Pdata ( x ) log ( D ( x ) ) + PG ( x ) log (1 − D ( x ) ) dx
G

x

D

= E x ~ Pdata log ( D ( x ) ) + E x ~ P ( x) log (1 − D ( x ) )

(1)

G

(

)

= E x ~ Pdata log ( D ( x ) ) + E z ~ noise log 1 − D ( G ( z ) ) 



The D ( x ) = pdata ( x ) / ( pdata ( x ) + pG ( x ) ) is the optimal solution for the discriminator. The original GAN has many
problems such as unstable training process, gradient disappearance, mode collapse, etc [36]., therefore, a large number
of GAN-based improved generative adversarial networks have been generated. The Info GAN used in this paper belongs
to the improved network based on GAN.

2.2 Open-Set Identification Problem

2

2
22
1
1

2

1

1 1

1

2

1

2

1
3

4

2

1

1 1

3

1

2

1
1
3

3
3

3
3
3

?
? ?
??
?

4
4

1 1

1

2

2
3

4

3

4 4
4

3

2

1

3

4 4
4

2

2
22

2

4

4 4
4
4

2

2
22

3

4
3

3

3
3
3

?
? ?
??
?

4
4

3
3
3

3
3
3

(a)
(b)
(c)
Figure 2. How open set recognition and closed set recognition work.

Open set recognition refers to the recognition problem that the prior knowledge of the recognition target is
incomplete and contains unknown input categories. Distinguishing between known and unknown samples is the basic
problem of open set recognition. In the practical network environment, it is usually impossible to traverse and obtain all
possible types of intrusion traffic samples. Intrusion detection in real network environment is not a closed set problem

[37]. Therefore, in the process of intrusion detection, there will always be traffic types that have not appeared in training,
which is in line with the characteristics of the open set identification problem. Assuming that the intrusion traffic
detection model trained in the closed set is shown in Figure 2(a), it can classify the known four types of samples. If this
model is used directly in the open set, it leads to the misclassification of unknown types of traffic, which will pose a
threat to network security, as shown in Figure 2(b). Therefore, the problem of intrusion traffic detection must be
generalized from the closed set to the open set. By limiting the decision range of the model, the proposed model can
reject unknown samples and avoid classifying unknown samples into known classes, as shown in Figure 2(c).
The degree of openness (ope) is a measure of the proportion of unknown classes and the openness of the data set in
the problem of open set identification [38]. The calculation method is given in Eq. (2), where training classes represents
the number of known classes appearing in the training set, and target classes represents the number of target classes to
be identified.
ope = 1 −

2  training_classes
testing_classes + target_classes

(2)

The value range of ope is [0, 1). When the value of ope is 0, it means that the problem is a closed set problem,
and the number of training, testing, and target categories is equal; the larger the value of ope , the more open the problem
is. When the number of training classes categories is fixed, increasing testing classes or target classes improves the
openness. The key to the intrusion detection problem in the open set environment is to optimize the performance of
correctly rejecting unknown classes while maintaining the classification performance of known classes. To measure the
open-set recognition performance of the model, the open space risk [39] is introduced. Let f be a measurable
recognition function, x represents the samples in the feature set X , and y represents the category of the samples to
be recognized. When x  K denotes that the sample belongs to the feature space K of known class, K  X . Here
f y ( x ) means to identify the known category y of the sample and when f y ( x ) = 1 , it means that the recognition
function recognizes the category of sample x as y . When f y ( x ) = 0 , it means that the recognition function does not
recognize the category of the sample x as y . The variable O represents an open space, where the samples are far
enough from the features of known class samples, and the space S O includes training samples x  K of all known
classes and the open space O . Therefore, the open space risk RO ( f ) can be defined as Eq.(3):

 f ( x ) dx

RO ( f ) = O

y

 f ( x ) dx

(3)

y

SO

where R ( f ) depicts the proportion of open space samples identified as known class samples over the entire space
samples identified as known class samples [40]. Under the condition that the overall number of samples remains
unchanged, the greater the number of samples marked as known classes in the open space, the greater the open space
risk R ( f ) , and the worse the model's recognition performance for unknown class samples.
O

O

For an open set identification problem, given a known class sample set T = t1 , t2 ,..., t z  , there is an open set risk
(OSR), as given in Eq. (4):
OSR = RO ( f ) + r R ( f (T ) )

(4)

where R represents the empirical hazard function and r is the regularization constant. The open set recognition
model should find a suitable recognition function f , so that the OSR value is the smallest, as shown in Eq. (5):
f = arg min  RO ( f ) + r R ( f (T ) )
f H

(5)

2.3 Extreme Value Theory
Extreme Value Theorem (EVT) can be described as follows:
Let S = s1 , s2 ,..., sn  be a series of independent and identically distributed samples, let M n = max s1 , s2 ,..., sn  .

When n →  , a series of real numbers ( an , bn ) satisfies the relationship an > 0 and Eq.(6):
 M n − bn



 x  = F ( x)

(6)


where the function F is a non-degenerate distribution function that obeys one of the three types of extreme value
distributions (Gumbel, Frechet, Weibull). The EVT represents the distribution of extreme values when approaching the
limit. An extreme value distribution is a limiting distribution in which the maximum value of a large number of random
observations of any distribution occurs. The form of the three types of extreme value distributions can be unified as the
Generalized Extreme Value distribution (GEV), whose equation is as follows:
lim P 
n →

an

 1 − v − (1/ k +1)
, k  0,
e
v


(7)
GEV ( t ) = 
 1 e − ( x + e ) , k = 0.


where x = ( t −  ) /  , v = 1 + k ( t −  ) /  . k ,  ,  represent shape, scale, and position parameters, respectively. In [41],
−1/ k

−x

it is demonstrated that the Weibull distribution is the most suitable hypothesis for statistical meta-identification, which
can obtain higher accuracy in the identification problem, and its accuracy is also higher than GEV empirically. The
Weibull distribution is a continuous probability distribution, and its probability density function can be expressed as
follows:
 k  x k −1 −( x /  )
e
,x  0

(8)
f ( x;  , k ) =     
0, x  0

where x represents a random variable,  represents the scale parameter, and k represents the shape parameter. The
cumulative probability density function of the Weibull distribution, which can be expressed as follows:
k

1 − e−( x /  ) , x  0
F ( x;  , k ) = 
0, x  0
k

(9)

The common probability density function and distribution function diagram of Weibull distribution is shown in
Figure 3:

(a)
(b)
Figure 3. Probability density function and cumulative distribution function of Weibull distribution: (a) Probability density
function plot of Weibull distribution; (b) Cumulative probability density function plot of Weibull distribution

3 Open-set intrusion traffic detection method based on Info GAN and OpenMax
3.1 Experiment process
Use the label array N = B, A1 ,..., Ak  to represent the known traffic type, where B represents the normal traffic

label, and A1 ,..., Ak represents the known intrusion traffic label. Through the above known types of traffic, a training set
and a test set for training an intrusion traffic classification model under the condition of a closed set can be formed. Real
network traffic usually contains unknown types of attack traffic that do not appear in the training set. Here, U represents
the feature space of unknown traffic, and Ak +1 represents the label of unknown traffic. The data set containing the traffic
of N Ak +1 is called the open set. The algorithm proposed in this paper realizes the distinction between normal traffic
and known types of intrusion traffic and the classification of known intrusion traffic and detects unknown traffic to avoid
misclassification of the closed set classification model. The experimental flow of the open-set intrusion traffic detection
method based on Info GAN and OpenMax is shown in Figure 4.
Firstly, the original traffic data set is preprocessed, the traffic data is converted into a form suitable for processing
by the intrusion traffic classification model, and the data set is divided into three parts: training set, test set, and open
set. Among them, the training set and the test set contain the same intrusion traffic category, where the data of each
category is independent and non-repetitive, with no identical data between the training set and the test set compared with
the previous two, the open set adds new intrusion traffic categories and data. In the experiment, the training set was used
to train the intrusion traffic classification model based on Info GAN, and the labeled test set was used to test the intrusion
traffic classification performance of the trained model. Repeat the training and testing process to adjust the network
parameters until the model converges.
Label
Performance evaluation

Open set

Original
data

Data
preprocess

Training
set

Model
training

Closed classification model
based on Info GAN

Test set

Label
Performance evaluation

When model
converges

Closed model

+

OpenMax
algorithm

Open set intrusion traffic detection model
Recording unknown data

Figure 4. Experimental process of open-collection intrusion traffic detection method.

At this point, the intrusion traffic classification model can detect and classify intrusion traffic in a closed set. The
SoftMax layer in the classification network of the closed-set classification model is replaced with an OpenMax layer, so
that the probability calculation of the final output of the classification network includes the unknown class probability.
The parameter values of the OpenMax algorithm are adjusted, and the labeled open set data is used to test the unknown
class detection and classification performance of the open set intrusion traffic detection model. When the detection is
over, the open set detection model records the newly acquired intrusion traffic labels and data in its own database, and
turns the unknown class into a known class, to realize the continuous update and expansion of the model database and
the automatic improvement of the model recognition ability.

3.2 Intrusion detection method based on Info GAN
The adversarial training of the generator and the discriminator in the original GAN aims to train the generator to
have the ability to generate fake data that is consistent with the distribution of the real data. However, there is a problem
with this training method in that the input of the generator is a random noise signal z that obeys a normal distribution,
and there are no other constraints. After the training is completed, the single dimension z cannot be matched with the
semantic features of the output data, which leads to poor interpretability of GANs, making it difficult to verify whether
their representations are meaningful. Info GAN addresses this problem by improving the input noise vector. The input
noise is decomposed into two parts: the incompressible noise and latent vector, which are used for the structured semantic
features of the data distribution. Let c = c1 , c2 ,..., cL  denote the set of latent vectors and satisfy the relation of Eq.(10):
P ( c1 , c2 ,..., cL ) = iL=1 P ( ci )

(10)

The purpose of Info GAN is to train the network to discover and recover latent vectors in each sample data under
unsupervised conditions. The input incompressible noise z and latent vector c into the generator, and the generated
data is represented as G ( z , c ) . If the original GAN objective function is used for calculation, it causes the generator to
ignore the latent vector part, resulting in PG ( x | c ) = PG ( x ) . Chen X et al [42]. proposed to use the information
regularization method to solve this problem, i.e., the objective function needs to ensure that the mutual information
entropy value between the latent vector and the generated data should be high. The calculation method of mutual
information is as Eq.(11):

I ( X ; Y ) = H ( X ) − H ( X | Y ) = H (Y ) − H ( X | Y )

(11)

Where I ( X ; Y ) can be described as the uncertainty of X under the condition of known Y . When X and Y are
independent of each other, I ( X ; Y ) = 0 and when X and Y are related by a deterministic invertible function, the value
I ( X ; Y ) reaches the maximum. Therefore, in the case of a given PG ( x ) , PG ( x | c ) should be kept with a small entropy,
so the objective function used is as Eq.(12):
min max V1 ( D, G ) = V ( D, G ) −  I ( c; G ( z, c ) )
G

(12)

D

Here,  represents the hyperparameter, which can be 1. In practice, the unknown P ( c | x ) makes it difficult to
directly maximize I ( c; G ( z, c )) , so an auxiliary distribution Q ( c | x ) is introduced, and the calculation process is as
Eq.(13):
I ( c; G ( z , c ) ) = H ( c ) − H ( c | G ( z , c ) ) = E x ~ G ( z , c ) E c '~ P ( c| x ) log P ( c ' | x ) + H ( c )

(13)

By constructing the KL (Kullback– Leibler) divergence of log P ( c ' | x ) , Q ( c | x ) can be used to replace it with
Eq.(14):
E x ~ G ( z ,c ) E c '~ P( c| x ) log P ( c ' | x )


= E x ~ G ( z ,c )  DKL ( P ( c | x ) || Q ( c | x ) ) + E c '~ P( c| x ) log Q ( c ' | x )


0


 E x ~ G ( z ,c ) E c '~ P ( c| x ) log Q ( c ' | x )

(14)

Therefore, it can be concluded as Eq.(15). As the value of the right-hand side of the inequality is related to the
generator and auxiliary distribution Q ( c | x ) , it is abbreviated as L1 ( G , Q ) . Eq.(15) shows that the maximization of the
auxiliary distribution Q ( c | x ) can be used to approximate the lower bound of the mutual information I ( c; G ( z, c )) , and
L1 ( G , Q ) can be estimated by Monte Carlo sampling.

I ( c; G ( z , c ) )  E x ~ G ( z , c ) E c '~ P ( c| x ) log Q ( c ' | x ) + H ( c ) = L1 ( G, Q )

(15)

To sum up, the objective function of Info GAN can be replaced by Eq.(16):
min max VInfo ( D, G, Q ) = V ( D, G ) −  L1 ( G, Q )
G ,Q

(16)

D

From the perspective of the model structure, since the auxiliary distribution is introduced into the objective function,
the neural network needs to be used to parameterize Q in the network structure. In Info GAN, the network parameters of
Q rely on the discriminator network. Except for the difference in the number of outputs of the last layer of Dense, the
parameters of the remaining layers are consistent with the discriminator network, which only adds a minimal
computational cost to the original GAN. The workflow structure of Info GAN is shown in Figure 5. The role of the
generator includes synthesizing the noise z and the latent vector c into fake data, and under the guidance of the
discriminator to ensure that the generated data is consistent with the real data distribution; The classification network
extracts and classifies the latent vector c in the fake data, and after the training is completed, the test set is input into
the network to classify the latent vector c . The role of the discriminator is to adjust the parameters under the training of
real data, reject the pseudo data synthesized by the generator, guide the generator to generate more realistic data, and
prevent the generator from generating distorted data in order to make it easier for the classification network to extract
the latent vector c .
The setting of the latent vector c should have a significant impact on the data synthesis, so that the classification
network can recover and extract the latent vector according to the synthesized data. In this paper, the main purpose is to
classify and detect intrusion traffic, so the latent vector chooses One-hot encoding, and the number of encodings depends
on the number of classifications.

Latent
vector c

Random
noise z
D_loss
G_loss

Generator

Input data

Loss function

G(z)

c

Fake data

Classification
network Q

Labeling
G(z)
（Label=0） y=0

Discriminator

Latent vector
c result

Result
Output：0/1

x
y=1

Labeling
（Label=1）

Output result

Q_loss

Loss function
Network Parameter Sharing

Figure 5. Info GAN structure diagram.

The classification network Q in Info GAN relies on the discriminator. The parameters of the two networks are
shared and only differ in the final output Dense layer. The classifier, discriminator and generator structures are shown
in Figure 6.
Input

Batch_Normalization

Input
(Noise z)

Conv2DTranspose
(3×3 128 V)

4×4 Conv2D
(64 stride 2 S)

Flatten

Dense
(4×4×512)

Batch_Normalization
ReLU

Batch_Normalization
ReLU

Conv2DTranspose
(3×3 64 V)

Reshape
(4,4,512)

Batch_Normalization
ReLU

Conv2DTranspose
(4×4 256 V)

Conv2DTranspose
(2×2 1 V)

Batch_Normalization
ReLU

Tanh

LeakyReLU

Dense
(1)

4×4 Conv2D
(128 stride 2 S)

Sigmoid

Dense
(128)
Batch_Normalization
LeakyReLU
Dense
(c)

LeakyReLU
Output

Softmax

4×4 Conv2D
（256 stride 1 S）

Output

LeakyReLU

Discriminator

Output
(fake data)

Classifier

(a)

(b)

Figure 6. Discriminator, classifier, generator structure of Info GAN model: (a) Classifier and discriminator network
structure; (b) Generator network structure

As shown in Figure 6(a), the classifier and the discriminator share a 3-layer convolutional layer structure. The
activation function used in the convolutional layer is LeakyReLU, and the input of the network is the preprocessed
training set traffic data. The meaning of the specific parameters of each layer is as follows: "N×N" represents the size of
the convolution kernel of the two-dimensional convolution layer; In "(n stride m S/V)", n represents the number of
channels, and m represents the step size; When the zero-padding method is "padding=same", it is marked as "S" in the
figure, and when "padding=valid", it is marked as "V"; The value in brackets of the Dense layer indicates the number of
channels in this layer; "(c)" of the classifier Dense layer represents the number of latent vector types.
After the Flatten layer, the discriminator uses a Dense layer with a channel number of 1 to determine the authenticity
of the sample, and the activation function uses the Sigmoid function. After the classifier goes through the Flatten layer,
it goes through the Dense layer with 128 channels and the batch normalization layer. The activation function is
LeakyReLU, the classifier passes through the Dense layer with the number of channels c and divides the latent vector
into c classes. The activation function is SoftMax function.
It can be seen from Figure 6(b) that the input of the generator includes random noise z and latent vector c , and
after batch normalization, the size is converted to 4×4×512. Through the processing of 4 deconvolution layers, the size
becomes 11×11×1, the activation function is Tanh, and the output is fake data for the discriminator to identify. The
optimizer used in the algorithm is Adam, and the learning rate is 0.0002. The loss function of the generator and
classification network Q is categorical-crossentropy. The loss function of the discriminator is binary-crossentropy.

3.3 Open set detection method based on OpenMax structure

Required:
1. The activation vector of the previous layer of the SoftMax function of each sample v ( x ) = v1 ( x ) , v2 ( x ) ,..., vN ( x )
2. Known class data labels label = 1, 2,..., N
3. Training convergent Info GAN model under closed-set condition: q_model
4. Closed-set test set data and labels x = x1 , x2  ,..., x N  , y = label
Procedure:
from libMR import FitHigh
1: S = get _ correct _ vector ( v ( x )) //Retain the activation vectors of the samples correctly classified by q_model.
2: for j = 1
3:

N do

for i = 1, 2...len (S j ) do// i iterates over the index of the samples





4:

Si , j = v1 ( xi , j ) , v2 ( xi , j ) ,..., vN ( xi , j )

5:

 j = mean   Si , j  //Calculate the mean activation vectors (MAV) of the samples

6:

 j = ( j ,  j ,  j ) = FitHigh || S j −  j ||,

7:

if j £ a

8:
9:
10:
11:
12:
13:


 i




) //Calculate Weibull distribution parameters

 +1− j


rank _  ( j ) =

else

(

rank _  ( j ) = 0

end for
for i = 1 N do
s ( i ) = argsort ( Si , j )

  x −

s (i )






 s( i )


)



14:

s ( i ) ( x ) = 1 − rank _   (1 − exp  − 

15:

v s ( i ) ( x ) = vs ( i ) ( x )  s ( i ) ( x ) //Known class activation vectors after recalibration

 


s ( i )

16: end for
17: end for
18: v 0 ( x ) =  i v i ( x ) (1 − i ( x ) ) //Calculate the unknown class activation vector
19: P ( y = j | x ) =

ev ( x )
j

 e ()
N

vi x

, j = 0...N //Recalculate the probability of each class

i =0

20: y* = argmax P ( y | x ) //Output the class with the highest probability as the result

Algorithm I—OpenMax algorithm
The closed-set deep learning model cannot detect unknown category data because the model usually uses the
SoftMax function as the activation function at the Dense layer of the category output. Let the number of categories of
the data in the closed set be y = 1, 2,..., N . The SoftMax function is a gradient logarithmic normalization tool in the class
probability distribution. Its function is to convert the vector z into a vector  ( z ) with element values  0，
1 , and the
sum of the element values is 1. The input of the SoftMax function is the N-dimensional node weight vector processed
by the Dense layer, which is called the Activation Vector (AV), which can be expressed as follows:
v ( x ) = v1 ( x ) , v2 ( x ) ,..., vN ( x ) . The calculation method of the SoftMax function is shown in Eq.(17).
P ( y = j | x) =

e

v j ( x)

 e ()
N

vi x

(17)

i =1

vi ( x )

In the Eq.(17), the denominator sums e
for all known classes to ensure that the probabilities of all class outputs
sum to 1. In the open-set recognition task, it is inappropriate to make the sum of the probabilities of the classes belonging
to the known set equal to 1. Therefore, the SoftMax function needs to be replaced, and the probability that the category

belongs to the unknown set is introduced on the basis of maintaining its original function.
The open set detection method based on OpenMax can achieve the above purpose. The algorithm uses the activation
vector x of the previous layer of the SoftMax layer as input to avoid logical normalization of the activation vector by the
SoftMax function. The distribution of the input activation vectors is calculated by EVT, and it is found that these
distributions obey the Weibull distribution [43]. The OpenMax algorithm can be summarized in Algorithm I.
The above code introduces the main calculation process of the OpenMax algorithm, where S represents the set of
samples correctly classified by q_model. Here, S j  represents the set of samples of each label, j represents the class
of label, Si , j represents a specific sample in the sample set whose label is j .
The tail size  represents the number of correctly classified samples used to fit the Weibull distribution. The
selection method of the tail is as follows: the samples in the sample set S are divided into S j  according to the labels
and || S j −  j || represents the distance value between AV of the sample and the MAV of this class. For each sample, the
distance || S j −  j || is calculated separately. The distance values are then sorted from large to small, and the first 
distance values are selected to form the tail according to the tail size.
Required:
1. Tail distance between sample AV and MAV {x}, x j =|| S j −  j ||
2. Tail size 
Procedure:
from libMR import FitHigh
1: x = ln x
2: range = max(x) − min( x)
3: for j = 1... do
4:

dj =

x j − max(x)
range

5: end for


6: mean =


j =1

dj



  ( x j − mean)2 
7: std = sqrt   j =1

 −1


6  std

8: sigmahat =
9: suma =






j =1

e

d j / sigmahat


10: muhat = sigmahat  ln ( suma )

11: scale = exp ( range  muhat + max(x) ) // Scale parameter 
12: shape =

1
range  sigmahat

// Shape parameter 

Algorithm II—FitHigh algorithm
Alpha rank  represents the number of label types that need to adjust the activation vector   (0, N ] and should
be a positive integer. The algorithm fits a Weibull distribution using the FitHigh function of the libMR module. The
value of the tail size  determines the number of distance values participating in the Weibull distribution fitting, which
affects the parameters of the  j in the OpenMax algorithm,  j represents the scale parameter,  j represents the shape
parameter, and  j represents the location parameter. The default value of  j is 0, and the values of  j and  j are
calculated by the FitHigh function. The FitHigh algorithm can be summarized in Algorithm II.

4 Results and Discussion

4.1 Preprocessing of the dataset
The experiment used the CICIDS2017 intrusion traffic data set expanded by WGAN-div[44] as the experimental
data. The CICIDS2017 dataset is an intrusion traffic feature dataset established by the Canadian Institute of Cyber
Security based on normal and attack type traffic captured within five days[45]. The attack traffic in this dataset included
several small categories, and the data was uniformly identified with six types of attack traffic according to the major
categories, namely Botnet, Brute Force, DoS, Infiltration, PortScan, and Web Attack. The steps of experimental data
preprocessing are as follows:
(1) Data cleaning and removal of redundant features. After analysis, it was found that not all the features of the
samples in the data set had valid values, with some data displaying the value NAN on the feature "Bwd Packet Length
Max". The value Infinity appeared on the features "Bwd Packet Length Max" and "Bwd Packet Length Min". Intrusion
detection algorithms could not read these values which needed to be removed or replaced. This paper replaced the NAN
value with the average value of the data of its type in this dimension, and the Infinity value was replaced with the
maximum value of the data of its type in this dimension[46] to realize data cleaning of outliers. The "fwd_header_length"
feature in the dataset appeared twice, and the data values of each sample were the same, necessitating the removal of
redundant columns.
(2) Remove all zero features. There were a total of 10-dimensional features in the data set, which took the value of
0 on all samples and could not play a feature role in intrusion detection. Such features are called all-zero features. In the
CICIDS 2017 dataset, they are as follows: Bwd PSH Flags, Fwd URG Flags, Bwd URG Flags, CWE Flags Count, Fwd
Avg Bytes/Bulk, Fwd Avg Packets/Bulk, Fwd Avg Bulk Rate, Bwd Avg Bytes/Bulk, Bwd Avg Packets/Bulk, and Bwd
Avg Bulk Rate. All zero features were removed during this study to improve model accuracy.
(3) Remove irrelevant network flow features. These features included the source address, destination address,
source port number, destination port number, collection time and serial number, amongst others, of the traffic collected,
which were used to distinguish network traffic. The format of these features was not suitable for the intrusion detection
model to read. These features were Flow ID, Source IP, Destination IP, Timestamp, Source Port, and Destination Port
in the dataset.
(4) After the above features were removed, the data set features were reduced from 85 to 69 dimensions, and the
samples of the remaining features were normalized according to Eq.(18). To adapt to the input size of the intrusion
detection model, zero-padded the feature dimension of the processed samples to expand to 121 dimensions. The data
was then randomly rearranged according to the label and modified the size to be two-dimensional.
x* =

x − xmin
xmax − xmin

(18)

The test set data was labeled to evaluate the model's performance, whilst the training set was not labeled.

4.2 A traffic classification model for open-set detection based on misuse detection
The model proposed in this section is an open-set misuse detection algorithm suitable for closed-set models with
normal traffic and a certain amount of intrusion traffic characteristics. Firstly, the intrusion traffic detection algorithms
based on SoftMax and OpenMax were designed to test their ability to classify known traffic and detect unknown traffic.
Then, according to the advantages and disadvantages of the two, an O-S open-set detection traffic classification model
was proposed, and its performance analysed.

4.2.1 Open set detection classification model and performance analysis
This section primarily evaluates the detection performance of the open-set detection model on unknown class
datasets and the classification performance on known traffic. Firstly, the intrusion traffic classification model based on
Info GAN was trained, and the classification performance of the unsupervised learning model was evaluated using the
accuracy rate, precision rate, recall rate, and F1 score [47] and the calculation formula is as Eq.(19). The definition of
each parameter in the formula is as follows: TP represents the number of positive examples that are correctly classified,
FN represents the number of positive examples that are wrongly classified as negative examples, TN represents the
number of negative examples that are correctly classified, and FP represents the number of positive examples that are
wrongly classified as positive examples. The higher the accuracy rate, the better the overall performance of the algorithm;

the higher the precision rate and recall rate, the lower the false alarm rate of the algorithm.
TP + TN
TP + TN + FP + FN
TP
Precision =
TP + FP
TP
Recall =
TP + FN
Precision  Recall
F1 = 2 
Precision + Recall

Accuracy =

(19)

The distribution of experimental data is shown in Table 1. Figure 7 shows the change of the loss function G_loss
of the generator, the loss function D_loss of the discriminator, and the loss function Q_loss of the classifier in the Info
GAN model with the number of training epochs during the training process of the training set. As the number of training
rounds increased, the loss function value of the model first gradually decreased, and the value between epoch=305~360
reached the minimum. In epoch=400~700, the value of the loss function fluctuated considerably, and then with the
increase in the number of training rounds, the value tended to be stable and gradually decrease, which indicates that the
model was close to convergence. Overall, the value of G_loss changes less than the other two, and the value of D_loss
changes the most.
Table 1 Data distribution of CICIDS2017 intrusion traffic dataset.
Data type

Quantity (training)

Proportion (training)

Quantity (test)

Proportion (test)

Normal

3048

13.26%

30958

14.43%

Botnet

3139

13.66%

30485

14.21%

Brute Force

3273

14.24%

30801

14.36%

DoS

3479

15.14%

30142

14.05%

Infiltration

3483

15.15%

30422

14.18%

PortScan

3078

13.39%

30916

14.41%

Web Attack

3486

15.17%

30792

14.35%

Total

22986

100.00%

214516

100.00%

Figure 7. Loss function change curve of Info GAN model

This study first examined the classification performance of the Info GAN model under the closed set condition. The
Info GAN model adopted Adam as the optimizer with a learning rate of 0.0002, and the loss function of the generator
and classification network Q was categorical-crossentropy. The loss function of the discriminator was binarycrossentropy, and the activation function used by the model was SoftMax. The number of latent vector categories was
set to 7. The classification performance evaluation and confusion matrix of the intrusion traffic classification model
based on Info GAN are shown in Table 2 and Figure 8. The classification of the closed set was carried out using all the
data in Table 1. Table 2 shows the evaluation results of the classification performance of various types of traffic
according to the precision rate, recall rate and F1 score, and the maximum value on the evaluation criteria of each
category is bolded.
The above results show that the intrusion traffic classification model based on Info GAN can effectively classify
all types of intrusion traffic, and maintain a high classification accuracy rate, with the overall classification accuracy rate

reaching 96.01%. The model had the highest precision rate for the classification of Portscan traffic, reaching 99.6%, and
it had the highest recall rate and F1 score for the classification of Infiltration traffic, which were 99.9% and 99.7%
respectively. The recall rate of Normal traffic was lower than other types of traffic, which indicates that more Normal
type traffic was misclassified as other types, resulting in confusion between Normal traffic and other types of traffic.
The closed set recognition performance of the classifier had a strong correlation with the open set recognition
performance [48], and the high-precision closed set recognition effect provided more correctly classified samples to
participate in the calculation of MAV by the OpenMax algorithm. The generalization and accuracy of MAV were
improved, which in turn improved the open-set recognition performance of the model.
Table 2 Detailed results of closed test set multi-classification.
Precision

Recall

F1-score

Normal

0.957

0.788

0.864

Botnet

0.940

0.990

0.964

Brute force

0.971

0.988

0.979

DoS

0.890

0.987

0.936

Infiltration

0.994

0.999

0.997

Portscan

0.996

0.984

0.990

Web attack

0.979

0.988

0.984

Figure 8. Confusion matrix for closed test set classification by Info GAN model

In the experiment of unknown intrusion traffic detection, six types of intrusion traffic were regarded as unknown
set traffic, and one type of intrusion traffic was selected as unknown traffic in turn. After determining the type of traffic
to be selected as the unknown set, the normal traffic of the training set of the closed-set classification model and the
other 5 types of intrusion traffic data were used as input. Eliminating the traffic was used as the unknown set from the
training set. When the closed-set classification model reached convergence, the OpenMax algorithm in Section 3.3 was
used to adjust the AV of the sample, and to introduce the probability of unknown categories. A good unknown traffic
detection model should have both high classification accuracy for known traffic and a high detection rate for unknown
traffic. The open-set traffic of the model included traffic types belonging to closed-set training and unknown traffic
types. The open-set was used to evaluate the performance of the intrusion traffic detection models with activation
functions SoftMax and OpenMax to test their ability to classify known traffic and the ability to detect unknown traffic.
The experiment sets up the set of candidate values of hyperparameters  and  , as shown in Eq.(20). Figure 9
shows the classification accuracy of intrusion detection classification model based on the OpenMax algorithm on the
open test set under all hyperparameter values.
In each picture, the open test set contains different types of unknown traffic, with the unknown traffic category
indicated in the title of the picture. In Figure 9(a), the unknown flow detection model used the Euclidean distance to
calculate the distance value between the sample AV and this type of MAV; in Figure 9(b), the unknown flow detection
model used the cosine distance to calculate the above distance.
 = 2500 + 2500 N  , N  0,11
 = 4,5,6

(20)

(a)

(b)
Figure 9. The effect of hyperparameters on accuracy: (a) The effect of hyperparameters on accuracy (Euclidean distance);
(b) The effect of hyperparameters on accuracy (Cosine distance)

Figure 9 illustrates that the values of hyperparameters  and  both affect the test accuracy of the open set. From
Figure 9, the following conclusions can be drawn:
(1) When the alpha rank  remains unchanged, and when the tail size  is    2500,17500 , the detection
accuracy of the model for most unknown traffic fluctuates in different magnitudes. In this interval, the model obtains the
maximum value of the detection rate of unknown traffic. As the value of the tail size continues to increase, the detection
accuracy of the model for unknown traffic decreases. This shows that when the tail size is too large, the model enters a
state of overfitting, and traffic classification becomes overconfident. This makes the model misclassify more unknown
class traffic as known classes.
(2) When the value of alpha rank is different, the detection accuracy curve has a similar trend of change, which is
especially apparent for the unknown types of models such as DoS, Web attack and PortScan. When   17500,30000 ,

the unknown detection rate of the model at  =6 was higher than the other two, and the slope of the curve descent was
gentler. When  =6 , the model had the highest unknown detection rate for most types of unknown traffic. This shows
that with the increase of alpha rank, the stability of the model gradually increases, and the performance of open set
detection and recognition also improves.
Figure 10 shows the highest detection rates of the OpenMax model using Euclidean and cosine distances for
different unknown flows. When the model used the cosine distance to calculate the distance between the AV of the
sample and the MAV of the class, the highest detection accuracy for all types of unknown traffic was higher than that
using the Euclidean distance. Therefore, it can be concluded that the cosine distance is suitable for unknown traffic
detection models. Based on the above discussion, the most suitable hyperparameter values and distance types for each
unknown traffic were selected according to the model's detection accuracy for unknown traffic, with the results shown
in Table 3.
Table 3 Hyperparameter selection results.
Unknown traffic type

Alpha rank

Tail size

Distance type

Botnet

6

12500

Cosine

Brute force

4

5000

Cosine

DoS

6

2500

Cosine

Infiltration

5

7500

Cosine

Portscan

6

7500

Cosine

Web attack

6

17500

Cosine

Figure 10. Influence of distance type on detection accuracy.

Since the SoftMax algorithm does not perform computations for unknown class probabilities, its performance is
not affected by hyperparameters. Selecting the corresponding hyperparameters according to Table 3 and evaluating the
unknown traffic detection performance of the models based on OpenMax and SoftMax. Table 4 and Figure 11 show the
accuracy, precision, recall, and F1 scores of the two models for different types of unknown traffic detection results. It
should be noted that the open set contains different types of unknown traffic and normal traffic and known types of
attack traffic. The evaluation results mentioned above are a comprehensive evaluation of the known traffic classification
performance and unknown traffic detection performance of the model. Each row in Table 4 represents the detection
performance of SoftMax and OpenMax-based models for different types of unknown traffic. The data marked in bold
indicate the maximum value of each column of data in the table. It indicates that the model has the best classification
performance for this type of open set, The following conclusions can be drawn from Table 4 and Figure 11.
The overall performance of the OpenMax-based open-set detection traffic model is better than the SoftMax-based
model and, with the exception when the unknown traffic type is Infiltration, the accuracy rates of the two models are
similar. In other cases, the evaluation results of the OpenMax-based model for different types of unknown traffic are
higher than that of the SoftMax-based model.
It can be seen from the results in Figure 8 that the SoftMax algorithm can classify traffic of known types with high
precision. The reason for the performance degradation, such as the classification accuracy of SoftMax-based models, is
the misclassification of unknown types of traffic. This shows that the OpenMax algorithm is effective in detecting
unknown traffic, meaning that the model can detect unknown traffic while maintaining good classification performance
for known types of traffic.

Table 4 Performance evaluation of Open-set detection for SoftMax and OpenMax models.
Unknown traffic type

SoftMax

OpenMax

Accuracy

Precision

Recall

F1-score

Accuracy

Precision

Recall

F1-score

Botnet

0.814

0.749

0.812

0.768

0.847

0.881

0.846

0.855

Brute force

0.837

0.752

0.839

0.786

0.909

0.916

0.910

0.912

DoS

0.818

0.742

0.814

0.769

0.899

0.904

0.899

0.900

Infiltration

0.795

0.716

0.794

0.749

0.793

0.873

0.794

0.811

Portscan

0.768

0.744

0.770

0.734

0.905

0.920

0.905

0.907

Web attack

0.817

0.734

0.819

0.770

0.835

0.900

0.836

0.849

Figure 11. Performance evaluation of Open-set detection for SoftMax and OpenMax models.
Table 5 Detailed results of open-set detection of SoftMax and OpenMax models.
Unknown type
Botnet
Brute force
DoS
Infiltration
Portscan
Web attack
Unknown type
Botnet
Brute force
DoS
Infiltration
Portscan
Web attack

model
S
O
S
O
S
O
S
O
S
O
S
O
model
S
O
S
O
S
O
S
O
S
O
S
O

Normal
Rec
F1
0.941 0.635
0.866 0.761
0.927 0.685
0.877 0.814
0.844 0.610
0.851 0.790
0.696 0.522
0.514 0.633
0.934 0.560
0.879 0.850
0.788 0.585
0.594 0.717
Infiltration
Pre
Rec
F1
0.995 0.997 0.996
1.000 0.991 0.995
0.998 0.997 0.998
1.000 0.989 0.994
0.996 0.997 0.997
1.000 0.983 0.991
\
\
\
\
\
\
0.997 0.997 0.997
1.000 0.980 0.990
0.993 0.998 0.996
1.000 0.983 0.992
Pre
0.479
0.678
0.544
0.760
0.477
0.737
0.417
0.825
0.400
0.823
0.465
0.903

Botnet
Rec
F1
\
\
\
\
0.991 0.985
0.913 0.931
0.992 0.954
0.960 0.949
0.997 0.964
0.885 0.910
0.570 0.720
0.782 0.858
0.997 0.949
0.840 0.898
Portscan
Pre
Rec
F1
0.994 0.979 0.986
1.000 0.967 0.983
0.993 0.990 0.991
1.000 0.980 0.990
0.992 0.990 0.991
1.000 0.965 0.982
0.959 0.990 0.974
1.000 0.926 0.962
\
\
\
\
\
\
0.994 0.988 0.991
1.000 0.935 0.966
Pre
\
\
0.980
0.949
0.919
0.939
0.933
0.936
0.977
0.951
0.905
0.963

Brute force
Rec
F1
0.981 0.969
0.735 0.836
\
\
\
\
0.995 0.901
0.977 0.952
0.993 0.912
0.735 0.828
0.990 0.966
0.964 0.961
0.993 0.936
0.732 0.831
Web attack
Pre
Rec
F1
0.851 0.989 0.915
0.971 0.892 0.930
0.781 0.995 0.875
0.981 0.949 0.965
0.987 0.882 0.931
0.986 0.847 0.911
0.969 0.909 0.938
0.986 0.790 0.877
0.903 0.976 0.938
0.985 0.911 0.947
\
\
\
\
\
\
Pre
0.957
0.968
\
\
0.823
0.927
0.844
0.948
0.944
0.959
0.886
0.960

Pre
0.969
0.999
0.965
0.996
\
\
0.891
0.996
0.990
0.998
0.896
0.994
Pre
0.000
0.548
0.000
0.728
0.000
0.738
0.000
0.417
0.000
0.728
0.000
0.477

DoS
Rec
F1
0.797
0.874
0.743
0.852
0.972
0.969
0.917
0.955
\
\
\
\
0.971
0.929
0.824
0.902
0.923
0.955
0.839
0.912
0.972
0.932
0.840
0.911
Unknown
Rec
F1
0.000
0.000
0.731
0.626
0.000
0.000
0.743
0.735
0.000
0.000
0.706
0.722
0.000
0.000
0.887
0.567
0.000
0.000
0.977
0.834
0.000
0.000
0.924
0.629

Table 5 shows the detailed detection results of the SoftMax-based and OpenMax-based models on the open set data.
The first column of the table represents the type of unknown traffic in the open set. Model "S" indicates the detection
result of the SoftMax-based model, and model "O" indicates the detection result of the OpenMax-based model. The
bolded "Normal, Botnet, ..., Web attack" etc. represents the classification results of known traffic in the open set. There
are corresponding unknown traffic in the open set, so when this type of traffic is unknown traffic, the classification result
is represented by "\" and "Unknown" represents the detection result of the model on the unknown traffic in the open set.
"Pre" means Precision, "Rec" means Recall, and "F1" means F1 score. Combining Table 2 and Table 5, the following
conclusions can be drawn:
(1) The SoftMax-based model achieved a classification accuracy of 0.957 for normal traffic in the closed set
classification test. In contrast, the model’s classification accuracy for normal traffic in the open set classification test

dropped significantly. However, the recall rate remained high, and the classification accuracy of other known types of
traffic did not drop significantly. This shows that the SoftMax-based model misclassified the unknown traffic in the open
set as normal traffic, which resulted in a significant drop in the classification accuracy of only normal traffic.
(2) The model based on OpenMax has a detection recall rate of over 70% for various types of unknown traffic.
When the unknown traffic type is Portscan, the model has the highest detection recall rate of unknown classes, 97.7%.
This shows that the model can effectively detect traffic types that do not appear in the training set and identify different
types of unknown traffic. However, the detection accuracy of unknown classes was generally low, indicating that
although the model can accurately detect unknown types of traffic from the open set, it also misclassifies known types
of traffic as unknown traffic, resulting in false alarms.
(3) The recall rate of the SoftMax-based model for known types of traffic was generally higher than that of the
OpenMax-based model, indicating that the former has better classification performance for known traffic than the latter.
OpenMax-based models introduce probabilistic estimates for unknown traffic, but also lead to false alarms for unknown
types of traffic. Compared with the former, the classification performance of known types of traffic was degraded,
although the model still can effectively identify and distinguish known types of traffic.

Figure 12. Confusion matrix for open set detection of OpenMax model.

Figure 12 shows the confusion matrix for the OpenMax-based model for the detection and classification of openset traffic. From the confusion matrix, the model can detection different types of open sets at the simultaneously, but
there are false alarms in the detection of unknown traffic, i.e., known traffic is misclassified as unknown traffic. When
the unknown traffic is Infiltration and Web attack, the false alarm rate is the highest. According to Eq.(21), when the
unknown traffic types are Infiltration and Web attack, the false positive rates (FPR) of the two models are 20.3% and
17.1%, respectively. When the unknown traffic is Botnet, Brute force, or DoS, the model confuses the identification of
some unknown traffic and normal traffic. This problem can be solved by using a fine-grained classification method, as
described in Section 4.3.
This section proposes an OpenMax-based Info GAN model, which can detect and classify open-set traffic. The
model can efficiently classify known classes of traffic (normal traffic and known types of attack traffic). Compared with
the closed-set model using the SoftMax algorithm, the OpenMax model introduces an unknown class activation vector,
adjusts the classification probability, and can detect unknown class traffic.

4.2.2 O-S open-set traffic detection classification model and performance analysis
By comparing the performance of the two models in Table 5, it was found that the SoftMax-based model had better
classification performance for known types of traffic than the OpenMax-based model, but the SoftMax algorithm could
not detect unknown types of traffic that have not appeared in the training set. The OpenMax-based model can detect
unknown types of traffic, but due to the introduction of probability estimation of unknown types, the model demonstrates
different degrees of false alarms under different open sets, and the ability to identify known types of traffic was reduced.

In response to this problem, this section proposes an open-set detection method that combines SoftMax and OpenMax
algorithms, namely the O-S open-set traffic detection and classification model.
The structure of the O-S open-set traffic detection and classification model is shown in Figure 13. The principle is
to play the respective advantages of the open-set detection model and the closed-set intrusion classification model, that
is, the high classification accuracy of the SoftMax algorithm for known traffic and the high-precision detection rate of
the OpenMax algorithm for unknown traffic. The false alarm defect of OpenMax algorithm is improved by introducing
SoftMax algorithm. In a network environment with unknown intrusion traffic, the closed-set intrusion traffic
classification model based on Info GAN and the open-set detection model based on OpenMax was first trained according
to the method shown in Figure 4. The O-S open-set detection traffic classification model uses the above two models
simultaneously for intrusion detection and classification.
Known traffic and labels and unknown traffic and labels are composed of a and b, as shown in Figure 13. Steps a1,
a2 indicate that the open-set traffic was first classified, and unknown traffic was detected using the OpenMax-based
open-set intrusion detection model. The classification result of this part of unknown traffic showed a false alarm problem,
i.e., some known traffic was misclassified as unknown traffic, resulting in poor identification performance.
The unknown traffic and labels output by step a2 are input into the closed-set Info GAN intrusion traffic
classification model trained with the same training set, namely b1. From the data conclusions in Table 5, it can be seen
that the misclassification of unknown traffic by the SoftMax-based model is mainly normal traffic. Therefore, step b2
discards the result that the closed set model is judged to be normal, i.e., if the judgment result is normal traffic, the
original label is retained and classified as unknown type traffic. Step b3 indicates that the results judged to be other types
of known traffic are retained, the original unknown label is replaced, and this part of the traffic is divided into the known
traffic result according to the new label.
In the O-S open-set traffic detection and classification model, the unknown traffic is first detected by the OpenMaxbased open-set detection model, and then the results are input into the closed-set Info GAN model to use SoftMax to
remove false-alarm misclassified traffic. Part of the known class traffic is identified and classified by the OpenMaxbased open-set detection model, and the rest comes from the adjustment, the identification and classification of the falsealarm traffic by the closed-set Info GAN model.
Open set
data

Preprocess

Open set intrusion
traffic detection
model

a2

a1

Known traffic
and label

Unknown traffic
and label
b1

b3

b2

Closed classification
model based on Info
GAN

Figure 13. O-S open set traffic detection classification model structure.

Table 6 and Figure 14 show the accuracy, precision, recall, and F1 scores of the O-S model for different types of
unknown traffic detection results. Table 8 shows the detailed results of the O-S model for classification and detection on
the open set. Figure 15 shows the confusion matrix for O-S model detection and classification of open set traffic.
Comparing and observing Table 4, Table 6, Table 5, and Table 7, the following conclusions can be drawn:
(1) The overall performance of the O-S model was better than that of the OpenMax-based model. Comparing Table
4 and Table 6, when the unknown traffic was Brute force, the performance of the two was similar. In the classification
and detection of other types of open sets, the performance of the O-S model was better than that of the OpenMax model.
The O-S model had the most obvious improvement in the classification and detection performance of the open set with
unknown traffic type of Infiltration, and the classification accuracy rate increased from 79.3% to 89.3%. The accuracy,
precision, and recall rate of the O-S open set classification detection model were above 88%, which shows that the
SoftMax algorithm to deal with false alarm traffic can effectively solve the defects of the OpenMax algorithm and reduce
the error of known traffic. classification, and improved the performance of the model.
(2) Comparing the data in Table 5 and Table 7, it can be found that the precision rate of the O-S model for unknown
traffic detection was higher than that of the OpenMax-based model, indicating that the number of known traffic
misclassified as unknown reduced. Figure 15 shows that compared with the OpenMax-based model, the number of false
alarm traffic detected by unknown is less. When the unknown traffic is Infiltration and Web attack, the false alarm rate
reduces from 20.3% and 17.1% to 3.2% and 3.8%.
(3) Compared with the OpenMax model, the O-S model had similar classification accuracy and recall for known
traffic. However, when the unknown traffic was Botnet and Brute force, the detection recall rate of O-S for unknown

traffic dropped significantly. Through the confusion matrix, it was found that in the process of detecting and classifying
these two open sets, the O-S model misclassifies the unknown traffic correctly classified in step a1 as the type of Web
attack when performing the detection and classification of step b3 in Figure 13. The preset algorithm prevented the O-S
model from misclassifying unknown traffic as normal traffic in step b3, but it was difficult to handle the behavior of
misclassifying unknown traffic as known other types of attack traffic.
Table 6 Performance evaluation of O-S open set detection model.
Model

O-S
Accuracy

Precision

Recall

F1-score

Botnet

0.885

0.893

0.883

0.882

Brute force

0.901

0.912

0.902

0.895

DoS

0.912

0.921

0.911

0.911

Infiltration

0.893

0.891

0.894

0.886

Portscan

0.930

0.934

0.929

0.930

Web attack

0.908

0.909

0.909

0.903

Figure 14. Performance evaluation of the O-S open set detection model.

To summarize, this section proposes an O-S model, which first performs known traffic classification and unknown
traffic detection through OpenMax's method. The traffic judged to be unknown is then input into a SoftMax-based
closed-set model, using SoftMax to eliminate false alarm traffic for known traffic. Because the SoftMax algorithm cannot
detect unknown traffic, it misclassified unknown traffic as normal traffic. Therefore, when classifying the open set with
the SoftMax model, the model's label classified as normal traffic should be ignored to avoid misclassification of real
unknown traffic. The O-S model detected unknown traffic in the open set with better overall performance than that of
the OpenMax model by reducing the number of false alarm traffic and improving the accuracy of unknown traffic
detection.
Table 7 Detailed results of O-S model open set detection.
Unknown type
Botnet
Brute force
DoS
Infiltration
Portscan
Web attack
Unknown type
Botnet
Brute force
DoS
Infiltration
Portscan
Web attack

Normal
Rec
F1
0.866 0.761
0.877 0.814
0.851 0.790
0.514 0.633
0.879 0.850
0.594 0.717
Infiltration
Pre
Rec
F1
0.995 0.997 0.996
0.998 0.997 0.998
0.998 0.997 0.998
\
\
\
0.997 0.997 0.997
0.993 0.998 0.996
Pre
0.678
0.760
0.737
0.825
0.823
0.903

Pre
\
0.953
0.918
0.932
0.951
0.907
Pre
0.994
0.994
0.995
0.959
\
0.994

Botnet
Rec
F1
\
\
0.995 0.974
0.991 0.953
0.997 0.963
0.845 0.895
0.997 0.950
Portscan
Rec
F1
0.979 0.986
0.990 0.992
0.989 0.992
0.990 0.974
\
\
0.988 0.991

Brute force
Rec
F1
0.981 0.969
\
\
0.995 0.918
0.993 0.912
0.990 0.965
0.993 0.936
Web attack
Pre
Rec
F1
0.854 0.977 0.912
0.781 0.995 0.875
0.985 0.873 0.926
0.969 0.909 0.938
0.905 0.975 0.939
\
\
\
Pre
0.957
\
0.852
0.844
0.941
0.886

Pre
0.969
0.965
\
0.891
0.998
0.896
Pre
0.806
0.933
0.965
0.817
0.923
0.785

DoS
Rec
F1
0.803
0.878
0.972
0.969
\
\
0.971
0.929
0.844
0.914
0.972
0.932
Unknown
Rec
F1
0.581
0.675
0.491
0.643
0.681
0.799
0.886
0.850
0.977
0.949
0.822
0.803

Figure 15. Confusion matrix for open set detection of O-S model.

4.3 Abnormal traffic detection and classification system and performance analysis
This section proposes an anomaly traffic detection and classification system, which combines the advantages of
unsupervised learning and OpenMax algorithm based on anomaly detection technology, so that the system has the
function of anomaly detection. Given that the detected unknown traffic is recorded, and the Info GAN model does not
need to label the traffic, the next time the same type of traffic is encountered, it was processed by the method of known
class traffic classification. That is, the classification model was retrained by using the updated intrusion traffic database
to expand the intrusion traffic categories that can be classified by the model. When the same type of intrusion traffic is
encountered later, the model can classify it as a known traffic class. The feature of anomaly detection technology is that
the system only records normal traffic and behavior and detects the deviation between normal traffic and intrusion traffic.
By observing the confusion matrices in Figs.12 and 15, it is found that even when the model learns the characteristics of
normal traffic and known intrusion traffic, the OpenMax-based and O-S models still misclassify some unknown traffic
as normal traffic. In anomaly detection technology, this situation leads to the missed alarm of intrusion traffic, and an
effective anomaly detection model cannot be established, thus bringing the risk of intrusion to the user system.
The reason for the missing alarm problem is that Table 1 follows the same traffic type division method as the
CICIDS2017 data set. It categorizes normal traffic in the training set into a single class and labels it with the same label.
Normal traffic may have multiple behavioral patterns. For the Info GAN model with high classification accuracy for
normal traffic, its classification decision range usually covers normal traffic with multiple behavior patterns. Figure 16(a)
shows the above situation, i.e., the range of the model's classification decision for normal traffic is too wide, which can
ensure a high recognition rate of the model for normal traffic in the test set, but also leads to the distance confusion
problem. The distance confusion problem is reflected in the Info GAN model that the distance between normal traffic
may be greater than the distance between normal traffic and unknown traffic[49]. In this case, the SoftMax algorithm of
closed sets is overconfident in the classification of normal traffic. Unknown traffic that meets the distance confusion
problem is misclassified as normal traffic, which eventually leads to a low detection recall rate for unknown traffic.
This section proposes a fine-grained classification-based approach to address distance confusion. That is, by
clustering normal traffic into different subclasses, normal traffic with similar behavior patterns can be clustered together
[50]. Label each subclass with a different label and train the Info GAN model under the closed set using normal traffic
with subclass labels. This subclass label is characterized by evaluating the model's performance for each subclass
classification of normal traffic based on the subclass label during training and testing of the closed-set model. In the
classification and detection of open-set traffic, when the model is confused with the subclass classification of normal
traffic, the recognition performance of the model for normal traffic is not degraded. For example, the model misclassifies
normal traffic belonging to the first subclass in the open set as the second subclass, but both of the above two subclasses
belong to the labels of normal traffic, and both are regarded as normal traffic labels when evaluating the open set. The
purpose of the above method is to limit the scope of the Info GAN model's classification decision for normal traffic, and

to make the model learn more fine-grained features of normal traffic by classifying subclass traffic. When the model
converges on the fine-grained-based normal traffic training set, its classification decision range can be represented by
Figure 16(b). At this time, the model can accurately classify each subclass of normal traffic and ensure that the distance
between normal traffic of the same subclass is smaller than the distance between normal traffic and unknown traffic, i.e.,
the distance confusion problem is eliminated.
3

3

a

3

3
33
3 3

3

3

3

?
? ? ?
? ??
?
? ?
? ???
3 3

?

3

b

a
aa
a a

3

3

a
b

b

b

b

b

?
? ? ?
? ??
?
? ?
? ???
c c

?

3
3

3

(a)

c

c
c

c

(b)

Figure 16. The impact of single class and fine-grained classification on model classification performance.

The datasets used in the anomaly detection experiments based on fine-grained classification are shown in Table 8.
The first column of normal traffic in Table 8 is used to train the Info GAN model under the closed set, the label of normal
traffic is set to 0, and the label has different numbers of sub-labels to train the Info GAN model. The open set in the third
column includes normal traffic and attack traffic, and the labels are set to 0 and 1, respectively. The attack traffic includes
the six types of intrusion traffic shown in Table 1. According to Eq.(2), the openness of the dataset is 0.5. In the unknown
traffic set, the attack traffic in the open set all comes from the training set intrusion traffic in Table 1, and the attack
traffic in the open set all comes from the open set intrusion traffic in Table 1. In this way, it can ensure that the proportion
of various types of intrusion traffic data in the attack traffic is similar and the distribution is balanced to test whether the
anomaly detection model can detect all types of intrusion traffic.
Table 8 Data distribution of abnormal traffic detection and classification system.
Data type
Normal
Attack

Quantity (training)
5743
\

Quantity (test)
28511
\

Quantity (open set)
3058
19855

In order to achieve a reasonable and effective fine-grained classification of normal traffic, a PCA visualization
operation was performed on normal traffic data. Figure 17 shows a PCA scatter plot for normal traffic. It can be judged
from Figure 17 that normal traffic can be divided into at least five sub-categories. Set the number of subclasses to 5~10
and use the unsupervised clustering algorithm K-means to cluster the normal traffic in the test set and the open set to
obtain the subclass label of each traffic, which is used to test the Info GAN model classification performance for subclass
traffic. In tests on the open set, Info GAN classifies normal traffic by subclass labels. However, in the final performance
evaluation, as long as the Info GAN model can classify normal traffic into one of the subclass labels, it is considered
that the model has correctly classified the normal traffic. That is, the fine-grained classification of normal traffic only
improves the performance of the Info GAN model but does not participate in the performance evaluation of the Info
GAN. The number of subclasses can be thought of as a hyperparameter on par with tail size  and alpha rank  .

Figure 17. Two-dimensional characteristic distribution of normal flow after PCA processing.

Figure 18 shows the structure of the fine-grained anomaly detection model. The experimental process of anomaly
detection based on fine-grained classification is as follows: First, the Info GAN model under the condition of closed set
was trained through the training set and test set of Normal type traffic in Table 8, and the Kmeans algorithm [51] was

used to perform unsupervised clustering and summarization according to the number of subclasses. Subclass labels were
labeled, and the processed Normal traffic was input into the Info GAN model for training, and the activation method
adopted SoftMax. It should be noted that the labels of subclass traffic were only used for model training, not for
evaluating the model's performance. When the model converges, the test set of Normal traffic was used to calculate the
MAV for each subclass of traffic. According to the OpenMax algorithm in Section 3.3, the training of the Info GAN
model under the condition of the open set was carried out. The unknown traffic dataset containing normal traffic and
various types of attack traffic in Table 1 was used as an open set to test the model's performance. When the abnormal
traffic detection model converges, the model's performance was evaluated by the open set. Figure 18 shows the basic
structure of the fine-grained anomaly detection model.
Label
Performance evaluation

Open set

Normal PCA+Kmeans
traffic Fine-grained
processing

Normal 1
Normal 2
.
.
.

Training
set

Model
training

Closed classification
When model
model based on Info GAN converges

Test set

Label
Performance evaluation

Closed model

+

OpenMax
algorithm

Open set intrusion traffic detection model

Normal s

Recording unknown data

Figure 18. Structure of an abnormal traffic detection model based on fine-grained classification.

Table 9 shows the effects of the number of normal traffic subclasses, tail size, and alpha rank on the accuracy of
the InfoGAN model for detecting unknown traffic. Among them, the first column of data represents the normal traffic
sub-category number s . The second column of data represents alpha rank  . "0.5k~20.5k" represents the tail size 
in turn. The data in the table represents the classification accuracy of the Info GAN model for the open set traffic,
including the classification of normal traffic and the detection of unknown traffic. To select the optimal value of the
parameters, the experiment sets the number of subclasses of normal traffic to be 5~10, and the values of tail size and
alpha rank are adjusted as follows:  = 500 + 2000N , N  0,10 ,  = 1, 2,3, 4,5 according to the performance of the
model in Figure 9. When calculating the sample AV and MAV, the cosine distance was uniformly used. The bold data
in the table represents the maximum value of the model detection accuracy in the case of the number of subclasses.
Table 9 Influence of parameters on the accuracy of anomaly detection classification model.
s
5

6

7

8

9

10


1
2
3
4
5
1
2
3
4
5
1
2
3
4
5
1
2
3
4
5
1
2
3
4
5
1
2
3
4
5

0.5k
0.218
0.233
0.232
0.223
0.214
0.230
0.277
0.279
0.235
0.215
0.272
0.369
0.371
0.366
0.348
0.291
0.323
0.338
0.327
0.312
0.242
0.308
0.315
0.311
0.301
0.323
0.350
0.359
0.358
0.354

2.5k
0.294
0.301
0.296
0.290
0.276
0.422
0.422
0.415
0.405
0.357
0.494
0.556
0.558
0.553
0.543
0.399
0.429
0.434
0.435
0.425
0.322
0.618
0.662
0.644
0.604
0.453
0.591
0.655
0.655
0.646

4.5k
0.397
0.436
0.394
0.365
0.295
0.484
0.482
0.446
0.423
0.390
0.555
0.586
0.644
0.630
0.582
0.433
0.524
0.561
0.542
0.503
0.392
0.735
0.789
0.755
0.692
0.551
0.711
0.815
0.822
0.800

6.5k
0.478
0.477
0.460
0.443
0.317
0.572
0.521
0.464
0.438
0.401
0.602
0.687
0.743
0.722
0.657
0.497
0.675
0.698
0.670
0.580
0.439
0.737
0.795
0.761
0.697
0.558
0.715
0.814
0.825
0.807

8.5k
0.549
0.513
0.486
0.453
0.330
0.634
0.573
0.488
0.447
0.411
0.672
0.774
0.867
0.805
0.719
0.620
0.744
0.759
0.748
0.680
0.438
0.737
0.795
0.760
0.697
0.558
0.714
0.814
0.825
0.806

10.5k
0.596
0.556
0.498
0.461
0.336
0.678
0.601
0.516
0.454
0.417
0.707
0.822
0.882
0.852
0.756
0.684
0.779
0.785
0.778
0.731
0.438
0.737
0.795
0.760
0.697
0.558
0.714
0.814
0.825
0.806

12.5k
0.596
0.556
0.498
0.461
0.336
0.678
0.601
0.516
0.454
0.417
0.707
0.822
0.882
0.852
0.756
0.684
0.779
0.785
0.778
0.731
0.438
0.737
0.795
0.760
0.697
0.558
0.714
0.814
0.825
0.806

14.5k
0.596
0.556
0.498
0.461
0.336
0.678
0.601
0.516
0.454
0.417
0.707
0.822
0.882
0.852
0.756
0.684
0.779
0.785
0.778
0.731
0.438
0.737
0.795
0.760
0.697
0.558
0.714
0.814
0.825
0.806

16.5k
0.596
0.556
0.498
0.461
0.336
0.678
0.601
0.516
0.454
0.417
0.707
0.822
0.882
0.852
0.756
0.684
0.779
0.785
0.778
0.731
0.438
0.737
0.795
0.760
0.697
0.558
0.714
0.814
0.825
0.806

18.5k
0.596
0.556
0.498
0.461
0.336
0.678
0.601
0.516
0.454
0.417
0.707
0.822
0.882
0.852
0.756
0.684
0.779
0.785
0.778
0.731
0.438
0.737
0.795
0.760
0.697
0.558
0.714
0.814
0.825
0.806

20.5k
0.596
0.556
0.498
0.461
0.336
0.678
0.601
0.516
0.454
0.417
0.707
0.822
0.882
0.852
0.756
0.684
0.779
0.785
0.778
0.731
0.438
0.737
0.795
0.760
0.697
0.558
0.714
0.814
0.825
0.806

The following conclusions can be drawn from the data in Table 9: (1) When the number of subclasses and alpha
rank are fixed, as the tail size increases, the detection accuracy of the model increases continuously. The accuracy of all
models reaches the maximum value at the tail size   10.5k , and then the accuracy of the model does not improve as

the tail size increases. (2) When the number of subclasses of normal traffic is s = 7 , alpha rank  = 3 , and tail size
 =10.5k , the detection accuracy of the model is the highest among all models, reaching 88.2%. Therefore, the above
parameter values are selected for the abnormal traffic detection and classification system.
Table 10 shows the classification results of normal traffic by the Info GAN model based on fine-grained
classification under the condition of closed set, where Normal1–Normal7 represents 7 sub-labels of normal traffic. From
Table 10, it can be found that the Info GAN model can accurately identify various types of normal traffic, and there is
little confusion between them. This shows that normal traffic can indeed be divided into different subclasses, and there
is a large distance gap between samples of different subclasses.
Table 10 Fine-grained classification results of closed-set model for normal traffic.
Precision

Recall

F1-score

Normal1

0.985

0.995

0.990

Normal2

0.998

0.992

0.995

Normal3

0.993

1.000

0.997

Normal4

1.000

0.957

0.978

Normal5

0.998

0.999

0.999

Normal6

0.995

0.996

0.996

Normal7

0.983

0.994

0.989

Table 11 shows the detection and classification performance of the abnormal traffic detection and classification
system for open-set traffic. The normal traffic used subclass labels to accurately observe the confusion between normal
traffic and unknown traffic. To verify the effectiveness of the abnormal traffic detection model, the closed-set Info GAN
model, whose activation method is SoftMax, was also evaluated on the open-set performance, and the results of the two
were compared. From Table 11, the following conclusions can be drawn:
(1) The abnormal traffic detection model has the highest detection accuracy for subcategories Normal3, Normal6,
and Normal7, reaching 100%. The OpenMax model has higher F1 scores for most normal traffic subclasses than the
SoftMax model. This shows that the abnormal traffic detection model can solve the distance confusion problem of these
sub-categories of traffic, and correctly distinguish normal traffic from unknown traffic. The model has a high recall rate
for the subcategory Normal4, but the recognition accuracy rate is low, indicating that the model misclassifies more
unknown traffic as the fourth subcategory. The main factors affecting the classification accuracy of the model for normal
traffic are the subcategories Normal1, Normal2, and Normal4.
(2) The SoftMax-based Info GAN model has a high recall rate for the detection of normal traffic, but the
classification precision is low, and it cannot detect unknown traffic. In contrast, the detection accuracy and recall rate of
the abnormal traffic detection model for unknown traffic remain above 92%, which can effectively detect most unknown
traffic.
(3) The recognition accuracy and recall rate of the abnormal traffic detection model for Normal1 and Normal2
traffic are both at low levels, the main reason is that the normal traffic was misclassified as unknown traffic. This shows
that the abnormal traffic detection model solves the distance confusion problem of most normal traffic, but some normal
traffic still has this problem.
Table 11 Detailed detection results of abnormal traffic detection model.
Data type
Normal1
Normal2
Normal3
Normal4
Normal5
Normal6
Normal7
Unknown

Precision
0.005
0.237
1.000
0.157
0.388
1.000
1.000
0.924

OpenMax
Recall
0.004
0.217
0.899
0.714
0.556
0.609
0.693
0.922

F1-score
0.005
0.227
0.947
0.257
0.457
0.757
0.819
0.923

Precision
0.191
0.077
0.949
0.088
0.069
0.180
0.203
0.000

SoftMax
Recall
0.994
0.992
1.000
0.979
1.000
0.997
0.995
0.000

F1-score
0.320
0.142
0.974
0.162
0.129
0.305
0.338
0.000

Figure 19 shows the confusion matrix for the detection of open-set traffic by the abnormal traffic model, which
merges the subclasses of normal traffic, all denoted by the label 0. Among them, the abnormal traffic detection model
had a classification accuracy of 0.552 for normal traffic, a recall rate of 0.622, and an F1 score of 0.585. The model has
a detection precision of 0.941 for unknown traffic, a recall of 0.922, and an F1 score of 0.931. Compared with the Info
GAN model based on SoftMax, the abnormal traffic model maintains a high detection accuracy for unknown traffic and
can effectively detect unknown types of attack traffic from open set traffic. Moreover, the abnormal traffic detection
model can solve the distance confusion problem of normal traffic with subclasses 3, 6, and 7 and correctly distinguish
the normal traffic from unknown traffic. The disadvantage of the algorithm is that the accuracy of the recognition of

normal traffic is lower than that of the SoftMax-based Info GAN model. This is because the anomaly detection model
still has misclassification in the detection of unknown traffic. Thus, the normal traffic with subclasses 1, 2, and 4 still
has the problem of distance confusion, which is also where the algorithm needs to be improved in the future.

Figure 19. Confusion matrix for abnormal traffic detection models.

To verify that the proposed algorithm maintains excellent classification detection performance for different
intrusion traffic datasets, we add another set of experiments in Section.4 of the paper. The Info GAN model is used to
detect and classify the NSL-KDD intrusion traffic dataset in open set conditions. The NSL-KDD dataset includes five
types of traffic data, one of which is normal traffic labeled as Normal, and the other four are attack traffic labeled as
DoS, Probing, R2L, and U2R[52]. Each attack traffic can be divided into several sub-categories. To facilitate statistical
detection, we do not distinguish among the sub-categories but classify and identify them according to the five
categories.The experiments use the same training model approach as when classifying the CICIDS2017 dataset. Tables
12 and 13 show the results of multi-classification and binary classification of the NSL-KDD dataset with the use of
OpenMax and SoftMax, respectively.
Table 12 shows the multi-classification results of the Info GAN model based on OpenMax and SoftMax for the
NSL-KDD intrusion traffic dataset in the misuse detection condition. The open set detection model achieves the highest
recognition accuracy when the unknown traffic type is R2L. In all types of unknown traffic experiments, the OpenMaxbased model has performed better than the SoftMax-based model in all aspects. Table 12 also shows the best
hyperparameter compositions for the OpenMax-based model in identifying different types of unknown traffic. The
distance types used are all cosine distances. Compared to the SoftMax function, the OpenMax function has the highest
accuracy of improvement for the open set model when the unknown traffic type is DoS, with an accuracy increase of
14.3%.
Table 13 shows the binary classification results of the Info GAN model based on OpenMax and SoftMax for the
NSL-KDD intrusion traffic dataset in the anomaly detection condition. All four types of intrusion traffic are labeled as
"Attack" and the normal traffic is labeled as "Normal". Through the fine-grained classification method, the algorithm
classifies normal traffic into five subclasses to avoid the confusion problem of distance among normal traffic samples.
The SoftMax-based model cannot effectively identify unknown types of traffic. And due to the misclassification of
unknown traffic, the model also has low classification accuracy on normal traffic of different subclasses. The OpenMaxbased model maintains a high classification precision rate for both unknown and normal traffic. The results from Table
12 and Table 13 illustrate that the OpenMax-based open set Info GAN model can effectively detect and classify the
traffic in the NSL-KDD dataset. It shows that the proposed algorithm is robust and applicable to different intrusion traffic
datasets.
Table 12 Performance evaluation open-set detection models (NSL-KDD).
Unknown traffic type

SoftMax

OpenMax

Accuracy

Precision

Recall

F1-score

Accuracy

Precision

Recall

F1-score

Alpha rank

Tailsize

Dos

0.582

0.515

0.582

0.504

0.724

0.751

0.724

0.699

3

12500

Probing

0.792

0.752

0.792

0.730

0.826

0.845

0.826

0.808

4

18500

R2L

0.831

0.743

0.831

0.782

0.859

0.855

0.859

0.835

4

4500

U2R

0.815

0.838

0.815

0.765

0.847

0.864

0.847

0.830

4

2500

Table 13 Detailed detection results of abnormal traffic detection models (NSL-KDD).

SoftMax

OpenMax

Data type

Quantity of data

Precision

Recall

F1-score

Precision

Recall

F1-score

Normal1

1108

0.225

1.000

0.367

0.746

0.656

0.698

Normal2

307

0.224

0.987

0.365

0.362

0.648

0.464

Normal3

1568

0.878

1.000

0.935

1.000

0.843

0.915

Normal4

6647

0.950

0.998

0.974

0.954

0.930

0.942

Normal5

81

0.022

1.000

0.042

1.000

0.012

0.024

Unknown

9083

0.000

0.000

0.000

0.865

0.902

0.883

Accuracy

0.516

Accuracy

0.885

5 Conclusion
This paper first proposes an unsupervised intrusion traffic classification model based on Info GAN. Under the
closed set condition, the model effectively classified seven kinds of traffic in the CICIDS2017 dataset, and the overall
classification accuracy rate reached 96.1%. The characteristic of the Info GAN model is that it does not rely on the labels
of the training set data but instead realizes the unsupervised classification of intrusion traffic by combining random noise
with latent vectors. This avoids the heavy lifting of labeling the training data and significantly expands the range of data
that the model can use for training.
Aiming at the classification problem of open-set traffic detection based on misuse detection technology, this paper
proposed an open-set intrusion traffic detection method based on Info GAN and OpenMax. Firstly, the Info GAN model
under the condition of closed set was trained, whilst the training set traffic samples included normal traffic and all known
types of intrusion traffic. After the closed set model converged, the activation vector of the known traffic was adjusted
by the OpenMax algorithm to introduce the activation vector of the unknown traffic, and the probability of the unknown
traffic was calculated. The results show that the OpenMax-based Info GAN model can effectively detect all types of
unknown intrusion traffic while maintaining high classification accuracy for known traffic. The model showed the lowest
detection accuracy for Infiltration traffic, 79.3%, and the highest detection accuracy for Brute force traffic, 90.9%. To
solve the false alarm problem of misclassification of known traffic by OpenMax algorithm, an O-S open-set traffic
detection and classification model was also proposed. This model combined the advantages of SoftMax algorithm and
OpenMax algorithm and utilizes the feature of the SoftMax model that classified most unknown traffic as normal traffic.
This model also further processed the classification results based on the OpenMax Info GAN model and eliminated
known traffic misclassified as unknown. Experimental results show that the O-S algorithm improved the detection
performance of different types of unknown traffic. Among them, when the unknown traffic is Infiltration and Web attack,
the classification accuracy of the open set traffic is improved the most, which is increased to 89.3% and 90.8%
respectively.
Addressing the problem of open-set traffic detection and classification based on anomaly detection technology, to
solve the problem of distance confusion caused by only learning normal traffic features, this paper proposed an Info
GAN detection and classification model based on fine-grained classification and OpenMax. Under the condition of a
closed set, by subclassing normal traffic, the Info GAN model learned the more refined features of normal traffic and
narrowed the range of classification decisions of the model. Based on the fine-grained closed set Info GAN model, the
classification accuracy rate reached 99.3%, solving the distance confusion problem of normal traffic. The experimental
results show that the overall classification accuracy of the abnormal traffic detection model reached 88.2%, indicating
that the model can detect abnormal traffic. Among them, the detection precision and recall rate of unknown traffic were
both above 92%. The model solves the problem of distance confusion in the normal traffic of some subclasses, and the
distance confusion problem of some subclasses has not been solved, which leads to the problem that the classification
accuracy of the model for normal traffic is not high. This will need to be addressed in future work.

Data availability
The datasets used and/or analysed during the current study available from the corresponding author on reasonable
request.

References
[1] B. Mukherjee, L. T. Heberlein, K. N. Levitt, “Network intrusion detection,” in IEEE network, vol. 8,
no. 3, pp. 26-41, 1994.

[2] J. P. Anderson, “Computer security threat monitoring and surveillance, James P,” Anderson Co., Fort
Washington, PA, 1980.
[3] Z. Ahmad, A. Shahid Khan, C. Wai Shiang, et al., “Network intrusion detection system: A systematic
study of machine learning and deep learning approaches,” in Trans. Emerg. Telecommun. T., vol. 32,
no. 1, pp. e4150, 2021.
[4] A. L. Buczak, E. Guven, “A survey of data mining and machine learning methods for cyber security
intrusion detection,” in IEEE Commun. Surv. Tut., vol. 18, no. 2, pp. 1153-1176, 2015.
[5] S. Anwar, J. Mohamad Zain, M. F. Zolkipli, et al., “From intrusion detection to an intrusion response
system: fundamentals, requirements, and future directions,” in Algorithms, vol. 10, no. 2, pp. 39,
2017.
[6] H. J. Liao, C. H. R. Lin, Y. C. Lin, et al., “Intrusion detection system: A comprehensive review,” in
J. Netw. Comput. Appl., vol. 36, no. 1, pp.16-24, 2013.
[7] A. Shameli-Sendi, N. Ezzati-Jivan, M. Jabbarifar, et al., “Intrusion response systems: survey and
taxonomy,” in Int. J. Comput. Sci. Netw. Secur., vol. 12, no. 1, pp. 1-14, 2012.
[8] Y. Yang, K. McLaughlin, T. Littler, S, et al., “Rule-based intrusion detection system for SCADA
networks,” in Proceedings of IET Renewable Power Generation Conference, Beijing, China, 2013,
pp. 1-4.
[9] D. E. Denning, “An intrusion-detection model,” in IEEE T. Software Eng., vol. 2, pp. 222-232, 1987.
[10] Z. K. Maseer, R. Yusof, N. Bahaman, et al., “Benchmarking of machine learning for anomaly based
intrusion detection systems in the CICIDS2017 dataset,” in IEEE Access, vol. 9, pp. 22351-22370,
2021.
[11] Y. Xin, L. Kong, Z. Liu, et al., “Machine learning and deep learning methods for cybersecurity,” in
IEEE Access, vol. 6, pp. 35365-35381, 2018.
[12] M. Safaldin, M. Otair, L. Abualigah, “Improved binary gray wolf optimizer and SVM for intrusion
detection system in wireless sensor networks,” in J. Amb. Intel. Hum. Comp., vol. 12, no. 2, pp.15591576, 2021.
[13] M. Al-Qatf, L. Yu, M. Al-Habib, et al., “Deep Learning Approach Combining Sparse Autoencoder
With SVM for Network Intrusion Detection,” in IEEE Access, vol. 6, pp. 52843-52856, 2018.
[14] A. Ahmim, L. Maglaras, M. A. Ferrag, et al., “A novel hierarchical intrusion detection system based
on decision tree and rules-based models,” in Proceedings of 2019 International Conference on
Distributed Computing in Sensor Systems, IEEE, 2019, pp. 228-233.
[15] Y. LeCun, Y. Bengio, G Hinton, “Deep learning,” in nature, vol. 521, no. 7553, pp. 436-444, 2015.
[16] E. Aminanto, K. Kim, “Deep learning in intrusion detection system: An overview,” in Proceedings
of 2016 International Research Conference on Engineering and Technology, Higher Education
Forum, 2016.
[17] H. Choi, M. Kim, G. Lee, et al., “Unsupervised learning approach for network intrusion detection
system using autoencoders,” in J. Supercomput., vol. 75, no. 9, pp. 5597-5621, 2019.
[18] R. Vinayakumar, M. Alazab, K. P. Soman, et al., “Deep learning approach for intelligent intrusion
detection system,” in IEEE Access, vol. 7, pp. 41525-41550, 2019.
[19] M. Wengang, Z. Yadong, G. Jin, “Abnormal Traffic Detection Method Based on LSTM and
Improved Residual Network Optimization,” in Journal of Communications, vol. 2, no. 5, pp. 23-40,
2021.
[20] X. B. Tang, L. M. Zhang, Z. G. Zhong, “Intrusion Traffic Detection and Recognition based on
ADASYN and Improved Residual Network,” in Systems engineering and electronics, vol. 44, no. 12,
pp. 3850-3862, 2022.
[21] P. Laskov, P. Düssel, C. Schäfer, et al., “Learning intrusion detection: supervised or unsupervised,”
in Proceedings of International Conference on Image Analysis and Processing, Springer, Berlin,
Heidelberg, 2005, pp. 50-57.
[22] S. Mokhtari, K. Yen, “Measurement data intrusion detection in industrial control systems based on
unsupervised learning,” in Appl. Comput. Intell. S., vol. 1, no. 1, pp. 61-74, 2021.

[23] X. Zhang, “Network intrusion detection using generative adversarial networks,” University of
Canterbury, 2020.
[24] H. Chen, L. Jiang, “Efficient GAN-based method for cyber-intrusion detection,” in arXiv:1904.02426,
2019.
[25] L. Vu, Q. U. Nguyen, “Handling Imbalanced Data in Intrusion Detection Systems using Generative
Adversarial Networks,” in Journal of Research and Development on Information and
Communication Technology, vol. 2020, no. 1,pp. 1-13, 2020.
[26] J. H. Lee, K. H. Park, “GAN-based imbalanced data intrusion detection system,” in Pers. Ubiquit.
Comput., vol. 25, no. 1, pp. 121-128, 2021.
[27] S. Kong, D. Ramanan, “Opengan: Open-set recognition via open data generation,” in Proceedings of
the IEEE/CVF International Conference on Computer Vision, 2021, pp. 813-822.
[28] H. Zhang, A. Li, J. Guo, et al., “Hybrid models for open set recognition,” in Proceedings of European
Conference on Computer Vision, Springer, Cham, 2020, pp. 102-117.
[29] G. Chen, L. Qiao, Y. Shi, et al., “Learning open set network with discriminative reciprocal points,”
in Proceedings of European Conference on Computer Vision. Springer, Cham, 2020, pp. 507-522.
[30] P. Perera, V. I. Morariu, R. Jain, et al., “Generative-discriminative feature representations for openset recognition,” in Proceedings of IEEE/CVF Conference on Computer Vision and Pattern
Recognition, 2020, pp. 11814-11823.
[31] H. M. Yang, X. Y. Zhang, F. Yin, et al., “Convolutional prototype network for open set recognition,”
in IEEE Trans. Pattern. Anal., vol. 44, no. 5, pp. 2358 - 2370, 2020.
[32] R. Tang, Z. Yang, Z. Li, et al., “Zerowall: Detecting zero-day web attacks through encoder-decoder
recurrent neural networks,” in Proceedings of IEEE INFOCOM 2020-IEEE Conference on Computer
Communications, IEEE, 2020, pp. 2479-2488.
[33] Y. Zhang, J. Niu, D. Guo, et al., “Unknown network attack detection based on open‐set recognition
and active learning in drone network,” in Trans. Emerg. Telecommun. T., vol. 33, no. 10, pp. 387392, 2021.
[34] Z. Zhang, Q. Liu, S. Qiu, et al., “Unknown attack detection based on zero-shot learning,” in IEEE
Access, vol. 8, pp. 193981-193991, 2020.
[35] I. Goodfellow, J. Pouget-Abadie, M. Mirza, et al., “Generative adversarial nets,” in Proceedings of
Advances in neural information processing systems, 2014.
[36] M. Arjovsky, S. Chintala, L. Bottou, “Wasserstein generative adversarial networks,” in Proceedings
of International conference on machine learning, 2017, pp. 214-223.
[37] S. Xu, L. Li, H. Yang, et al., “KCC Method: Unknown Intrusion Detection Based on Open Set
Recognition,” in Proceedings of IEEE 33rd International Conference on Tools with Artificial
Intelligence, IEEE, 2021, pp. 1343-1347.
[38] W. J. Scheirer, A. de Rezende Rocha, A. Sapkota, et al., “Toward open set recognition,” in IEEE
Trans. Pattern. Anal., vol. 35, no. 7, pp. 1757-1772, 2012.
[39] W. J. Scheirer, L. P. Jain, T. E. Boult, “Probability models for open set recognition,” in IEEE Trans.
Pattern. Anal., vol. 36, no. 11, pp. 2317-2324, 2014.
[40] F. Gao, L. Yang, H. Li, “A review on open set recognition,” in Journal of Nanjing University (Natural
Science), vol. 58, no. 1, pp. 115-134, 2022.
[41] W. J. Scheirer, A. Rocha, R. J. Micheals, et al., “Meta-recognition: The theory and practice of
recognition score analysis,” in IEEE Trans. Pattern. Anal., vol. 33, no. 8, pp. 1689-1695, 2011.
[42] X. Chen, Y. Duan, R. Houthooft, et al., “Infogan: Interpretable representation learning by information
maximizing generative adversarial nets,” in Proceedings of the 30th International Conference on
Neural Information Processing Systems, 2016, pp. 2180-2188.
[43] A. Bendale, T. E. Boult, “Towards open set deep networks,” in Proceedings of the IEEE conference
on computer vision and pattern recognition, 2016, pp. 1563-1572.
[44] J. Wu, Z. Huang, J. Thoma, et al., “Wasserstein divergence for gans,” in Proceedings of the European
Conference on Computer Vision, 2018, pp. 653-668.

[45] R. Panigrahi, S. Borah, “A detailed analysis of CICIDS2017 dataset for designing Intrusion Detection
Systems,” in International Journal of Engineering & Technology, vol. 7, no. 3, pp. 479-482, 2018.
[46] Z. Pelletier, M. Abualkibash, “Evaluating the CICIDS-2017 dataset using machine learning methods
and creating multiple predictive models in the statistical computing language R,” in Science, vol. 5,
no. 2, pp. 187-191, 2020.
[47] R. K. Malaiya, D. Kwon, J. Kim, et al., “An empirical evaluation of deep learning for network
anomaly detection,” in Proceedings of 2018 International Conference on Computing, Networking
and Communications, IEEE, 2018, pp. 893-898.
[48] S. Vaze, K. Han, A. Vedaldi, et al., “Open-Set Recognition: A Good Closed-Set Classifier is All You
Need,” in Proceedings of International Conference on Learning Representations, 2021.
[49] H. Park, J. Noh, B. Ham, “Learning memory-guided normality for anomaly detection,” in
Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2020, pp.
14372-14381.
[50] J. Yang, X. Chen, S. Chen, et al., “Conditional variational auto-encoder and extreme value theory
aided two-stage learning approach for intelligent fine-grained known/unknown intrusion detection,”
in IEEE Trans. Inf. Foren. Sec., vol. 16, pp. 3538-3553, 2021.
[51] I. Goodfellow, Y. Bengio, A. Courville, “Deep learning,” MIT press, 2016.
[52] S. Farhat, M. Abdelkader, A. Meddeb-Makhlouf, et al., “Comparative Study of Classification
Algorithms for Cloud IDS using NSL-KDD Dataset in WEKA,” in Proceedings of 2020
International Wireless Communications and Mobile Computing, Limassol, Cyprus, IEEE, 2020, pp.
445-450.
Author contributions
Conceptualization: J.F., C.X.; methodology: J.F., C.X.; formal analysis & data curation: J.F., C.X.; writing—original
draft preparation: Z.Z.; writing—review & editing: J.F., C.X.; supervision: C.X.; all authors have read and agreed to the
published version of the manuscript.

Funding
This research was supported in part by the National Natural Science Foundation of China under Grant 91538201, in part
by Taishan Scholar Project of Shandong Province under Grant ts201511020.

Competing interests
The authors declare no competing interests.
PAPER_TEXT
