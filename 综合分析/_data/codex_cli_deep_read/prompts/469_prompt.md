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
# [469] Integrating Explainable AI for Effective Malware Detection in Encrypted Network Traffic
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
编号：469
题名：Integrating Explainable AI for Effective Malware Detection in Encrypted Network Traffic
年份：2025
DOI：10.48550/arXiv.2501.05387
来源：arXiv preprint
PDF：paper/10.48550_arXiv.2501.05387.pdf
已有粗分类：恶意流量、暗网与攻击检测
二级关联：无
相关性：强相关，分数 15
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\469.txt
- 原始字符数：43204
- 本次发送字符数：43204
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Integrating Explainable AI for Effective Malware
Detection in Encrypted Network Traffic
Sileshi Nibret Zeleke1[0009−0006−8172−9646] Amsalu Fentie
Jember
, and Mario Bochicchio1,2[0000−0002−9122−6317]
1[0009−0004−7356−682X]

Department of Computer Science, University of Bari, Bari, Italy
Digital Health National Lab, CINI - Consorzio Interuniversitario Nazionale per
l’Informatica, Roma, Italy
{sileshi.zeleke,amsalu.jember,mario.bochicchio}@uniba.it
1

arXiv:2501.05387v1 [cs.CR] 9 Jan 2025

2

Abstract. Encrypted network communication ensures confidentiality,
integrity, and privacy between endpoints. However, attackers are increasingly exploiting encryption to conceal malicious behavior. Detecting unknown encrypted malicious traffic without decrypting the payloads remains a significant challenge. In this study, we investigate the integration
of explainable artificial intelligence (XAI) techniques to detect malicious
network traffic. We employ ensemble learning models to identify malicious activity using multi-view features extracted from various aspects of
encrypted communication. To effectively represent malicious communication, we compiled a robust dataset with 1,127 unique connections, more
than any other available open-source dataset, and spanning 54 malware
families. Our models were benchmarked against the CTU-13 dataset,
achieving performance of over 99% accuracy, precision, and F1-score. Additionally, the eXtreme Gradient Boosting (XGB) model demonstrated
99.32% accuracy, 99.53% precision, and 99.43% F1-score on our custom
dataset. By leveraging Shapley Additive Explanations (SHAP), we identified that the maximum packet size, mean inter-arrival time of packets,
and transport layer security version used are the most critical features for
the global model explanation. Furthermore, key features were identified
as important for local explanations across both datasets for individual
traffic samples. These insights provide a deeper understanding of the
model’s decision-making process, enhancing the transparency and reliability of detecting malicious encrypted traffic.
Keywords: XAI · Encrypted malware · SHAP · Ensemble tree · TreeShap

1

Introduction

Malware represents a persistent cyber threat, and with the widespread adoption
of encryption in network communications, it is increasingly being transmitted
over encrypted channels [29]. As encryption becomes more prevalent for securing
networks, including its use by malware to evade detection and analysis, the ability to inspect encrypted traffic for signs of malicious behavior has become crucial

2

Sileshi N. Zeleke et al.

for effective cybersecurity. This gap is addressed by encrypted network analysis,
which provides methods and resources for deciphering encrypted data and identifying indicators of compromise or hostile activity over encrypted communication
channels. Traditional malware detection techniques may struggle to identify encrypted malware, and deep packet inspection can compromise the privacy of the
payload [31]. To overcome this challenge, some studies have focused on analyzing encrypted traffic through decryption, which can also compromise privacy.
However, many of these studies primarily consider the efficiency or accuracy of
intelligence-based detection systems. Most research prioritizes the efficiency and
accuracy of these systems while neglecting the importance of explainability in cybersecurity tasks. A better understanding of the model’s decisions in classifying
specific traffic flows as malicious or normal is essential for effective analytics.
Explainable Artificial Intelligence (XAI) has emerged as a means to interpret
the outputs of machine learning algorithms. XAI techniques can be categorized
into local and global interpretations. Local methods provide insights into specific instances, while global methods offer a comprehensive interpretation of the
model. Global explanations focus on interpreting the model’s behavior across the
entire test sample, enhancing the interpretability of the model. XAI techniques
can be either model-agnostic or model-dependent, depending on how much they
rely on specific AI models. While model-agnostic approaches can theoretically
be applied to any AI model, model-dependent methods are specifically designed
for a given model [30].
In this study, We analyzed raw encrypted traffic from 6 different sources
to extract and analyze different feature sets that can discriminate malicious
flows from normal flows. The features include a handshake, certificate, interarrival time and packet length, statistical features, meta-connection features,
and cipher suite used. Despite progress, challenges remain in multi-view feature
analysis, deep feature analysis, and efficient detection and classification models.
We extract diverse features from encrypted traffic and regard encrypted traffic as sample nodes, then use AI for malicious traffic detection. This research
addresses gaps in explainability of model decisions and feature engineering of
flows of encrypted network traffic. A diverse feature set of encrypted network
communication, including server-side features, have important roles in detection
but have not been analyzed in previous studies.
The main contributions of this study are:
− Explainable approach to detect encrypted malware in network traffic.
− Identify important features from server-side, time-related, payload-related,
or other sets for detection models.
− A dataset containing 1,127 malware traffic from 54 different malware families
which represent significant number of malware variants is presented for the
research community.
The rest of the paper is organized as follows. Section 2, is a literature review
of existing encrypted malware detection studies and usage of explainable models for malware detection. Section 3 describes the proposed malware detection
methodology. The experimental setup and test results are presented in Section 4.

