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
# [491] MoCC-BD-FID: Multi-Objective Clustering Combination-Based Backdoor Defense for Federated Intrusion Detection of Industrial Control Systems
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
编号：491
题名：MoCC-BD-FID: Multi-Objective Clustering Combination-Based Backdoor Defense for Federated Intrusion Detection of Industrial Control Systems
年份：2025
DOI：10.1109/tifs.2025.3586479
来源：IEEE Transactions on Information Forensics and Security
PDF：paper/10.1109_TIFS.2025.3586479.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：联邦学习、隐私保护与分布式协同
相关性：中相关，分数 9
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\491.txt
- 原始字符数：76420
- 本次发送字符数：76420
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
6868

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

MoCC-BD-FID: Multi-Objective Clustering
Combination-Based Backdoor Defense for
Federated Intrusion Detection of
Industrial Control Systems
Guo-Qiang Zeng , Senior Member, IEEE, Jun-Min Shao, Kang-Di Lu , Member, IEEE, Guang-Gang Geng ,
and Jian Weng , Senior Member, IEEE
Abstract—Deep learning and federated learning (FL) play a
crucial role in ensuring the security of industrial control systems
(ICSs), but they also face severe security threats, especially
the threat of backdoor attacks. Most FL backdoor defense
methods primarily focus on a single clustering strategy, resulting in low true positive rates (TPR) and true negative rates
(TNR) in the attack classification task. Due to the excessive
combination scheme of currently available clustering strategies,
it is difficult to manually select an appropriate combination
scheme of clustering strategies to defense backdoor attacks in
federated ICSs. This work is the first time to automatically
design a multi-objective clustering combination-based backdoor
defense for federated intrusion detection in ICSs, called MoCCBD-FID. The automated design issue of clustering strategies
combination for backdoor defense is formulated as a mixedvariable multi-objective optimization problem, which considers
both combinatorial variables, i.e., the combination length and
the specific combination of clustering strategies, and continuous
variables, i.e., the confidence levels of each combined clustering
as the decision variables, and considers maximization of both
TPR and TNR as the two objectives. To describe and evolve the
Received 5 November 2024; revised 24 May 2025 and 26 June 2025;
accepted 1 July 2025. Date of publication 7 July 2025; date of current
version 10 July 2025. This work was supported in part by Zhejiang Provincial Natural Science Foundation of China under Grant LZ25F030007; in
part by the National Natural Science Foundation of China under Grant
61972288, Grant 62403122, and Grant 92067108; in part by the KeyArea Research and Development Program of Guangdong Province under
Grant 2020B0101090004; in part by Shanghai Sailing Program under Grant
24YF2701300; in part by the Natural Science Foundation of Guangdong
Province under Grant 2021A151501131; in part by the Ministry of Industry
and Information Technology (MIIT) Project Industrial Internet Identification Resolution System Security Monitoring and Protection under Grant
TC220H078; and in part by Guangdong Key Laboratory of Data Security and Privacy Preserving, National Joint Engineering Research Center
of Network Security Detection and Protection Technology. The associate
editor coordinating the review of this article and approving it for publication was Dr. Daisuke Mashima. (Corresponding authors: Guo-Qiang Zeng;
Kang-Di Lu.)
Guo-Qiang Zeng is with the National-Local Joint Engineering Research
Center of Digitalized Electrical Design Technology, Wenzhou University,
Wenzhou 325035, China, and also with the College of Cyber Security and the
National Joint Engineering Research Center of Network Security Detection
and Protection Technology, Jinan University, Guangzhou 510632, China
(e-mail: zeng.guoqiang5@gmail.com).
Jun-Min Shao, Guang-Gang Geng, and Jian Weng are with the College
of Cyber Security and the National Joint Engineering Research Center
of Network Security Detection and Protection Technology, Jinan University, Guangzhou 510632, China (e-mail: shaojunmin@stu2021.jnu.edu.cn;
gggeng@jnu.edu.cn; cryptjweng@gmail.com).
Kang-Di Lu is with the College of Information Science and Technology,
Donghua University, Shanghai 201620, China (e-mail: kangdilu@dhu.edu.cn).
Digital Object Identifier 10.1109/TIFS.2025.3586479

different combinations of 12 clustering strategies with confidence
levels, we develop an efficient mixed and variable-length encoding
mechanism, and the specifically tailored crossover operation
and mutation operation under the framework of nondominated
sorting genetic algorithm II. The experiments are conducted on
the three widely-used ICS datasets including Secure Water Treatment, Water Distribution, and Power System Attack datasets
under two different backdoor attacks. The experimental results
demonstrate that MoCC-BD-FID outperforms the single clustering strategy-based backdoor defense methods and five existing
backdoor defense methods, i.e., Krum, Weak-DP, FoolsGold,
DeepSight, and CrowdGuard, in terms of the classification
accuracy of the poisoned model on regular samples and backdoor
samples, TPR, and TNR.
Index Terms—Industrial control systems, federated intrusion
detection, backdoor defense, automated clustering combination,
multi-objective optimization.

I. I NTRODUCTION

I

NDUSTRIAL control systems (ICSs) are vital for managing and automating essential infrastructure, including smart
grids, water treatment plants, and manufacturing operations
[1], [2]. However, ICSs are highly susceptible to cyber-attacks
due to their increased connectivity with information technology networks and the adoption of Internet of Things devices
[3]. Recently, a variety of increasingly severe cyber-attacks
on ICSs have been reported [4], [5]. These attacks have not
only led to significant financial losses for affected companies
and entities, but also posed serious risks to the safety of local
people. Consequently, the security issue of ICS has garnered
considerable attention from the research community.
To guarantee the safe operations of a specific ICS, an
intrusion detection system (IDS) is often implemented for
real-time monitoring [6]. If any intrusions are detected within
the system, the IDS triggers an alert and initiates defensive
measures against both known and unknown cyber-attacks. Due
to its strong fitting and learning abilities, the deep learning
model has emerged as the top choice for most IDSs [7].
Furthermore, federated learning (FL) has gained widespread
adoption across various domains as an effective solution for
addressing data privacy concerns [8], [9]. Therefore, some
recent works have prioritized integrating FL with deep learning
for the intrusion detection [10], [11], [12]. Utilizing FL in IDSs
not only safeguards data privacy and security but also delivers
high classification accuracy for cyber-attacks [13], [14].

1556-6021 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

ZENG et al.: MoCC-BD-FID OF INDUSTRIAL CONTROL SYSTEMS

Although FL provides an effective method for protecting
data privacy, it simultaneously presents some challenges in
ensuring security [15]. Because FL allows federated training
without compromising data privacy, the heterogeneous distribution of data among federated clients makes it difficult
for the server to verify the integrity of local model updates.
This vulnerability makes the IDSs deployed in ICSs based
on FL susceptible to backdoor attacks [16], [17], [18], [19].
For instance, during the federated training phase, malicious
clients can tamper with the training data or model updates in
specific ways, and finally upload the poisoned updates to the
server. When the server aggregates these malicious updates, it
can lead to a global model with a backdoor, thereby forming
a backdoor attack. Therefore, it is urgent to design effective
backdoor defense schemes for federated intrusion detection of
ICSs.
In response to the new threats posed by backdoor attacks,
several clustering strategy-based backdoor defense methods
have been proposed. These techniques aim to enhance the
security of deep learning models, reduce the impact of backdoor attacks, and improve the robustness of models. It is
worth noting that most methods use a single clustering strategy
to cluster the processed client update parameters [20], [21]
with low true positive rates (TPR) and true negative rates
(TNR) in the attack classification task. Only a few methods
adopt a combination of two clustering strategies, but these
methods were designed by trial and error [22], [23]. Due to
the low interpretability of deep learning models in a federated
framework, the updated parameters of the model occurring at
the client side are generally complex and difficult to interpret.
Even after operations such as pruning, dimensionality reduction, and similarity calculation are performed on the model
update parameters by using lower dimensions to represent
these update parameters, there are still significant challenges
in accurately clustering updated parameters. Using various
advanced clustering strategies can effectively address this
issue. Therefore, clustering results of these update parameters
largely depend on whether the selected clustering strategy
can accurately perform clustering, which is the most critical
step in backdoor defense. Determining the applicability of
the selected clustering strategy is often by experimentally
comparing its test performance with other clustering strategies
[24]. However, when it is necessary to select two or more clustering strategies for combination, experimentally comparing is
clearly no longer applicable due to the excessive variety of
combination scheme of clustering strategies.
In order to employ the combination of various clustering
strategies with confidence levels to defend against backdoors,
we establish it as a mixed-variable multi-objective optimization problem. Due to the population-based characteristics,
multi-objective evolutionary algorithms, e.g., nondominated
sorting genetic algorithm II (NSGA-II) [25], are naturally
well-suited for solving multi-objective problems. However,
evolutionary algorithms do not possess efficient techniques
for generating offspring to address the mixed-variable multiobjective optimization problem. Some evolutionary operation
frequently used in continuous problems, e.g., simulated binary
crossover [26] and differential evolution mutation [27], can

6869

