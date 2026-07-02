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
# [433] Fed-UGI: Federated Undersampling Learning Framework With Gini Impurity for Imbalanced Network Intrusion Detection
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
编号：433
题名：Fed-UGI: Federated Undersampling Learning Framework With Gini Impurity for Imbalanced Network Intrusion Detection
年份：2024
DOI：10.1109/tifs.2024.3516547
来源：IEEE Transactions on Information Forensics and Security
PDF：paper/10.1109_TIFS.2024.3516547.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：联邦学习、隐私保护与分布式协同
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\433.txt
- 原始字符数：79487
- 本次发送字符数：79487
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
1262

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

Fed-UGI: Federated Undersampling Learning
Framework With Gini Impurity for Imbalanced
Network Intrusion Detection
Ming Zheng , Member, IEEE, Xiaowen Hu , Ying Hu , Xiaoyao Zheng , Senior Member, IEEE,
and Yonglong Luo
Abstract—In the modern interconnected world, the popularization of networks and the rapid development of information
technology led to the increasing security risks and threats in
network systems. The existing intrusion detection system is
constantly challenged by various malicious intrusion attacks.
Machine learning algorithms have been widely used in intrusion
detection. However, the model training requires the support of
a sufficient high-quality samples, especially attack traffic data.
Network intrusion detection datasets may not be shared between
organizations due to data security and some privacy policy concerns. The federated learning framework is an optimal approach
to address this issue, in which organizations collaborate to train
a global model shared by multiple parties while keeping the data
local to the client, guaranteeing the data privacy and security of
all parties. However, there is a problem of class imbalance in the
network traffic data owned by the organizations, which seriously
affects the detection performance of the model and leads to a
high consumption of model training time. Therefore, this study
proposed a novel federated undersampling learning framework
with Gini impurity, namely Fed-UGI. The framework is based
on the hash-based block undersampling method to rebalance
the client, which can solve the influence of imbalanced training
data on the model detection performance and improve the model
training efficiency. Moreover, the client weighted aggregation
strategy based on Local Gini impurity can further optimize
the effect of global model aggregation and reduce the impact
of the dispersion degree and information difference in client
data on model aggregation. In addition, extensive experiments
on intrusion detection datasets show that compared to SOTA
methods, the proposed Fed-UGI method has a good detection
effect on the three metrics of F1-score, G-mean and AUC,
the training time of the model is reduced by 51.76%-92.58%,
especially in highly class imbalance situation.

Index Terms—Federated learning, imbalanced data, network
intrusion detection, undersampling.

I. I NTRODUCTION

W

ITH the further internationalization, openness and personalization of the Internet, the network makes our
lives more convenient, but it also makes the threat of network
security quite common in our daily lives. Criminals can take
advantage of security loopholes in the network to carry out
malicious activities such as illegal invasion, destruction, theft
and tampering of target systems [1]. Illegal access to personal
information, online fraud, network intrusion, cyber theft and
other activities may lead to personal financial losses, privacy
leakage, system paralysis, seriously affecting social production
and life, and harming national interests. Network security is
related to personal security, enterprise security, but also related
to national security. In this case, further research is needed
to establish a Network Intrusion Detection System (NIDS)
that can effectively detect attacks to ensure a secure network
environment [2].
In the past decade, various network intrusion detection
methods based on machine learning have been proposed [3].
Learning complex patterns from the high-dimensional data
of deep learning makes it a suitable solution for detecting
network intrusion. Building detection models using machine
learning or deep learning algorithms has been widely used in
NIDS [4]. Although previous research has shown that they
can achieve significant performance compared to traditional
methods [5], their better performance usually requires large
amounts of attack instance data to support. However, in the
real world, there are not many high-quality samples of attack
network traffic available to organizations, and most network
traffic datasets suffer from serious class imbalance. These
problems also exist in the widespread use of real datasets
UNSW-NB15 [6], CSE-CIC-IDS2018 [7] and CICIDS’17 [7].
Specifically, the data belonging to the normal network traffic
of majority class accounts for a large proportion in the dataset
samples, while the data belonging to the attack network traffic
of minority class accounts for a small proportion compared
to the normal network traffic data of majority class. The class
imbalance problem may degrade the detection performance in
recognizing the attack network traffic data of minority class,
leading to a large number of false positives [8].

Received 30 January 2024; revised 18 September 2024 and 21 October 2024; accepted 3 December 2024. Date of publication 12 December 2024;
date of current version 17 January 2025. This work was supported in part by
the National Natural Science Foundation of China under Grant 62306009 and
Grant 62272006, in part by the Major Project of Natural Science Research in
Colleges and Universities of Anhui Province under Grant KJ2021ZD0007,
in part by Wuhu Science and Technology Bureau Project under Grant
2022jc11, in part by the Major Natural Science Research Project for Anhui
Universities under Grant 2023AH040026, and in part by the Key Research
and Development Project for Wuhu City under Grant 2022yf55. The associate
editor coordinating the review of this article and approving it for publication
was Dr. Weizhi Meng. (Corresponding author: Yonglong Luo.)
Ming Zheng, Ying Hu, Xiaoyao Zheng, and Yonglong Luo are with
the School of Computer and Information, Anhui Normal University, Wuhu
241002, China, and also with the Anhui Provincial Key Laboratory of
Industrial Intelligence Data Security, Anhui Normal Unviersity, Wuhu, Anhui
241002, China (e-mail: mzheng@ahnu.edu.cn; ylluo@ustc.edu.cn).
Xiaowen Hu is with the School of Computer and Information, Anhui
Normal University, Wuhu 241002, China (e-mail: xwhu@ahnu.edu.cn).
Digital Object Identifier 10.1109/TIFS.2024.3516547
1556-6021 © 2024 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

ZHENG et al.: Fed-UGI: FEDERATED UNDERSAMPLING LEARNING FRAMEWORK WITH GINI IMPURITY

Fig. 1. An application example of federated learning, the server and various
organizations collaborate to train the global model.

The intrusion detection model constructed based on a limited number of imbalanced network traffic data and deep
learning methods have limitations such as insufficient ability
to detect network intrusion [9]. An effective solution is to
collect network traffic data from different organizations into
a data center and train deep learning models based on data
samples from the data center. Each organization contains a
certain amount of network traffic data that exists in the form
of silos. However, it is a fact that attack network traffic
data is private and confidential, which involves the security
of governments, enterprises, research institutes, and even the
countries. In addition, there are data protection regulations and
privacy policies such as GDPR and CCPA, and organizations
are not allowed to share network traffic datasets. Therefore, the
Federated Learning (FL) framework is needed to address this
issue [10]. In the FL framework, the demand for sufficient
training data can be addressed while keeping the data local
to the client, and a multi-party shared global model can be
collaboratively trained while ensuring client data privacy and
security, as shown in Fig. 1. However, currently FL is mostly
used in the field of image data, and few studies have applied
it to the field of tabular data for network intrusion detection
[11], [12]. Another challenge is that the distribution of network
traffic data owned by each organization is imbalanced. That is,
the normal network traffic data accounts for a large proportion
in the dataset, and the attack network traffic data is much
less than the normal network traffic data. This makes the
model tend to learn more from the normal network traffic data
of majority class, while ignoring the more important attack
network traffic data of minority class.
In FL, the distribution of network traffic datasets for each
client is usually imbalanced, and the imbalance in client
dataset is a relative imbalance. That is to say, the number
of attack network traffic data is not absolutely rare [13],
but takes a small proportion in the whole dataset compared
with the number of normal network traffic data. The number
of clients participating in FL usually involves thousands or
even millions, and the data varies greatly between different
clients due to user habits and devices used. In other words,
the degree of imbalance between normal network traffic data

1263