Explainable AI for Encrypted Malware Traffic

3

However, Section 5 discusses and concludes the paper with remarks and future
work ideas.

2

Related Work

Recent advances in encrypted traffic analysis for malware detection and XAI
have attracted significant research attention. Notably, Cisco has pioneered the
implementation of an encrypted traffic analyzer in their security devices. The
proposed supervised models are trained with multi-view features such as transport layer security (TLS) handshake metadata. Moreover, DNS contextual flows
and HTTP metadata from the same source IP within a 5-minute interval, have
shown the potential of AI models to identify malware traffic [1]. By observing the
disparities between malicious and normal network flow’s contextual information
were can capture strong discriminatory feature set [2].
Analytical techniques to infer HTTP semantics from passive observations of
HTTPS can reveal the significance of important fields [3]. The study conducted
in [4] performed a feature analysis of encrypted malicious traffic within HTTPS
network traffic, utilizing datasets captured from two research projects at the
Czech Technical University. This analysis involved 72 network traffic captures,
comprising 59 malware and 13 normal pcap files. Another study [5] identified
encrypted malware traffic using unsupervised learning methods. The distance
metric was employed to construct a new malware class termed FClass. 83 numerical features were extracted from four categories: TCP/IP header, time-based,
length-related, and packet variation features. The 10 most relevant features were
then utilized for classification. In the study presented in [6], NetConverse examined the flow of traffic associated with various ransomware families within the
Windows ransomware network. Features were extracted from unencrypted web
traffic to train classifiers, achieving an accuracy of 97.1% with a decision tree
classifier. A primary limitation of this paper is that it extracts features solely
from unencrypted traffic and focuses on only a subset of ransomware families.
Biflow, as described in [7], is a flow-based system that aggregates data packets
from two families.
In addition, the aforementioned experiments were conducted on a limited
number of ransomware families. To enhance the accuracy of malware identification, a technique proposed by [10] involves decrypting suspected encrypted
flows and performing conventional deep packet inspection using intrusion signatures. Another study by [11] utilized statistical and sequence features from both
flow-level and host-level perspectives to characterize encrypted traffic, acknowledging the challenges associated with decryption. They introduced a detection
framework based on ensemble learning that incorporates real malware, including
normal traffic generated by legitimate hosts and malicious traffic produced by
malware-infected hosts.
Most studies have focused on the availability of expert-labeled data for detection algorithms. However, the study by [12] addressed the challenge posed by the
scarcity of high-dimensional labeled data by proposing an unsupervised anomaly

4

Sileshi N. Zeleke et al.

detection method. This method utilizes a three-layer autoencoder for feature
compression, enhancing model efficiency, and employs the classical K-means algorithm for unsupervised classification. In addition to the proposed solution,
the study exclusively analyzed normal encrypted traffic. To identify encrypted
malicious traffic, Wang et al. [29] extracted characteristics from HTTPS traffic
and integrated them into shallow machine-learning models. To tackle the issue
of low classification accuracy in current encrypted traffic classification methods, particularly for traffic with similar fingerprints, Shen et al. [8] developed
an attribute-aware encrypted traffic classification method based on second-order
Markov chains.
In general, multi-view feature extraction, machine learning algorithms, and
ensemble learning frameworks play a critical role in malware detection within
encrypted networks. While most studies emphasize enhancing the accuracy and
efficiency of detecting malware in encrypted traffic, the explainability of AI models remains a crucial aspect that requires further investigation.

3

Methodology

The overall design of the proposed framework, as illustrated in Fig. 1, consists
of four core components: flow construction and feature extraction, data preprocessing, model training and validation, and the explanation module. Below, we
provide a detailed description of each component. These components highlight
their synergistic interactions within the framework. To the best of our knowledge, an explainable encrypted malware detection system at the network level
has not been studied. This makes our proposed method a novel approach, as it
integrates flow construction, feature extraction, data preprocessing, and XAI.
3.1

Data Preparation

We collect publicly available and proprietary malicious network traffic to create
a robust dataset that encompasses various types and families of malware. To
achieve this, we gathered raw network traffic from multiple sources as follows:
We obtained 614 ransomware traffic samples from 17 different ransomware types
provided by the Information Security and Object Lab. Additionally, we acquired
more Trojan horse samples from [32], which includes 175 raw network traffic
samples composed of 12 families, the sample includes the notorious Zeus and
Emotet. Another source of malware traffic for our analysis is malware traffic
analysis [14] and the Czech Republic (CTU-13) [15], from which we obtained
305 and 36 traffic samples, respectively. The malicious samples collected from the
aforementioned sources comprise 54 different families, each exhibiting distinct
communication properties, as shown in Table 1. The sample count varies among
families due to the availability of raw traffic. For example, Teslacrypt is the most
represented malware family in our dataset. For the machine learning model used
for malware detection, the dataset is not problematic even if the families are

