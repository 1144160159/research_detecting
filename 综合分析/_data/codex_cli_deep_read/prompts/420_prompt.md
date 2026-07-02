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
# [420] Ensuring Zero Trust IoT Data Privacy: Differential Privacy in Blockchain Using Federated Learning
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
编号：420
题名：Ensuring Zero Trust IoT Data Privacy: Differential Privacy in Blockchain Using Federated Learning
年份：2024
DOI：10.1109/tce.2024.3444824
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2024.3444824.pdf
已有粗分类：联邦学习、隐私保护与分布式协同
二级关联：IoT、车联网、工业互联网与边缘安全
相关性：弱相关，分数 3
已有代码状态：已下载；DP_Blockchain -> source\DP_Blockchain

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\420.txt
- 原始字符数：54889
- 本次发送字符数：54889
- 是否截断：False

代码包：
- 仓库：DP_Blockchain
  - URL：https://github.com/tariqaup/DP_Blockchain
  - 状态：downloaded
  - 本地目录：source\DP_Blockchain
  - 顶层结构：Book1.xlsx、Data-Queries).rar、LR1 base latency.xlsx、MajorCode.txt、lr throput based.xlsx、lr throput proposed model.xlsx、lr2 letancy proposed.xlsx、results.PNG
  - 主要语言：
  - README 标题：
  - README 运行线索：
  - 关键文件：{}
  - 数据集线索：

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 1, FEBRUARY 2025

1167

Ensuring Zero Trust IoT Data Privacy: Differential
Privacy in Blockchain Using Federated Learning
Altaf Hussain, Wajahat Akbar, Tariq Hussain , Ali Kashif Bashir, Maryam M. Al Dabel ,
Farman Ali , and Bailin Yang

Abstract—In the increasingly digitized world, the privacy and
security of sensitive data shared via IoT devices are paramount.
Traditional privacy-preserving methods like k-anonymity and
l-diversity are becoming outdated due to technological advancements. In addition, data owners often worry about misuse and
unauthorized access to their personal information. To address
this, we propose a secure data-sharing framework that uses local
differential privacy (LDP) within a permissioned blockchain,
enhanced by federated learning (FL) in a zero-trust environment.
To further protect sensitive data shared by IoT devices, we
use the Interplanetary File System (IPFS) and cryptographic
hash functions to create unique digital fingerprints for files. We
mainly evaluate our system based on latency, throughput, privacy
accuracy, and transaction efficiency, comparing the performance
to a benchmark model. The experimental results show that
the proposed system outperforms its counterpart in terms of
latency, throughput, and transaction efficiency. The proposed
model achieved a lower average latency of 4.0 seconds compared
to the benchmark model’s 5.3 seconds. In terms of throughput,
the proposed model achieved a higher throughput of 10.53 TPS
(transactions per second) compared to the benchmark model’s 8
TPS. Furthermore, the proposed system achieves 85% accuracy,
whereas the counterpart achieves only 49%.

Manuscript received 3 April 2024; revised 28 June 2024; accepted
2 August 2024. Date of publication 16 August 2024; date of current version
12 June 2025. This work was supported in part by the “Pioneer” and
“Leading Goose” Research and Development Program of Zhejiang Province
under Grant 2023C01150, and in part by the Zhejiang Provincial Natural
Science Foundation of China under Grant LD24F020003. (Altaf Hussain and
Tariq Hussain are the first co-authors.) (Corresponding authors: Bailin Yang;
Farman Ali.)
Altaf Hussain is with the Department of Computer Science and
BI, Khushal Khan Khattak University, Karak 27200, Pakistan (e-mail:
altaf.hussain@kkkuk.edu.pk).
Wajahat Akbar is with the School of Electronic and Control Engineering,
Chang’an University, Xi’an 710064, China (e-mail: wajahatakbar32@
gmail.com).
Tariq Hussain and Bailin Yang are with the School of Computer
Science and Technology and the School of Mathematics and Statistics,
Zhejiang Gongshang University, Hangzhou 310018, China (e-mail:
uom.tariq@gmail.com; ybl@zjgsu.edu.cn).
Ali Kashif Bashir is with the Department of Computing and Mathematics,
Manchester Metropolitan University, M15 6BH Manchester, U.K., and also
with the Centre for Research Impact and Outcome, Chitkara University
Institute of Engineering and Technology, Chitkara University, Rajpura 140401,
India (e-mail: Dr.alikashif.b@ieee.org).
Maryam M. Al Dabel is with the Department of Computer Science and
Engineering, College of Computer Science and Engineering, University of
Hafr Al Batin, Hafar Al Batin 39524, Saudi Arabia (e-mail: maldabel@
uhb.edu.sa).
Farman Ali is with the Department of Applied AI, School of Convergence,
College of Computing and Informatics, Sungkyunkwan University, Seoul
03063, South Korea (e-mail: Farman0977@g.skku.edu).
Data is available on-line at https://github.com/tariqaup/DP_Blockchain.
Digital Object Identifier 10.1109/TCE.2024.3444824

Index Terms—Blockchain, differential privacy, federated learning, Internet of Things, zero trust security.

I. I NTRODUCTION
HE SMART home systems (SHS) that use the Internet
of Things (IoT) have become very popular recently. The
concept of SHS is also applied to create IoT applications
in various areas such as smart cities, agriculture, healthcare services, etc. [1]. The rapid increase in IoT devices
results in generating vast amounts of data (i-e., big data)
every fraction of a second. These data contain sensitive
information about the owners, which requires security and
privacy [2], [3]. The term ’‘privacy” refers to the notion that
an individual’s data will be treated discreetly or that access
to the data will require authorization. “Security” refers to the
ability to protect sensitive data from both eavesdroppers and
intruders [4], [5].
Privacy-Preserving Data Sharing (PPDS) methods address
risks of re-identification of data owners or revealing sensitive information [6]. PPDS includes various techniques
such as data masking [7], lightweight mutual authentication [8], encryption [9], k-anonymization [10], [11], and
l-diversity [12] that meet privacy requirements [13]. However,
these techniques have limitations such as background knowledge, homogeneity, and inference attacks, while FL poisoning
attacks present a significant obstacle to achieving data privacy [14]. To address these limitations of the existing PPDS
methods, a robust “Zero Trust Architecture (ZTA)” is needed
to guarantee a secure mechanism for data transfer without risking the re-identification of data owners’ sensitive information.
The ZTA is a practical implementation emphasizing trust
as a vulnerability rather than a fundamental component in
network security [15]. ZTA is based on segmenting networks
into microcores and perimeters. It suggests that everything,
even inside the perimeters of a network, is untrusted instead
of building a trusted domain around the network. Thus, it
promotes the “never trust, always verify” principle within
enterprise networks as well [16].
Additionally, the current methods used to anonymize data
often depend on trusting the people who hold the data or the
companies they hire to do it for them. This could be problematic if these parties are semi-honest and could potentially
cause harm [17], [18]. Likewise, if data controllers receive
data owners’ datasets with inadequate PPDS techniques, they
could engage in malicious activities, posing as attackers with