and attack network traffic data is not the same in the local
datasets of different clients. The clients of different sizes may
have different amounts of data in their network traffic datasets.
In addition, due to the differences in local data distribution
among clients, from a global perspective, the overall data
distribution obtained by aggregating all client datasets is often
imbalanced [14]. That is, attack network traffic data accounts
for a small proportion in the whole global dataset, and most
of the data is normal network traffic data. In this study, the
imbalance problem in FL is summarized into three categories:
1) local imbalance, the local network traffic data distribution
of each client is imbalanced. That is, compared with normal
network traffic, the proportion of attack network traffic in
the client dataset is much smaller, and the local imbalance
is relative imbalance; 2) global imbalance, from a global
perspective, the collection of network traffic data from all
clients is imbalanced; 3) size imbalance, the number of the
network traffic data owned by each client is uneven. The
main goal of FL is to protect the data privacy of all clients
participating in federated training and collaborate with all
parties to train a shared global model with better performance
[15]. However, previous studies have shown that the problem
of imbalance across clients can hinder the goal and prolong
the training time, and the class imbalance leads to lower
classification accuracy for the attack network traffic data of
minority class [16].
To solve the above problems, we propose Fed-UGI, which
takes into account the data privacy protection of each organization and applies it to the learning and detection of imbalanced
network traffic data. The contribution of this study can be
summarized as follows:
• The proposed Fed-UGI can preprocess imbalanced
datasets to construct balanced training data blocks for
local models that trained with different data blocks in each
local epoch, while keeping the data local to the client for
privacy.
• This study proposed a new client weighted aggregation
strategy based on Local Gini impurity (LG), which takes
into account the differences among different client data
and can reduce the impact of local models that perform
poorly during training process on global model.
• Extensive experiments are conducted on real datasets, and
the experimental results demonstrate that the Fed-UGI
can achieve better performance of the network intrusion
detection model with the advantage of reducing the training time of the model by 51.76%-92.58%, especially in
highly class imbalance situation.
The rest of the paper is organized as follows. In Section II,
we review the related research work, including the FL in
NIDS, imbalanced data learning and the imbalanced data
challenge in FL. In Section III, the motivation is elaborated.
In Section IV, the Fed-UGI method proposed in this study
is introduced in detail. In Section V, in order to evaluate the
performance of Fed-UGI, sufficient experimental verification
is performed on the basis of existing datasets. In Section VI,
we set up ablation experiments to discuss the effectiveness of
each improvement in the Fed-UGI. In Section VII, we discuss
the limitations of our approach in this study and the solutions

1264

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

we envision to address them. The contents and experimental
results of this study are summarized, and the future research
work is prospected in Section VIII.
II. R ELATED W ORK
A. Federated Learning in NIDS
FL, a distributed machine learning framework, can realize
mobile device training on the premise of data privacy and
security [17]. FL eliminates the need for data sharing as FL
provides collaborative learning between devices and machine
learning models can be trained on data distributed across
multiple devices [18], [19]. In the FL system, server randomly
selects a subset Kt ⊆ K of clients to participate in training
in each round of communication and provides them with the
current global model [20]. Clients train the downloaded global
model on the local dataset and upload the updated models to
the FL server to aggregate. Repeat the process many times,
and eventually build a general and powerful machine learning
model. FedAvg [21] is the most basic algorithm in FL, where
the server aggregates the global model parameters according
to the local dataset size of the client:
X
θ[k]Wkt+1
(1)
W t+1 =
k∈Kt

where θ is the federated aggregation vector which determines
the contribution of the received local models and Wkt+1 denotes
the updated model of client k. FedAvg employs the number
of local samples | Dk | of client k as the federated aggregation
vector, with weights proportional to the size of the local
dataset:
|Dk |
, ∀k ∈ Kt .
(2)
θ[k] = P
|D j |
j∈Kt

By analyzing Eq. 2, the aggregation strategy of FedAvg is to
aggregate model parameters according to the size of the client
local dataset. Such aggregation method implicitly implies that
models trained on more samples are better than models trained
on fewer samples, thus increasing their contribution to the
aggregation process. However, relying solely on the size of the
data may not be reasonable, as the data distribution between
clients in FL is uneven and imbalanced. This strategy ignores
other important properties of the model and data, especially
in terms of training convergence, which may lead to problems
[22]. Considering this situation, if a client has a large but
severely imbalanced dataset, then the model parameters trained
on this client will differ significantly from the optimal values.
However, the traditional aggregation strategy based on dataset
size will make the updated global model parameters tend to
the client model parameters, which will lead to the global
model performance deviation from the optimal value, and even
lead to the risk of global model divergence on the imbalanced
dataset [23].
Recently, some aggregation methods have improved model
aggregation based on FedAvg, but FedAvg is the first and most
widely used. MOON [24] aims to optimize model aggregation
by adding model contrast loss as a regularization term to
minimize the differences between local and global models.
FedAMP [25] performs personalized aggregation on both the

server and the client, regardless of local targets. PartialFed [26]
learns aggregation policies locally to select parameters in a
global or local model. However, this choice does not accurately
capture the required information in the global model. The
personalization aggregation process in these methods cannot
not directly applied to most existing FL frameworks and does
not focus on information such as data distribution and quality
of the client local dataset. These findings inspired us to further
optimize the model aggregation process by using a new metric
to analyze the quality of the client local dataset and fairly
measure the data distribution differences among clients to
determine the contribution of their local model parameters in
the aggregation process.
Since researchers proposed FedAvg [21] in 2017, there is a
significant development on FL, leading to FL application in a
variety of fields involving sensitive data. However, few studies
have applied FL to the field of network intrusion detection.
Some researchers have proposed the use of FL to perform
intrusion detection work in IoT networks [27]. FedDef [28],
a FL-based NIDS, is an optimization-based input perturbation
defense strategy with theoretical guarantees that achieves high
utility by minimizing the gradient distance and strong privacy
protection by maximizing the input distance. EEFED [29],
a FL framework for collaborative development of security
intrusion detection models, effectively reduces the negative
impact of data imbalance and non-IID on FL and improves
the stability of the model through a personalized updating
algorithm and an optimal backtracking parameter replacement
strategy.
Recently, research on network intrusion detection that
applies FL to various scenarios mainly focuses on protecting
privacy and reducing communication overhead [30], [31], and
few studies have paid attention to the problem of declining
accuracy of intrusion detection due to the imbalance of network traffic data distribution [32].
B. Imbalanced Network Traffic Data Learning
It is general that the data distribution is imbalanced in the
real world. The distribution of normal traffic and attack traffic
data in the network is usually imbalanced. When there is class
imbalance in the data distribution, the normal traffic samples of
the majority class account for a very large proportion of the
whole training data, while the attack samples of the minority class will account for a much smaller proportion. Class
imbalance can seriously affect the performance of machine
learning detection algorithms [32], [33]. FedAvg is a classical
training method that can train models and aggregate them with
local datasets from collaborative clients while protecting data
privacy. However, it does not take into account the impact of
imbalanced data distribution on model training. The distribution of local network traffic datasets on clients is relatively
imbalanced, which results in poor detection performance of
the model. On the one hand, in the training process, the model
will learn more from normal network traffic samples, while
ignoring more important attack network traffic samples, which
will cause its prediction results to be biased to normal network
traffic data, thus ignoring more important attack network traffic
data. On the other hand, due to the large scale of the client

ZHENG et al.: Fed-UGI: FEDERATED UNDERSAMPLING LEARNING FRAMEWORK WITH GINI IMPURITY

dataset, there are a large number of redundant normal network
traffic samples, resulting in imbalanced training data and a
long training time for the model. As a result, FedAvg may
not perform well in imbalanced data scenarios. During FL
training, when the model encounters class imbalance, it may
lead to the generation of skewed local models during training
because the model learns more from the majority class sample
and ignores the minority class sample. In general, these models
affect global model convergence and performance during the
aggregation phase. Relevant studies have shown that the final
quality of deep neural network models is determined by
the first few training cycles. In the critical period, defects
such as low quality or quantity of training data will lead to
irreversible degradation of model performance, no matter how
much additional training is conducted after this period [34].
This phenomenon was revealed in latest work of FL [35],
[36], which aroused our attention to the data quality problem
of imbalanced training datasets for FL models. In view of
this finding, we will design a new framework based on FL to
overcome the challenge of imbalanced dataset distribution in
FL. While ensuring data privacy and security, we will solve
the problem of imbalanced dataset distribution, reduce the size
of the training dataset, and train the model on a balanced
dataset. This will improve the detection performance of the
model while reducing its training time.
C. Imbalanced Data Challenge in Federated Learning
The challenge of imbalanced data in FL and its impact
on FL training has attracted extensive interest in the field
of machine learning research. Many approaches have been
proposed to address the challenge of imbalanced data in FL.
From the perspective of balanced sampling, Astraea [37] introduces an additional virtual component called an intermediary
to access the label distribution of the clients, and then performs
data rebalancing sampling and client rearrangement training.
However, approaches similar to Astraea that require collecting
information about the local data class distribution of clients
will lead to the potential risk of privacy leakage, and the
introduced mediator increases the complexity of FL and incurs
more overhead.
Some scholars have addressed the FL with class imbalance
problem in terms of client selection. Wang et al. [38] proposed,
FedACS, an analytic-driven client selection framework, which
quantifies the category distribution heterogeneity in a FL
environment based on Hoeffding inequality, and then selects
clients with low data heterogeneity to form an ideal client
pool based on Thompson sampling. Tang et al. [39] proposed
FedCor, an FL framework constructed with an active client
selection strategy based on correlation, which can effectively
mitigate the accuracy degradation caused by data heterogeneity
and significantly improve the convergence of FL. CriticalFL
[40] identifies the Critical Learning Period (CLP) during
FL training online by examining changes in the Federated
Gradient Norm (FGN) metric, and then adaptively determines
the number of clients participating in each training round.
CriticalFL can adapt to choose more clients to participate in
training in the CLP while choosing fewer clients elsewhere,
while improving test accuracy while maintaining comparable