be introduced to solve the integer and categorical variables
after minor adjustments. In [28], a rounding operation was
considered based on continuous variable operators. For combinatorial optimization problems, offspring generation methods
must be customized to fit the unique characteristics of each
problem. Yet, these approaches often lack generalizability
and cannot be easily applied to solving various problems.
Therefore, for mixed-variable multi-objective clustering combination optimization problem, we need to carefully design
coding mechanism, crossover operation, and mutation operation to obtain more effective backdoor defense strategy.
Based on the abovementioned considerations, this paper
proposes a multi-objective clustering combination-based backdoor defense for federated intrusion detection of ICSs, called
MoCC-BD-FID. The main idea behind this method firstly formulates the combination scheme of clustering strategies with
confidence levels for effective backdoor defense of IDSs in
ICSs as a mixed-variable multi-objective optimization problem
with both combinatorial and continuous decision variables
by optimizing the trade-off between TPR and TNR. Then,
we solve the established problem efficiently by designing
a specifically tailed evolutionary algorithm under NSGA-II
framework [25].
The main contributions of this work are summarized as
follows:
(1) Most federated IDSs for ICSs focus on detecting
cyber-attacks and do not consider the possibility of backdoor
attacks in the system. Additionally, most clustering strategybased backdoor defense methods typically use a single or
two types of clustering strategies and contain the following
shortcomings: low performance in TPR and TNR and lack
an effective automatic selection mechanism to choose different combination schemes when involving multiple clustering
strategies. This work originally develops a backdoor defense
method through the automated design combination scheme
of 12 different clustering strategies for federated intrusion
detection of ICSs. To the best of our knowledge, this paper is
the first to automatically design the backdoor defense method
for federated intrusion detection of ICSs from the perspective
of multi-objective clustering combination.
(2) In the design process, the defense strategy against
backdoor attacks for federated intrusion detection of ICSs
utilizing a combination of different clustering strategies is
formulated as a mixed-variable multi-objective optimization
problem, where maximization of both TPR and TNR is defined
as the two objective functions. Furthermore, we develop an
efficient mixed-variable and variable-length encoding scheme,
and the specified crossover and mutation operations under the
framework of NSGA-II to describe and evolve various combinations of 12 classic clustering strategies with confidence
levels, i.e., the proportion of each clustering strategy in the
classification result.
(3) The experimental results on three ICS intrusion datasets
including Secure Water Treatment (SWaT) [29], Water Distribution (WADI) [30], and Power System Attack (PSA)
[31] datasets indicate that the MoCC-BD-FID obtains satisfactory defense performance against two different backdoor
attacks, i.e., SIG [32] and BadNet [33]. Moreover, the

6870

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

proposed MoCC-BD-FID outperforms other 12 types of single
clustering strategy-based backdoor methods and five existing
backdoor defense methods including three classical methods,
i.e., Krum [34], Weak-DP [35], FoolsGold [36] and two manually designed methods, i.e., DeepSight [37] and CrowdGuard
[22], in terms of the classification accuracy of the poisoned
model on regular samples and backdoor samples, TPR, and
TNR.
II. R ELATED W ORKS
In order to effectively address the challenges posed by
backdoor attacks in FL, various defense methods were presented [21], [22], [23], [24], [38], [39]. Zhang et al. [21]
presented SecFedNIDS, which first provided an efficient lowdimensional representation of the client local model update
parameters and then used the Stochastic Outlier Selection
(SOS) strategy to cluster these parameters, thereby identifying and filtering out malicious update parameters. Rieger
et al. [22] proposed federated backdoor detection method,
called CrowdGuard. It utilized feedback from clients regarding
specific models and removed compromised models using
a step-by-step pruning approach. Additionally, CrowdGuard
implemented a stacked clustering method on the server side to
strengthen its resistance against malicious client input. In [23],
RDFL was proposed. In RDFL, appropriate update parameters
were selected to compute the cosine distance. HDBSCAN and
Hierarchical Clustering strategies were combined to perform
adaptive clustering to detect and remove suspicious malicious
client updates, followed by adaptive pruning and noise addition
operations. Nguyen et al. [24] proposed the FLAME defense
framework. It first measured the angular differences between
all model update parameters by calculating the cosine distance of the update parameters from each client model in
pairs. Then, it clustered these update parameters based on
the dynamic HDBSCAN clustering strategy to identify and
filter out malicious updates. Finally, in the server-side parameter aggregation phase, it effectively eliminated backdoors
by dynamically pruning the update parameters and adding
sufficient noise. In [37], a model filtering method, called
DeepSight, was presented. DeepSight employed three novel
techniques to analyze the training data distribution and detect
subtle differences in neural networks, enabling it to identify
suspicious model updates. By clustering these updates and
applying weight clipping defenses, it effectively mitigated the
impact of potential backdoor contributions from undetected
poisoned models. Chen et al. [39] presented RFBDS method
and the privacy-preserving version, i.e., PrivRFBDS to ensure
the elimination of malicious backdoors. RFBDS first used
Amplified Magnitude Sparsification to extract the major client
local model update parameters and then calculated the median
Euclidean distance between the model updates. After that, it
performed clustering based on the OPTICS or DBSCAN strategy and finally executed an adaptive model pruning operation
to remove existing backdoors.
Most methods use a single clustering strategy to cluster
the processed client update parameters, while only a few
methods combined two clustering strategies. Due to the low
interpretability of deep learning models, the model update

Fig. 1. The process of backdoor attack in FL.

parameters from clients are complex and difficult to interpret.
Even after pruning, dimensionality reduction, and similarity calculations of the model update parameters, accurately
clustering these parameters remains a significant challenge.
Although there are backdoor defense methods based on two
clustering strategies, these methods are obtained through manually designed based on the extensive experience of experts,
making it difficult to apply when multiple clustering strategies
are involved.
III. T HE P ROPOSED M O CC-BD-FID M ETHOD
A. Assumptions
1) Attacker’s Goals: The goal of the attacker is to compromise the global intrusion detection model. The attacker
manipulates the controlled clients to perform local training
and sends malicious local update parameters to the server.
During the server’s parameter aggregation process, a specific
backdoor is implanted into the global model. This backdoor
causes the global model to misjudge specific traffic types, such
as classifying malicious traffic as normal, thereby facilitating
attacks on ICSs. The process of the backdoor attack in FL is
illustrated in Fig. 1.
2) Attacker’s Strategy: The attacker considers two types of
backdoor attacks against FL, called the SIG backdoor attack
[32] and the BadNet backdoor attack [33]. Both types of
attacks are simple and efficient to implement in real-world
settings. The SIG attack uses an overlaid sinusoidal signal as
a trigger, while BadNet uses a small square with a maximum
pixel value of 255 as a trigger. These methods are applied to
traffic to construct backdoor samples while adhering to certain
constraints in ICSs.
B. The Process of Backdoor Defense
In the scenario of defending against backdoor attacks in
federated intrusion detection of ICS, it is crucial to process the
updated parameters uploaded by clients. Typically, each update
parameter contains a large number of features, including a lot
of redundant information. To reduce this redundant information and lower the complexity of subsequent computations, it

ZENG et al.: MoCC-BD-FID OF INDUSTRIAL CONTROL SYSTEMS

6871

is necessary to first perform dimensionality reduction on the
update parameters. Here, principal component analysis (PCA)
is used to perform dimensionality reduction on the update
parameters shown in (1) as follows:
2
3
2
3
W11 . . . W1n
V11 . . . V1k
6 W21 . . . W2n 7
6 V21 . . . V2k 7
7
6
7
W=6
(1)
4 ... ... ... 5 → V = 4 ... ... ... 5
Wm1 . . . Wmn
Vm1 . . . Vmk
where W represents the set of updated parameters from all
clients participating in training under the federated framework.
m is the number of clients, with each row representing the
update parameters of a single client. n denotes the number
of features included in each update parameter. V is the value
after PCA and k is the number of features contained in each
update parameter after dimensionality reduction after PCA.
For the updated parameters V after dimensionality reduction, pairwise cosine distances are calculated to obtain the
cosine distance matrix H shown in (2)-(3) as follows:
2
3
cos11 cos12 . . . cos1m
6 cos21 cos22 . . . cos2m 7
7
H=6
(2)
4 ...
... ... ... 5
cosm1 cosm2 . . . cosmm
Vu × Vv
, 1 ≤ u, v ≤ m
(3)
cosuv = cos(Vu , Vv ) = 1 −
kVu k kVv k
It is worth noting that one advantage of calculating cosine
distance is that even if a malicious client scales up the local
model’s updated parameters to enhance its impact, the cosine
distance remains unaffected because the angle between the
update weight vectors is not changed.
Using the optimized combination scheme of clustering
strategies obtained by MoCC-BD-FID method to cluster the
cosine distance matrix H. Suppose the optimized combination
scheme is the Cluster = [l, (x1 , cl1 ) , . . . , (x j , cl j ), . . . , (xl , cll )],
then the classification results of all clustering strategies are
combined to obtain the final result of each updated parameter.
The specific calculation process is given in (4) as follows:
result =