Explainable AI for Encrypted Malware Traffic

5

Fig. 1. Overview of the proposed explainable malware detection pipeline

imbalanced, as all malware families represent a single class (i.e., the malware
class).
Acquiring normal traffic captured in a local area network (LAN) setup at the
enterprise network edge or host is relatively straightforward compared to obtaining malware traffic. In our study, we utilized two sources for normal traffic data:
self-collected traffic from the Addis Ababa Science and Technology campus network and data from the CTU-13 dataset [15]. For the self-collected data, we
configured a local host to capture traffic flow while visiting web servers of legitimate Fortune companies. The traffic collection procedure is briefly presented
on [28]. The comprehensive data processing procedure is presented in detail in
Algorithm 1.
3.2

Flow Construction and Feature Extraction

To better characterize the communication between the client and server, it is
essential to establish a bi-directional flow based on the source and destination
ports, source and destination IP addresses, and the connection protocol. We
utilized Joy framework [16], an open-source tool for flow generation, to create
flows from raw network traffic. After constructing a 5-tuple bi-directional flow, we
proceeded to extract features from various perspectives. In our multi-view feature
extraction strategy, we extract features from connection metadata, certificate
information, time and length-related data, handshake details, and statistical
features. Connection flow metadata describes the number of bytes or packets

6

Sileshi N. Zeleke et al.

sent to or received from the client within a specific time window; in our case,
this window is 30 minutes. The packet length and inter-arrival time between two
consecutive sessions vary for normal and malware communications [17].
To represent these features, we employed one-hot encoding, such that if a
certain cipher suite is present in the offer or accepted list, we encode it as 1;
otherwise, we encode it as 0. The same technique is applied to TLS extensions
and version numbers. To extract time and packet-related features, we utilized
a Markov chain sequencing by discretizing the data into equal-sized bins. A
Markov chain consists of a set of states and transitions sequentially from one
state to another [33].
Table 1. Malware family, type, and number of samples included as a raw pcap
Family
Type
# Samples Family
Type
# Samples
Cerber
Ransomware
124
Win32.Blocker Ransomware
18
Mole
Ransomware
4
Zeta
Ransomware
3
2
Zeus
Trojan
101
CryptoShield Ransomware
Jaff
Ransomware
3
Nemucod
Ransomware
2
Ransomware
3
Stealer
Ransomware
3
Unlock26
Locky
Ransomware
100
BankerX-gen Ransomware
3
WannaCry
Ransomware
10
Rig
Downloader
17
Ransomware
2
Trickbot
Trojan
88
Xorist
Zeus-panda
Trojan
23
Icedid
Trojan
13
Trojan
13
Ursnif
Virus
5
Gootkit
Neutrino
Rootkits
2
Boleto
Downloader
12
Ransomware
2
Vawtrak
Trojan
7
ZLoader
BazarLoad
Backdoor
1
Kovter
Trojan
3
Hancitor
Rootkits
54
Dreambot
Trojan
9
Nymaim
Downloader
1
Ramnit
Worm
1
Petya
Ransomware
2
Upatre
Ransomware
10
Ransomware
8
Crypt R
Ransomware
14
Crysis
Sage
Ransomware
5
Bunitu T
Ransomware
10
Ransomware
2
Crthrazy
Ransomware
6
CTBLocker
Spora
Ransomware
30
Troldesh
Ransomware
9
GlobeImposter Ransomware
7
Emotet
Ransomware
9
TeslaCrypt
Ransomware
331
Tofsee
Ransomware
11
Dridex
Trojan
23
Gandcrab
Ransomware
3
Spyware
2
Loveyou
Virus
1
Azorult
Qakbot
Trojan
5
Spelevo
Exploit Kit
3
Chthonic
Trojan
1
Fallout
Rootkits
1
Angler
Exploit Kit
2
Miuref
Trojan
3

Moving through all states generates a transition matrix. We used three different states for our analysis. We experimented with two datasets for this study.
The first dataset was self-compiled, as described in Sec. 3.1 and the other is the
CTU-13. The CTU-13 botnet dataset contains 38,898 botnet samples and 53,314
normal samples.

Explainable AI for Encrypted Malware Traffic

3.3

7

Detection Model

To detect and classify malware in encrypted networks, various conventional and
deep learning algorithms can be employed, as discussed in the existing literature.