1265

or even better communication efficiency. However, in the
practical application of FL, the client available in each round
of communication are unenforceable, so the applicability of
these strategies is limited.
In addition, FedAMP [25] is based on an attentional messaging mechanism that enables more efficient pair-to-pair
collaboration between FL clients with similar data distributions
without violating client data privacy. FedGR [41] proposed the
imbalanced softmax function and gravitational regularizer to
deal with the imbalance of sample number within the client
and promote cooperation among clients to solve the label
imbalance of cross-client. Ratio Loss [16] deploys a monitor
on the server or client device to monitor the training data
composition of each round. When the monitor continuously
detects similar imbalanced components, the system mitigates
the impact that has occurred by applying the loss function
Ratio Loss in FL. However, the global model has learnt the
imbalanced data, which has an irreversible adverse effect on
the model.
Recently, FedNoRo [42] used knowledge distillation and
distance-aware aggregation functions to update the federated
model, and introduced logical adjustment (LA) to address data
heterogeneity and class imbalance. Zhang et al. [43] designed
an efficient heterogeneity sensing client sampling mechanism,
namely Fed-CBS, based on a category imbalance measurement
with privacy protection, which can effectively reduce the class
imbalance of client packet datasets.
III. M OTIVATION
To show the impact of imbalanced problems in training data
on FL, we use the FedAvg framework to train multi-layer
perceptron (MLP) based on imbalanced datasets. However,
since there is no large distributed network traffic dataset,
the experiment constructs a distributed dataset by resampling
the UNSW-NB15 dataset [6]. The UNSW-NB15 dataset is
provided by the Cybersecurity Lab at the University of New
South Wales (UNSW) in Sydney. The dataset simulates the
network traffic in the real network environment and contains
various common network attacks and normal traffic for intrusion detection research.
A. Imbalanced Dataset
We construct four distributed UNSW-NB15 datasets: UN1,
UN2, UN3, and UN4, and the detailed information is shown in
Table I. UN1 and UN2 are size imbalance and global balance,
the difference between them is that UN1 is local balance and
UN2 is local imbalance. UN2 and UN3 are size imbalance
and local imbalance, the difference between them is that UN2
is global balance while UN3 is global imbalance. In addition,
UN4 has more than twice as much training data as UN3. Note
that the test set is balanced, and there are no identical samples
between the training sets for each client.
B. Model Architecture
The MLP model contains two fully connected layers, in
which the connection between the input layer and the hidden

1266

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

TABLE I
S ETTING OF D ISTRIBUTED UNSW-NB15 DATASET

Fig. 2. F1-score, G-mean and AUC evaluated on distributed UNSW-NB15.
TABLE II
C OMPARISON OF M ETRICS ON D ISTRIBUTED UNSW-NB15 DATASET
A FTER 250 C OMMUNICATION ROUNDS

layer uses ReLU activation function. After activating the function, a dropout layer is created with a retention probability of
0.5 and the hidden layer is followed by a softmax output layer.
In addition, the loss function is classification cross entropy,
and the metrics of classification performance are F1-score,
G-means and AUC, instead of accuracy or top-1 accuracy.
We will show the reasons for choosing F1-score, G-means
and AUC as the evaluation metrics of model performance in
Section V.
C. FL Setting
We adopt a similar notation as in [17] to set the FL as
follows: the communication round T is 250, the total number
of clients N is 20, and the fraction C of clients participating
in the communication in each round is 0.5. For local training,
the local epochs E is 5 and the local batch B is 16. Each client
updates the weights via the SGD optimizer, with learning rate
η = 0.1 and no weight decay.
Fig. 2 shows the test results of F1-score, G-mean and AUC
on four distributed UNSW-NB15 datasets. The experimental
results show that local imbalance and global imbalance will
lead to the degradation of model performance.
Qualitatively, for the global balance but local imbalanced
dataset UN2, compared with UN1, it can be concluded from
Table II and Fig. 3 (a), (b) and (c) that F1-score, G-mean
and AUC decrease by 1.48%, 1.67% and 1.71%, respectively.
Therefore, the local imbalance will lead to the degradation of
model performance. Compared with UN2, F1-score decreased
by 12.08%, G-mean decreased by 9.89%, and AUC decreased
by 7.59%. For UN4, although the amount of training data of

Fig. 3. Metrics and confusion matrixes evaluated on distributed UNSW-NB15
after 250 communication rounds.

UN4 is more than twice that of UN3, it does not improve the
performance of the classification model.
To elucidate the impact of the class imbalance problem,
Fig. 3 (d) and (e) show the confusion matrix of UN1 and
UN3. Label 0 corresponds to the category of the majority class
sample, and label 1 corresponds to the category of the minority
class. We can find from the comparison in Fig. 3 that for the
confusion matrix of UN3, category 1 (minority class) samples
are not well classified, and the training process of the model
is more inclined to classify the majority class samples, thus
ignoring the more important minority class samples.
The class imbalance problem in FL leads to poor performance of the trained model, and the prediction of the
minority class is often more difficult. More importantly, a
model learning on a dataset with imbalanced distribution
will lead to irreversible degradation, resulting in irreversible
effects. These problems motivate us to design a method for
balancing the training dataset that can preprocess the local
data while protecting the client privacy, and at the same time
performs more efficiently both in terms of communication and
computation.
In summary, the main challenges of network intrusion
detection based on FL are the class imbalanced problems in
local datasets of clients and the data difference across the
clients, which can lead to poor performance of local models
trained by FL, and the convergence and performance of global
models can be affected by the aggregation of some malicious
or poorly performing local models on the server. When the
distribution of the client dataset is imbalanced, the trained
local model will tend to the normal network traffic data and
ignore the attack network traffic data, and the parameters of
the local model will deviate from the optimal value. During
the aggregation phase, the local model parameters uploaded
by these clients negatively affect the parameters updated by
the global model, ultimately resulting in poor performance of
the global model. However, it is not appropriate to upload or
share the local data and data distribution information of client,
as it leads to the risk of client data privacy leakage. To solve
these issues, this study proposes Fed-UGI and applies it to

ZHENG et al.: Fed-UGI: FEDERATED UNDERSAMPLING LEARNING FRAMEWORK WITH GINI IMPURITY

imbalanced network intrusion detection. The framework firstly
solves the impact of imbalanced data on local model training
by preprocessing local data at the client, and improves the
effect of global model aggregation through the client weighted
aggregation strategy based on Local Gini impurity to further
improve the classification performance and communication
efficiency of the model.
Algorithm 1 Training process of Fed-UGI
Input: Total number of clients: N, total communication
rounds: T, the fraction of participating clients: c, dataset of
client k: Dk .
Output: Trained model WT on round T
1:
Clients Rebalancing
2:
for each client i = 1 to N do
3:
DU
i ← Algorithm 2(Di , E);
4:
Server Executes
5:
Initialize W0 ;
6:
Collect clients Local Gini impurity: LG;
7:
for round t = 1 to T do
8:
K = max(c · N, 1)
9:
Kt ← (random subset of K clients);
10:
// Client Update:
11:
for each client k ∈ Kt parallelly do
12:
wkt+1 ← Algorithm 3(Wt , k);
13:
Send wkt+1 to the server;
14:
end for
15:
// Server Update:
k
16:
wkt+1 ← (Collect local parameters Wt+1
for k ∈
Kt );
17:
Wt+1 ← Algorithm 4(wkt+1 , LGK );
18: end for

IV. P ROPOSED M ETHOD
A. Fed-UGI Framework
In order to solve the above problems in the network
intrusion detection based on FL, this study proposes FedUGI, which can rebalance the training dataset of each client
while ensuring the privacy of the client. At the same time, the
aggregation process is optimized considering the data differences between different clients. Fed-UGI is able to mitigate
the imbalance problem in the FL process on both the model
training and the parameter aggregation, and thus is efficient
and effective in both communication and computation.
An overview of proposed Fed-UGI is shown in Fig. 4. As
shown from Fig. 4, Fed-UGI consists of two components: FL
server and clients. FL server is responsible for maintaining
the global model, deploying the global model to the clients,
and aggregating the local models uploaded by the clients. The
client maintains the local model and trains the model using
its local dataset. The local data distribution of the client is
imbalanced, resulting in local imbalance. The data volume of
different clients is different, that is, there is size imbalance.
In addition, from a global perspective, data collection is
uneven across all clients and the degree of class skew varies
from client to client. In the classical FedAvg, the influence of

1267