l
X

x j × cluster j = [r1 , r2 , . . . , rh , . . . , rm ]

(4)

j=1

where l is the encoding length. cl j represents the selected
clustering strategy. cluster j is the classification result of the
clustering strategy on the cosine distance matrix. x j denotes
the confidence level of cluster j . For the clustering result of a
single clustering strategy, the category with the highest proportion is labeled as 0, meaning a normal update, while all other
categories are labeled as 1, indicating an abnormal update.
If there are multiple categories with the highest proportion,
one category is randomly selected to be labeled as 0, and the
remaining categories are labeled as 1.
Set the classification threshold th, and classify the result of
the combined clustering result to obtain the final classification
predict shown in (5) as follows:
predict
( = [pr1 , pr2 , . . . , pri , . . . , prm ]
0, rh < th
pri =
1<h<m
1, rh ≥ th,

(5)

Finally, select the updated parameters from the classification
results of 0 in the prediction. Carry out server-side parameter
aggregation and then redistribute the aggregated parameters to
each client.
C. Problem Formulation
In this paper, the searching for an optimized combination
scheme of clustering strategies is formulated as a mixedvariable multi-objective optimization problem. The detailed
decision variables, i.e., X = [l, x1 , cl1 , . . . , x j , cl j , . . . , xl , cll ]
with two objective functions F(X) are given as follows:
max F(X) = ( f1 (X), f2 (X))
(
f1 = TPR = T P/(T P + FN)
f2 = TNR = T N/(T N + FP)
Xl
s.t.
x j = 1, [cl1 , . . . , cl j , . . . , cll ] ∈ ClusterSet, 1 ≤ l
j=1

≤ 12

(6)

where
[T P, T N, FP, FN] = f (Wte , labelte , X ∗ )
X ∗ = arg min MSE(Wtr , labeltr , X)
X

1 XN
(li − ri )2
MSE =
i=1
N
labeltr = [l1 , l2 , . . . , li , . . . lN ]
result = [r1 , r2 , . . . , ri , . . . rN ]
Xl
=
(x j × cl j (Wtr ))
j=1

(7)

where f1 and f2 represent two objective functions to obtain
TPR and TNR. It should be noted that the TPR and TNR
mentioned above are metrics used to evaluate the effectiveness
of clustering methods. Here, TNR represents the proportion
of normal gradients correctly identified as normal in the
clustering results. Generally, we aim for higher TNR values
because only gradients classified as normal are aggregated
to update the global model. A higher TNR indicates fewer
malicious gradients being incorporated into the global model.
TPR measures the proportion of malicious gradients correctly identified as malicious in the clustering results. These
definitions differ from the TPR and TNR metrics used in
conventional model performance evaluation. TP represents the
number of malicious samples correctly classified as intrusions.
TN represents the number of normal samples correctly classified as normal. FP represents the number of normal samples
incorrectly classified as intrusions. FN represents the number
of malicious samples incorrectly classified as normal. Wtr is
the training set and Wte is the test set, respectively. labeltr and
labelte are the labels correspond to Wtr and Wte , respectively,
indicating the nature of the updates: 0 for normal updates
and 1 for malicious updates. l is the length of the selected
clustering strategies. [cl1 , . . . , cl j , . . . , cll ] is a combination
scheme of clustering strategies, containing a free combination
scheme of 12 different clustering strategies. ClusterSet is
the set of 12 different clustering strategies. [x1 , . . . , x j , . . . , xl ]
denotes the confidence level for each clustering strategy in

6872

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

TABLE I
T HE I NDEX AND C ORRESPONDING C LUSTERING S TRATEGY

the combination. The sum of all confidence levels equals
1. cl j (Wtr ) represents the clustering result of a single clustering
strategy on the update parameters within each sample group.
result is the result of clustering based on the combination
scheme. X ∗ is the optimal X according to the minimization
of mean squared error (MSE). N is the number of samples. f
is the relationship of testing result to obtain TP, TN, FP, and
FN based on Wte , labelte , and X ∗ .
Table I gives the index and the corresponding clustering
strategy. The details of 12 clustering strategies are described
as follows:
1) HDBSCAN: HDBSCAN is a density-based clustering
strategy aiming to identify clusters with varying densities and
can handle noise points. HDBSCAN combines the advantages
of DBSCAN and hierarchical clustering, effectively dealing
with noise and outliers in the data.
2) DBSCAN: DBSCAN is a density-based clustering strategy used to identify clusters with high density and effectively
handles noise points. DBSCAN does not require the number of
clusters to be specified in advance and can adaptively identify
clusters of arbitrary shapes. It is insensitive to the choice of
parameters.
3) K-Means: K-Means is a common clustering strategy
used to divide data points into K different clusters, aiming
to minimize the squared distance between each data point and
the center of its respective cluster. K-Means accomplishes the
clustering process by iteratively optimizing the positions of
the cluster centers.
4) MeanShift: MeanShift is a density-based nonparametric
clustering strategy used to discover density estimate patterns
in data, especially suited for identifying clusters of arbitrary
shapes. MeanShift continuously adjusts the positions of data
points, moving them towards the local maxima of the data
density, thereby locating the centers of the clusters.
5) OPTICS: OPTICS is a density-based clustering strategy
designed to identify cluster structures and noise points in data.
Similar to the DBSCAN, OPTICS can also handle clusters of
arbitrary shapes and does not require the pre-specification of
the number of clusters.
6) Spectral Clustering: Spectral Clustering is a spectral
clustering strategy based on graph theory and spectral theory
groups data by transforming it into a low-dimensional feature
space and performing clustering in space. Spectral clustering
strategies are typically used to handle clustering problems
involving non-spherical and linearly inseparable data.
7) Gaussian Mixture: Gaussian Mixture is a probabilistic
model used to describe data distributions formed by the
combination of multiple Gaussian distributions, typically used

for clustering analysis and density estimation problems. The
basic assumption is that the data is a mixture of multiple
Gaussian distributions.
8) MiniBatch KMeans: MiniBatch KMeans is a variant of
the K-Means strategy aiming to accelerate the computation
speed of the K-Means strategy, making it particularly suitable
for handling large-scale datasets. Unlike the traditional KMeans strategy, which processes all data points at once, the
MiniBatchKMeans strategy updates cluster centers using small
batches, thereby reducing computational complexity.
9) Birch: Birch is a hierarchical clustering strategy for
large-scale datasets. It aims to cluster efficiently by gradually
reducing the dimensions and density of the dataset, making
it suitable for handling large amounts of data while being
constrained by memory.
10) Agglomerative Clustering: Agglomerative Clustering is
a hierarchical clustering strategy. Agglomerative Clustering
starts from each data point, treating each data point as an
individual cluster, and then gradually merges adjacent clusters
until the stopping condition is met.
11) Affinity Propagation: Unlike traditional clustering
strategies based on distance or density, the Affinity Propagation strategy determines the propagation weights between
data points by calculating the similarity between them, thereby
achieving clustering.
12) SOS: SOS is an anomaly detection algorithm based
on random sampling, which is used to select outliers or
anomalous values in a dataset. SOS identifies potential outliers
by randomly selecting samples and calculating similarity to
other samples.
D. The Framework of MoCC-BD-FID Method
In this work, we propose a clustering combination optimization approach that combines multiple clustering algorithms to
enhance the robustness of detection. This optimization problem is inherently a mixed-variable multi-objective optimization
problem. NSGA-II excels in such scenarios due to their natural
selection mechanisms, which enable global search capabilities
without relying on continuous differentiability.
In addition, NSGA-II inherently supports mixed-variable
encoding and parallel computation, accelerating convergence
for mixed-variable multi-objective optimization problem. In
contrast, reinforcement learning requires extensive environmental interaction, particularly suffering from action space
explosion in mixed-variable settings, leading to high training
costs. Sparse and delayed reward signals further complicate
policy exploration in multi-objective optimization. Bayesian
optimization depends on prior distribution modeling with
insufficient priors or sparse data, convergence slows and suboptimal solutions. Deep learning models, primarily designed
for classification and regression, struggle to directly handle
mixed-variable multi-objective optimization. Therefore, we
use NSGA-II as the main optimization tool to solve the mixedvariable multi-objective optimization problem.
The diversity of clustering algorithms results in an enormous number of possible combinations. For instance, simple
permutations and combinations of 12 fundamental methods
already yield over 4,000 candidate solutions. Furthermore,

ZENG et al.: MoCC-BD-FID OF INDUSTRIAL CONTROL SYSTEMS

Algorithm 1 Framework of the Proposed MoCC-BD-FID
Method