Algorithm 1 Data Processing Algorithm
Input: Path of pcap files (P )
Output: Normalized CSV file (N )
1: Initialize variables
2: for each f ∈ P do
3:
Construct 5-tuple flow (F )
4:
if duration(F ) < 30 min then
5:
Split F into 30-min windows
6:
Filter non-encrypted flows
7:
else
8:
Discard F
9:
end if
10:
if three-way handshake completed then
11:
Pre-process F
12:
else
13:
Discard F
14:
end if
15:
if non-encrypted connection then
16:
Discard F
17:
else
18:
for each flow fi ∈ F do
19:
Extract features (handshake, metadata, stats)
20:
for each packet pi and inter-arrival time τi do
21:
Create 3 states (150 bytes/ms)
22:
Initialize 3 × 3 transition matrix (M )
23:
Determine state of pi in M
24:
Compute transition probabilities
25:
end for
26:
end for
27:
Update dataset features
28:
end if
29:
Append processed data to dataset
30: end for
31: return N

However, studies [18], [17], [4], [18], [19], and [20] indicate that tree-based
ensemble models demonstrate superior performance. Specifically, study [29] conducted a comparison of deep learning algorithms and random forest (RF) for
analysis of encrypted malware traffic, concluding that RF outperformed all other
models across every baseline presented. In light of this, we train and test ensemble algorithms, including RF, XGBoost, and extremely randomized trees.

8

Sileshi N. Zeleke et al.

Random Forest: Widely used ensemble learning method that operates on the
principle of constructing a robust decision tree by aggregating the predictions of
multiple trees, a technique also known as bagging.
m

y=

n

1 XX
Wi (xj , z)yj
m i=1 j=1

(1)

Where y represents output, m, n,W , and z are a number of trees, data sample,
weight value and new data point to be predicted respectively. Also i represents
the respective tree and x_j denotes the neighbor of z that share the same leaf
in tree i. To better exploit the performance of RF appropriate tuning of the
number of estimators, maximum depth of the tree, minimum sample split, and
minimum samples of leaf is important [21].
Extreme Gradient Boosting: Unlike RF, XGB employs a distinct technique
known as boosting to create a robust classifier. This method incrementally enhances a weak classifier by adding one classifier at a time to improve the existing
ensemble. According to [22], key parameters of XGB include the number of estimators, the maximum depth of the tree, learning rates, and the gamma value,
which indicates the minimum loss reduction.
Extremely Randomized Trees: Also known as Extra Trees, has a structure
similar to that of RF [26]. However, the trees are generated with greater randomness to enhance diversity by selecting a random subset of features at each node.
Additionally, this method employs random partitioning rather than seeking the
optimal partition. This inherent randomness improves the model’s generalization
performance and helps prevent overfitting.
3.4

Evaluation Metrics

To evaluate performance, we considered precision, recall, F1-score, accuracy, and
an evaluation metric known as the Matthews Correlation Coefficient (MCC). The
MCC is particularly valuable because it incorporates all values from the confusion matrix to assess the effectiveness of a binary classification model, providing
more comprehensive information than the F1-score and accuracy alone. This
is primarily because the MCC accounts for the balance between true positives
(TP), true negatives (TN), false positives (FP), and false negatives (FN).
3.5

Explainability

To effectively explain tree-based models both globally and locally, SHAP has
demonstrated strong performance in previous studies related to network traffic.
SHAP is grounded in cooperative game theory, specifically the Shapley values
[24]. These values represent the average contribution of each player across all

Explainable AI for Encrypted Malware Traffic

9

possible coalitions. In the context of machine learning, players are replaced by
attributes from the sample, and their contributions are aggregated to determine
the output of the algorithm. This technique falls under the category of additive
feature attribution methods. SHAP is characterized by its properties of efficiency,
symmetry, dummy, and additive. Regarding efficiency, the total sum of Shapley
values, or the marginal contribution of each feature, is equal to the value of the
total coalition. Symmetry ensures that each feature has an equal opportunity to
influence the outcome, regardless of the order in which they are considered. If a
particular feature does not affect the predicted value, regardless of the coalition
group, its value is assigned as zero, which is referred to as the dummy property
[24]. Furthermore, we adopt TreeExplainer, a technique specifically designed for
tree-based models [25].
3.6

Experimental Settings

The experiment was conducted on Google Colab Pro with V100 GPUs for both
datasets. Moreover, To simulate the real-world scenario of malicious traffic occurrences in any given communication environment, we oversample our normal
samples using an adaptive synthetic sampling technique. The normal-to-malware
proportion of the imbalanced dataset is 98.97% to 1.03%. The other dataset is
the CTU-13 botnet dataset [15]. We used validation curves to identify optimal hyperparameters for the RF model. We train the model based on 10-fold
cross-validation, the best parameters obtained from the validation curve are
n_estimators=23, max_depth=42, min_samples_split=6, and min_samples_leaf=2.
However, for XGB the best values of parameters were obtained using natureinspired genetic algorithm, the best parameters are n_estimators=23, max_depth=43,
learning_rate=0.47, min_child_weight=0.4, gamma=3.28, colsample=1, and
subsample=0.82 Moreover, for the Extra Trees model, we utilized the default
hyperparameters. Since the primary objective of this study is not to identify
the best-performing AI models, we focus on a basic implementation that can
perform consistently across all datasets.