T

c 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
1558-4127 
See https://www.ieee.org/publications/rights/index.html for more information.

1168

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 1, FEBRUARY 2025

harmful intentions such as stealing sensitive data or misusing
data owners’ sensitive information [19].
Blockchain technology has recently emerged as a critical
solution for safeguarding sensitive data, providing a decentralized method for managing sensitive data records, ensuring
authentication, preventing tampering, and facilitating secure
data sharing [20]. Through its resilience, blockchain empowers
data owners to manage their data. Differential privacy (DP)
offers another mathematical framework for privacy-preserving
without disclosing sensitive information [21]. DP quantifies
the privacy loss associated with specific data analysis and
achieves this by introducing controlled or randomized noise
while maintaining the desired level of privacy. LDP, a type of
DP, preserves privacy at the individual data point level rather
than the aggregate level, ensuring that no individual data point
can be linked to a specific user [22].
FL presents another significant advancement in PPDS techniques, particularly in the domain of machine learning [23].
Fl allows model training to be conducted across multiple
decentralized devices or servers without centralizing the sensitive data [24]. Instead, individual devices or nodes compute
model updates on their local data and only share encrypted
or aggregated information with a central server or among
themselves. This approach minimizes the risk of exposing
raw data to third parties, thereby enhancing privacy protection [24], [25]. By leveraging FL in conjunction with LDP and
blockchain technology, we can ensure the confidentiality of
sensitive information and maintain control over data ownership
and usage rights. The integration of FL further strengthens the
resilience of blockchain-based systems by enabling collaborative model training while preserving the privacy of individual
data points. To address the identified issues and limitations,
we propose a mechanism that combines blockchain technology
with LDP and FL to achieve robust data privacy and security
for sharing sensitive data. This research is motivated by the
challenges outlined in [11], detailed below in the ’‘Motivation”
section.
A. Motivation
In this section, we carefully examined the problems with
the existing methods of sharing data owners’ data. Due to
pressing privacy concerns, there is a fundamental lack of
trust in any data controller or entity involved in this process.
As illustrated in Fig. 1, sharing sensitive data directly with
controllers without applying any PPDS technique by data
owners could potentially be viewed as adversaries since
controllers may not be trusted to handle sensitive data. This
ambiguity renders that the data controllers may be semi-trust
actors in this scenario. Moreover, The existing scheme [11] has
implemented k-anonymity on the data owners’ sensitive data
to reduce the risk of de-identification. But With k-anonymized
data, there remains the possibility of an attribution disclosure
attack due to a lack of trust for data controllers, as shown in
Fig. 1. There is no sense in sharing sensitive information with
controllers without any privacy whatsoever, and data owners
will never want to do so without any protection. In a nutshell,
they consistently prioritize the utmost privacy when sharing

Fig. 1.

Attacker Model.

Fig. 2.

Poisoning Attack in FL.

data with controllers in a zero-trust environment. Fig. 1, along
with Fig. 2, serves to elucidate the attacker models, shedding
light on how adversaries can potentially engage in malicious
activities, especially in the context of FL.
FL is vulnerable to several attacks, compromising its privacy and security guarantees. Data poisoning attacks involve
malicious participants injecting false data to skew the model
performance, as shown in Fig. 2. Model poisoning attacks
are more sophisticated, where adversaries manipulate model
updates to degrade or control the final aggregated model.
Inference attacks seek to deduce sensitive information about
the training data from the shared model updates. The proposed
work used blockchain technology to solve FL issues and
prevent data poisoning, model poisoning, and inference
attacks. Authenticating all entities through blockchain ensures
their identities are verified. The main contributions of the
proposed model are:
• To enhance data privacy and security within IoT
networks, a novel approach is introduced that combines
LDP, Permissioned blockchain, and alongside FL in a
zero-trust environment that will protect against poisoning,
background knowledge, and inference attacks.

HUSSAIN et al.: ENSURING ZERO TRUST IOT DATA PRIVACY: DIFFERENTIAL PRIVACY IN BLOCKCHAIN USING FL

•

The registration process on the permissioned blockchain
will provide an extra layer of security by verifying the
identities of all the entities.
• The experimental results demonstrate higher transaction
efficiency, throughput, and low latency and outperforms
with respect to its counterpart in other performance
metrics.
II. R ELATED W ORK
IoT devices generate high volumes of data, so network
security goes beyond conventional measures like firewalls and
access control. In dynamic IoT environments, real-time monitoring, data handling and storage, access management, and
security are all challenges [26]. The authors of [42] propose
a zero-trust model that enables hierarchical mining based on
IoT. The authors describe IoT infrastructure as a zero-trust
model. To address this issue, Amatista has been introduced as
a blockchain-based middleware. The relentless advancement
of technology has woven its threads of innovation into every
corner of the world where human beings exist, bestowing us
with improved features and applications that have transformed
how we navigate the world. Now, this transformation is more
palpable than in the realm of healthcare [27], [28]. With the
advancement of technology like 5G [29], the healthcare sector
has profoundly evolved, catalyzed by these technological
strides. Among the most noteworthy shifts is the digitization of
medical records, a repository of sensitive patient information
that has transitioned from paper to electronic realms on the
network [30]. While this transition has streamlined many
aspects of healthcare, it has also unveiled new avenues for
digital privacy and security breaches. In a world where
medical records encompass deeply personal and private data,
sharing such intimate information electronically has spurred
the emergence of concerns [31], [32]. With advancements
in technology, the challenge of safeguarding the sanctity of
medical records has become more pronounced, especially in
light of their historical attractiveness to data thieves. This
confluence of digitization and data vulnerability casts an even
greater imperative on fortifying the security and privacy of
patients’ information [20].
Encryption has emerged as a cornerstone of data security
strategies, ensuring the confidentiality of patient information
by rendering it unreadable without the appropriate decryption
key. An encryption technique is used in [33]. However,
implementing encryption techniques can introduce processing
overhead and potential obstacles to key management and
distribution problems.
Role-based Access Control (RBAC) has been used in [34]
to restrict data access based on users’ roles, effectively
minimizing the risk of unauthorized data exposure. While
RBAC offers a structured approach to access management, its
complexity can lead to misconfigurations and challenges in
accommodating evolving access requirements.
In technological advancement, blockchain technology has
garnered attention for its potential to ensure data immutability
and transparency, which are critical for maintaining trustworthy audit trails in healthcare environments. Researchers in [21]