the above imbalance problem is not taken into account. FedUGI framework is improved on the basis of typical FL training
to solve the shortcomings of existing FL methods in handling
imbalanced data. Firstly, in order to solve the problem of local
imbalance in the clients, we rebalance the training dataset of
the client and considers the privacy protection in FL. Secondly,
on the basis of federated undersampling learning framework,
the aggregation strategy based on Local Gini impurity is
designed to eliminate the influence of global imbalance and
size imbalance on global model aggregation. Combining these
two approaches, Fed-UGI can achieve a better performing
global model with less training time between the clients and
the server in a data privacy protected and efficient way.
Algorithm 1 shows the training process of Fed-UGI. Before
FL training, client re-balancing strategy is adopted to construct
balanced training data blocks by using hash-based block
undersampling (HBU) method. After starting the FL training
task, the server first initializes the global model to start the
training. Subsequently, the FL server starts a new round of
communication t and deploys the global model to all clients.
Next, the server randomly selects the clients to participate in
the FL model training task, and the selected clients upload the
model update parameters after completing the local training
task. Finally, at the end of the communication round, FL
server collects parameters uploaded by clients participating
in training and weights the uploaded model parameters for
aggregation based on Local Gini impurity. The server then
updates the global model to Wt+1 and ends this round. The
starting model for the next communication round is Wt+1 .
B. Fed-UGI Workflow
The Fed-UGI workflow includes client rebalancing, initialization, training, and aggregation, as shown in Fig. 5.
1) Client Rebalancing: Before the initialization phase of
the FL server, the clients participating in the FL model training
task need to rebalance the local data with class imbalance
1
(O),
to resolve the local imbalance in the client data. The
problem of local imbalance in the client data can lead to weight
divergence and precision loss of the model trained on this
dataset. Considering that the local network traffic dataset of
the client is relative imbalanced, the undersampling method
can balance its categories, and reduce the training data scale
to improve the training efficiency.
In addition, due to the data distribution between clients is
different, i.e., the label of minority class in the local data of
different clients may be different, that is, category label c is a
minority class in client A, but it is a majority class in client B.
To solve the above imbalance problems, this study proposes
the Algorithm 2, that is, an undersampling method that uses
hash method [44] to divide majority class samples and construct balanced data blocks with the same number of the local
epoch.
The Algorithm 2 can make good use of the distribution
characteristics of the dataset and retain more information
of the majority class samples. The local model trained on
the balanced data block can better learn the features of the
minority class samples, preventing the model from ignoring
the minority class samples and improving the classification

1268

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

Fig. 4. Fed-UGI framework overview.

Fig. 5. Fed-UGI workflow.

performance of the model. At the same time, we also considered the need to protect data privacy, achieving a balance in
the training dataset while ensuring that the data is local to the
client, avoiding the risk of data leakage. The Algorithm 2 has
solved the local imbalance in clients and relieved the global
imbalance to a certain extent.
Due to the mismatch in class distribution between different
clients, the Algorithm 2 adaptively discriminates between
majority and minority classes in the dataset by counting the
number of occurrences of samples from each class in the
dataset (lines 1-3). Define the number of data blocks dividing
the client dataset consistent with the local epoch (line 4), and
define the number of hash bits as [45]:
NB = dlog2

3Nma j
e
Nmin

(3)

where Nma j and Nmin denote the sample number of majority
and minority class, respectively. Firstly, the Algorithm 2 uses
the Iterative Quantization (ITQ) method to encode a binary
hash for each majority class sample and divides them into
hash subspaces based on the encoding. Samples with the same
hash encoding will be divided into the same hash subspace
(lines 7-9). ITQ [44] is an unsupervised hashing method
that preserves the similarity information between the samples
well. The ITQ method processes samples of majority class by
principal component analysis (PCA) to find the direction of
high variance of the samples in the feature space and to get
their representations in a new orthogonal projection space. In
this new projection space, a unit hypercube is formed centered
on the origin of the PCA projection space. Each vertex of
the hypercube represents a hash code, and each vertex is

ZHENG et al.: Fed-UGI: FEDERATED UNDERSAMPLING LEARNING FRAMEWORK WITH GINI IMPURITY

associated with the sample closest to it, which is assigned
the corresponding hash code. Then, a rotation operation is
performed with the aim of minimizing the quantization loss
between the hash code and the original feature vector of the
sample, denoted as:
Q (B, R) = PB − VRP2

(4)

where B, R, V and || · || denote the hash codes of the dataset
samples, the rotation matrix, real-valued data descriptors after
the PCA projection, and the Frobenius norm, respectively.
The hash code and rotation matrix are iteratively updated
to minimize quantization loss. Finally, the optimal set of
hash codes and the optimal rotation matrix of the sample are
obtained.
Algorithm 2 The HBU for rebalancing client datasets
Input: Client training dataset: D = {(xi , yi )}, i = 1, . . ., p;
yi ∈{0,1}, local epoch E.
Output: Processed dataset: DU .
Clients:
1: Calculate the size of class 0 and class 1: C0 , C1 ;
2: Identify the majority and minority class: Dma j , Dmin ;
3: Identify the size of Dma j and Dmin : Nma j , Nmin ;
4: Identify the number of data block: Nd ← E;
5: Calculate the number of hash bits N B by Equation (3);
6: Calculate the number of hash subspaces: n = 2NB ;
7: Perform hash code on each sample in Dma j by using ITQ;
8: Assign each sample in Dma j to n hash subspaces;
9: for i = 1 to Nd do
10:
Weighted all samples in Dma j by Equation (5);
11:
Select Nmin samples in Dma j according to weight
distribution to form D∗ ;
12:
Obtain balanced data block di ← D∗ ∪ Dmin ;
13:
Append di to DU ;
14: end for
15: return DU
Next, the Algorithm 2 constructs balanced training data
blocks. Each training data block consists of all samples in the
minority class and the same number of samples in the majority
class as the minority class. The majority class samples are
divided into hash subspaces by assigned hash codes. First,
each sample i is weighted, and the sampling weight based on
Hamming distance is defined as [45]:
8
<1,
di = 0
wiH =
(5)
1
:
, di , 0
n · di
where n and di denote the number of the hash subspaces and
the Hamming distance between the hash codes corresponding
to sample i and each hash subspace. After that, according
to the weight distribution wH i, Nmin samples are sampled
from majority class to form a majority class subset D∗ , and a
balance training data block is obtained by combining D∗ and
minority class Dmin (line 10-12). Finally, the local dataset of
client is preprocessed, and a new dataset DU for client model
training is constructed. The Algorithm 2 solves the influence
of local imbalance in the training dataset and reduces the

1269

global imbalance at the same time, but it does not completely
eliminate the global imbalance and size imbalance, because it
is considered that the useful information of majority class may
be lost when constructing data blocks with too few samples
of majority class.
2) Initialization: In the initialization phase of the FL model
training task, the FL server first waits for the clients participating in the training to join. Clients participate in training
by sending calculated Local Gini impurity values to the server
2
(O).
Gini impurity [46] denotes a measure of the probability
that a randomly selected sample in the set of samples is
misclassified, which measures the degree of disorder in the set.
Given that the set D contains M categories and the probability
of sample points belonging to category m is pm , then Gini
impurity is defined as:
Gini(D) = 1 −

M
X

p2m

(6)

m=1

The larger the Gini impurity value, the more chaotic the set
is, the greater the uncertainty, and the greater the amount of
information. On the contrary, the smaller the Gini impurity
value, the more ordered the set is, the smaller the uncertainty,
and the smaller the amount of information. We consider the
case that the network traffic dataset has two categories in
this study, i.e., normal traffic data and attack traffic data. The
sample set Dk of client k can be divided into two subsets C0
and C1 , and the Local Gini impurity of client k is defined as:
2
1 
X
|Ci |
(7)
LG(k) = 1 −
|Dk |
i=0

where | Dk | and | Ci | denote the size of dataset Dk and the
size of each subset Ci . It has been analyzed that the larger the
LG(k) value of the local dataset Dk of client k, the higher the
value of Gini impurity is, indicating that the dataset is more
discrete, more random and more informative. Once the clients
participating in federated training are identified, the FL server
initializes the weights and optimizers of the global model and
collects LG uploaded by all clients.
3) Training: In other FL frameworks, the local models of
clients are trained with the same training datasets in each
local epoch, while the proposed Fed-UGI training the local
model with different data blocks in each local epoch. And
each training block is perfectly balanced.
At the beginning of each communication round, the Server
3 and randomly
sends the current global model to all clients (O)
selects fraction C clients to participate in FL training. The
detailed process of client training is shown in Algorithm 3.
The client involved in the training first downloads the global
model from the server. Each client performs rounds E of local
training during the local training process. In each epoch, the
model is trained on the balanced data block De using the mini4
batch SGD algorithm (O):
w0 = w − η∇1(w; De )

(8)