the introduction of clustering method confidence parameters
significantly increases complexity, causing the number of
candidate solutions to grow exponentially. Under these circumstances, exhaustive enumeration becomes computationally
infeasible. Therefore, to efficiently identify optimal solutions,
we employ NSGA-II that automatically optimize strategies
to balance search breadth with computational cost, evaluating
and selecting the best clustering combination strategy through
objective function assessment.
The overall framework of the proposed MoCC-BD-FID
method is given in Fig. 2. The pseudocode of MoCCBD-FID method is shown in Algorithm 1. The proposed
MoCC-BD-FID method consists of four main parts: population initialization, fitness calculation, offspring generation
and environmental selection. First, determine the related input
parameters including population size N, the maximum number
of generation G, crossover probability θc , mutation probability
θm , and the set of 12 clustering strategies ClusterSet. Use the
developed encoding scheme to randomly initialize the parent
population S 0 containing N individuals and evaluate the fitness
of all individuals in S 0 . Next, perform the developed crossover
operation and mutation operation on the parent population
S 0 to generate the offspring population Qg , and evaluate the
fitness of all individuals in Qg . Merge the parent population
S n and offspring population Qg for environmental selection to
obtain the next generation population and update S n . Repeat
the above operations until the G are reached. Obtain the
Pareto front in the final population as the corresponding
combination scheme of clustering strategies and the confidence

6873

Algorithm 2 Fitness Calculation

level corresponding to each clustering strategy, and select one
solution in Pareto front for backdoor attack defense in the
FL-based intrusion detection system of ICS.
We employ NSGA-II to obtain clustering combination strategy for the cosine similarity matrix clustering. In practical
deployment, the MoCC-BD-FID is conducted offline. During
online detection, the optimized clustering scheme is directly
applied without introducing additional latency, thus satisfying
real-time response requirements. Furthermore, since FL model
aggregation is inherently periodic, the MoCC-BD-FID only
needs to be executed once during the initial federated training
phase. Subsequent model update cycles do not require multiple
iterations.
E. Population Initialization
Initialize N individuals as the initial population S 0 =
{Indii , i = 1, 2, . . . , N}, where Indii represents the encoding
of the i-th individual. Each individual represents a combination scheme of clustering strategies for backdoor defense.
The encoding format of each individual in the population
is Indii = [li , (xi1 , ci1 ), . . . , (xi j , ci j ), . . . , (xili , cili )], where li
represents the length of the current individual encoding. The
maximum length of an individual encoding is 12 and the
minimum length is 1. ci j represents the j-th encoding in the
i-th individual, where 1 ≤ j ≤ li . ci j is an integer between 1 and
12, corresponding to the serial number of a selected clustering
strategy. xi j represents the confidence level of the clustering
strategy ci j , with values ranging from 0 to 1. Fig. 3 shows
an example of mixed-variable encoding scheme of clustering
strategy.
F. Fitness Calculation
The pseudocode for fitness calculation of MoCC-BD-FID
is shown in Algorithm 2. For each individual Indii in the
population S n , decode the Indii and construct the combination
scheme of clustering strategies to form a backdoor defense.
The combination scheme is evaluated using each sample set
from the training set. For each sample set W, we can calculate
H and result according to (1)–(3)

6874

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

Fig. 2. The overall framework of the proposed MoCC-BD-FID method.

where lr is the learning rate. For the updated xi , perform
normalization according to (10)-(11) as follows:
sumx =

l
X

xi , i = 1, 2, . . . , l

(10)

i=1

xi
, i = 1, 2, . . . , l
(11)
sumx
The final confidence level xi is optimized based on all samples
in the training set. Then, the combination scheme is tested
using the test set, which is composed similarly to the training
set. For each sample wte in the test set, the clustering results
are classified according to (1)–(4). For each sample in the test
set, based on the true label labelte of each sample, TPR and
TNR are calculated as the fitness of the current combination
scheme.
normxi =

Fig. 3. An example of mixed-variable encoding scheme of clustering strategy.

Calculate the loss between the result and the true label
labletr = [l1 , l2 , . . . , lN ], as shown in (8):
N

loss =

1 X
(li − ri )2
N

(8)

i=1

Optimize the confidence coefficient xi through the gradient
descent method, as shown in (9)
xi = xi − lr ×

∂loss
,1 ≤ i ≤ l
∂Xi

(9)

G. Offspring Generation
The population S n undergoes crossover and mutation operations to produce the offspring population Qg . Two individuals
are randomly selected from S n and denoted as Indi1 and Indi2 ,
respectively. A random real number rc within the range (0,1)
is generated. If rc < θc , a position is randomly selected from

ZENG et al.: MoCC-BD-FID OF INDUSTRIAL CONTROL SYSTEMS

6875

Fig. 4. An example of the developed crossover operation.

Fig. 5. An example of the developed mutation operation.

Indi1 and Indi2 as the crossover point, and a single-point
crossover is performed on Indi1 and Indi2 to produce two
offspring individuals, i.e., c1 and c2 . If rc ≥ θc , then c1 = Indi1
and c2 = Indi2 .
Mutation operation is then performed on the offspring after
crossover. For each individual ci , a random real number rm
within the range (0,1) is generated. If rm < θm , a position is
randomly selected from ci as the mutation point. An integer pi
within the range from 1 to 12 that is different from the initial
value at the mutation point is randomly generated, replacing
the value at the mutation point in ci , thereby producing a
mutated individual.
The above-mentioned crossover operation and mutation
operation are repeated until the number of individuals in the
offspring population Qg reaches N. Fig. 4 and Fig. 5 provide
an example of the crossover operation and mutation operation,
respectively.
H. Environmental Selection
During the environmental selection phase, the framework of
NSGA-II [25] is used for environmental selection. First, the
parent population and the offspring population are merged, and
a fast non-dominated sorting is performed on the combined
population. Then, the individuals in the population are ranked
based on dominance and non-dominance relationship and the
crowding distance. Finally, an elitist strategy is adopted to
select N individuals as the next generation population.
IV. E XPERIMENTAL R ESULTS
The experiments are carried out on a server equipped with
R XeonO
R E5-2683v3 @ 2.00 GHz processor, 256 GB
an IntelO

of memory, and 4 A100-PCIE graphics cards. Binary supervised learning tasks are conducted by using SWaT, WADI,
and PSA datasets that contain normal and attack samples. For
dataset processing, Min-Max normalization is applied to the
SWaT, WADI, and PSA datasets.
During the experiments, we configure 100 federated client
nodes, with each client’s training data maintaining independent
and identically distributed characteristics to the greatest extent
possible. Four A100 GPUs are allocated to these simulated
clients to provide computational resources for data processing
and federated training. Among these 100 federated clients,
we randomly selected 10 clients as malicious participants,
whose training datasets contained a small proportion of backdoor attack samples. Each client performed local training
to generate either normal or backdoor-embedded gradients
for server-side parameter aggregation. The GPU acceleration
significantly reduces the overall federated training duration,
thereby shortening running time. Additionally, the NSGA-II
primarily relied on CPU computation, where GPU acceleration
showed limited performance improvement.
A. Datasets
(1) SWaT [29]: The SWaT (Secure Water Treatment) dataset
originates from physical testbed systems for water treatment
managed by Singapore’s Public Utility Board. Within the
field of cyber-security, SWaT is frequently utilized to examine
the impact of cyber-attacks on ICSs, assess the efficacy of
intrusion detection techniques, and measure the resilience of
defense mechanisms under cyber-attack scenarios. This dataset
monitors 51 different variables and includes data reflecting
various operational conditions, such as normal operations and
attack situations.
(2) WADI [30]: WADI (Water Distribution) is an expanded
version of the SWaT system. It represents a distribution
network made up of numerous water distribution pipelines,
making it a more intricate and practical water treatment
system. The dataset tracks 123 variables and encompasses data
from both normal operations and attack conditions.
(3) PSA [31]: The PSA (Power System Attack) dataset,
developed by Uttam Adhikari and Shengyi Pan from Oak
Ridge National Laboratories in USA, integrates measurement
data capturing typical operations, equipment malfunctions, and
cyberattack behaviors in power grids. It employs four primary data sources: phasor measurement units (PMUs), snort,
control panel logs, and relay statuses, collectively forming a

6876

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

TABLE II
T HE S TATISTICS OF DATASETS

accuracy of the poisoned model on regular samples (MA) and
the classification accuracy of the poisoned model on backdoor
samples (BA). The detailed definitions of MA and BA are
given in (12) and (13) as follows:
TP + TN
T P + T N + FP + FN
TN
BA =
T N + FP