1169

used blockchain. Yet, its high computational demands and
scalability issues have raised concerns about its practicality
for large-scale healthcare systems.
Another technique, the Anomaly Detection System, is used
by [35] to rescue the data in healthcare. Anomaly Detection
System has proven valuable in identifying unusual patterns in
data access, thereby avoiding the detection of unauthorized
activities. However, striking a balance between accurate detection and a low rate of false positives remains an ongoing
challenge. Moreover, these systems may struggle to identify
new or previously unseen attack patterns.
Bio-metric authentication is used, relying on unique physical traits for robust user verification, significantly advancing
healthcare data security. However, concerns regarding biometric data compromise and the potential for false acceptance or
rejection warrant careful consideration.
The researcher also uses the homomorphic encryption
technique in [36], allowing computations on encrypted data
without decryption, which holds promise for preserving privacy during data processing. Nevertheless, its computational
intensity can lead to slower processing speeds, and successful
implementation often necessitates specialized expertise.
Tokenization [37] has been employed to replace sensitive
data with tokens, thereby limiting the exposure of valuable
information within the system. While effective token management is crucial, it’s important to note that tokenization might
not comprehensively address all security concerns, such as
insider threats.
Firewalls and Intrusion Detection Systems (IDS) are used
in [38]; they serve as essential safeguards by monitoring and
controlling network traffic. However, their efficacy against
advanced or zero-day attacks is limited, and the occurrence of
false positives and negatives can impact their reliability.
Data masking is used in [39], which involves obfuscating
original data while retaining its format and offers a practical
approach for testing and analysis. However, reversible masking
techniques can potentially result in data leaks, and ensuring the
consistency of masked data presents an additional challenge.
K-anonymization is used in [11] for enhancing privacy
by generalizing data to a level where individuals cannot
be uniquely identified. However, balancing privacy and data
utility can be complex, and re-identification attacks remain a
major concern.
T-closeness in [40] Guarantees that the distribution of sensitive information within an equivalence class closely mirrors
the distribution in the entire data set. However, achieving tcloseness might necessitate significant data distortion.
L-diversity introduces diversity within anonymity groups
in [41] to mitigate the risk of attribute disclosure. However,
achieving l-diversity can result in increased data distortion and
a trade-off between privacy and data quality.
Table II represents existing schemes, their achievements,
and limitations.
III. P RELIMINARIES
This section provides an in-depth overview of the proposed
method, encompassing its core functionality, definitions, and

1170

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 1, FEBRUARY 2025

TABLE I
N OTATIONS

TABLE II
S UMMARY OF T ECHNIQUES , ACHIEVEMENTS AND L IMITATIONS

communication model. We present a crucial safeguarding
approach to bolster security within the demanding landscape
of IoT networks. This method is designed to fortify the
security framework, ensuring its robustness and resilience. The
following are some key concepts that will be used in the
proposed method, and they is necessary to understand their
importance in the data-sharing process.

A. Differential Privacy
DP stands as a foundational concept in the domain of
data privacy, providing a quantifiable measure of the level
of privacy safeguards provided by a specific data analysis or
query; its primary function is to ensure that the incorporation
or omission of an individual’s data from the data set will not
significantly modify the results of the analysis. In mathematical terms, its definition can be articulated as follows:
A stochastic algorithm denoted as A, operating on a domain
D and yielding results in the codomain R, guarantees ε-DP

if, for any pair of data set D and D that vary only in the
information of a single individual and for all measurable sets
O ⊆ R,
Pr[A(D) = O]
≤ e .
Pr[A(D ) = O]
where the probability is taken over the randomness of the
algorithm A.
In this definition, ε is a non-negative privacy parameter.
Smaller values of ε correspond to stronger privacy guarantees,
with ε = 0 being perfect privacy (no information leakage).
Theorem 1 (LDP): Let  > 0 be a privacy parameter, and
let D be a dataset. A randomized algorithm A is said to satisfy
-Local DP if, for all possible outcomes O and for all datasets
D and D that differ in a single data point, we have:
Pr[A(D) = O]
≤ e .
Pr[A(D ) = O]
Proof: Let D and D be datasets that differ in exactly one
data point. We need to show that for any possible outcome

HUSSAIN et al.: ENSURING ZERO TRUST IOT DATA PRIVACY: DIFFERENTIAL PRIVACY IN BLOCKCHAIN USING FL

1171

O of the randomized algorithm A, the following inequality
holds:
Pr[A(D) = O]
≤ e .
Pr[A(D ) = O]
1) Step 1: Understand the Definition of -LDP: According
to the definition, a randomized algorithm A satisfies -LDP
if:

  
Pr[A(D) = O] ≤ e · Pr A D = O ,
for all possible outcomes O and for any datasets D and D
differing in one data point.
2) Step 2: Express the Definition in Terms of the Ratio:
Rewrite the definition to express it in terms of a ratio:
Pr[A(D) = O]
≤ e .
Pr[A(D ) = O]
3) Step 3: Consider the Outcome Probability for Datasets
D and D : Let’s denote:
PD (O) = Pr[A(D) = O]

  
PD (O) = Pr A D = O
We aim to show:
PD (O)
≤ e .
PD (O)
4) Step 4: Apply the Definition Directly: From the definition of -LDP, we have:
PD (O) ≤ e · PD (O).
5) Step 5: Isolate the Ratio: Divide both sides of the
inequality by PD (O):
PD (O)
≤ e .
PD (O)
6) Step 6: Conclude the Proof: The inequality PPD(O)
≤ e
D (O)
demonstrates that the probability of obtaining the outcome O
when applying the algorithm A to dataset D is at most e times
the probability of obtaining the same outcome when applying
the algorithm to dataset D . This satisfies the definition of LDP. Thus, we have shown that the randomized algorithm A
satisfies -LDP for datasets D and D differing in a single data
point.
B. Federated Learning
In a federated learning scenario, our objective is to train
a global model M across n decentralized user, each with its
local data set Di . The objective is to find the optimal model
parameters M ∗ that minimize a global loss function. This can
be formally defined as:
∗

M = arg min
M

n

i=1

Fig. 3.

Communication Model.