4

Experimental Result and Discussions

In this section, we present and analyze the performance of our proposed models.
We also introduce the performance of various classifiers across different datasets
and propose an explainable framework. Our approach not only utilizes machine
learning models to analyze patterns in encrypted traffic but also provides both
global and local explanations for the best-performing algorithm.
4.1

Detection Model Performance

The evaluation of the classification models on the CTU-13 dataset, our dataset
(balanced), and imbalanced classes reveals key insights into their performance.
As the CTU-13 dataset was collected in a real-world communication setting, the

10

Sileshi N. Zeleke et al.

approaches and results can be replicated in other datasets and real-world scenarios. Across all datasets, XGB consistently achieved the highest MCC, making it
the most reliable model for class prediction, as shown in Fig. 2. In the CTU-13
dataset, XGB attains an MCC of 99.81%, surpassing RF (99.52%) and ExTree
(99.43%), indicating superior overall predictive power, while effectively accounting for both false positives and false negatives, as shown in Fig. 2(a). Similarly,
in the balanced dataset shown in Fig. 2(b), XGB again outperforms the other
models with an MCC of 99.01%, compared to RF’s 98.24% and ExTree’s 95.93%.
In the imbalanced version of our dataset, Fig. 2(c) shows that XGB maintains
its edge with an MCC of 98.82%, demonstrating robust performance in imbalanced settings compared to RF (98.16%) and ExTree (98.44%). The high MCC
values for XGB across all datasets indicate that it is less influenced by skewed
class distributions and manages true negatives more effectively than RF and
ExTree, which are crucial for balanced evaluation. Additionally, the XGBoost
model’s ability to handle missing values and its support for parallel processing
makes it suitable for large-scale malware detection tasks.

(a)

(b)

(c)

Fig. 2. Radar plot for performance comparison of the proposed malware detection
across different datasets and metrics: (a) CTU-13; (b) Our dataset; (c) Our imbalanced
dataset

The confusion matrix in Fig. 3 illustrates the ability of the model to accurately classify malicious and normal traffic. In the CTU-13 dataset, shown in Fig.
3(a), the model achieves near-perfect detection with minimal false positives and
false negatives. Fig. 3(b) shows the performance based on our dataset trained using oversampling techniques. Although the false negative rate is slightly higher,
the low false positive rate ensures that normal traffic is not wrongly flagged
as malware, making it suitable for deployment in real-world encrypted network
environments, where accuracy is paramount. The slightly higher false negative
count may be attributed to variations in the traffic patterns or encryption methods. However, the model continues to demonstrate robust generalization to new
data.
In both cases, the model’s robust performance indicates its capability to manage the complexities introduced by encryption, which has traditionally posed

Explainable AI for Encrypted Malware Traffic

11

challenges for malware detection owing to limited visibility in the content of
network packets. The low rates of both false positives and false negatives imply that this approach can enhance the precision and effectiveness of malware
detection systems, in an encrypted environment.

(a)

(b)

Fig. 3. Confusion matrix comparison on: (a) CTU-13; (b) Our imbalanced dataset

4.2

Explaining Detection Model

Visualizing the best-performing model’s decision-making process using XAI techniques helps to identify malicious behavior and understanding such a decision
is crucial for cyber-analytics. An insight into the decision helps administrators
identify the part of the network, part of the features, the security policies compromised by attackers, and potential biases using the techniques provided by
SHAP.

Global Explainability: The SHAP summary plot illustrates the global importance of features, showing their contribution to model decisions and their impact
direction (positive or negative) for the individual samples. Fig. 4 presents the ten
most influential features of the XGBoost model trained on our dataset. The color
bar indicates the impact of the features, with blue indicating positive influences
and red indicating negative ones. The horizontal violin plot displays the distribution of Shapley values for each data instance. A higher ‘Max_Bpckt’ value
significantly impacts decision-making, distinguishing between malicious and normal traffic based on packet size. The ‘Mean_f_inter’ feature captures the average
time interval between consecutive packets during a session, as malware traffic
often exhibits distinctive timing characteristics compared to legitimate traffic,
such as irregular or bursty patterns. Additionally, feature bytes_in, which is
the number of bytes sent from the client, positively impacts the model’s decision, revealing the distinct behavior of malicious servers that exfiltrate client
data. This finding regarding feature importance corroborates a previous study
on adversarial malicious encrypted malware traffic analysis [27].

12

Sileshi N. Zeleke et al.

Fig. 4. Summary plot of global explanation of XGBoost model trained using our
dataset