MA =
128-dimensional feature set. Each PMU records 29 electrical
parameters, which are combined with relay alarms and logs.
The dataset also includes 12 control panel log columns and
one labeled attack-type column. Here, we use subset 1 from
PSA as the case study.
The SWaT and WADI datasets originate from Singapore’s
ICSs, while SPA dataset comes from Oak Ridge National
Laboratories in the USA. Using SPA dataset demonstrates the
transferability of the proposed MoCC-BD-FID approach for
different ICSs.
Table II gives the statistics of SWaT, WADI, and PSA
datasets.
B. Attack Scenarios
First, the effectiveness of backdoor attacks in the datasets of
ICSs is validated by generating respective backdoor samples
using SIG and BadNet methods, which are then added to the
training set for producing malicious update parameters. In the
FL setup, the number of malicious clients is set to 10%, with
each malicious client’s training set containing 5% backdoor
samples. As a deep learning-based detection method, 1D-CNN
has been widely applied in ICSs and has achieved good results
[14]. Thus, we use 1D-CNN model to deploy in the federated
IDS.
The WADI dataset serves as an extension of the SWaT
dataset, both targeting water treatment-related industrial control scenarios. They share consistent data collection methods,
sensor/actuator types, and data format designs, resulting in
similar feature semantics. For clarity, we use the SWaT dataset
as an example here. In SWaT, each sample contains 51
features, where some features represent sensor readings, i.e.,
continuous values within specific ranges, and other features
indicate controller states, i.e., discrete and limited values, e.g.,
0 for “off” and 1 for “on”.
When constructing backdoor samples from initial samples,
typically normal attack samples, we modify specific feature values to embed backdoors while ensuring compliance
with feature characteristics and physical constraints. For SIG
backdoor samples, we generate a 51-dimensional discrete
low-frequency sine wave signal aligned with SWaT’s feature
dimensions. Then, superimpose sine wave components only on
sensor features while preserving controller values and dynamically adjust certain controller features based on physical
system constraints to maintain operational logic. For BadNet
backdoor samples, we select 2-4 critical sensors as triggers,
assigning fixed values, e.g., median feature values, that satisfy
physical constraints. Then, maintain unchanged values for
remaining sensors and controllers and ensure trigger consistency across all BadNet samples. To measure the effectiveness
of backdoor attacks, we use two metrics: the classification

(12)
(13)

To comprehensively evaluate the classification performance,
we employ other three metrics including, precision (Pre),
recall (Rec), F1-score (F1), and false positive rate (FPR). The
detailed expressions of Pre, Rec, and F1 are given as follows:
TP
T P + FP
TP
Rec =
T P + FN
2 × Pre × Rec
F1 =
Pre + Rec
FP
FPR =
FP + T N
Pre =

(14)
(15)
(16)
(17)

The definitions of TP, TN, FN, and FP have been previously
explained in (6).
Table III shows the effectiveness of backdoor attack methods, i.e., SIG and BadNet, without filtering malicious update
parameters. As can be seen from Table III, without defense,
the SIG and BadNet backdoor attacks can eventually achieve
a high success rate after multiple rounds of federated training.
Additionally, Fig. 6 presents the confusion matrix of the
classification model. From Fig. 6 and Table III, we can see
that the model maintains strong classification performance
both before and after suffering from backdoor attacks. Fig. 7
presents the results of SIG and BadNet on the SWaT dataset,
including the original samples, SIG backdoor attack-based
samples, and BadNet backdoor attack-based samples. From
Fig. 7, it can be seen that the attack samples generated by
the SIG and BadNet method are close to the original samples.
Clearly, both SIG and BadNet ensure that the generated attack
samples are closely matched to the original samples.
False alarms refer to the misclassification of normal traffic
and it can be quantified by the model’s FPR metric. Based on
the FPR calculations, we can obtain the detailed false alarms
per hour. For the SWaT dataset, the FPR ranges from 0.0055
to 0.0063, resulting in 20 to 23 false alarms per hour. For the
WADI dataset, the FPR ranges from 0.0010 to 0.0011, yielding
4 false alarms per hour.
The TPR quantifies the system’s ability to detect actual
attacks, while the TNR reflects system stability, and the
FPR represents operational costs associated with false alarms.
Although even small FPR values, e.g., 0.01%, can generate
significant false alarms in large-scale ICSs, we can develop
efficient and standardized alarm rationalization by incorporating specific Industrial Cybersecurity Standards. For instance,
we can design a natural language processing model based
on the ISA 18.2 industrial alarm management standard to
automatically map penetration testing findings to Adversarial
Tactics, Techniques, and Common Knowledge relationships,

ZENG et al.: MoCC-BD-FID OF INDUSTRIAL CONTROL SYSTEMS

6877

Fig. 6. The confusion matrix of the classification model. (a) SWaT dataset under no backdoor attack; (b) SWaT dataset under SIG attack; (c) SWaT dataset
under BadNet attack; (d) WADI dataset under no backdoor attack; (e) WADI dataset under SIG attack; (f) WADI dataset under BadNet attack.

Fig. 7. Results of backdoor attack on SWaT dataset. (a) Original sample; (b) SIG backdoor attack-based sample; (c) BadNet backdoor attack-based sample.
TABLE III
T HE C LASSIFICATION P ERFORMANCE OF THE M ODEL ON THE SWAT AND WADI DATASET U NDER D IFFERENT ATTACK S CENARIOS

thereby achieving rationalized alarm management [40]. Furthermore, as suggested in [41], applying MoCC-BD-FID to
more realistic training datasets enhances the identification of
genuine attacks. Additionally, we proactively address noisy
labels that may arise from attack attempts or benign triggers,
further improving alarm rationalization. For systems that cannot tolerate any false positives, we can integrate ε-classifiers,
adopting zero false positives as the primary decision-making
metric [42].

C. Evolutionary Process of MoCC-BD-FID Method
Fig. 8 presents the Pareto fronts of MoCC-BD-FID on the
SWaT and WADI datasets under SIG and BadNet backdoor
attacks. We provide the Pareto fronts at generations 1, 5,
10, and 20. As shown in Fig. 8, for the SWaT dataset, both
the convergence and diversity of the Pareto fronts improve

continuously throughout the evolutionary process. Specifically,
the results at the 20th generation are significantly better than
those generated randomly at the 1st generation. For the WADI
dataset, the quality of the Pareto fronts also improves steadily.
Although some solutions are similar in the 5th and 10th
generations, the diversity of solutions improves by the 20th
generation, which is an important metric for Pareto fronts. The
diversity of solutions provides more options for users, which is
crucial in practical applications. Hence, using TPR and TNR
as two objective functions, the designed NSGA-II method
can obtain satisfactory Pareto fronts. This indicates that our
designed encoding method, crossover operation, and mutation
operation can effectively handle the established mixed-variable
multi-objective optimization problem.
The combination scheme of clustering strategies obtained
for SWaT and WADI in the backdoor attack scenarios of SIG
and BadNet are as follows: For SWaT: [(1, 0.3), (10, 0.3),

6878

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

Fig. 8. The Pareto front of the proposed MoCC-BD-FID method. (a) SWaT dataset under SIG attack; (b) SWaT dataset under BadNet attack; (c) WADI
dataset under SIG attack; (d) WADI dataset under BadNet attack. Gen-i, i = 1, 5, 10, 20 represents the ith generation.

(12, 0.4)] and [(11, 0.4), (12, 0.6)]. For WADI: [(3, 0.1),
(6, 0.5), (12, 0.4)] and [(1, 0.2), (11, 0.3), (12, 0.5)]. Fig. 8
shows the corresponding combination scheme of clustering
strategies. For example, in the SIG attack scenario of the
SWaT dataset, the combination scheme of clustering strategies
is [(1, 0.3), (10, 0.3), (12, 0.4)], which indicates the use
of three combination strategies: HDBSCAN, Agglomerative
Clustering, and Affinity Propagation and the corresponding
confidence levels are 0.3, 0.3, and 0.4.

TABLE IV
C OMPARISON OF BACKDOOR D EFENSE BY D IFFERENT M ETHODS
AGAINST SIG BACKDOOR ATTACK ON THE SWAT DATASET

D. Comparison With Single Clustering-Based Defense
First, collect sample parameters of normal and malicious
updates generated during the SIG and BadNet backdoor
attacks to serve as a training set for offline optimization in
the defense phase. To enhance the robustness of the backdoor
defense, the training set includes samples that each contain
10% of malicious update parameters produced by SIG and
BadNet. The optimized combination scheme of clustering
strategies is then applied to two different scenarios, i.e., SIG
and BadNet.
1) Backdoor Defense for SWaT Dataset: Table IV and
Table V present the backdoor defense experimental results
on the SWaT dataset. It should be noted that the minor
differences in MA metrics in Table VI are related to our
designed backdoor attack approach. A successful backdoor
attack should maintain model performance on normal samples
while effectively triggering specific backdoor samples. This
means metrics like accuracy and F1-score on normal test sets
should show no significant difference from clean models, while
accurately identifying backdoor samples.
The BA primarily depends on the clustering methods
employed. The experiments reveal that single clustering methods can initially identify normal gradients, i.e., high TNR,
precisely in early federated training rounds due to their
dominant proportion. However, if any round exhibits poor
clustering performance on normal gradients, the aggregated

TABLE V
C OMPARISON OF BACKDOOR D EFENSE BY D IFFERENT M ETHODS
AGAINST BAD N ET BACKDOOR ATTACK ON THE SWAT DATASET

global model incorporates more backdoor parameters, subsequently increasing difficulty in identifying normal gradients in

ZENG et al.: MoCC-BD-FID OF INDUSTRIAL CONTROL SYSTEMS

TABLE VI
C OMPARISON OF BACKDOOR D EFENSE BY D IFFERENT M ETHODS
AGAINST SIG BACKDOOR ATTACK ON THE WADI DATASET