where L(M, Di ) is the local loss function for the user i. The
global loss function is the sum of the local losses across all
users. The optimization process involves adjusting the model
parameters M iteratively to minimize this global loss function.
The final result, M ∗ , is the set of model parameters that
achieves the minimum global loss.
C. Blockchain-Based Communication Model
This section provides a general overview and defines
the entities and underlying technologies considered in the
proposed work. The proposed model involves three main
participants: IoT data owners, data controllers, and end users.
Data owners are the residents and citizens who participate in
data collection; data controllers are the service providers (such
as Google for Nest devices and Amazon for Ring devices)
responsible for collecting, storing, and securing the data. A
data consumer is an entity that seeks to utilize data collected
by IoT devices, such as companies analyzing usage patterns to
improve product performance and researchers studying urban
behavior and smart home environments. FL and LDP are pivotal elements within this data-sharing framework. To achieve a
balance between security and privacy, All three key entities are
registered on a permissioned blockchain, Providing seamless
communication between data consumers. Data controllers and
processors. Concurrently, we adopt the concept of a selfsovereign identity (SSI) management system, an essential
component of digital identity management. This approach
empowers individuals with full autonomy over their own
identities, granting them the authority to manage their identity
information independently. We also develop a robust peer-topeer (P2P) network. Ensure reliable transfer of data through a
communication channel. Data consumers and facilitators can
benefit from a globally trained model. Verification of identity
through interactions. Fig. 3 serves as a visual illustration of
the communication model.
IV. P ROPOSED M ODEL

L(M, Di )

= arg min(L(M, D1 ) + L(M, D2 ) + . . . + L(M, Dn ))
M

= arg min Local Loss1 + Local Loss2 + · · ·
M

+ Local Lossn ,
(1)

In this section, we demonstrate our blockchain-based
proposed model in detail. It uses LDP for anonymization and
FL for collaborative model training. FL allows data owners
to train their models locally on their devices and share only
the encrypted model updates, ensuring that raw data remains
private and secure throughout the process.

1172

Fig. 4.

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 1, FEBRUARY 2025

Proposed model for secure IoT data sharing.

Outlined below are several key steps of the model’s operation, as depicted in Fig. 4:
1) Registration of Entities: To validate the identities of
all entities—data owners, data controllers, and data
consumers—registration on a permissioned blockchain
is required. This protects against interference in the datasharing process and adds an extra layer of security.
2) Blockchain bid posting and IPFS data storage: A
company or researchers ( data consumers) submit a bid
on the blockchain and upload a dataset specifications
file to IPFS. Bids may include links to specification
files, bid expiry dates, payment amounts, and tags (e.g.,
smart home energy usage). A data set requirement file
encompasses information about the data set schema,
such as the type of device, energy consumption, and
timestamps.
3) Accessing Bids on the Blockchain: The data controller
(e.g., service providers) accesses the data set specifications and identifies all bids of interest posted by data
consumers.
4) Requesting Data Acquisition to make an Offer: Data
controllers interconnect with data owners to get their
datasets. The data controller sends a base model for
training on local data. Data owners train this model, add
differential private noise, and return updated parameters.
This process iterates until the model is fully trained and
a final updated global model is created.
5) Posting offer on Blockchain and Data Set Specifications
on IPFS: Once the data controller has received the most
updated version of the global models, they formulate an
offer and post it on the blockchain. The offer includes a
link to the data specs file on IPFS. The data controller

also reveals the specifications file on IPFS, which
includes the data controller’s publicly accessible decentralized identities (DIDs). Data consumers acknowledge
the offer and access the data specs file uploaded on IPFS
by the data controller.
6) Exchange of Identity Proofs: Both parties establish
a secure P2P communication channel to exchange
information and identity proofs.
7) Confirming Identity: The identities of both parties (i.e.,
the controller and consumer) are verified using the SSI
ledger.
8) Payment to the Controller: After agreeing to the terms
of the offer, the data utilized launches a P-to-P protected
channel and makes the required payments to the data
controller.
9) Sharing the updated Global Model: Upon successful
verification, the final version of the updated model is
shared with the data consumer via the secure channel.
10) Compensation to data owners: After completing the
process of anonymized data sharing, the data controller
compensates the specific data owner.
Algorithm 1 begins by registering each entity (i.e., data
owners (P), data controllers (C), and data consumers (S)) on
B (line 1-3). S then post bids on the B and upload their data
specifications on I (line 4-6). C access these bids from the B
and identify their bids of interest (lines 7-9). Subsequently, C
send their initial global model G to each P, who trains the
model locally in the FL process and adds differential private
and sends back the updated model θp (line 10-15). The process
in lines 10-15 repeats till the model is fully trained for the
FL process, and finally, C receives updated global model G ∗
from P. C then formulate an offer based on G ∗ , post this offer

HUSSAIN et al.: ENSURING ZERO TRUST IOT DATA PRIVACY: DIFFERENTIAL PRIVACY IN BLOCKCHAIN USING FL

Algorithm 1 Blockchain-Based Secure Data Sharing With
LDP and FL
Input:
P: List of Data Owners
C: List of Data Controllers
S: List of Data Consumers
B: Permissioned Blockchain
I: Interplanetary File System (IPFS)
G: Initial Global Model
Output:
G ∗ : Final updated Global Model
·························································
1: for each entity e ∈ (P ∪ C ∪ S) do
2:
Register e on B
3: end for
4: for each consumer s ∈ S do
5:
s posts bids on B and uploads data specifications on I
6: end for
7: for each controller c ∈ C do
8:
c accesses bids from B and identifies bids of interest
9: end for
10: for each controller c ∈ C do
11:
for each owner p ∈ P do
12:
c sends G to p
13:
p trains G locally, applies DP and sends updated
model parameters θp back
14:
end for
15: end for
16: for each controller c ∈ C do
17:
c formulates an offer and posts it on B
18:
c uploads updated data set specifications on I
19: end for
20: for each consumer s ∈ S do
21:
if s accepts the offer then
22:
s makes payment to c through a secure P2P channel
c and s exchange identity proofs via a secure P2P
channel
24:
Identities are verified using the self-sovereign identity
(SSI) ledger
25:
end if
26: end for
27: for each controller c ∈ C do
28:
c shares the final updated global model G ∗ with s via
a secure P2P channel
29: end for
30: for each controller c ∈ C do
31:
for each owner p ∈ P do
32:
c compensates p after successful data sharing
33:
end for
34: end for
23:

on B and upload G ∗ dataset specification to I (line 16-19). If
S accepts an offer, They make a payment to C and exchange
identity proofs via a secure P2P channel and verify identities
via SSI ledger (lines 20-26). C share G ∗ with S via a secure
P2P channel. Finally, C compensates the specific P for their
contribution and successful data-sharing (lines 27-34).

Fig. 5.

1173

Latency.

V. I MPLEMENTATION AND R ESULTS
This section provides a detailed description of the model’s
implementation and testing approaches. Using the Remix
Ethereum platform, we built a private Ethereum blockchain
network to enhance the effectiveness and throughput of
blockchain transactions. In addition, the FL and LDP
processes were executed using Python. Proof-of-Authority
(POA) was the consensus protocol we chose. The simulation
has three main functions: registration, offer, and finalization.
Finalization is a payable function, whereas offer and registration are non-payable. A particular dataset is registered through
the register function, which is the first step. Subsequently,
offers are generated and responded to the registered bid using
the offer function.
We conducted experiments involving multiple arbitrary data
owners in the FL context. Our experimentation comprised
70 rounds of transactions, each encompassing the complete
trading procedures, including bidding, offers exchanges, finalization, and FL rounds.
Subsequently, we conducted a comprehensive comparative
analysis between the proposed scheme and the approach
presented by [11]. The findings are presented in the subsequent
figures. In our experiments, we accessed the privacy accuracy,
transaction latency, throughput, transaction efficiency, correlation, and analysis of variance. The subsequent sections delve
into the detailed outcomes of the proposed experiments.
A. Latency
Latency is the time required for a transaction to be submitted, integrated into the blockchain, and validated. It can be
calculated using the following equation (2) [27].
Latency = Cost/Throughput

(2)

We measured the transaction latency for 70 rounds of
transactions carried out within our proposed model and compared these results with the benchmark model [11] as shown
in Fig. 5. The latency assessment is conducted through the
system’s processor clock, particularly during key bidding
phases like registration, offering, and finalization, utilizing the
formula specified in equation (2).
Fig. 5 clearly shows that the proposed model outperformed
the benchmark in terms of latency. The proposed model
achieved a lower average transaction latency of 4.0 seconds,
while the benchmark model had a latency of 5.6 seconds. The

1174

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 1, FEBRUARY 2025

Fig. 6.

Throughput.
Fig. 7.

Base model accuracy vs. proposed model federated accuracy.

Fig. 8.

Base model accuracy vs. proposed model personnel accuracy.

increase in latency with each subsequent transaction is due
to the direct relationship between latency and the number of
transactions. As the transaction count grows, the time required
to process each transaction increases, consequently elevating
the overall latency.
B. Throughput
Throughput on a blockchain refers to the rate at which valid
transactions are processed per second (tps). It is calculated
using the equation (3).
Throughput(TP) = execution cost/latency

(3)

To assess the efficiency of our proposed model, we measured TP for key procedures (offer, finalize, register) during
the experiment. This throughput was calculated using the
formula outlined in Equation (3). To visualize the performance
improvement, Fig 6 comprehensively compares throughput
between our model and benchmark models, all processing 70
transactions.
Fig. 6 compares the benchmark model and the proposed
model’s throughput, clearly showing that the proposed model
achieved a higher throughput than its counterpart. The
proposed model achieved an average throughput of 10.23
tps, while the benchmark model achieved a throughput of
8 tps. It is important to note that an inverse relationship
exists between the number of transactions and throughput;
as the number of transactions increases, throughput tends to
decrease. Therefore, in each subsequent transaction, throughput decreases in Fig. 6.
C. Accuracy
Accuracy represents the mean of the accurate prediction
produced by the model, as shown in equation (4).
Accuracy = (validtransactions)/(TotalTransactions)

(4)

To evaluate the accuracy of the proposed scheme, we experimented with 70 iterations on three different IoT-connected
device data. We employed LDP to preserve privacy while calculating the scheme’s accuracy for both federated and personal
(individual) settings. The results are presented in Figs 8 and 7,
respectively, subsequently comparing these results with those
obtained by [11]. Personal accuracy signifies the accuracy of

an individual model, whereas federated accuracy represents the
accuracy achieved when aggregating models from all clients
to a global model.
The proposed scheme demonstrated an enhanced privacy
accuracy of 85% in both personal and federated settings
compared to the approach presented by [11], which achieved
an accuracy of 49%. The improved accuracy in our proposed
models can be attributed to the robust training mechanism
employed in FL and the applied LDP, which enhances data
accuracy. Both LDP and FL are new methods that improve
accuracy and ensure strong data privacy. The experiments for
the proposed model were executed within a Python Anaconda
environment to implement FL and LDP.
D. Transaction Efficiency
Another performance metric for the proposed model is
transaction efficiency (TE). It can be calculated using the
following equation (5).
TE =

Total Throughput
.
Resource Consumption

(5)

Throughput is the total number of transactions the system
performs in a specific time. Resource consumption refers to the
specific resources consumed to perform the total throughput;
here, resource consumption is the execution cost in the
form of gas used. In the experiment, transaction efficiency

HUSSAIN et al.: ENSURING ZERO TRUST IOT DATA PRIVACY: DIFFERENTIAL PRIVACY IN BLOCKCHAIN USING FL

Fig. 9.

1175

Throughput Transactions efficiency (TTE).

is evaluated for 70 rounds of transactions. Fig. 9 visually
represents the transaction efficiency comparison between the
proposed and base models. The visual representation shows
that the proposed model has better transaction efficiency than
the base model. The successive decrease in efficiency for
each subsequent transaction is due to the inverse relationship
between transaction efficiency and latency.

Fig. 10.

Consistency of transaction throughput.

Fig. 11.

Analysis for privacy loss ().

E. Performance Consistency of Transaction Throughput
Standard deviation is a statistical measure that quantifies
the degree of variation or dispersion within a dataset. It is an
essential tool in understanding the consistency of data. In the
context of transaction throughput, a lower standard deviation
indicates more consistent performance, while a higher standard
deviation signifies greater variability. The standard deviation
(σ ) is calculated using formula in equation (6):


N
1 
(6)
σ =
(xi − μ)2
N
i=1

where N is the number of throughput values, xi represents each
throughput value, and μ is the mean throughput.
The performance of the proposed and base models is compared by analyzing the standard deviation of their throughput
values. The proposed model shows σ of approximately 8.34,
while the base model has a slightly lower σ of about 6.57,
as shown in Fig. 10. Although the proposed model exhibits
higher variability, it generally achieves a higher throughput,
indicating better performance when peak throughput is prioritized. This analysis suggests that the proposed model in terms
of achieving a higher transaction throughput.
F. Comparative Analysis of Privacy Loss ()
Privacy Loss () is a metric used to quantify the amount
of privacy leakage or risk in a system, particularly in the
context s involving data privacy and security. A lower ()
value indicates better privacy preservation, suggesting less
information leakage per transaction.
We observe distinct trends in comparing the performance of
the base and proposed models based on their privacy loss ()
values. The base model initially starts with a higher () value
of around 4.5 and gradually decreases to about 0.6 over 70