In normal traffic, the standard deviation of the byte inter-arrival time between the two flows positively impacts decision-making. Additionally, ’certValidDays’, which represents the number of days a certificate remains valid, significantly influenced the results. Malware authors aim to remain undetected, leading
to a higher number of validation days in the malware communication. Fig. 5 illustrates the model trained on CTU-13 data, revealing that features like minimum
forward packet length ’fwd Pkt Len Min’, packet length standard deviation ’Pkt
Len STD’ and bytes forwarded ’init Bwd Win Bytes’ affect the models positively
impact model performance like our dataset.
Local Explainability: The force plot is a part of TreeExplainer in SHAP. It
is useful for visualizing the impact of features on individual predictions made
by tree-based models. Fig. 6 and 7 show the model’s prediction decomposed
into the sum of the effects of each feature value on the model output from
the base value prediction. The explanation of an expected feature that affects
the target class centers on the plot around the x-axis. Features that have a
favorable influence on the prediction are displayed in red, whereas those that
have a negative influence are displayed in blue. As shown in Fig. 6, was 4.97,
which is higher than the base value indicating that the features associated with
the malware class are pushed to the right (higher values) as predicted by the
red color. For instance, ’num_pkts_out’ positively affects the malware class
(indicated by the red region), thereby shifting the class malware prediction to
the right. In contrast, the malware class is negatively correlated with the feature

Explainable AI for Encrypted Malware Traffic

13

Fig. 5. Summary plot of global explanation of XGBoost model trained using CTU-13
dataset

’Flow IAT Min’ feature, as shown in Fig. 7. A lower value indicates that malware
prediction is pushed to the left. However, the force to drive the prediction to the
right (higher value) is the largest because the feature values that are in the red
area are greater than the other feature values that are in the blue area.

Fig. 6. Local explanation based on our dataset

4.3

Discussion

The global explanation reveals that the mean number of bytes sent and received
by a client and server indicates a significant difference in the data transmission

14

Sileshi N. Zeleke et al.

Fig. 7. Local explanation based on CTU-13 dataset

patterns between normal traffic and that associated with malware. Specifically,
the data transmitted from the server to the client are typically greater in normal
traffic than in malware scenarios. This suggests that legitimate client applications
tend to receive a substantial amount of data at the onset of communication, in
contrast to malware client applications. Conversely, when a client transmits data
to the server, the mean number of bytes in the normal traffic is comparatively
lower. This observation may reflect the behavior of malware, which often involves
collecting and transmitting a client’s status and data to a command and control
server. Furthermore, the model’s focus on the packets sent and received by clients
and servers indicates that malware traffic is characterized by a higher volume of
packets transferred. This pattern suggests that malware actors deliberately send
numerous packets containing small amounts of data to evade detection, thereby
minimizing bandwidth consumption and reducing the likelihood of triggering
security alerts.
Furthermore, the TLS employed in the communication provided critical insights. As demonstrated in Fig. 4 and 7, the TLS version significantly influences
the performance of the detection model. This phenomenon can be attributed to
the tendency of normal communications to favor newer TLS versions, whereas
malicious actors often opt for older versions. Generally, when selecting cipher
suites, malware authors tend to prefer simpler and outdated parameters to optimize the utilization of limited computational resources. In addition, the interarrival time differences between multiple packets within a flow are utilized as
time-series elements. The interval times of forwarded backward flows can substantially impact models, with normal flows exhibiting a more positive correlation than those associated with malware. By identifying the most significant
features for detection, security professionals can prioritize their efforts more effectively. Moreover, insights derived from SHAP values can assist in the customization of alert systems. For instance, if communication to a web server indicates
the transmission of a large packet, it may raise concerns regarding the socket,
potentially triggering an alert..

Explainable AI for Encrypted Malware Traffic

4.4

15

Comparison of the Proposed Work with Existing Works

In this section, we present a comparative analysis of our approach to explainable
malware detection in encrypted network traffic, about existing methodologies.
By evaluating both traditional and contemporary methods, we intend to underscore the innovations and enhancements presented by our model, particularly regarding its capacity to provide transparency in decision-making while sustaining
robust performance in complex encrypted environments. The proposed explainable model incorporates TLS, statistical, and flow metadata features for binary
classification, resulting in an innovative approach to encrypted malware detection. Moreover, [34] proposed an ensemble model using self-attention techniques
for multiclass classification and achieved an accuracy of 96.71%. Our system
outperforms in terms of accuracy metrics when using the CTU-13 dataset in
addition to the enhancement of the interpretability of models.

5

Conclusion

Encrypted network communications play a critical role in safeguarding privacy.
The ability to detect malware without decrypting the payload while providing
explanations for detection decisions is a vital practice in the field of cybersecurity. This process requires the development and evaluation of features that
accurately represent encrypted traffic through the application of artificial intelligence algorithms. The extracted features encompass a range of attributes associated with the encrypted communication between clients and servers. These
attributes include handshake details, such as the ciphers offered and accepted,
the TLS extensions that are advertised and supported, certificate information,
timing and length characteristics, connection metadata, and statistical data regarding packets and bytes in bi-directional flow. Although several studies have
focused on malware detection, there is a notable scarcity of research addressing the explainability of such detection systems. In this study, we introduce an
efficient explainable detection model based on tree ensemble methods. The proposed framework was evaluated using both a self-collected dataset and a baseline
dataset. Our detection results demonstrated significant improvements compared
to those of related studies.
The primary objective of this study is to investigate the explainability of a
model’s decisions. We utilized the SHAP method to examine both global and
local explainability, thereby identifying the features that exerted the greatest
influence on the model’s predictions. The results illustrate the varying contributions of the different features to the model for each class. Moreover, we also
contribute a comprehensive dataset composed of 54 different malware types and
1,127 unique malware traffic captures that occurred in cyberspace. In future research, a more comprehensive analysis of malware communication, along with
enhanced explainability through the use of additional samples to detect zero-day
attacks, may represent a promising avenue for exploration.