later rounds. This leads to gradually deteriorating clustering
performance, demonstrating the limitation of single clustering
methods, i.e., their lack of robustness. A single round of
poor clustering can significantly compromise overall defense
effectiveness, causing BA to increase and stabilize at higher
values while TNR approaches undefended states. This explains
why most single clustering methods show similar BA and TNR
metrics. In contrast, the proposed combined multiple clustering
approach enhances robustness, where poor performance of
any single method in a particular round doesn’t affect overall
clustering effectiveness, thereby improving TNR and reducing
BA.
Regarding TPR metrics, the generally low values in the
tables result from our experimental setup where malicious
clients constituted only 10% of SWaT dataset participants,
with backdoor samples accounting for merely 0.5% of each
malicious client’s training data. This configuration makes
backdoor attacks stealthier, causing most clustering methods
to perform poorly in identifying malicious gradients, hence the
similarly low TPR values across different methods.
From Tables IV–V, it can be observed that:
MoCC-BD-FID achieves the best overall performance.
Although the TPR value of Agglomerative Clustering is
0.1203, slightly higher than the 0.12 of MoCC-BD-FID, all
other single cluster-based defense methods performed worse
than MoCC-BD-FID. Specifically, when comparing MoCCBD-FID with Spectral Clustering, it can be observed that all
other performance indices of MoCC-BD-FID are much better
than those of Spectral Clustering. Similarly, when comparing
MoCC-BD-FID with Agglomerative Clustering, the other performance indices of MoCC-BD-FID are significantly better.
This shows that the proposed MoCC-BD-FID has a strong
defense effect against SIG backdoor attacks in the SWAT
dataset.
Comparing the defense methods based on single cluster
strategy with the no-defense scenario, the BA value under
the no-defense condition is the worst. Intuitively, since nodefense does not account for defending against backdoor
attacks, its BA value is the highest. The results obtained by
MoCC-BD-FID are based on a combination of three clustering

6879

strategies with different confidence levels. Compared with a
single clustering strategy, MoCC-BD-FID achieves the lowest
BA value, as it can better defend against backdoor attacks.
Moreover, these three clustering strategies are automatically
selected without requiring manual trial and error, which is one
of the advantages of MoCC-BD-FID.
By analyzing the results of single cluster strategy, it can be
seen that no single cluster strategy method can achieve the
best result. This also indicates the necessity of selecting an
appropriate combination scheme of clustering strategies.
In the case of the BadNet backdoor attack, we can also
obtain similar results. The MoCC-BD-FID method achieves
the best results. Although its TPR value is not as good as
HDBSCAN and SOS, this performance index of MoCC-BDFID are very close to those of HDBSCAN and SOS. Further
comparison between MoCC-BD-FID and SOS shows that the
BA value of MoCC-BD-FID is 0.2185, much smaller than the
BA value of SOS. Additionally, the TNR value of MoCCBD-FID is 0.9586, which is much higher than the 0.9173 of
SOS.
Comparing the defense performances in the SIG and BadNet
scenarios, we can see that the BA values in the SIG scenario
are all larger than those in the BadNet scenario, indicating that
the SIG attack has a more severe impact. However, MoCC-BDFID can still maintain the BA value below 0.3, demonstrating
the effectiveness of MoCC-BD-FID in defending against backdoor attacks.
Regarding the issue of low TPR and TNR accuracy in single
cluster strategy-based backdoor defense method, the proposed
MoCC-BD-FID improves performance and surpasses all single
cluster strategy-based methods, except that under SIG attacks,
the TPR is lower than DBSCAN and Spectral Clustering.
Here, we need to emphasize that although we consider various
clustering strategies, the combination scheme is automatically
selected and does not require trial-and-error method.
2) Backdoor Defense for WADI Dataset: Tables VI shows
the defense results on the WADI dataset under SIG backdoor attack. From Table VI, we can see that MoCC-BD-FID
achieves the best overall performance. Although the TPR
value is 0.1483, ranking third, it is only slightly worse
than MeanShift and MiniBatchKMeans but better than other
strategies. Analyzing the BA value, we observe that MoCCBD-FID’s value of 0.03 is significantly better than other
methods, especially compared to OPTICS, which has a BA
value as high as 0.72. Furthermore, the results reveal that
MeanShift performs best in TPR. SOS achieves the best BA
result among single clustering strategies, but its TPR and TNR
are not the best. This shows that single clustering strategies
may perform well in certain aspects but struggle to achieve
the best overall performance. MoCC-BD-FID, targeting the
SIG backdoor attack on the WDIA dataset, automatically
selects the combination scheme of clustering strategies with
corresponding confidence levels, achieving better overall performance than single clustering strategies while overcoming
the design process relied on experts.
Regarding the scenario of BadNet backdoor attacks on the
WADI dataset, Table VII presents the comparison results of
MoCC-BD-FID and other single clustering strategies. From

6880

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

Fig. 9. The final clustering combination strategy obtained from Pareto front of the proposed MoCC-BD-FID method. (a) SWaT dataset under SIG attack; (b)
SWaT dataset under BadNet attack; (c) WADI dataset under SIG attack; (d) WADI dataset under BadNet attack.

Fig. 10. The rank of four performance indices of MoCC-BD-FID and other compared methods: (a) SIG backdoor attack on SWaT dataset; (b) BadNet
backdoor attack on SWaT dataset; (c) SIG backdoor attack on WADI dataset; (d) BadNet backdoor attack on WADI dataset.
TABLE VII

TABLE VIII

C OMPARISON OF BACKDOOR D EFENSE BY D IFFERENT M ETHODS
AGAINST BAD N ET BACKDOOR ATTACK ON THE WADI DATASET

C OMPARISON OF F IVE E XISTING BACKDOOR D EFENSES AGAINST SIG
BACKDOOR ATTACK ON THE SWAT DATASET

MoCC-BD-FID method rank first or second, especially the
BA, TPR, and TNR metrics. Since MoCC-BD-FID is essentially a backdoor defense method, the BA metric is very
important and always ranks first. The TPR and TNR metrics,
which are the objective functions during evolutionary process,
can dominate most methods. This indicates the effectiveness
of MoCC-BD-FID.
Table VII, it can be seen that MoCC-BD-FID has the best
overall performance. Especially, in the BA value, it achieves
as low as 0.1682, which is significantly better than the highest
value of 0.7925. The TPR metric ranks second, just behind
SOS’s 0.29. Additionally, MoCC-BD-FID achieves the best
TNR, indicating that MoCC-BD-FID is effective in handling
BadNet attacks.
Fig. 10 gives the rank of four performance indices of
MoCC-BD-FID and other compared method. From Fig.
10, it can be seen that most performance indices of the

E. Comparison With Existing Backdoor Defense
To further demonstrate the effectiveness of the proposed
backdoor defense method, we select five existing backdoor
defense methods including three classic backdoor defense
methods, i.e., Krum [34], Weak-DP [35], FoolsGold [36] and
two manually designed methods, i.e., DeepSight [37] and
CrowdGuard [22], as comparison methods on the SWaT and
WADI datasets.

ZENG et al.: MoCC-BD-FID OF INDUSTRIAL CONTROL SYSTEMS

TABLE IX
C OMPARISON OF F IVE E XISTING BACKDOOR D EFENSES AGAINST BAD N ET BACKDOOR ATTACK ON THE SWAT DATASET

6881

TABLE XII
C OMPARISON OF BACKDOOR D EFENSE BY D IFFERENT M ETHODS
AGAINST SIG BACKDOOR ATTACK ON THE SPA DATASET

TABLE X
C OMPARISON OF F IVE E XISTING BACKDOOR D EFENSES AGAINST SIG
BACKDOOR ATTACK ON THE WADI DATASET

TABLE XIII
C OMPARISON OF BACKDOOR D EFENSE BY D IFFERENT M ETHODS
AGAINST BAD N ET BACKDOOR ATTACK ON THE SPA DATASET

TABLE XI
C OMPARISON OF F IVE E XISTING BACKDOOR D EFENSES AGAINST BAD N ET BACKDOOR ATTACK ON THE WADI DATASET

Table VIII and Table IX show the comparison of six
defense methods under SIG backdoor attack and BadNet
backdoor attack on the SWaT dataset, respectively. From
Table VIII, MoCC-BD-FID outperforms the existing five
methods. Although the MA value of MoCC-BD-FID is 0.9883,
slightly lower than DeepSight’s 0.9893 and CrowdGuard’s
0.9884, the other metrics are all the best. It should be noted
that the BA metric of MoCC-BD-FID is significantly higher
than that of manually designed CrowdGuard and DeepSight.
This shows that the method of automatically selecting a
combination scheme of clustering strategies can effectively
defend against SIG backdoor attacks. Similarly, from Table IX,
we can see that MoCC-BD-FID is only slightly lower than
Krum’s 0.9885 in the MA metric, while it performs best in
all other aspects, especially with a significant improvement in
the BA value.
Table X and Table XI present the defense comparison
results of MoCC-BD-FID and five other methods under SIG
and BadNet attacks on the WADI dataset, respectively. From
Table X, it can be observed that all the metrics of MoCCBD-FID are the best, with significant improvements in both
the BA and TNR metrics. From Table XI, although the MA
value of MoCC-BD-FID is slightly inferior to other methods,
its BA, TPR, and TNR values are much better than those of
the other methods.