Training under this framework can make the model better learn
the features and distinctions between different categories and
avoid the bias of sample categories. All participating clients

1270

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

Algorithm 3 The process of ClientUpdate
Input: Global model Wt on round t, local epochs: E, client k
rebalanced dataset: DU
k .
Output: Trained model wkt+1 on clients k.
1: Download global model from server wt ← Wt ;
2: for each Local Epoch e = 1 to E do
3:
De ← (extract balanced data block from DU
k .);
4:
wkt+1 ← wt - η∇`(wt ; De );
5: end for
6: return wkt+1 to Server
Algorithm 4 The AggregateLG for Server update
K
Input: The uploaded parameters of clients: wt+1
, the Local
K
Gini impurity of clients: LG .
Output: Updated model Wt+1 .
Server:
1: for Each Client k ∈ Kt do
2:
Calculate the federated aggregation vector θ[k] by
Equation (9);
3: end for
4: Aggregate local models to Wt+1 by Equation (10);
5: return Wt+1

TABLE III
E XPERIMENTAL N OTATIONS

TABLE IV
DATASET I NFORMATION

TABLE V

send updates of the model to the FL server after completing
5
the local training (O).
4) Aggregation: Since the data of each client are independently, the distribution quantity and probability of each
category sample in the local dataset of different clients will
vary greatly. So, a new client weighted aggregation strategy is
proposed, which takes into account the dispersion degree and
information difference of the original data from each client,
and based on this, measures the contribution degree of local
model parameters of each client in the aggregation process. We
weight the local parameters collected by FL Server based on
the Local Gini impurity uploaded by the clients for weighted
6
aggregation (O),
with weights proportional to the Local Gini
impurity value, and define the LG-based federated aggregation
vector as:
LG(k)
θ[k] = P
, ∀k ∈ Kt.
(9)
LG( j)
j∈Kt

V. E XPERIMENT AND E VALUATION
In this section, we evaluate the performance of Fed-UGI
through experiments. First of all, the detailed settings during
the experiment are given, including the introduction of the
datasets, the SOTA FL methods, the FL parameter settings and
the evaluation criteria. Then, the performance of the proposed
Fed-UGI for network intrusion detection is compared with
some SOTA methods. The symbols used in the experiment
are listed in Table III.
A. Experimental Settings

Finally, FL server aggregates all the local parameters and
updates the global model to:
Wt+1 =

PARAMETER S ETTINGS ON D IFFERENT DATASETS

X

θ[k]wkt+1

(10)

k∈Kt

The global model parameter updating process of FL server
is shown in Algorithm 4, which mainly includes two steps.
First, the server calculates federated aggregation vector to
determine the weights of local parameter aggregation according to the Local Gini impurity of participating training clients.
Next, the global parameters are calculated according to Eq. 10
to obtain the global model Wt+1 for the next communication
round.

1) Datasets: Three widely used network intrusion detection
datasets are used for experiments, namely UNSW-NB15 [6],
CSE-CIC-IDS2018 [7] and CICIDS’17 [7]. For the experiments conducted on each dataset, our method and other
comparison methods all adopt 10-fold cross-validation, taking
the average value of ten results as a comprehensive evaluation
of model performance to reduce random errors. The detailed
information of the dataset used in this study, such as the
number of features, label attributes, number of samples in each
class and imbalance ratio (IR), are shown in Table IV.
2) Environmental Setup: In the Fed-UGI method, we use
cross entropy as a loss function and set the number of
communication rounds R to 250, SGD with a learning rate η
to 0.1 as the optimizer for all optimization processes, and test

ZHENG et al.: Fed-UGI: FEDERATED UNDERSAMPLING LEARNING FRAMEWORK WITH GINI IMPURITY

TABLE VI
C ONFUSION M ATRIX

of attack traffic as normal traffic. Therefore, in order to
reasonably evaluate the effectiveness of our approach, we used
three evaluation metrics commonly used in imbalanced data
classification study, F1-score, G-mean and the area under curve
(AUC) measure model performance based on the receiver
operating characteristic (ROC) curve [48], [49]. In addition,
we compare the training time of all methods from the start of
FL training to the end of the final communication. The results
of the evaluation metrics are calculated through the confusion
matrix shown in Table VI:
F1 − score =
G − mean =

Fig. 6. ROC curve and AUC diagram.

batch size to 512. For local training, the local epoch and local
batch size are set to 5 and 16, respectively. For heterogeneous
data distribution among clients, Dirichlet distribution is used
to divide the data. In this study, MLP is used as global model
and local model, each of which has two fully connected layers,
where the connection between the input layer and the hidden
layer uses a ReLU activation function. The structure of the
model is adjusted for different datasets with different settings
for the number of hidden layer neurons, but the same structure
is maintained between the comparison methods. The MLP
model is implemented in PyTorch [47]. And we implement the
proposed Fed-UGI based on the PyTorch federated framework
[21]. The settings of client-related parameters for each dataset
and the number of neurons in the hidden layer of the MLP
model setup are shown in Table V. The total number of clients
N is divided according to the size of the three datasets, and
the value of Dirichlet parameter αd is set to 1.0 to simulate
the scenario of imbalanced client data distribution in FL. The
fraction c sets 10 clients to participate in each training round
for each dataset. The number of neurons in the hidden layer
in the MLP model is set differently depending on the number
of features in the data set but all models use the same MLP
on the same data set to ensure fairness.
3) Baseline and Comparison Methods: We compare our
proposed Fed-UGI with the other five SOTA baseline methods
including Ratio Loss [16], FedCor [39], FedNoRo [42] and
CriticalFL [40], FedDef [28]. In addition, we have added
an experiment on the model performance of all data owners
trained on local datasets without the FL framework.
4) Performance Evaluation Metrics: accuracy is not a suitable criterion for evaluating model performance in imbalanced
data classification problems. For example, in a network traffic
dataset, the ratio of normal traffic data to attack traffic data is
99:1. The model tends to predict that all data is normal, then
the classification accuracy of normal traffic will reach 99%.
However, the classification accuracy of attack traffic will be
0, which is not meaningful in practical applications, and it is
likely to cause immeasurable losses due to misidentification

1271

TP
TP
· T P+FP
2 · T P+FN
TP
TP
T P+FN + T P+FP

r

TN
TP
·
T P + FN T N + FP

(11)
(12)

The shaded area under the ROC curve in Fig. 6 is the value
of AUC. and the x- and y-axes represent the false positive
rate and true positive rate, respectively. The larger the value
of AUC, the higher the performance of the model.
5) Statistical Tests: To further discuss and evaluate the
effectiveness of Fed-UGI objectively, we used statistical tests
to determine whether there are significant differences in model
performance across all methods on different network intrusion
detection datasets. The statistical test has been used in a
number of empirical studies in machine learning and other
fields [50], [51]. The statistical tests process consists of three
steps. First, on each dataset, all methods are ranked from best
to worst according to the test performance of each method, and
the order values 1, 2, . . ., the best method order value is 1; if
the test performance of any of the methods is the same, the
order value is equally divided. The Friedman test is then used
to determine whether these methods all perform identically. If
not, then the hypothesis that all methods perform identically
is rejected, indicating that the performance of the methods
is significantly different. A post-hoc test is needed to further
distinguish the methods. Finally, Nemenyi post-hoc test is used
to follow up to check whether there is a significant difference
between any two methods. Nemenyi post-hoc test determines
the gap between the two methods according to the critical
range. If the difference between the average order values of
the two methods exceeds the critical range, the hypothesis
that the two methods have the same performance is rejected
with the corresponding confidence level. Therefore, the test
results concludes that the performance of the two methods
is significantly different. In this study, the confidence level
α = 0.05.
B. Experimental Results
In this section, we experiment with Fed-UGI and five SOTA
baseline methods on the UNSW-NB15, CICIDS’17 and CSECIC-IDS2018 datasets. In addition, the statistical test results
of all methods are given.
1) Performance Comparison Results: As shown in
Table VII, we give the results under the evaluation metrics of
F1-score, G-mean and AUC, and the training time required
for all methods to complete 250 communication rounds,
respectively. The results show that Fed-UGI achieves the best

1272

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

TABLE VII
C OMPARISON R ESULTS OF M ODEL P ERFORMANCE FOR E ACH M ETHOD

results on all metrics. On the UNSW-NB15 dataset, compared
with Ratio Loss that performs best in the baseline methods,
our method increases by 1.13%, 1.61% and 1.27% in F1score, G-mean and AUC, respectively, and more importantly,
the training time is reduced by about 67.73%. On the CSECIC-IDS2018 dataset, compared with the optimal Ratio Loss,
Fed-UGI further improves by 3.43%, 7.42% and 1.8%, respectively. Compared with other baseline methods, the training
time is reduced by approximately 51.76% to 80.38%. On the
CICIDS’17 dataset, the results of all the baseline methods
are poor, which indicates that none of these methods can
effectively identify attack traffic samples of minority classes
in the network traffic data, or even ignore the attack traffic
samples altogether in the highly imbalanced situation.
The model obtained from Fed-UGI training can achieve
the best detection results in terms of F1-score, G-mean and
AUC, which can effectively solve the adverse effect of highly
imbalanced data on model training and reduce the training
time by 83.02%-92.86% compared with other methods. Based
on this, it can be seen from the experimental results that
our method achieves the optimal detection effect and can
effectively detect normal and attack network traffic data in
imbalanced network traffic data, especially in highly class
imbalance situation. Meanwhile, the training time required is
drastically reduced to improve the training efficiency of the
model.
In the experimental results on the UNSW-NB15, CICIDS
’17 and CSE-CIC-IDS2018 datasets, the Fed-UGI method
performed better in detection performance on the UNSWNB15 and CICIDS’ 17 datasets. It is considered that the
three datasets are different in terms of data scale, degree
of imbalance in data distribution and number of features.
Our Fed-UGI first uses HBU method to balance the data

distribution of the highly imbalanced local dataset on the
client, and obtains the balanced dataset to train the local model,
while reducing the dataset size and training time. However,
the local model of other baseline methods is trained directly
on the highly imbalanced dataset, and the obtained model
parameters will seriously deviate from the optimal value.
Although these baselines will later improve model performance through loss functions and knowledge distillation, the
impact of highly imbalanced data on the model is irreversible,
and in the aggregation stage, these deviated model parameters
will exacerbate the divergence of global model parameters,
leading to poor performance of baseline methods. In addition,
LG-based weighted aggregate strategy proposed in Fed-UGI
can further optimize the effect of model parameter aggregation.
As a result, our Fed-UGI has the best performance over other
baseline methods on F1-score, G-mean and AUC, and shows
a definite advantage in training time.
In Fig. 7, the detection performance of models trained by
all data owners on their local datasets is shown. As shown
in Fig. 7 (a), on the UNSWNB15 dataset, the dotted lines
in the figure represent the performance results of our FedUGI method. It can be found that without FL framework, the
performance of 100 data owners on F1 score, G-mean, and
AUC metrics is poor. In Fig. 7 (b) and (c), for the CSE-CICIDS2018 and CICIDS ’17 datasets, the values of F1-score
and G-mean for the model trained by all data owners on
imbalanced local datasets are 0, and the values of AUC are
0.5, indicating that the model cannot identify attack network
traffic samples. All samples are predicted as normal network
traffic samples, and the model tends to predict randomly.
Fed-UGI is based on a FL framework that collaborates
with various clients for training which can learn sufficient
attack network traffic data and normal network traffic data.

ZHENG et al.: Fed-UGI: FEDERATED UNDERSAMPLING LEARNING FRAMEWORK WITH GINI IMPURITY

1273

TABLE VIII
O RDER VALUE OF M ETHODS C OMPARISON ON E ACH M ETRIC

Fig. 7. Without FL framework result.

Fig. 8. Results of Nemenyi post-hoc test.

In addition, Fed-UGI solves the problem of imbalanced data
distribution and avoids the skew of the model on imbalanced
datasets.
2) Statistical Test Results: We used statistical test to further validate the significance of the difference in detection
performance between our method and SOTA methods. For
each evaluation metric, the test performance of each method
on each dataset is ranked from best to worst. Table VIII
shows the order value and average order value of the test

performance for each method on all datasets. In terms of
evaluation metrics F1-score, G-mean, AUC and training time,
the results of Friedman test TF are calculated to be 1.962,
1.865, 3.676, 9.250, respectively, and the critical value of F
test when confidence α = 0.05 is 3.326. In metrics F1-score
and G-mean, the results of Friedman test TF are all smaller
than the critical value of F test, so the hypothesis that the
performance of all algorithms on F1-score and G-mean is the
same cannot be rejected.
On both metric AUC and training time, the Friedman test
results TF are greater than the critical value of F test, so the
hypothesis that the performance of all algorithms is the same
is rejected, indicating that the performance of all methods is
significantly different on AUC and training time. The Nemenyi
post-hoc test is then used to further distinguish the methods
in metrics AUC and training time. Nemenyi post-hoc test
calculated that the critical range CD is 3.353. We mainly
analyzed the gap between Fed-UGI and other methods, and
the test results can be visually displayed in Fig. 8, where
the vertical axis shows each method, the horizontal axis is
the average orderh value. For each method, a dot is used

1274

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

TABLE IX
A BLATION E XPERIMENT R ESULTS

to display its average order value, and the horizontal line
centered on the dot represents the size of the critical range.
As shown in Fig. 8 (a), in evaluation metric AUC, FedUGI performs better than other methods and is significantly
better than FedCor and FedDef method. For metric training
time shown in Fig. 8 (b), Fed-UGI outperforms other methods and significantly outperforms the CriticalFL and FedDef
methods.
In conclusion, the proposed Fed-UGI can greatly reduce
the training time consumption of FL model while improving
the performance of network intrusion detection model. Meanwhile, the Fed-UGI outperforms and significantly outperforms
the FedCor method, the CriticalFL method and FedDef method
in the statistical tests of the evaluation metrics AUC and the
training time.
VI. D ISCUSSION
In this section, we further used the UNSW-NB15,
CICIDS’17 and CSE-CIC-IDS2018 datasets for ablation
experiments to verify the effectiveness of each improvement
in Fed-UGI. The component AVG in the experiment refers to
the aggregation strategy in FedAvg, and LGW represents the
LG-based weighted aggregate strategy proposed in Fed-UGI.
Table IX shows a comparison of combining the HBU
method and the LGW aggregate strategy with only one of the
improved combinations on the three experimental datasets. We
also implemented the FedAvg method and compared it to FedUGI. The combination (1) of each dataset indicates that there
is no improved component, that is, the underlying FedAvg
method. Combination (2) contains only LGW improvement,
combination (3) contains only HBU improvement, and combination (4) contains all improvements at the same time.
The results of four groups of experiments on the dataset
UNSW-NB15 are analyzed as follows. Compared with (1),
after adding only the LGW aggregate strategy in (2), F1score, G-mean and AUC increase by about 0.29%, 1.97%
and 0.89%, respectively. (3) Compared with (1), which adds
the HBU method, F1-score, G-mean and AUC increase by
about 2.33%, 2.46% and 1.88%, respectively. When the same

parameter aggregation strategy is added, (3) compared with
(1), the training time is reduced by 55.63%; (4) Compared
with (2), the training time decreased by 55.47%. (4) Contains
HBU and LGW aggregate strategy, its performance is the best
compared to (1), (2), and (3).
The results of four groups of experiments on the dataset
CSE-CIC-IDS2018 are analyzed as follows. (2) Compared
with (1), LGW aggregate strategy can increase F1-score, Gmean and AUC by 4.52%, 7.55% and 1.61%, respectively.
(3) Compared with (1), HBU method can increase F1-score,
G-mean and AUC by 7.55%, 13.29% and 3.14% respectively.
Containing HBU and LGW aggregate strategy in (4), the
model performs best with the least training time.
The imbalance ratio of dataset CICIDS’17 is as high as
38.54, and the client local data after Dirichlet partition is also
high imbalanced. Combination (1), that is, FedAvg method
in the case of highly class imbalance situation, the values
of F1-score and G-mean are 0, and the value of AUC is
0.5, indicating that the model cannot identify attack samples
of minority class, and all samples are predicted as normal
traffic, which means that the model tends to random prediction.
The results of (2) and (3) show that both HBU method
and LGW aggregate strategy can solve the problem that the
model cannot identify attack samples of minority class due
to highly class imbalance in the local data of the client.
(4) Compared with (2), under the same parameter aggregation
strategy, combined with HBU method, G-mean and AUC can
be increased by 5.34% and 5.00% respectively, and the training
time can be reduced by 87.22%. (4) Compared with (3),
LGW improvement is further added while HBU method is
also adopted, which further improves the performance of the
model.
The reason why the performance of the model can be
improved while the training time can be reduced is that the
HBU method can construct balanced training data blocks to
support the model training on the premise of retaining the
information of important samples of majority class, and at the
same time reduce the scale of training data, thus reducing the
training time. All improvements are included in (4), resulting

ZHENG et al.: Fed-UGI: FEDERATED UNDERSAMPLING LEARNING FRAMEWORK WITH GINI IMPURITY

in the best value. According to the results of ablation experiments, the components in Fed-UGI can effectively improve
the performance of the final model detection results. Based
on this, we can see that every improvement in Fed-UGI is
useful. The HBU method in Fed-UGI mainly solves the local
imbalance in the client, so that the local model can be trained
on the balanced data and the data scale can be reduced at the
same time. However, there are still differences in the degree
of data dispersion and the amount of information between the
clients. Therefore, it is important to combine the two strategies.
After the local model training is completed, we adopted a new
parameter weighted aggregation strategy to further optimize
the effect of parameter aggregation, so as to achieve the
goal of improving the performance of the federated model
and shortening the training time. Compared with the FedAvg
method, the training time is reduced by 55.65%-87.20%.
VII. L IMITATION
This study focuses on the binary problem of network
intrusion detection. The model detects normal network traffic
and attack network traffic, without considering to distinguish
specific types of attacks. Each client dataset typically focuses
on detecting some type of attack. In other words, the types
of attacks in different client networks may not be the same.
When a client uses the global model to detect attacks on
its network, how to make the global model effectively detect
specific attacks on the client network is worth further research.
At present, we propose two solutions to solve this problem.
One is to use a new detection method to further identify
the attack types of all attack network traffic data based on
the binary classification of network intrusion we have done.
The other is to take this problem as a multi-classification
problem of network intrusion detection, and identify various
types of attack categories by improving the detection model.
In addition, this study is to analyze historical network traffic
data. For real time applications, we have not yet tried to study
real-time network traffic data and we believe that the Fed-UGI
can be implemented based on Apache Flink to solve this issue.
VIII. C ONCLUSION AND F UTURE W ORK
Due to the continuous opening of the Internet, the security
risks and threats it faces are increasing, and the effective
detection of network intrusion to maintain a secure network
environment is becoming more and more important. This study
proposes a novel federated undersampling learning framework
with Gini impurity, namely Fed-UGI. First of all, since the
application of machine learning algorithms to network intrusion detection requires a large number of high-quality data
to support model training, but all parties cannot share data
in the security and privacy requirements of network traffic
data. Therefore, it is proposed to coordinate multi-participant
collaborative training in FL framework to adequately train
the global model shared by multiple parties while satisfying
privacy protection and data security. Secondly, we design a
federated undersampling learning framework, which avoids
training on network traffic data with class imbalance to
produce biased models and prevents models from ignoring

1275

important attack network traffic data of minority class. By
rebalancing the local training data of each client, the local
model can be trained on different balanced data blocks in
each local epoch, which improves the detection performance
of attack network traffic data and maintains stable performance
in highly class imbalance situations. Finally, based on the
federated undersampling learning framework, we propose a
new client weighted aggregation strategy, which measures the
dispersion degree and information difference of the client data
through the Local Gini impurity, to measure the contribution
of local model parameters to the global model and further
improve the detection performance of the global model. In
addition, experimental results show that Fed-UGI can achieve
higher detection performance with less training time compared
to baseline methods. Finally, the ablation experiments verified
that the improvements of the components in Fed-UGI are
effective. It is worth noting that we provide a FL framework
that is not limited by any detection model, that is, the imbalanced treatment of client rebalancing in this framework can
support for any more advanced intrusion detection model, and
the client weighted aggregation strategy is also generic.
In the future, we will make the framework more flexible
and versatile to be applied in more critical areas. Consider that
there is less data in some organizations, while there are also
local imbalance, global imbalance, and size imbalance in FL.
In addition, there is also the problem of multi-classification in
FL based network intrusion detection, and the global model
needs to detect specific attack types on the clients. In future
studies, we aim to further improve the performance of the
model on the basis of solving these problems without violating
privacy protection requirements.
R EFERENCES
[1] V. Kumar and D. Sinha, “Synthetic attack data generation model applying generative adversarial network for intrusion detection,” Comput.
Secur., vol. 125, Feb. 2023, Art. no. 103054.
[2] K. He, D. D. Kim, and M. R. Asghar, “Adversarial machine learning
for network intrusion detection systems: A comprehensive survey,” IEEE
Commun. Surveys Tuts., vol. 25, no. 1, pp. 538–566, 1st Quart., 2023.
[3] H. Jmila and M. I. Khedher, “Adversarial machine learning for network
intrusion detection: A comparative study,” Comput. Netw., vol. 214, Sep.
2022, Art. no. 109073.
[4] N. Wang, Y. Chen, Y. Xiao, Y. Hu, W. Lou, and Y. T. Hou,
“MANDA: On adversarial example detection for network intrusion
detection system,” IEEE Trans. Depend. Sec. Comput., vol. 20, no. 2,
pp. 1139–1153, Mar. 2023.
[5] T. Zebin, S. Rezvy, and Y. Luo, “An explainable AI-based intrusion
detection system for DNS over HTTPS (DoH) attacks,” IEEE Trans.
Inf. Forensics Security, vol. 17, pp. 2339–2349, 2022.
[6] N. Moustafa and J. Slay, “UNSW-NB15: A comprehensive data set for
network intrusion detection systems (UNSW-NB15 network data set),”
in Proc. Mil. Commun. Inf. Syst. Conf. (MilCIS), Nov. 2015, pp. 1–6.
[7] I. Sharafaldin, A. H. Lashkari, and A. A. Ghorbani, “Toward generating
a new intrusion detection dataset and intrusion traffic characterization,”
in Proc. 4th Int. Conf. Inf. Syst. Secur. Privacy, Jan. 2018, pp. 108–116.
[8] A. Krause, E. Brunskill, K. Cho, B. Engelhardt, S. Sabato, and
J. Scarlett, “A theoretical analysis of the learning dynamics under
class imbalance,” in Proc. 40th Int. Conf. Mach. Learn., Jul. 2023,
pp. 10285–10322.
[9] J. L. Guerra, C. Catania, and E. Veas, “Datasets are not enough:
Challenges in labeling network traffic,” Comput. Secur., vol. 120, Sep.
2022, Art. no. 102810.
[10] X. Hao, C. Lin, W. Dong, X. Huang, and H. Xiong, “Robust and secure
federated learning against hybrid attacks: A generic architecture,” IEEE
Trans. Inf. Forensics Security, vol. 19, pp. 1576–1588, 2024.

1276

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

[11] D. Wagner et al., “United we stand: Collaborative detection and mitigation of amplification DDoS attacks at scale,” in Proc. ACM SIGSAC
Conf. Comput. Commun. Secur., Nov. 2021, pp. 970–987.
[12] E. M. Campos et al., “Evaluating federated learning for intrusion
detection in Internet of Things: Review and challenges,” Comput. Netw.,
vol. 203, Feb. 2022, Art. no. 108661.
[13] H. He and E. A. Garcia, “Learning from imbalanced data,” IEEE Trans.
Knowl. Data Eng., vol. 21, no. 9, pp. 1263–1284, Sep. 2009.
[14] Z. Shen, J. Cervino, H. Hassani, and A. Ribeiro, “An agnostic approach
to federated learning with class imbalance,” in Proc. 10th Int. Conf.
Learn. Represent., Apr. 2022, pp. 1–12.
[15] F. Lai, X. Zhu, H. V. Madhyastha, and M. Chowdhury, “Oort: Efficient
federated learning via guided participant selection,” in Proc. 15th
USENIX Symp. Operating Syst. Des. Implement. (OSDI), Jul. 2021,
pp. 19–35.
[16] L. Wang, S. Xu, X. Wang, and Q. Zhu, “Addressing class imbalance
in federated learning,” in Proc. AAAI Conf. Artif. Intell., Feb. 2021,
pp. 10165–10173.
[17] Q. Li et al., “A survey on federated learning systems: Vision, hype and
reality for data privacy and protection,” IEEE Trans. Knowl. Data Eng.,
vol. 35, no. 4, pp. 3347–3366, Apr. 2023.
[18] Z. Pan, L. Hu, W. Tang, J. Li, Y. He, and Z. Liu, “Privacypreserving multi-granular federated neural architecture search—A
general framework,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 3,
pp. 2975–2986, Mar. 2023.
[19] W. Huang, J. Liu, T. Li, T. Huang, S. Ji, and J. Wan, “FedDSR:
Daily schedule recommendation in a federated deep reinforcement
learning framework,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 4,
pp. 3912–3924, Apr. 2023.
[20] H. Zhou, G. Yang, H. Dai, and G. Liu, “PFLF: Privacy-preserving
federated learning framework for edge computing,” IEEE Trans. Inf.
Forensics Security, vol. 17, pp. 1905–1918, 2022.
[21] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. Y. Arcas,
“Communication-efficient learning of deep networks from decentralized data,” in Proc. 20th Int. Conf. Artif. Intell. Statist., Apr. 2017,
pp. 1273–1282.
[22] U. Michieli and M. Ozay, “Are all users treated fairly in federated
learning systems?,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. Workshops (CVPRW), Jun. 2021, pp. 2318–2322.
[23] G. Wang, C. X. Dang, and Z. Zhou, “Measure contribution of participants in federated learning,” in Proc. IEEE Int. Conf. Big Data (Big
Data), Dec. 2019, pp. 2597–2604.
[24] Q. Li, B. He, and D. Song, “Model-contrastive federated learning,” in
Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2021, pp. 10713–10722.
[25] Y. Huang et al., “Personalized cross-silo federated learning on nonIID data,” in Proc. AAAI Conf. Artif. Intell., May., May 2021,
pp. 7865–7873.
[26] B. Sun, H. Huo, Y. Yang, and B. Bai, “PartialFed: Cross-domain
personalized federated learning via partial initialization,” in Proc. Adv.
Neural Inf. Process. Syst. (NeurIPS), 2021, pp. 23309–23320.
[27] P. Tian, Z. Chen, W. Yu, and W. Liao, “Towards asynchronous federated
learning based threat detection: A DC-Adam approach,” Comput. Secur.,
vol. 108, Sep. 2021, Art. no. 102344.
[28] J. Chen, Y. Zhao, Q. Li, X. Feng, and K. Xu, “FedDef: Defense against
gradient leakage in federated learning-based network intrusion detection
systems,” IEEE Trans. Inf. Forensics Security, vol. 18, pp. 4561–4576,
2023.
[29] X. Huang, J. Liu, Y. Lai, B. Mao, and H. Lyu, “EEFED: Personalized
federated learning of execution & evaluation dual network for CPS intrusion detection,” IEEE Trans. Inf. Forensics Security, vol. 18, pp. 41–56,
2023.
[30] J. Gao et al., “Secure aggregation is insecure: Category inference attack
on federated learning,” IEEE Trans. Depend. Sec. Comput., vol. 20,
no. 1, pp. 147–160, Jan. 2023.
[31] J. Zhou et al., “A differentially private federated learning model against
poisoning attacks in edge computing,” IEEE Trans. Depend. Sec. Comput., vol. 20, no. 3, pp. 1941–1958, Jun. 2023.
[32] H. Ding, Y. Sun, N. Huang, Z. Shen, and X. Cui, “TMG-GAN:
Generative adversarial networks-based imbalanced learning for network intrusion detection,” IEEE Trans. Inf. Forensics Security, vol. 19,
pp. 1156–1167, 2024.
[33] A. Ito, K. Saito, R. Ueno, and N. Homma, “Imbalanced data problems in
deep learning-based side-channel attacks: Analysis and solution,” IEEE
Trans. Inf. Forensics Security, vol. 16, pp. 3790–3802, 2021.

[34] S. Jastrzebski et al., “Catastrophic Fisher explosion: Early phase Fisher
matrix impacts generalization,” in Proc. 38th Int. Conf. Mach. Learn.,
Jul. 2021, pp. 4772–4784.
[35] G. Yan, H. Wang, and J. Li, “Seizing critical learning periods in federated learning,” in Proc. AAAI Conf. Artif. Intell., 2022, pp. 8788–8796.
[36] G. Yan, H. Wang, X. Yuan, and J. Li, “DeFL: Defending against
model poisoning attacks in federated learning via critical learning
periods awareness,” in Proc. AAAI Conf. Artif. Intell., Feb. 2023,
pp. 10711–10719.
[37] M. Duan, D. Liu, X. Chen, R. Liu, Y. Tan, and L. Liang, “Self-balancing
federated learning with global imbalanced data in mobile systems,” IEEE
Trans. Parallel Distrib. Syst., vol. 32, no. 1, pp. 59–71, Jan. 2021.
[38] Z. Wang, Y. Zhu, D. Wang, and Z. Han, “FedACS: Federated skewness analytics in heterogeneous decentralized data environments,” in
Proc. IEEE/ACM 29th Int. Symp. Quality Service (IWQOS), Jun. 2021,
pp. 1–10.
[39] M. Tang et al., “FedCor: Correlation-based active client selection strategy for heterogeneous federated learning,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022, pp. 10102–10111.
[40] G. Yan, H. Wang, X. Yuan, and J. Li, “CriticalFL: A critical learning
periods augmented client selection framework for efficient federated
learning,” in Proc. 29th ACM SIGKDD Conf. Knowl. Discovery Data
Mining, Aug. 2023, pp. 2898–2907.
[41] S. Guo et al., “FedGR: Federated learning with gravitation regulation
for double imbalance distribution,” in Proc. Int. Conf. Database Syst.
Adv. Appl., Apr. 2023, pp. 703–718.
[42] N. Wu, L. Yu, X. Jiang, K.-T. Cheng, and Z. Yan, “FedNoRo: Towards
noise-robust federated learning by addressing class imbalance and label
noise heterogeneity,” in Proc. 32nd Int. Joint Conf. Artif. Intell., Aug.
2023, pp. 4424–4432.
[43] J. Zhang et al., “Fed-CBS: A heterogeneity-aware client sampling
mechanism for federated learning via class-imbalance reduction,” in
Proc. 40th Int. Conf. Mach. Learn., Jul. 2023, pp. 41354–41381.
[44] Y. Gong, S. Lazebnik, A. Gordo, and F. Perronnin, “Iterative quantization: A procrustean approach to learning binary codes for large-scale
image retrieval,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 35,
no. 12, pp. 2916–2929, Dec. 2013.
[45] W. W. Y. Ng, S. Xu, J. Zhang, X. Tian, T. Rong, and S. Kwong,
“Hashing-based undersampling ensemble for imbalanced pattern classification problems,” IEEE Trans. Cybern., vol. 52, no. 2, pp. 1269–1279,
Feb. 2022.
[46] S. Nembrini, I. R. König, and M. N. Wright, “The revival of the
Gini importance?,” Bioinformatics, vol. 34, no. 21, pp. 3711–3718, Nov.
2018.
[47] A. Paszke et al., “Automatic differentiation in PyTorch,” in Proc. Adv.
Neural Inf. Process. Syst. (NeurIPS), Workshop Autodiff Decis. Program
Chairs, 2017, pp. 1–4.
[48] Y. Yan, Y. Zhu, R. Liu, Y. Zhang, Y. Zhang, and L. Zhang, “Spatial
distribution-based imbalanced undersampling,” IEEE Trans. Knowl.
Data Eng., vol. 35, no. 6, pp. 6376–6391, Jun. 2023.
[49] T. Zhu, X. Liu, and E. Zhu, “Oversampling with reliably expanding
minority class regions for imbalanced data learning,” IEEE Trans.
Knowl. Data Eng., vol. 35, no. 6, pp. 6167–6181, Jun. 2023.
[50] J. M. Leski, R. Czabanski, M. Jezewski, and J. Jezewski, “Fuzzy
ordered c-means clustering and least angle regression for fuzzy rulebased classifier: Study for imbalanced data,” IEEE Trans. Fuzzy Syst.,
vol. 28, no. 11, pp. 2799–2813, Nov. 2020.
[51] L. Li, H. He, and J. Li, “Entropy-based sampling approaches for multiclass imbalanced problems,” IEEE Trans. Knowl. Data Eng., vol. 32,
no. 11, pp. 2159–2170, Nov. 2020.

Ming Zheng (Member, IEEE) received the Ph.D.
degree from the School of Information Science and
Engineering, Yunnan University, Kunming, China, in
2020. He is currently a Lecturer with the School of
Computer and Information, Anhui Normal University. His research interests include imbalanced data
mining, federated learning, and privacy protection.

ZHENG et al.: Fed-UGI: FEDERATED UNDERSAMPLING LEARNING FRAMEWORK WITH GINI IMPURITY

1277

Xiaowen Hu received the B.E. degree in computer science and technology from Anhui Normal
University, Wuhu, China, in 2022, where she is
currently pursuing the M.E. degree with the School
of Computer and Information. Her current research
interests include federated learning, data mining, and
privacy protection.

Xiaoyao Zheng (Senior Member, IEEE) received
the M.S. degree in computer science from the School
of Computer Science, Hefei University of Technology, Hefei, China, in 2005, and the Ph.D. degree in
human geography from Anhui Normal University,
Wuhu, China, in 2018. Since 2021, he has been a
Professor with the School of Computer and Information, Anhui Normal University. His research interests
include data mining, information security, and big
data analysis.

Ying Hu received the Ph.D. degree from the School
of Information and Control Engineering, China University of Mining and Technology, Xuzhou, China,
in 2022. Her research interests include feature
selection, federated learning, and multi objective
optimization.

Yonglong Luo received the Ph.D. degree in computer science from the School of Computer Science
and Technology, University of Science and Technology of China, Hefei, China, in 2005. He is
currently a Professor with the School of Computer
and Information, Anhui Normal University, Hefei.
He is also the Director of Anhui Provincial Key
Laboratory of Industrial Intelligence Data Security.
His research interests include information security,
privacy protection, and data mining.
PAPER_TEXT