iterations, indicating a slower rate of privacy improvement. On
the other hand, the proposed model begins with a lower ()
value near 4.0 and decreases more rapidly to approximately 0.1
over the same number of iterations, as shown in Fig. 11. This
faster reduction suggests a more effective privacy-preserving
mechanism in the proposed model than the base model.
G. Comparing Throughput-Latency Trade-off
In Fig. 12 comparing through and latency trade-offs
between the base and the proposed models, we observe clear
differences in how they handle the transaction processing. The
base model consistently shows lower throughput values at
various latency levels compared to the proposed model. This
suggests the proposed model can handle more transactions per
unit of time while keeping latency in check better than the
base model.
H. 95th Percentile Latency Comparison
In performance investigation, the 95th percentile latency is
a metric demonstrating the latency value less which 95% of
latency amount falls. This measure is crucial for considering
the worst-case performance scenarios that an arrangement
strength counter. The bar chart in Fig. 13 compares the 95th

1176

Fig. 12.

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 1, FEBRUARY 2025

Throughput-latency Trade-off.

Fig. 14.

Fig. 13.

95th percentile latency.

percentile latencies of base and proposed models. The base
model shows a 95th percentile latency of nearly 9.32 seconds, while the proposed model demonstrates a lower 95th
percentile latency of around 7.96 seconds. This specifies that
the proposed model not only achieves in terms of average
latency but also preserves more reliable performance under
high-load circumstances. The lower 95th percentile latency of
the proposed model recommends it can holder the widely hold
of the transactions more efficiently, making it a more robust
excellent for applications with low latency responses.
I. Comparison of Precision, Recall and F1-Score
In assessing the machine learning models, precision, recall,
and F1-score are crucial to measure the performance widely.
Precision is the ratio of the true positive prediction to the
total number of predictions, demonstrative the accuracy of the
positive prediction, and can be considered using equation (7).
Recall is the ratio of the true positive prediction to the total
number of actual positives, imitating the model’s capability
to recognize all the appropriate occurrences as shown in

Comparison of Precision, Recall, and F1-Score.

equation (8). The F1-Score is the harmonic mean of precision
and recall, utilizing equation (9), providing a balance between
the two metrics.
TP
(7)
Precision =
TP + FP
TP
Recall =
(8)
TP + FN
Precision × Recall
F1-Score = 2 ×
(9)
Precision + Recall
The bar chart in Fig. 14 illustrates the precision, recall, and
F1-Score for the Base and Proposed Model. The proposed
model outperforms the base model across all three metrics,
with a precision of 0.89, a Recall of 0.93, and an F1-Score
of 0.91. In contrast, the base model has a precision of 0.80,
a recall of 0.83, and an F-Score of 0.82. This shows that the
proposed model predicts more accurately and retrieves a higher
proportion of the actual positives, achieving a better balance
between precision and recall.
J. Linear Regression
1) Correlation: The correlation coefficient (commonly
denoted as r ) between variables X and Y in a dataset with
n pairs of observations can be calculated using the following
equation (10).
 n

 n
n ni=1 (Xi Yi ) −
i=1 Xi
i=1 Yi
r=
2
2
 n
 n
n ni=1 Xi2 −
n ni=1 Yi2 −
i=1 Xi
i=1 Yi
(10)
X, Y: Variables for which correlation is being calculated
: The summation symbol.
n: Present the number of data points.
XY: Product of X and Y.
XY: Sum of the products of X and Y.

HUSSAIN et al.: ENSURING ZERO TRUST IOT DATA PRIVACY: DIFFERENTIAL PRIVACY IN BLOCKCHAIN USING FL

1177

TABLE III
C ORRELATION M ATRIX FOR T HROUGHPUT (P ROPOSED M ODEL )

TABLE IV
A NALYSIS OF VARIANCE FOR T HROUGHPUT (P ROPOSED M ODEL )

Fig. 15.

Throughput-based model correlation with explanatory variables.

Fig. 16. Throughput proposed model correlation with explanatory variables.

X, Y: Sum of X values and Y values, respectively.
2) Analysis of Variance (ANOVA): ANOVA employs the Fstatistic to assess the significance of variation between group
means relative to variation within groups. One-way ANOVA
calculates the F-statistics as in equation (11).
F=

MSbetween
MSwithin

(11)

The general steps for calculating ANOVA involve computing the sum of squares. The degree of freedom and mean
square are used to compute the F-statistic.
Throughput Proposed Model: The R2 value indicates that
73% of the variability in the dependent variable, Proposed
Model, is explained by the three explanatory variables. Pvalue of the F-statistic from the ANOVA table and a sig-level
of 5%, the explanatory variables provide significantly more
explanatory power than a basic mean. This highlights the
substantial contribution of the explanatory variables to the
model.
Latency Proposed Model: The R-squared value indicates
that 49% of the variability in the dependent variable, the
Proposed Model, is explained by the three explanatory variables. P-value of the F-statistic in the ANOVA IV and a
significance level of 5%, the explanatory variables provide
significantly more information than a basic mean.
Fig. 15 shows the correlation for the throughput of the
base model. Fig shows that the relationship of federated

Fig. 17.

Latency-based model correlation with explanatory variables.

accuracy with benchmark model accuracy, personal accuracy, and throughput base model is weakly positive, strongly
positive, and weak negative, respectively. The relationship
between benchmark model accuracy and personal accuracy
and throughput base model is weak and negative. In contrast,
the personal accuracy and throughput base models have a
strong positive relationship.
Fig. 16 shows the correlation for the throughput of the
proposed model. The proposed model has weak negative,
personal, and benchmark model accuracy, which has a weak
positive relation with federated accuracy.
Fig. 17 and Fig. 18 show the correlation between the
latency of the base and the proposed model, respectively.
In Fig. 17 benchmark model accuracy has a weak negative,

1178

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 1, FEBRUARY 2025

TABLE V
C ORRELATION M ATRIX FOR L ATENCY (P ROPOSED M ODEL )

TABLE VI
A NALYSIS OF VARIANCE FOR L ATENCY (P ROPOSED M ODEL )

TABLE VII
C OMPARISON TABLE FOR BASE AND P ROPOSED S CHEME