16

Sileshi N. Zeleke et al.

Acknowledgments. This study is partially supported by the Age-It project
under the National Recovery and Resilience Plan (NRRP) program funded by
the NextGenerationEU.

References
1. B. Anderson and D. A. McGrew, "Identifying Encrypted Malware Traffic with Contextual Flow Data," in Proceedings of the 2016 ACM Workshop on Artificial Intelligence and Security (AISec@CCS 2016), Vienna, Austria, 2016, pp. 35-46.
2. B. Anderson, A. Chi, S. Dunlop, and D. McGrew, "Limitless HTTP in an HTTPS
World: Inferring the Semantics of the HTTPS Protocol without Decryption," in
Proceedings of the Ninth ACM Conference on Data and Application Security and
Privacy (CODASPY 2019), Richardson, TX, USA, 2019, pp. 267-278.
3. B. Anderson and D. A. McGrew, "TLS Beyond the Browser: Combining End Host
and Network Data to Understand Application Behavior," in Proceedings of the
Internet Measurement Conference (IMC 2019), Amsterdam, The Netherlands, 2019,
pp. 379-392.
4. A. S. Shekhawat, F. Di Troia, and M. Stamp, "Feature Analysis of Encrypted Malicious Traffic," CoRR, vol. abs/2312.04596, 2023.
5. J. Liu, Z. Tian, R. Zheng, and L. Liu, "A Distance-Based Method for Building
an Encrypted Malware Traffic Identification Framework," IEEE Access, vol. 7, pp.
100014-100028, 2019.
6. W. Yu-Lun, C. Jen-Chun, C. Rong-Jaye, and W. Shiuh-Jeng, "Feature-SelectionBased Ransomware Detection with Machine Learning of Data Analysis," in Proceedings of the 2018 3rd International Conference on Computer and Communication
Systems (ICCCS), 2018, pp. 85-88.
7. O. M. K. Alhawia, J. Baldwin, and A. Dehghantanha, "Leveraging Machine Learning Techniques for Windows Ransomware Network Traffic Detection," CoRR, vol.
abs/1807.10440, 2018.
8. M. Shen, M. Wei, L. Zhu, and M. Wang, "Classification of Encrypted Traffic with
Second-Order Markov Chains and Application Attribute Bigrams," IEEE Transactions on Information Forensics and Security, vol. 12, pp. 1830-1843, 2017.
9. D. Rui, G. Chuan, L. Bo, Y. Lixia, L. Hongyu, and C. Shaojie, "SSL Malicious Traffic
Detection Based On Multi-view Features," in Proceedings of the 9th International
Conference on Communication and Network Security (ICCNS 2019), Chongqing,
China, 2020, pp. 40-46.
10. B. Xu, G. He, and H. Zhu, "ME-Box: A Reliable Method to Detect Malicious
Encrypted Traffic," Journal of Information Security and Applications, vol. 59, 2021.
11. C. Zhao, S. Li, X. Wu, W. Han, Z. Tian, and M. Chen, "A Novel Malware Encrypted Traffic Detection Framework Based On Ensemble Learning," in Proceedings
of the Sixth IEEE International Conference on Data Science in Cyberspace (DSC
2021), 2021, pp. 614-620.
12. S. Han, Q. Wu, H. Zhang, and B. Qin, "Light-weight Unsupervised Anomaly Detection for Encrypted Malware Traffic," in Proceedings of the 7th IEEE International
Conference on Data Science in Cyberspace (DSC 2022), 2022, pp. 206-213.
13. B. Jethva, I. Traore, A. Ghaleb, K. Ganame, and S. Ahmed, "Multilayer Ransomware Detection Using Grouped Registry Key Operations, File Entropy and File
Signature Monitoring," Journal of Computer Security, vol. 28, no. 3, pp. 337-373,
2020.

Explainable AI for Encrypted Malware Traffic

17