F. Transferability
This subsection demonstrates the transferability of MoCCBD-FID. While previous experimental results focused on
Singapore’s ICSs, we here employ the PSA dataset from
Oak Ridge National Laboratories in the USA. Tables XII
and XIII present the backdoor defense results against BadNet
backdoor attack and SIG backdoor attack on the PSA dataset.
The results show that MoCC-BD-FID achieves similar MA
values while obtaining the best BA values compared to nodefense and other single clustering methods. For TPR and
TNR metrics, MoCC-BD-FID delivers the best performance
against SIG backdoor attack. Against BadNet backdoor attack,
MoCC-BD-FID achieves 0.2164 in TPR, slightly lower than
the top-performing Birch single clustering method, but significantly outperforms other single clustering approaches.
To further demonstrate the effectiveness of MoCC-BD-FID
on the PSA dataset, we compared it with Krum [34], Weak-DP
[35], FoolsGold [36], DeepSight [37], and CrowdGuard [22].
Table XIV presents the comparison results between MoCCBD-FID and these five methods against SIG backdoor attacks
on the SPA dataset, while Table XV shows the defense performance comparison of all six methods against BadNet backdoor
attacks on SPA dataset. The results in Tables XIV and XV

6882

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

TABLE XIV
C OMPARISON OF F IVE E XISTING BACKDOOR D EFENSES AGAINST SIG
BACKDOOR ATTACK ON THE SPA DATASET

then leverage the distributional similarity between backdoor
samples and OOD samples to obtain the required backdoor
samples for MoCC-BD-FID. This enables MoCC-BD-FID to
detect OOD backdoors to some extent. Also, MoCC-BD-FID
can be extended to solve OOD backdoors by designing a
method to mount clean-label backdoor attacks or predicting
label transitions based on counterfactual explanation [44], [45].
V. C ONCLUSION

TABLE XV
C OMPARISON OF F IVE E XISTING BACKDOOR D EFENSES AGAINST SIG
BACKDOOR ATTACK ON THE SPA DATASET

demonstrate that MoCC-BD-FID achieves best performance,
particularly in terms of the BA metric, obtaining values of
0.2062 and 0.1908 for SIG backdoor attack and BadNet
backdoor attack scenarios, respectively. These comprehensive
results confirm that MoCC-BD-FID can be successfully transferred to other ICS environments while maintaining excellent
performance.
G. Discussion
In real ICSs, online testing of new IDSs is typically not
permitted. Performance evaluation of novel IDSs is generally
first conducted on public datasets or experimental testbeds.
Considering data privacy and security concerns when actual
systems are under attack, complete datasets are rarely publicly available. In academic research, experimental approaches
can simulate attacks on practical systems to generate highly
representative data including the characteristics of large-scale
and operational environments [43]. In this paper, we employ
the SWaT, WADI, and SPA datasets, which largely reflect the
characteristics of real systems, and are widely used in existing
literature to validate the effectiveness of model. Therefore, if
MoCC-BD-FID performs well on these datasets, it should also
achieve good performance when applied to practical systems.
In practical deployment, the MoCC-BD-FID is conducted
offline. During online detection, the optimized clustering
scheme is directly applied without introducing additional
latency, thus satisfying real-time response requirements. Furthermore, since FL model aggregation is inherently periodic,
the MoCC-BD-FID only needs to be executed once during
the initial federated training phase. Subsequent model update
cycles do not require multiple iterations. Therefore, when
deployed in practical systems, MoCC-BD-FID can achieve
real-time detection.
Detecting out of distribution (OOD) backdoors remains a
challenging task, and MoCC-BD-FID can be extended for
OOD backdoor detection. Following [44], we first inject
indicator tasks into the global model by using OOD data,

In this paper, we have proposed a multi-objective clustering
combination-based backdoor defense for federated intrusion
detection of ICSs, called MoCC-BD-FID. In MoCC-BD-FID,
we establish the automated design issue of clustering strategies
combination for defense method as the mixed-variable multiobjective optimization problem by maximizing both TPR
and TNR. Besides, we have developed an efficient encoding
strategy, crossover operation and mutation operation under the
framework of NSGA-II to describe and evolve the different
combination schemes of 12 classic clustering strategies with
different confidence levels. The effectiveness of the backdoor
defense strategy is illustrated by subjecting 1D-CNN to two
different attack scenarios including SIG and BadNet on three
widely-used ICS intrusion datasets i.e., SWaT, WADI, and
PSA. The experimental results have shown that MoCC-BDFID achieves better performance in MA, BA, TPR and TNR
than other 12 single cluster strategy-based methods, three
classic backdoor defense methods, i.e., Krum [34], Weak-DP
[35], FoolsGold [36] and two manually designed methods,
i.e., DeepSight [37] and CrowdGuard [22]. In addition, the
combination scheme of clustering strategies is automatically
designed by the developed NSGA-II, which overcomes the
difficulty in determining combination scheme involving more
than two clustering strategies.
This work focuses on the automatic selection of an appropriate combination of clustering strategies for defending
against backdoor attacks, so the illustrated deep learning
model employed in this study is a simple 1D-CNN, whose
detection performance especially the FPR can be further
improved. In practical deployments, more advanced models
such as automated federated IDS (Fed-GA-CNN-IDS) [14]
and multi-objective discrete extremal optimization-based CNN
(MODEO-CNN) [47] will be adopted to further reduce the
FPR. For federated IDSs, FPR is directly correlated with
model performance after federated training. However, FL
encounters increasing convergence challenges with more participating clients, making it difficult to obtain optimal models.
For future work, we plan to implement multi-dimensional
collaborative optimization through personalized FL, efficient
aggregation strategies, and automated deep learning techniques
to systematically reduce FPR while improving convergence
efficiency. Also, it will be interesting to develop more robust
defense methods against OOD backdoor attacks.
R EFERENCES
[1]

H. Zhu, M. Liu, C. Fang, R. Deng, and P. Cheng, “Detectionperformance tradeoff for watermarking in industrial control systems,”
IEEE Trans. Inf. Forensics Security, vol. 18, pp. 2780–2793, 2023.

ZENG et al.: MoCC-BD-FID OF INDUSTRIAL CONTROL SYSTEMS

[2]