VI. C ONCLUSION AND F UTURE P ROSPECTS

Fig. 18.

Latency proposed model correlation with explanatory variables.

while personal accuracy and latency have a strong positive
relationship with federated accuracy. The latency base model
has a weak negative, and personal accuracy has a strong positive relation with benchmark model accuracy. Latency-based
models and personal accuracy have a weak negative relation.
In Fig. 18, the benchmark model and personal accuracy have a
weak positive, while the latency proposed model has a strong
positive relation with federated accuracy. The latency proposed
model has weak negative and personal accuracy and a strong
positive relationship with benchmark model accuracy. Latency
proposed model and personal accuracy have a weak negative
relation.
K. Comparison Table
In Table VII, we provide a side-by-side comparison of the
base scheme, referenced from [11], and our proposed scheme,
highlighting key performance metrics and security features.

This research introduces a resilient, secure, and zerotrust architecture for exchanging sensitive information in IoT
networks, ensuring the highest level of privacy preservation
throughout the process. The approach integrates a robust P2P
communication channel to guarantee the safe transmission of
sensitive data. FL empowers models to operate locally and
precisely on the data owner’s side, avoiding the need for central data aggregation. LDP further fortifies privacy by offering
robust guarantees to each user during data collection and analysis. In the proposed framework, data owners have exclusive
authority over implementing LDP, ensuring robust data privacy
protection within a zero-trust architecture for sharing their
data sets. Blockchain technology, which fosters a decentralized
environment, effectively eliminates the vulnerability of a single
point of failure. The blockchain meticulously records the
registration of different entities, bids, offers, and prices, while
the data set specifications are saved in a decentralized file
system, i.e., IPFS. The proposed architecture’s fundamental performance metrics revolve around throughput, latency,
privacy, accuracy, ANOVAN, and correlation matrix, all of
which are essential for ensuring its effectiveness. The results
of our comparison metrics indicate the proposed model’s
significant advantages over the base-scheme model. We intend
to explore the integration of quantum cryptography to enhance
data security further. Additionally, we plan to investigate
the application of advanced machine-learning techniques to
improve the accuracy and efficiency of our models. Further
studies will also focus on optimizing performance metrics
to ensure scalability in larger environments and leveraging
generative AI to create synthetic datasets for more robust
model training and validation.

HUSSAIN et al.: ENSURING ZERO TRUST IOT DATA PRIVACY: DIFFERENTIAL PRIVACY IN BLOCKCHAIN USING FL

R EFERENCES
[1] T. Magara and Y. Zhou, “Internet of Things (IoT) of smart homes:
Privacy and security,” J. Electr. Comput. Eng., vol. 2024, no. 1, 2024,
Art. no. 7716956.
[2] L. Y. Rock, F. P. Tajudeen, and Y. W. Chung, “Usage and impact of
the internet-of-things-based smart home technology: A quality-of-life
perspective,” Univers. Access Inf. Soc., vol. 23, no. 1, pp. 345–364,
2024.
[3] T. Wang, S. Zhang, Q. Yang, and S. C. Liew, “Account service network:
A unified decentralized web 3.0 portal with credible anonymity,” IEEE
Netw., vol. 37, no. 6, pp. 101–108, Nov. 2023.
[4] A. A. Abba Ari, O. K. Ngangmo, C. Titouna, O. Thiare, A. Mohamadou,
and A. M. Gueroui, “Enabling privacy and security in cloud of
things: Architecture, applications, security & privacy challenges,” Appl.
Comput. Informat., vol. 20, nos. 1–2, pp. 119–141, 2024.
[5] Z. Liu, Z. Xu, X. Zheng, Y. Zhao, and J. Wang, “3D path planning in
threat environment based on fuzzy logic,” J. Intell. Fuzzy Syst., vol. 46,
no. 3, pp. 7021–7034, 2024.
[6] D. Han et al., “LMCA: A lightweight anomaly network traffic detection model integrating adjusted mobilenet and coordinate attention
mechanism for IoT,” Telecommun. Syst., vol. 84, no. 4, pp. 549–564,
2023.
[7] C. Ni, L. S. Cang, P. Gope, and G. Min, “Data anonymization evaluation
for big data and IoT environment,” Inf. Sci., vol. 605, pp. 381–392,
Aug. 2022.
[8] M. N. Khan, H. U. Rahman, T. Hussain, B. Yang, and S. M. Qaisar,
“Enabling trust in automotive IoT: Lightweight mutual authentication scheme for electronic connected devices in Internet of
Things,” IEEE Trans. Consum. Electron., early access, Jun. 6, 2024,
doi: 10.1109/TCE.2024.3410300.
[9] P. Panahi, C. Bayilmis, U. Çavusoglu, and S. Kaçar, “Performance
evaluation of lightweight encryption algorithms for IoT-based applications,” Arab. J. Sci. Eng., vol. 46, no. 4, pp. 4015–4037, 2021.
[10] J. Guo, M. Yang, and B. Wan, “A practical privacy-preserving publishing
mechanism based on personalized k-anonymity and temporal differential
privacy for wearable IoT applications,” Symmetry, vol. 13, no. 6, p. 1043,
2021.
[11] M. Rodriguez-Garcia, M. A. Sicilia, and J. M. Dodero, “A privacypreserving design for sharing demand-driven patient datasets over
permissioned blockchains and P2P secure transfer,” PeerJ Comput. Sci.,
vol. 7, p. e568, Jun. 2021.
[12] B. B. Mehta and U. P. Rao, “Improved l-diversity: scalable anonymization approach for privacy preserving big data publishing,” J. King Saud
Univ.-Comput. Inf. Sci., vol. 34, no. 4, pp. 1423–1430, 2022.
[13] X. Yin, Y. Zhu, and J. Hu, “A comprehensive survey of
privacy-preserving federated learning: A taxonomy, review, and
future directions,” ACM Comput. Surv., vol. 54, no. 6, pp. 1–36,
2021.
[14] N. Deepa et al., “A survey on blockchain for big data: Approaches,
opportunities, and future directions,” Future Gener. Comput. Syst.,
vol. 131, pp. 209–226, Jun. 2022.
[15] E. B. Fernandez and A. Brazhuk, “A critical analysis of zero trust
architecture (ZTA),” Comput. Stand. Interfaces, vol. 89, Apr. 2024,
Art. no. 103832.
[16] S. M. Awan, M. A. Azad, J. Arshad, U. Waheed, and T. Sharif, “A
blockchain-inspired attribute-based zero-trust access control model for
IoT,” Information, vol. 14, no. 2, p. 129, 2023.
[17] K. Yu, L. Tan, M. Aloqaily, H. Yang, and Y. Jararweh, “Blockchainenhanced data sharing with traceable and direct revocation in
IIoT,” IEEE Trans. Ind. Informat., vol. 17, no. 11, pp. 7669–7678,
Nov. 2021.
[18] S. Shi, D. Han, and M. Cui, “A multimodal hybrid parallel network
intrusion detection model,” Connect. Sci., vol. 35, no. 1, 2023,
Art. no. 2227780.
[19] X. Qin, Y. Huang, Z. Yang, and X. Li, “A blockchain-based
access control scheme with multiple attribute authorities for
secure cloud data sharing,” J. Syst. Archit., vol. 112, Jan. 2021,
Art. no. 101854.
[20] I. Yaqoob, K. Salah, R. Jayaraman, and Y. Al-Hammadi, “Blockchain
for healthcare data management: opportunities, challenges, and future
recommendations,” Neural Comput. Appl., vol. 34, pp. 11475–11490,
Jul. 2022.