14. B. Duncan, "Malware-Traffic-Analysis," 2021. [Online].
Available: https://www.malware-traffic-analysis.net [Accessed: June 4, 2023].
15. Stratosphere, "Stratosphere Laboratory Datasets," 2021. [Online]. Available:
https://www.stratosphereips.org/datasets-ctu13 [Accessed: June 11, 2023].
16. D. McGrew, B. Anderson, B. Hudson, and P. Perricone, "Joy," 2017. [Online].
Available: https://github.com/cisco/joy [Accessed: January 3, 2024].
17. B. Anderson and D. McGrew, "Machine Learning for Encrypted Malware Traffic
Classification: Accounting for Noisy Labels and Non-Stationarity," in Proceedings
of the 23rd ACM SIGKDD International Conference on Knowledge Discovery and
Data Mining (KDD 2017), 2017, pp. 1723-1732.
18. S. N. Zeleke, S. Zemene, and M. Bochicchio, "Ensemble Learning for Encrypted
Malware Detection and Classification," in Proceedings of the International Conference on Information and Communication Technology for Development for Africa
(ICT4DA 2023), 2023, pp. 132-137.
19. Fang, Y., Xu, Y., Huang, C., Liu, L., Zhang, L.: Against Malicious SSL/TLS
Encryption: Identify Malicious Traffic Based on Random Forest. In: Yang, X.-S.,
Sherratt, R.S., Dey, N., Joshi, A. (eds.) Proceedings of the Fourth International
Congress on Information and Communication Technology (ICICT 2019), pp. 99115. Springer, 2019. https://doi.org/10.1007/978-981-32-9343-4_10.
20. Zheng, R., Liu, J., et al.: Two-layer detection framework with a high accuracy and
efficiency for a malware family over the TLS protocol. PLoS One 15(5), 1 (2020).
https://doi.org/10.1371/journal.pone.0232696.
21. Makariou, D., Barrieu, P., Chen, Y.: A random forest based approach for predicting spreads in the primary catastrophe bond market. Insurance: Mathematics and
Economics 101, 140-162 (2021). https://doi.org/10.1016/j.insmatheco.2021.07.003.
22. Chen, J., Zhao, F., Sun, Y., Yin, Y.: Improved XGBoost model based on genetic
algorithm. International Journal of Computer Applications in Technology 62(3),
240-245 (2020). https://doi.org/10.1504/ijcat.2020.106571.
23. Zhang, T., Qiu, H., Mellia, M., Li, Y., Li, H., Xu, K.: Interpreting AI for Networking: Where We Are and Where We Are Going. IEEE Communications Magazine
60(2), 25-31 (2022). https://doi.org/10.1109/MCOM.001.2100736.
24. Lundberg, S.M., Lee, S.-I.: A Unified Approach to Interpreting Model Predictions.
In: Advances in Neural Information Processing Systems 30 (NIPS 2017), pp. 47684777. Curran Associates Inc., Long Beach, CA, USA (2017)
25. Lundberg, S.M., Erion, G.G., Chen, H., DeGrave, A.J., Prutkin, J.M., Nair, B.G.,
Katz, R., Himmelfarb, J., Bansal, N., Lee, S.-I.: Explainable AI for Trees: From
Local Explanations to Global Understanding. CoRR abs/1905.04610 (2019)
26. Wu Q.-W. and Cao R.-F. and Xia, J.-F. and et al.: Extra Trees Method for Predicting LncRNA-Disease Association Based on Multi-Layer Graph Embedding Aggregation. IEEE/ACM Transactions on Computational Biology and Bioinformatics
19(6), 3171-3178 (2022). https://doi.org/10.1109/TCBB.2021.3113122
27. Li M. and Wu Z. and Chen K. and Wang, W.: Adversarial Malicious Encrypted
Traffic Detection Based on Refined Session Analysis. Symmetry 14(11) (2022).
https://doi.org/10.3390/sym14112329
28. Jorgensen S. and Holodnak J. and et al.: Extensible Machine Learning for Encrypted Network Traffic Application Labeling via Uncertainty Quantification. IEEE
Transactions on Artificial Intelligence 5(1), 420-433 (2024).
https://doi.org/10.1109/TAI.2023.3244168
29. Wang, Z., Fok, K.W., Thing, V.L.L.: Machine Learning for Encrypted Malicious
Traffic Detection: Approaches, Datasets and Comparative Study. Computers & Security (2023). https://doi.org/10.1016/j.cose.2021.102542

18

Sileshi N. Zeleke et al.

30. Bonifazi, G., Cauteruccio, F., et al.: A Model-Agnostic, Network Theory-Based
Framework for Supporting XAI on Classifiers. Expert Systems with Applications
241 (2024). https://doi.org/10.1016/j.eswa.2023.122588
31. Alraizza A. and Algarni, A.: Ransomware Detection Using Machine Learning: A
Survey. Big Data and Cognitive Computing 7(3), 143 (2023).
https://doi.org/10.3390/BDCC7030143
32. Roques, O.: Detecting Malware in TLS Traffic. Master’s thesis, Imperial College,
London, UK (2019)
33. Ross, S.M.: Introduction to Probability Models. Technometrics 40, 78-78 (1975).
https://doi.org/10.1080/00401706.1998.10485493.
34. Kondaiah, C., Pais, A.R. and Rao, R.S:. Enhanced Malicious Traffic Detection in
Encrypted Communication Using TLS Features and a Multi-class Classifier Ensemble. J Netw Syst Manage 32, 76 (2024). https://doi.org/10.1007/s10922-024-09847-3
PAPER_TEXT