V. Tay et al., “Taxonomy of fingerprinting techniques for evaluation of
smart grid honeypot realism,” in Proc. IEEE Int. Conf. Commun., Control, Comput. Technol. Smart Grids (SmartGridComm), Kalba, United
Kingdom, Oct. 2023, pp. 1–7.
[3] Y. Shan, Y. Yao, T. Zhao, and W. Yang, “NeuPot: A neural networkbased honeypot for detecting cyber threats in industrial control systems,”
IEEE Trans. Ind. Informat., vol. 19, no. 10, pp. 10512–10522, Oct.
2023.
[4] M. Asiri, N. Saxena, R. Gjomemo, and P. Burnap, “Understanding
indicators of compromise against cyber-attacks in industrial control
systems: A security perspective,” ACM Trans. Cyber-Phys. Syst., vol. 7,
no. 2, pp. 1–33, Apr. 2023.
[5] R. Langner, “Stuxnet: Dissecting a cyberwarfare weapon,” IEEE Secur.
Privacy, vol. 9, no. 3, pp. 49–51, May 2011.
[6] J. Chen, Y. Zhao, Q. Li, X. Feng, and K. Xu, “FedDef: Defense against
gradient leakage in federated learning-based network intrusion detection
systems,” IEEE Trans. Inf. Forensics Security, vol. 18, pp. 4561–4576,
2023.
[7] M. Kravchik and A. Shabtai, “Efficient cyber attack detection in industrial control systems using lightweight neural networks and PCA,” IEEE
Trans. Dependable Secure Comput., vol. 19, no. 4, pp. 2179–2197, Jul.
2022.
[8] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. Y. Arcas,
“Communication-efficient learning of deep networks from decentralized
data,” in Proc. 20th Int. Conf. Artif. Intell. Statist., 2017, pp. 1273–1282.
[9] H. Zhang, K. Zeng, and S. Lin, “Federated graph neural network for
fast anomaly detection in controller area networks,” IEEE Trans. Inf.
Forensics Security, vol. 18, pp. 1566–1579, 2023.
[10] A. Albaseer, N. Abdi, M. Abdallah, M. Qaraqe, and S. Al-Kuwari,
“FedPot: A quality-aware collaborative and incentivized honeypot-based
detector for smart grid networks,” IEEE Trans. Netw. Service Manage.,
vol. 21, no. 4, pp. 4844–4860, Aug. 2024.
[11] X. Huang, J. Liu, Y. Lai, B. Mao, and H. Lyu, “EEFED: Personalized
federated learning of execution & evaluation dual network for CPS intrusion detection,” IEEE Trans. Inf. Forensics Security, vol. 18, pp. 41–56,
2023.
[12] B. Ghimire and D. B. Rawat, “Recent advances on federated learning
for cybersecurity and cybersecurity for federated learning for Internet of
Things,” IEEE Internet Things J., vol. 9, no. 11, pp. 8229–8249, Jun.
2022.
[13] S. I. Popoola, R. Ande, B. Adebisi, G. Gui, M. Hammoudeh, and
O. Jogunola, “Federated deep learning for zero-day botnet attack
detection in IoT-edge devices,” IEEE Internet Things J., vol. 9, no. 5,
pp. 3930–3944, Mar. 2022.
[14] J.-M. Shao, G.-Q. Zeng, K.-D. Lu, G.-G. Geng, and J. Weng,
“Automated federated learning for intrusion detection of industrial control systems based on evolutionary neural architecture search,” Comput.
Secur., vol. 143, Aug. 2024, Art. no. 103910.
[15] X. Hao, C. Lin, W. Dong, X. Huang, and H. Xiong, “Robust and secure
federated learning against hybrid attacks: A generic architecture,” IEEE
Trans. Inf. Forensics Security, vol. 19, pp. 1576–1588, 2024.
[16] E. Bagdasaryan, A. Veit, Y. Hua, D. Estrin, and V. Shmatikov, “How
to backdoor federated learning,” in Proc. Int. Conf. Artif. Intell. Statist.,
2020, pp. 2938–2948.
[17] X. Gong, Y. Chen, Q. Wang, and W. Kong, “Backdoor attacks and
defenses in federated learning: State-of-the-art, taxonomy, and future
directions,” IEEE Wireless Commun., vol. 30, no. 2, pp. 114–121, Apr.
2023.
[18] Y. Wan, Y. Qu, W. Ni, Y. Xiang, L. Gao, and E. Hossain, “Data and
model poisoning backdoor attacks on wireless federated learning, and the
defense mechanisms: A comprehensive survey,” IEEE Commun. Surveys
Tuts., vol. 26, no. 3, pp. 1861–1897, 3rd Quart., 2024.
[19] T. D. Nguyen, T. Nguyen, P. L. Nguyen, H. H. Pham, K. D. Doan,
and K.-S. Wong, “Backdoor attacks and defenses in federated learning:
Survey, challenges and future research directions,” Eng. Appl. Artif.
Intell., vol. 127, Jan. 2024, Art. no. 107166.
[20] H. Jeong, H. Son, S. Lee, J. Hyun, and T.-M. Chung, “FedCC:
Robust federated learning against model poisoning attacks,” 2022,
arXiv:2212.01976.
[21] Z. Zhang, Y. Zhang, D. Guo, L. Yao, and Z. Li, “SecFedNIDS: Robust
defense for poisoning attack against federated learning-based network
intrusion detection system,” Future Gener. Comput. Syst., vol. 134,
pp. 154–169, Sep. 2022.
[22] P. Rieger, T. Krauß, M. Miettinen, A. Dmitrienko, and A.-R. Sadeghi,
“CrowdGuard: Federated backdoor detection in federated learning,”
2022, arXiv:2210.07714.

6883

[23] Y. Wang, D.-H. Zhai, Y. He, and Y. Xia, “An adaptive robust defending
algorithm against backdoor attacks in federated learning,” Future Gener.
Comput. Syst., vol. 143, pp. 118–131, Jun. 2023.
[24] T. D. Nguyen et al., “FLAME: Taming backdoors in federated learning,”
in Proc. 31st USENIX Security Symp. (USENIX Security), 2022,
pp. 1415–1432.
[25] K. Deb, A. Pratap, S. Agarwal, and T. Meyarivan, “A fast and elitist
multiobjective genetic algorithm: NSGA-II,” IEEE Trans. Evol. Comput., vol. 6, no. 2, pp. 182–197, Apr. 2002.
[26] K. Deb, K. Sindhya, and T. Okabe, “Self-adaptive simulated binary
crossover for real-parameter optimization,” in Proc. 9th Annu. Conf.
Genet. Evol. Comput., 2007, pp. 1187–1194.
[27] H. Li and Q. Zhang, “Multiobjective optimization problems with complicated Pareto sets, MOEA/D and NSGA-II,” IEEE Trans. Evol. Comput.,
vol. 13, no. 2, pp. 284–302, Apr. 2009.
[28] J. Liu, Y. Wang, B. Xin, and L. Wang, “A biobjective perspective for
mixed-integer programming,” IEEE Trans. Syst., Man, Cybern., Syst.,
vol. 52, no. 4, pp. 2374–2385, Apr. 2022.
[29] J. Goh, S. Adepu, K. N. Junejo, and A. Mathur, “A dataset to support
research in the design of secure water treatment systems,” in Proc. Int.
Conf. Crit. Inf. Infrastruct. Secur., 2017, pp. 88–99.
[30] C. M. Ahmed, V. R. Palleti, and A. P. Mathur, “WADI: A water
distribution testbed for research in the design of secure cyber physical
systems,” in Proc. Int. Workshop CySWater, 2017, pp. 25–28.
[31] S. Pan, T. Morris, and U. Adhikari, “Classification of disturbances and
cyber-attacks in power systems using heterogeneous time-synchronized
data,” IEEE Trans. Ind. Informat., vol. 11, no. 3, pp. 650–662, Jun.
2015.
[32] M. Barni, K. Kallas, and B. Tondi, “A new backdoor attack in CNNs
by training set corruption without label poisoning,” in Proc. IEEE Int.
Conf. Image Process. (ICIP), Sep. 2019, pp. 101–105.
[33] T. Gu, K. Liu, B. Dolan-Gavitt, and S. Garg, “BadNets: Evaluating
backdooring attacks on deep neural networks,” IEEE Access, vol. 7,
pp. 47230–47244, 2019.
[34] P. Blanchard, E. M. E. Mhamdi, R. Guerraoui, and J. Stainer, “Machine
learning with adversaries: Byzantine tolerant gradient descent,” in Proc.
Adv. Neural Inf. Process. Syst., vol. 30, Dec. 2017, pp. 118–128.
[35] Z. Sun, P. Kairouz, A. Theertha Suresh, and H. Brendan McMahan, “Can
you really backdoor federated learning?,” 2019, arXiv:1911.07963.
[36] C. Fung, C. J. Yoon, and I. Beschastnikh, “The limitations of federated
learning in Sybil settings,” in Proc. 23rd Int. Symp. Res. Attacks,
Intrusions Defenses, 2020, pp. 301–316.
[37] P. Rieger, T. Duc Nguyen, M. Miettinen, and A.-R. Sadeghi, “DeepSight:
Mitigating backdoor attacks in federated learning through deep model
inspection,” 2022, arXiv:2201.00763.
[38] X. Cao, J. Jia, and N. Z. Gong, “Provably secure federated learning
against malicious clients,” in Proc. AAAI Conf. Artif. Intell., 2021,
vol. 35, no. 8, pp. 6885–6893.
[39] Z. Chen, S. Yu, M. Fan, X. Liu, and R. H. Deng, “Privacy-enhancing
and robust backdoor defense for federated learning on heterogeneous
data,” IEEE Trans. Inf. Forensics Security, vol. 19, pp. 693–707, 2024.
[40] S. Alabdulhadi and A. Al-Matouq, “Efficient and standardized alarm
rationalization for cybersecurity monitoring,” IEEE Access, vol. 12,
pp. 166936–166944, 2024.
[41] L. Yang et al., “True attacks, attack attempts, or benign triggers?
An empirical measurement of network alerts in a security operations
center,” in Proc. 33rd USENIX Secur. Symp. (USENIX Secur. 24), 2024,
pp. 1525–1542.
[42] M. Sayad Haghighi, F. Farivar, and A. Jolfaei, “A machine learningbased approach to build zero false-positive IPSs for industrial IoT and
CPS with a case study on power grids security,” IEEE Trans. Ind. Appl.,
vol. 60, no. 1, pp. 920–928, Jan. 2024.
[43] R. Sommer and V. Paxson, “Outside the closed world: On using machine
learning for network intrusion detection,” in Proc. IEEE Symp. Security
Privacy, May 2010, pp. 305–316.
[44] S. Li and Y. Dai, “BackdoorIndicator: Leveraging OOD data for proactive backdoor detection in federated learning,” in Proc. 33rd USENIX
Secur. Symp. (USENIX Secur.), 2024, pp. 4193–4210.
[45] Y. Zeng, M. Pan, H. Just, L. Lyu, M. Qiu, and R. Jia, “Narcissus: A
practical clean-label Backdoor attack with limited information,” in Proc.
ACM SIGSAC Conf. Comput. Commun. Secur., 2023, pp. 771–785.
[46] H. Sui et al., “DMGNN: Detecting and mitigating backdoor attacks in
graph neural networks,” 2024, arXiv:2410.14105.
[47] K.-D. Lu, J.-C. Huang, G.-Q. Zeng, M.-R. Chen, G.-G. Geng, and
J. Weng, “Multi-objective discrete extremal optimization of variablelength blocks-based CNN by joint NAS and HPO for intrusion detection
in IIoT,” IEEE Trans. Dependable Secure Comput., early access, Feb.
24, 2025, doi: 10.1109/TDSC.2025.3545363.
PAPER_TEXT