1179

[21] B. Zaabar, O. Cheikhrouhou, F. Jamil, M. Ammi, and M. Abid,
“Healthblock: A secure blockchain-based healthcare data management
system,” Comput. Netw., vol. 200, Dec. 2021, Art. no. 108500.
[22] A. El Ouadrhiri and A. Abdelhadi, “Differential privacy for deep and
federated learning: A survey,” IEEE Access, vol. 10, pp. 22359–22380,
2022.
[23] C. Zhang, Y. Xie, H. Bai, B. Yu, W. Li, and Y. Gao, “A survey
on federated learning,” Knowl. Based Syst., vol. 216, Mar. 2021,
Art. no. 106775.
[24] T. Zhang, L. Gao, C. He, M. Zhang, B. Krishnamachari, and
A. S. Avestimehr, “Federated learning for the Internet of Things:
Applications, challenges, and opportunities,” IEEE Internet Things Mag.,
vol. 5, no. 1, pp. 24–29, Mar. 2022.
[25] H. Cheng, T. Lu, R. Hao, J. Li, and Q. Ai, “Incentive-based demand
response optimization method based on federated learning with a
focus on user privacy protection,” Appl. Energy, vol. 358, Mar. 2024,
Art. no. 122570.
[26] B. Kaur et al., “Internet of Things (IoT) security dataset evolution:
Challenges and future directions,” Internet Things, vol. 2, Jul. 2023,
Art. no. 100780.
[27] L. Javed, A. Anjum, B. M. Yakubu, M. Iqbal, S. A. Moqurrab,
and G. Srivastava, “Sharechain: Blockchain-enabled model for sharing
patient data using federated learning and differential privacy,” Expert
Syst., vol. 40, no. 5, 2023, Art. no. e13131.
[28] P. Tiwari, A. Lakhan, R. H. Jhaveri, and T.-M. Grønli, “Consumercentric Internet of Medical Things for cyborg applications based on
federated reinforcement learning,” IEEE Trans. Consum. Electron.,
vol. 69, no. 4, pp. 756–764, Nov. 2023.
[29] M. Kamrul Hasan et al., “A review on security threats, vulnerabilities,
and counter measures of 5G enabled Internet-of-Medical-Things,” IET
Commun., vol. 16, no. 5, pp. 421–432, 2022.
[30] W. N. Price and I. G. Cohen, “Privacy in the age of medical big
data,” Nat. Med., vol. 25, no. 1, pp. 37–43, 2019.
[31] K. Miyachi and T. K. Mackey, “hOCBS: A privacy-preserving
blockchain framework for healthcare data leveraging an on-chain and
off-chain system design,” Inf. Process. Manag., vol. 58, no. 3, 2021,
Art. no. 102535.
[32] K. Dev, I. Chih-Lin, and S. A. Khowaja, “Guest editorial DENSE—Data
integrity, integration and security issues for consumer data in industry
5.0,” IEEE Trans. Consum. Electron., vol. 69, no. 4, pp. 809–812,
Nov. 2023.
[33] S. Das and S. Namasudra, “A novel hybrid encryption method to secure
healthcare data in IoT-enabled healthcare infrastructure,” Comput. Elect.
Eng., vol. 101, Jul. 2022, Art. no. 107991.
[34] M. Fareed and A. A. Yassin, “Privacy-preserving multi-factor authentication and role-based access control scheme for the e-healthcare
system,” Bull. Electr. Eng. Informat., vol. 11, no. 4, pp. 2131–2141,
2022.
[35] A. M. Said, A. Yahyaoui, and T. Abdellatif, “Efficient anomaly detection
for smart hospital iot systems,” Sensors, vol. 21, no. 4, p. 1026, 2021.
[36] L. Zhang, J. Xu, P. Vijayakumar, P. K. Sharma, and U. Ghosh,
“Homomorphic encryption-based privacy-preserving federated learning
in IoT-enabled healthcare system,” IEEE Trans. Netw. Sci. Eng., vol. 10,
no. 5, pp. 2864–2880, Sep./Oct. 2023.
[37] Y. Zhuang, C. R. Shyu, S. Hong, P. Li, and L. Zhang, “Selfsovereign identity empowered non-fungible patient tokenization for
health information exchange using blockchain technology,” Comput.
Biol. Med., vol. 157, May 2023, Art. no. 106778.
[38] T. Lenard and R. Bolboaca, “A statefull firewall and intrusion
detection system enforced with secure logging for controller area
network,” in Proc. Eur. Interdiscipl. Cybersecur. Conf., 2021, pp. 39–45.
[39] M. Ahtesham, “Bigdata applications in healthcare: Security and privacy
challenges,” in Proc. Int. Conf. Digit. Technol. Appl., 2022, pp. 231–240.
[40] R. Bagai, E. Weber, and V. T. Gowda, “Data sanitization for t-closeness
over multiple numerical sensitive attributes,” Trans. Data Priv.,, vol. 16,
no. 3, pp. 191–210, 2023.
[41] K. Oishi, Y. Sei, Y. Tahara, and A. Ohsuga, “Semantic diversity: Privacy
considering distance between values of sensitive attribute,” Comput.
Secur., vol. 94, Jul. 2020, Art. no. 101823.
[42] M. Samaniego and R. Deters, “Zero-trust hierarchical management
in IoT,” in Proc. IEEE Int. Congr. Internet Things (ICIOT), 2018,
pp. 88–95, doi: 10.1109/ICIOT.2018.00019.
PAPER_TEXT
