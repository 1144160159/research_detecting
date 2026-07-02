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
# [183] Blockchain-Enabled Federated Learning for Enhanced Collaborative Intrusion Detection in Vehicular Edge Computing
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
编号：183
题名：Blockchain-Enabled Federated Learning for Enhanced Collaborative Intrusion Detection in Vehicular Edge Computing
年份：2024
DOI：10.1109/tits.2024.3351699
来源：IEEE Transactions on Intelligent Transportation Systems
PDF：paper/10.1109_TITS.2024.3351699.pdf
已有粗分类：联邦学习、隐私保护与分布式协同
二级关联：入侵检测与网络异常检测、IoT、车联网、工业互联网与边缘安全
相关性：强相关，分数 12
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\183.txt
- 原始字符数：58911
- 本次发送字符数：58911
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 7, JULY 2024

7661

Blockchain-Enabled Federated Learning for
Enhanced Collaborative Intrusion Detection
in Vehicular Edge Computing
Zakaria Abou El Houda , Member, IEEE, Hajar Moudoud , Member, IEEE,
Bouziane Brik , Senior Member, IEEE, and Lyes Khoukhi , Senior Member, IEEE

Abstract— Intelligent Transportation Systems (ITSs) are transforming the global monitoring of road safety. These systems,
including vehicular networks and transportation infrastructure,
are vulnerable to several security issues, which could disrupt
services and potentially cause harm to the users. It is crucial to
establish robust security measures to protect against evolving
attacks and ensure the safe and reliable operation of ITS.
Artificial Intelligence (AI)-based Intrusion Detection Systems
(IDS) are mainly used to enhance the security of ITS. The
adoption of AI-based techniques to secure ITS against new
emerging threats has been limited due to a lack of realistic and
recent data on these types of attacks (i.e., zero-day attacks).
In this context, we introduce a novel Edge-based Framework
that uses Federated Learning (FL) and blockchain to secure
ITS against new emerging threats. In particular, our proposed
framework consists of (1) a novel distributed Edge-based architecture that allows multiple Edge nodes to securely collaborate
while preserving their privacy; and (2) a decentralized and secure
reputation system based on blockchain technology to maintain
the reliability and trustworthiness of the FL process within the
ITS; This system manages reputation data for individual nodes
(such as vehicles), guaranteeing the integrity of the FL training
process. Experiment results using the UNSW-NB15 dataset show
that our proposed framework achieves high accuracy and F1
score (99%) in detecting new threats while ensuring the privacy
and reliability of the whole ITS. These results demonstrate the
effectiveness of our proposed framework in securing ITS.
Index Terms— Sustainable intelligent transportation systems,
green vehicular networks, intrusion detection systems, edge
computing, federated learning(FL), blockchain.

I. I NTRODUCTION

I

NTELLIGENT Transportation Systems (ITS) are a form of
transportation management that utilizes new emergent technologies to improve the efficiency, safety, and sustainability

Manuscript received 30 December 2022; revised 20 May 2023 and
2 November 2023; accepted 23 December 2023. Date of publication
25 January 2024; date of current version 2 July 2024. The Associate Editor
for this article was Z. Lyu. (Corresponding author: Zakaria Abou El Houda.)
Zakaria Abou El Houda is with Institut National de la Recherche Scientifique Centre Énergie Matériaux et Télécommunications (INRS-EMT),
Varennes, QC J3X 1S2, Canada (e-mail: zakaria.abouelhouda@inrs.ca).
Hajar Moudoud is with L@bISEN, ISEN Yncrea Ouest, 29200 Brest, France
(e-mail: hajar.moudoud@usherbrooke.ca).
Bouziane Brik is with the Computer Science Department, College of Computing and Informatics, Sharjah University, Sharjah, United Arab Emirates
(e-mail: bbrik@sharjah.ac.ae).
Lyes Khoukhi is with GREYC CNRS, ENSICAEN, Normandie University,
76000 Rouen, France (e-mail: lyes.khoukhi@ensicaen.fr).
Digital Object Identifier 10.1109/TITS.2024.3351699

of the current transportation systems. These systems include
a variety of technologies, such as traffic signal synchronization, Electronic toll collection (ETC), and real-time public
transportation information. These systems, including vehicular networks and transportation infrastructure, are complex
and require careful management to ensure their efficient
operation. Vehicular networks, also known as Vehicle-toEverything (V2X) communication, refer to the communication
technologies used to connect vehicles with other vehicles,
infrastructure, and pedestrians. These technologies enable
vehicles to exchange information, such as location, speed, and
traffic conditions, in real-time. Both vehicular networks and
ITS have the potential to greatly improve transportation, but
they also raise security and privacy concerns. Additionally,
the collection and storage of sensitive information, such as
location data, by ITS, may raise privacy concerns for individuals. It is crucial to establish robust security measures
to protect against evolving attacks and ensure the safe and
reliable operation of ITS. To address these security and privacy
concerns while still promoting sustainability, it is important to
prioritize privacy-aware secure collaborative learning methods.
Artificial intelligence (AI)-based intrusion detection systems
(IDS) are mainly investigated to enhance the security of ITS.
IDSs are largely used to enhance the security of ITS. An IDS
is a type of security software that monitors network traffic
and identifies potential threats or unauthorized activity. There
are two main types of IDS: (1) Network-based IDS which
monitors network traffic and looks for patterns or anomalies
that may indicate a security threat; and (2) Host-based IDS,
on the other hand, which monitors the activity on a specific
computer or device and looks for signs of an intrusion. In the
context of sustainable ITS, an IDS can be used to detect and
prevent cyber attacks on the network or specific devices within
the ITS. For example, an IDS could detect and prevent a
hacker from accessing traffic control systems or altering traffic
patterns. In addition to an IDS, other security measures can
be implemented to protect sustainable ITS, such as encryption,
regular software updates, and access controls. By implementing a combination of these measures, we can ensure the safe
and secure operation of sustainable ITS solutions.
The adoption of AI-based techniques to secure ITS against
emerging threats has been limited due to a lack of realistic and
recent data on these types of attacks. Without this data, it is

1558-0016 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

7662

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 7, JULY 2024

difficult for AI algorithms to accurately identify and mitigate
new threats (i.e., zero-day attacks) as they arise. To build
robust AI-based models for ITS infrastructure, it is essential
for organizations to collaborate in a privacy-aware manner.
With the increasing amount of personal data being collected
and processed by ITS, organizations need to prioritize the privacy of individuals and ensure that their personal information
is being handled responsibly [1], [2], [3], [4], [5], [6], [7], [8],
[9], [10], [11], [12].
Federated Learning (FL) is a distributed machine learning
approach in which multiple parties collaborate to build a model
without exchanging their sensitive data. Instead of sending
data to a central server to train a model, each party/agent
trains a model locally on its own data and sends only the
model parameters to the server. The server then combines
the model parameters from all parties to produce a global
model. One potential application of FL in ITS is to improve
traffic prediction and control. For example, traffic data from
multiple sources, such as sensors on roads, traffic cameras,
and GPS data from vehicles, could be used to train a global
model for traffic prediction. The model could then be used to
optimize traffic flow and reduce congestion. Blockchain technology could potentially be used to secure ITS by providing
a tamper-proof record of transactions and data. For example,
blockchain could be used to track the movement of vehicles
and ensure that only authorized vehicles have access to certain
areas. Blockchain can also be used to store data related to
maintenance and repairs, helping to ensure that vehicles are
properly maintained and safe to operate.
In this context, we propose a novel Edge-Enabled Framework that uses Federated Learning and blockchain to secure
the ITS network against emerging threats (i.e., zero-day
attacks). The use of Edge computing, blockchain, and FL
can enhance the security and privacy of ITS. Edge computing
brings security mechanisms closer to end devices, reducing
delays in communication and improving the overall security
of the system. FL, on the other hand, enables privacy-aware
collaborative learning between vehicles while preserving their
privacy. While Blockchain ensures the trustworthiness and
reliability of the FL training process. By leveraging these
technologies, we build secure and privacy-aware ITS-based
models that benefit both individuals and the overall transportation network. In particular, our proposed ITS-based framework
consists of (1) a novel distributed Edge-based architecture
that allows multiple Edge nodes to securely collaborate to
secure the ITS while preserving their privacy; and (2) a
blockchain-based reputation system that ensures the trustworthiness and reliability of the FL training process in ITS by
managing the reputation data for each node (e.g., vehicle)
participating in the learning process in a decentralized and
secure manner. The UNSW-NB15 dataset, which includes
well-known attacks and malware, was used to conduct in-depth
experiments to evaluate the effectiveness of decentralized
machine learning models in detecting these threats. The results
of these experiments showed a significant accuracy (99%)
and detection rate (99%), outperforming centralized machine
learning and deep learning models. In addition to their superior performance, our proposed framework also significantly

reduced delays and preserved privacy. These results demonstrate the potential of decentralized learning to enhance the
security of ITS and other IoT systems, while also protecting
the privacy of individuals (e.g., vehicle).
The main contributions of this paper are summarized as
follows:
• We design a novel distributed Edge-based architecture
that allows multiple Edge nodes to securely collaborate to
secure ITS while preserving their privacy. This architecture allows Edge nodes to securely collaborate and share
information and knowledge, ensuring the integrity and
reliability of the ITS while preserving the privacy of each
node.
• We propose a decentralized and secure reputation system
based on blockchain technology to maintain the reliability
and trustworthiness of the FL process within the ITS.
This system manages reputation data for individual nodes
(such as vehicles), guaranteeing the integrity of the FL
training process.
• We evaluate our proposed framework in terms of
accuracy, F1-score, precision, detection rate, and computational complexity. The UNSW-NB15 dataset, which
includes well-known attacks and malware, was used to
conduct in-depth experiments to evaluate the effectiveness of our proposed framework in detecting zero-day
attacks. The obtained results show a significant accuracy (99%) and detection rate (99%), outperforming
centralized machine learning and deep learning models.
In addition to their superior performance, our proposed
framework demonstrates its ability to effectively achieve
trustworthiness, efficiency, security, and privacy.
This paper is organized as follows. Section II presents
related work. Section III presents our system model.
Section IV discusses our blockchain-based reputation system. Section V presents the experimental setup and results.
Section VI evaluates the performance of our proposed framework and compares it with recent AI schemes. Finally,
Section VII concludes the paper and outlines future work.
II. R ELATED W ORK
AI techniques have been largely discussed in the literature
to detect intrusions in vehicular systems. One approach is
to use supervised learning algorithms to classify normal and
abnormal behavior in the vehicle’s system. In this context,
Singh et al. [13] proposed an AI model that can be used to
identify false position information transmitted by misbehaving
vehicles. The model was constructed using two different
classifiers, i.e., logistic regression and support vector machine.
Ghaled et al. [14] a new method for detecting security threats
in Vehicular networks by combining shared knowledge and
Ensemble Learning (EL) techniques. They proposed generating weighted random forest classifiers for each vehicle and
combining them through a reliable voting method. Additionally, each vehicle trains local classifiers using a random forest
algorithm and leverages the collective knowledge of multiple
vehicles. Gyawali et al. [15] proposed a novel mechanism
to prevent internal attacks on vehicular systems. Their proposed mechanism combines AI techniques with a reputation

ABOU EL HOUDA et al.: BLOCKCHAIN-ENABLED FL FOR ENHANCED COLLABORATIVE INTRUSION DETECTION

mechanism to detect attacks and ensure the dependability of
vehicles. The reputation mechanism is used to evaluate the
trustworthiness of vehicles and their actions, while the AI
component is used to analyze and interpret data to identify
attacks or other issues that may affect the reliability of the
vehicles. Tariq et al. [16] proposed a transfer learning-based
approach for intrusion detection on a Controller Area Network
(CAN). The authors employed a Convolutional LSTM network
and leveraged pre-trained models from other domains to
enhance the intrusion detection performance. Their approach
showed promising results in accurately detecting intrusions
at the CAN network, outperforming existing methods. Their
proposed model is fine-tuned using one-shot transfer learning.
FL is a promising approach that can be used to improve
the security and privacy of ITS. FL involves training local
networks based on weights obtained from a central model.
By training local networks on individual vehicles and aggregating their results at the central model, FL can enable vehicles
to learn from each other and improve their performance
while preserving their privacy. In this context, Lu et al.
[17] developed a privacy-aware data protection mechanism
for Vehicular cyber-physical systems (VCPS) that relies on
FL. This approach involves (1) data transformation; and
(2) collaborative data leakage detection. In the data transformation phase, data collected from individual vehicles
is protected through techniques such as encryption and
anonymization. The collaborative data leakage detection phase
involves training models on the transformed data using FL, and
then aggregating the results to detect any potential data leaks.
This approach allows vehicles to share data and collaborate on
tasks while still safeguarding the privacy of the data and protecting against potential threats. The scheme allows vehicles to
locally train models while ensuring the privacy of their data.
Kong et al. [18] presented an FL-based navigation scheme
that utilizes a homomorphic encryption scheme along with the
bounded Laplace mechanism to protect local model updates.
Despite its advantages, FL is still at risk of certain types of
attacks, including backdoor attacks. To protect against this type
of attack, it is important to implement measures such as strong
encryption and secure communication protocols, as well as to
continually monitor and assess the performance and behavior
of the models. Ensuring the reliability of participating nodes
is crucial in order to prevent these types of attacks.
From another point of view, the integration of blockchain
technology with FL to improve privacy protection in the
ITS is of paramount importance. Lu et al. [19] proposed a
blockchain-based approach to enhance secure data sharing in
the Internet of Vehicles (IoV). Their proposed scheme used
asynchronous federated learning, where data from multiple
vehicles is aggregated and analyzed without sharing the raw
data. By employing blockchain technology, the scheme ensures
data integrity, transparency, and immutability. To efficiently
select nodes, the framework employs a deep reinforcement
learning (DRL)-adopted asynchronous FL approach. The proposed framework also includes learning models that enhance
the reliability of data shared between a Roadside Unit (RSU)
and vehicles. This is achieved through a two-step verification
process, adding an extra layer of security and ensuring the

7663

integrity of the shared data. Liu et al. [20] proposed the
integration of blockchain and federated learning to improve
collaborative intrusion detection in vehicular edge computing. Their proposed work explores the use of blockchain
technology to enhance the security and privacy of the datasharing process. To secure the aggregation model, the authors
proposed using blockchain to store and share the training models. Otoum et al. [21] focused on securing critical
IoT infrastructures. The authors proposed a solution that
combines blockchain and federated learning techniques to
enhance the security and privacy of IoT systems. The use of
blockchain technology ensures data integrity and immutability,
while federated learning enables collaborative learning without
exposing sensitive data to a central authority. Trusted end
devices are included in the blockchain to ensure the accuracy
of the consensus algorithm. Kang et al. [22] examined the issue
of reliable federated learning in mobile networks. The authors
proposed a solution that improves the reliability and efficiency
of federated learning in the context of mobile networks. The
study investigated various strategies to optimize the learning
process and enhance the overall performance of federated
learning systems.
After a careful review of the research literature, we identified several limitations. Some solutions were computationally
expensive and were be suitable for resource-constrained environments. In addition, many of these solutions were trained
on outdated datasets, which can lead to inaccurate and inefficient AI-based intrusion detection models when it comes to
detecting zero-day attacks in vehicular networks. One of the
main problems is the lack of up-to-date datasets containing a
sufficient number of new attack records, as large institutions
are often reluctant to share sensitive data with the research
community due to privacy concerns. In light of these issues,
we propose a secure collaborative Edge-based attack detection framework that uses FL and blockchain-based solutions
to collaboratively and securely mitigate attacks in vehicular
networks while preserving privacy and ensuring reliability.
III. S YSTEM M ODEL
In this section, we describe our system model; it outlines
how the proposed framework ensures privacy-aware learning
using FL and blockchain. In collaborative learning, as proposed by McMahan et al. [23], the objective is to find a global
optimum solution through the collaboration and cooperation
of multiple independent agents/systems without sharing their
data. This can be thought of as a decentralized optimization
problem, in which each agent/system has its own data and
computational resources, and must work together to find a
solution that is optimal for the group as a whole.
Federated optimization algorithms aim to coordinate the
actions of these agents or systems in order to find an optimal
solution in a distributed manner, without the need for a
central authority or coordinator. Fig. 1 shows our proposed
architecture which includes three tiers. In our three-tier federated learning system, the first tier consists of nodes in a
vehicular network, such as vehicles equipped with sensors or
communication devices. These nodes collect data and perform
some initial processing, using local resources such as onboard

7664

Fig. 1.

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 7, JULY 2024

System architecture.

processors or Edge computing nodes. The second tier, the Edge
computing layer, consists of intermediate processing nodes
located closer to the edge of the network, such as at traffic
intersections or on-road infrastructure. These nodes perform
more complex tasks, such as binary classification, using more
powerful resources such as high-performance processors or
GPUs. The third tier, the cloud tier, consists of centralized
resources such as data centers or cloud servers, which are
used to perform the most computationally intensive tasks such
as multi-class classification. The three tiers work together to
analyze and classify data collected from the vehicular network,
using the resources available at each tier to perform the
necessary processing and analysis. The goal is to find an
optimal solution for the overall system, taking into account
the constraints and capabilities of each tier. This approach
allows the system to scale and adapt to changing conditions,
such as changes in the data being collected or changes in the
computational resources available at each tier. In our proposed
architecture, the Edge layer serves as an intermediary between
the first tier (consisting of nodes in a vehicular network)
and the third tier (consisting of centralized resources such as
data centers or cloud servers). The Edge layer aggregates the
local model updates sent from each node in the vehicular network and uses them to perform real-time, low-latency attack
detection using a binary classifier. Meanwhile, the cloud layer
investigates the specific type of attack that has been detected,
using a multi-class classifier to classify the attack into one of
several categories (such as DDoS, worms, or fuzzers). This

approach allows the system to quickly identify and classify
attacks occurring in the vehicular network, using the resources
available at each tier to perform the necessary processing and
analysis.
In this process, the Edge organization is responsible for initiating and managing the collaborative learning effort for an ITS.
This involves initializing the parameters of a shared FL learning model with an initial set of weights and selecting a group
of N authenticated and reputable Edge-based participants to
contribute to the learning process. The Edge organization may
use various criteria to select these participants, such as their
reputation or their ability to contribute high-quality data or
computational resources to the learning process. Once the
participants have been selected, the Edge organization can
begin the federated learning process, coordinating the actions
of the participants in order to find an optimal solution for the
overall system (see Fig. 2). In the context of an ITS, the Edge
organization is responsible for coordinating the collaborative
learning process among a group of authenticated Edge-based
participants. To do this, the organization first sends the shared
model to each participant. Each participant then uses their own
local ITS-based training data to perform local updates on the
model, using techniques such as gradient descent or stochastic
gradient descent. After the local updates have been completed,
each Edge node encrypts its updated model and divides it
into multiple shares. These encrypted model updates are then
sent to a secure aggregator, which combines (aggregates) the
updates from all of the participants and sends them back to

ABOU EL HOUDA et al.: BLOCKCHAIN-ENABLED FL FOR ENHANCED COLLABORATIVE INTRUSION DETECTION

the Edge organization. The Edge organization then decrypts
the aggregated model and sends the resulting global model
back to each Edge node, which can be used as the starting
point for a new learning cycle. This process can be repeated
iteratively, with the Edge organization coordinating the actions
of the participants in order to find an optimal solution for the
overall system [24], [25], [26], [27].
In this work, we aim to optimize the objective function
of a non-convex neural network. Specifically, we define the
optimization problem as follows:
N

min ϕ(wr )

wr ∈R d

where ϕ(wr ) =

1 X
ϕn (wr )
N

(1)

n=1

where N is the number of Edge participants.
The purpose of local learning is to find a set of parameters
wr that minimize the loss function, which can be expressed
as follows:
J

ϕn (wr ) =

∀n,

n
1 X
ϕ jn (wr ; x jn , y jn )
Jn

(2)

jn =1

At the start of each round r in the collaborative learning
process, each Edge node calculates the mean gradient on its
local ITS-based data using the current model parameters wr .
This calculation is performed using a batch or local mini-batch
of data and may involve one or several local epochs e. The
process can be described as follows:
grn = ∇ϕn (Wr ; br )

(3)

To perform local gradient descent on the shared FL model,
each Edge collaborator will need to have access to the current
model parameters and the local gradient that it calculated using
its own local ITS-based data, as follows:
∀n,

Wrn ← Wr − η∇ϕn (Wr ; br )

(4)

IV. S UBJECTIVE L OGIC
We are developing a novel blockchain-based reputation
system for our data-sharing network, harnessing the power
of subjective logic. Subjective logic is a probabilistic information fusion framework that enables the representation
and combination of subjective beliefs using opinions. Our
approach integrates the principles of subjective logic, allowing for the seamless representation and fusion of subjective
beliefs and opinions on the blockchain. By incorporating this
advanced methodology, our system accommodates a spectrum
of positive, negative, and uncertain statements, enabling a
comprehensive understanding of each participant’s trustworthiness. With the incorporation of logical operators, we are
establishing a sophisticated mechanism to correlate and analyze diverse opinions, thus fostering a robust and transparent
evaluation of participants’ interactions. This blockchain-based
model ensures the seamless integration of subjective beliefs,
paving the way for a secure and trustworthy environment
within our data-sharing network.

7665

A. Trusted Vehicle Opinions
Subjective logic serves as a valuable framework for managing uncertainties and subjective opinions within multi-agent
systems. In this context, the local opinion vector, denoted
j
as Oi = {bi , di , u i , a}, plays a pivotal role in capturing
the nuanced dynamics of trust and belief between individual
vehicles. Here, bi signifies the confidence or belief that vehicle
K i places in the information relayed by vehicle K j , while
di reflects the corresponding level of doubt or disbelief.
Complementing these, the parameter u i denotes the degree
of uncertainty that vehicle K i associates with the transmitted
data. Together, these components provide a comprehensive
representation of the intricate nature of trust and belief within
the vehicular network. Finally, the parameter a assumes significance as the base rate, influencing the calculation of the
expectation value of the probability of opinion, denoted as
E(Oi ) = bi + au i . By incorporating these elements, the local
opinion vector facilitates a structured and systematic approach
to managing trust relationships, enabling vehicles to make
well-informed decisions in the face of uncertainties. This is
calculated as follows:

αi→ j

bi→ j =



αi→ j + βi→ j




 di→ j = βi→ j + 2a − 2
αi→ j + βi→ j
(5)

2


u i→ j =



αi→ j + βi→ j


 a = base rate
j

The local opinion vector u i contains α positive events and
β negative events with uncertainty represented by a. The
extent of uncertainty within the vector is intricately tied to the
efficacy of communication established between vehicles i and
j. This communication quality, represented as 1−bi→ j −di→ j ,
serves as a metric for evaluating the likelihood of successful
data packet transmission during the exchange of information
for data sharing requests.
Subjective logic encompasses various types of opinions,
including hyper opinions, multinomial opinions, and binomial
opinions. Within the scope of this article, we concentrate on
uncertain binomial opinions (UBO) concerning binary events,
particularly those associated with valid or invalid data transmission. This selection is informed by the inherent uncertainty
prevalent in updates or data transmissions among vehicles
within the transportation system, always bounded from zero
local can be
on-wards. As a result, the local reputation Ti→
j
defined as follows:
local
local
local
Ti→
j = bi→ j + γ u i→ j

(6)

where γ ∈ [0, 1] denotes the level of uncertainty that impacts
the reputation of vehicles.
B. Multi-Weighted Local Opinions
Multi-weight subjective logic is an evolution of traditional
SL that involves weighting operations. In our framework,
different weights are used to formulate local opinions. In this

7666

Fig. 2.

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 7, JULY 2024

System process.

context, the following factors are taken into consideration
when calculating the reputation of a vehicle:
1) Vehicle Interaction: A higher frequency of interaction
indicates that the vehicle data requestor (ki ) has more
pre-existing information about the vehicle data provider
(k j ), thereby facilitating a more precise and dependable
calculation of reputation. Vehicles can either interact
honestly or dishonestly. Honest interactions increase the
trust of the vehicle and result in an increase in reward,
while dishonest interactions have the opposite effect.
We can define a vehicle interaction V I as the ratio of
the number of interactions between the data requestor
and the data provider during a time window, as follows:
possesses more pre-existing information about the data
provider (k j ), thereby facilitating a more precise and
dependable calculation of reputation.
αi→ j + βi→ j
Ii→ j = V P
k∈V αi→k + βi→k

(7)

2) Event Updates: In our framework, the trustworthiness
and reliability of a vehicle can change over time. The
reputation of a data provider (k j ) from the perspective
of a data requestor (ki ) is affected by both recent and
past events, with the former having a larger impact on
the local opinion. Typically, recent events are considered
within a one-week timeframe, and negative events carry
greater weight in shaping local opinions than positive
ones. This facilitates the generation of a reputation
calculation that is more precise and dependable.
Event updates reflect the effect of time on reputation,
in this context, the weight of positive events is represented by w1tcurr , while the weight of negative events is
represented by w2tcurr . It is stated that w1+w2 = 1, and
that w1 ≤ w2, implying that negative events are given
more weight than positive events. Additionally, σ and τ
where σ + τ = 1, represents the weights of recent event

and the weights of past events, respectively, as follows:
(
t
αi = w1tcurr (σ αitcurr + τ αi pas )
(8)
t
βi = w2tcurr (σβitcurr + τβi pas )
t

where αitcurr and αi pas represent the number of current
positive events and past positive events, respectively.
In this context, a vehicle interaction can be formulated
as follows:
Ii→ j =
t

V

t

w1tcurr (σ αitcurr + τ αi pas ) + w2tcurr (σβitcurr + τβi pas )
P
k∈V αi→k + βi→k
(9)

3) Trajectory Similarity: In transportation systems, data
collected by vehicles is considered to be relevant only
to the vehicles that collected it, and is limited in
scope to the specific location where it was collected.
To improve the relevance of the data and enable location
awareness, the trajectory similarity of the vehicles is
taken into consideration when calculating reputation
during data sharing among vehicles. A high trajectory
similarity indicates that the data being shared from the
data provider is more relevant and likely to be of high
quality, accuracy, and reliability. This consideration of
trajectory similarity is intended to help ensure that data
sharing among vehicles results in the most useful and
relevant information being shared.
Our framework introduces a trajectory similarity measure that
builds upon a modified version of the Hausdorff distance.
This measure is designed to capture the similarity between
two trajectories and can be used to compare and analyze
the movements of objects or individuals over time. Given a
universal set T and Hansdroff distance d : T x T → R between

ABOU EL HOUDA et al.: BLOCKCHAIN-ENABLED FL FOR ENHANCED COLLABORATIVE INTRUSION DETECTION

V ∈ T and W ∈ T , as follows:
h(V, W ) = max{ sup d(v, W ), sup d(V, w)}
v∈W

w∈V

(10)

where h(V, W ) ̸ = h(W, V ). As an extension we can define
h(V, W ) = max{h(V, W ), h(W, V )}.
The Hausdorff distance is a measure of similarity between
sets of points, but it has limitations when used to compare
sets with outlier points or time series data. It is affected by
the presence of outlier points and is not designed to consider
the order of points in a series. In order to improve the accuracy
and reliability of the matching process, we take two actions:
rejecting a certain proportion of the worst matches identified
under the maximum specified in the equation, and restricting
the set over which the minimum is calculated to a subset
of the second set. These actions aim to reduce the impact
of poor-quality matches and focus the matching process on
a specific subset of the second set, improving the overall
performance of the process, as follows:
α
h α,N ,C (V, W ) = or dv∈V
{

min

w∈N W (Cv ,W (v))

d(v, w)}

(11)

where C V,W : V → W maps each point v ∈ V to a
corresponding point w ∈ W and N W : W → V (W ) maps
each point w, which represents the neighborhood of that point
v. The functions N W and C V,W work together to create a
structure within which the matching process is performed. The
operator or d α f (x) refers to the value in the set f (x), i.e., the
image of the set x under the function f , that is grater than α
times the number of values in f (x), Here:
0
or dv∈V
{ f (v)} = min f (v)

(12)

0.5
ˇ
or dv∈V
{ f (v)} = f (v)

(13)

1
or dv∈V
{ f (v)} = max f (v)
v∈V

(14)

v∈V

Our aim is to identify the spatial patterns within the
trajectories. To achieve this, we’ve opted for arc-length parameterization. We define the length of a specific trajectory t as
follows:
X
|T | =
∥ti − ti−1 ∥2
(15)
i∈V

Additionally, we define the subsequent formed by the first k
k . We also define the relative
vehicle/points as Tk = {ti }i=1
position of the n th vehicle/point in T as:
πt (tn ) =

|Tn |
|T |

(16)

To express the correspondence structure C V,W , we define the
reverse transformation as follows:
|Tn |
r T (x) = T (arg min |a −
|)
(17)
n≤V
|T |
C V,W (v) = W (r W (πv (v)))
(18)
The neighborhood structure N W is defined as:
N W (w0 ) = {w ∈ Q∥πW (w0 ) − πW (w)| ≤ w/2}

(19)

where w is the parameter relative to the size of the
neighborhood.

7667

The Hausdorff distance is now represented by α, w, where
α and w are the specified parameters. It should be understood
that the arc-length parameterization is used for the correspondence in N W and C V,W , and w is used as the neighborhood
size. We can express the similarity as follows:
d 2 (v, w)
}
(20)
2α
where d(v, w) is the squared distance between v and w. The
overall weight of reputation for local opinions is:
sim(v, w) = exp{−

σi→ j = γ1 Ii→ j + γ2 sim(i, j)

(21)

where γ1 + γ2 = 1, and 0 ≤ γ1 ≤ 1 and 0 ≤ γ2 ≤ 1.
C. Recommended Opinions
In the context of blockchain networks, the consideration of
reputation opinions is crucial. Miners, who play a significant
role in maintaining the integrity of the blockchain, rely on
various sources of information to make informed decisions.
Apart from local reputation opinions, they also delve into
the blockchain to gather direct reputation opinions of selected
workers, updated by other nodes. This process enables them
to obtain recommended reputation opinions. Let’s assume that
miner m receives a set of recommended opinions about worker
r ec := br ec , d r ec , u r ec , as follows:
wi→
j
i→ j i→ j
i→ j
local
bi→r (brlocal
→w + dr →w )
wr = P
local
r ∈X (br →w + dr →w )

(22)

where r ∈ X is the recommender and dr →w + dr →w is the
familiarity value between recommender r and worker w and.
This value represents the similarity or relatedness between the
two recommenders or items, with a higher value indicating
a higher level of familiarity. In our framework, the set of
blockchain workers 8(W ) provide a set of recommendation
8(r ), we can express:
bi→r =

|8(Wi ) ∩ 8(r )|
|8(Wi ) ∪ 8(r )|

(23)

Finally,the recommended opinion is a composite of subjective opinions from various sources, such as neighboring
vehicles. These opinions are integrated and weighted to produce a single opinion, as:

X
r ec
r ec

b
=
wr bi→w

i→w



rX
∈X

 r ec
r ec
di→w =
wr di→w
(24)

rX
∈X


 u r ec =
ec

wr u ri→w

 i→w
r ∈X

D. Integrating Local Opinions With Recommended Opinions
After acquiring shared data from multiple data providers,
a data requestor might construct a subjective perception of
each provider, influenced by their past interactions. To ensure
the integrity of the process, it is essential to integrate these
individual viewpoints while shaping the ultimate, unified opinion. The combined reputation opinion of vi from worker w is

7668

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 7, JULY 2024

com = bcom , d com , u com and can be defined as
denoted as Ri→w
i→w i→w i→w
follows:

local u r ec + br ec u local

bi→w

i→w
i→w i→w
com
 bi→w
=


local + u r ec − u r ec u local

u

i→w
i→w
i→w i→w



local u com + d r ec u local
d
i→w i→w
i→w i→w
com
(25)
di→w
= local
r ec − u r ec u local

u
+
u

i→w
i→w
i→w i→w



r ec

u local

i→w u i→w
com


 u i→w = local
ec − u r ec u local
u i→w + u ri→w
i→w i→w

TABLE I
UNSW-NB15 L ABELS

Similarly, the composite reputation is:
com
com
com
Ti→
j = bi→ j + γ u i→ j

(26)

V. I MPLEMENTATION
In this section, we present the steps taken to implement
and evaluate our proposed framework. We begin by outlining
the experimental environment in which the framework was
tested. Next, we present the experimental results and provide
an analysis of the performance of our proposed framework.
This includes well-known metrics to measure the effectiveness
of AI models. Finally, we evaluate the effectiveness of the
framework based on the experimental results. This includes a
summary of the key findings from the experiments, as well as
any recommendations or next steps that we believe would be
beneficial for improving the framework in the future.
A. Experimental Results
We have implemented our proposed framework using Pysyft
[28] to easily build and train deep learning models in a federated setting, leveraging the powerful capabilities of PyTorch
to build and train our models. To simulate the ITS-based
environment test, we use Mininet [29], a virtual environment
for testing and simulating the behavior of vehicular networks.
Mininet allows users to create a virtual networks, consisting of
virtual hosts, switches, and links, and to test how the network
behaves under different conditions. Mininet can be used to
simulate a variety of network scenarios, including those related
to vehicular networks. In our tested scenario, Mininet was used
to create a virtual environment that includes virtual vehicles
equipped with sensors or communication devices, as well as
virtual infrastructures such as traffic lights or road signs.
In order to evaluate the efficacy and practicality of our
proposed framework, we carried out experiments utilizing
the UNSW-NB15 dataset, specifically focusing on attacks
within ITS. This dataset, renowned for its substantial volume
of data samples, served as an ideal resource for evaluating
the framework’s performance; it includes 100 GB of attack
traffic, such as backdoors, exploits, and shellcodes, which are
common types of attacks in ITS. By using the UNSW-NB15
dataset to evaluate our framework, we were able to assess
its performance in detecting different types of attacks and
identify any potential issues in ITS-based networks. This
dataset provided a realistic and representative testbed for
evaluating the effectiveness of our proposed framework in an
ITS setting.

In this study, we have defined two different scenarios to
test the effectiveness of our proposed framework: one for
multi-class classification and one for binary classification.
In the multi-class classification scenario, the model must
predict the correct class label from a set of multiple class
labels. In the binary classification scenario, the model must
predict between two class labels, typically represented as 0
(Normal) and 1 (Attack). We divide the UNSW-NB15 dataset
in order to give each participant a subset of the data and
also to deal with issues with non-i.i.d (as in “non-independent
and identically distributed data”). To evaluate the performance
of our framework, we tested a range of combinations of the
number of training rounds (varying from 10 to 50) and local
epochs (varying from 1 to 5). We used four participants (A, B,
C, and D, as shown in Fig. 1) in each scenario, each working
with their local data. To begin, we randomly initialized the
parameters of the global model and sent it to each participant.
Each participant then trained the model using their local data,
and the global model was tested on the test set. This process
allowed us to evaluate the performance of the model across all
of the participant’s data, including in the case of an imbalanced
dataset.
Fig. 3 shows the learning curves of the tested models in different scenarios, as represented by the negative log-likelihood
loss values, the x-axis represents the number of training
iterations or epochs, while the y-axis represents the negative
log loss. The curve shows the negative log loss decreasing over
time as the model is trained. As the FL model becomes more
accurate, the negative log loss decreases, eventually reaching
a minimum value where the FL model is most accurate. This
shows that the trained models used to detect zero-day attacks
in the ITS setting are able to learn from each other without
sharing their local data. This is achieved through the use of our
proposed framework, in a decentralized privacy-aware manner.
VI. P ERFORMANCE E VALUATION
To evaluate the performance of our proposed framework,
we used a variety of metrics, including accuracy, precision,
recall, F1-score, and the area under the receiver operating
characteristic (ROC) curve (AUC). These metrics allow us to
measure the effectiveness of the framework in different ways,
including its ability to classify instances accurately, identify
true positives and negatives, and distinguish between different
classes. The area under the ROC curve (AUC): This metric
measures the performance of the model in distinguishing

ABOU EL HOUDA et al.: BLOCKCHAIN-ENABLED FL FOR ENHANCED COLLABORATIVE INTRUSION DETECTION

Fig. 3.

Learning curves for (a) 10 rounds; (b) 25 rounds; and (c) 50 rounds.

Fig. 4.

Confusion matrices for Binary classification for (a) 10 rounds; (b) 25 rounds; and (c) 50 rounds.

Fig. 5.

Confusion matrices for Multi-class Classification for (a) 10 rounds; (b) 25 rounds; and (c) 50 rounds.

between positive and negative instances, calculated as the area
under the ROC curve. A model with a higher AUC score
is considered to be more effective at distinguishing between
positive and negative instances. These metrics are defined as
follows:
TP +TN
Accuracy =
(27)
T P + T N + FP + FN
TP
Pr ecision =
(28)
T P + FP
TP
Recall = D R = T P R =
(29)
T P + FN

Pr ecision ∗ Recall
Pr ecision + Recall
FP
FPR =
T N + FP
F1 = 2 ∗

7669

(30)
(31)

Figs. 4 and 5 show the confusion matrices on the UNSWNB15 test dataset for binary (Edge-based training) and
multi-class (cloud-based training) classification, respectively.
These obtained results show that our proposed framework has
achieved high performance in detecting the new attacks in
ITS, as indicated by the high values of accuracy, precision,
recall, and F1 score. The obtained accuracy, precision, recall,

7670

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 7, JULY 2024

Fig. 6.

ROC Curves for Binary classification for (a) 10 rounds; (b) 25 rounds; and (c) 50 rounds.

Fig. 7.

ROC Curves for Multi-class Classification for (a) 10 rounds; (b) 25 rounds; and (c) 50 rounds.

and F1-score of 99%, respectively, in the Edge-based training
step (binary classification) and the cloud-based step (multiclass classification) shows that the proposed framework is
able to correctly classify a large proportion of the ITS-based
attacks of the UNSW-NB15 dataset. Thus, the results obtained
in Figs. 4 and 5 show that the proposed framework is highly
effective at detecting ITS-based attacks with high accuracy and
privacy.
Figs. 6 and 7 show the confusion matrices on the
UNSW-NB15 test dataset for binary (Edge-based training) and
multi-class (cloud-based training) classification, respectively.
In both scenarios, our proposed framework achieves an AUC
of 99%. These results demonstrate that our proposed framework is highly effective at detecting ITS-based attacks with
high AUC in both scenarios while preserving participants’ data
privacy.

TABLE II
C OMPARATIVE A NALYSIS

framework with centralized AI-based schemes. The results
show that our proposed framework has the highest accuracy of
99% and the highest F1-score of 99%. These results demonstrate the effectiveness of our proposed framework in detecting
attacks while preserving the privacy of the participants.

A. Comparative Analysis
In this section, we evaluate the performance of our proposed framework with centralized AI-based schemes, using
the UNSW-NB15 dataset. To compare the performance of
these approaches, we use various evaluation metrics, including
accuracy, precision, recall, and F1-score.
In this study, we compare the performance of our proposed
framework with several recent centralized AI-based schemes,
including: SVM [30], StackEns [31], MultiStacking [32],
HybridML [33], LSTM [34], OnlineEns [35], TSE [36], StackExtra [37], and IDS-OGM [38]. Table II presents a comparison
of the accuracy, precision, recall, and F1-score of our proposed

VII. C ONCLUSION
In this paper, we introduced a novel framework for securing ITS against emerging threats using FL and blockchain
technology. Our proposed framework includes a distributed
Edge-based architecture that allows multiple Edge nodes to
collaborate in securing the ITS while preserving their privacy.
Then, we have introduced a decentralized and secure reputation system based on blockchain technology to maintain
the reliability and trustworthiness of the FL process within
the ITS. This system manages reputation data for individual
nodes (such as vehicles), guaranteeing the integrity of the FL

ABOU EL HOUDA et al.: BLOCKCHAIN-ENABLED FL FOR ENHANCED COLLABORATIVE INTRUSION DETECTION

training process. Evaluation of the proposed framework using
the UNSW-NB15 dataset, which contains well-known attacks
and malware, showed that our proposed framework achieved
high accuracy and F1 score of 99%, respectively, in detecting
ITS-related threats while preserving privacy and reliability.
These results demonstrate the effectiveness of our proposed
framework in securing ITS. For future work, we intend to
develop AI models that offer explanations, thereby increasing
the transparency of the FL training process and facilitating the
identification and prevention of backdoor attacks. Furthermore,
we aim to expand and enhance the scalability of the reputation
process. Lastly, we will extend the application of our framework to other datasets to ensure comprehensive testing and
validation.
R EFERENCES
[1] Z. A. El Houda, “Security enforcement through software defined
networks (SDN),” Ph.D. dissertation, Département d’informatique et
de Recherche Opérationnelle, Université à Montréal, Montreal, QC,
Canada, 2021.
[2] M. Abdel-Basset, N. Moustafa, H. Hawash, I. Razzak, K. M. Sallam,
and O. M. Elkomy, “Federated intrusion detection in blockchain-based
smart transportation systems,” IEEE Trans. Intell. Transp. Syst., vol. 23,
no. 3, pp. 2523–2537, Mar. 2022.
[3] Z. A. El Houda, B. Brik, and L. Khoukhi, “Ensemble learning for
intrusion detection in SDN-based zero touch smart grid systems,”
in Proc. IEEE 47th Conf. Local Comput. Netw. (LCN), Sep. 2022,
pp. 149–156.
[4] J. Zhao, X. Chang, Y. Feng, C. H. Liu, and N. Liu, “Participant selection
for federated learning with heterogeneous data in intelligent transport
system,” IEEE Trans. Intell. Transp. Syst., vol. 24, no. 1, pp. 1106–1115,
Jan. 2023.
[5] Z. A. E. Houda, A. Hafid, and L. Khoukhi, “Blockchain meets AMI:
Towards secure advanced metering infrastructures,” in Proc. IEEE Int.
Conf. Commun. (ICC), Jun. 2020, pp. 1–6.
[6] S. Liu, J. Yu, X. Deng, and S. Wan, “FedCPF: An efficientcommunication federated learning approach for vehicular edge computing in 6G communication networks,” IEEE Trans. Intell. Transp. Syst.,
vol. 23, no. 2, pp. 1616–1629, Feb. 2022.
[7] Z. A. E. Houda, A. S. Hafid, L. Khoukhi, and B. Brik, “When
collaborative federated learning meets blockchain to preserve privacy in healthcare,” IEEE Trans. Netw. Sci. Eng., vol. 10, no. 5,
pp. 2455–2465, Sep./Oct. 2023, doi: 10.1109/TNSE.2022.3211192.
[8] Y. Li, Y. Guo, M. Alazab, S. Chen, C. Shen, and K. Yu, “Joint optimal
quantization and aggregation of federated learning scheme in VANETs,”
IEEE Trans. Intell. Transp. Syst., vol. 23, no. 10, pp. 19852–19863,
Oct. 2022.
[9] Z. A. El Houda, L. Khoukhi, and B. Brik, “A low-latency fog-based
framework to secure IoT applications using collaborative federated
learning,” in Proc. IEEE 47th Conf. Local Comput. Netw. (LCN),
Sep. 2022, pp. 343–346.
[10] X. Ma, Q. Jiang, M. Shojafar, M. Alazab, S. Kumar, and S. Kumari,
“DisBezant: Secure and robust federated learning against Byzantine
attack in IoT-enabled MTS,” IEEE Trans. Intell. Transp. Syst., vol. 24,
no. 2, pp. 2492–2502, Feb. 2023.
[11] Z. A. E. Houda, B. Brik, A. Ksentini, L. Khoukhi, and M. Guizani,
“When federated learning meets game theory: A cooperative framework
to secure IIoT applications on edge computing,” IEEE Trans. Ind.
Informat., vol. 18, no. 11, pp. 7988–7997, Nov. 2022.
[12] R. Zhu, M. Li, H. Liu, L. Liu, and M. Ma, “Federated deep reinforcement
learning-based spectrum access algorithm with warranty contract in
intelligent transportation systems,” IEEE Trans. Intell. Transp. Syst.,
vol. 24, no. 1, pp. 1178–1190, Jan. 2023.
[13] P. K. Singh, S. Gupta, R. Vashistha, S. K. Nandi, and S. Nandi, “Machine
learning based approach to detect position falsification attack in vanets,”
in Proc. Int. Conf. Secur. Privacy. Cham, Switzerland: Springer, 2019,
pp. 166–178.
[14] F. A. Ghaleb et al., “Misbehavior-aware on-demand collaborative intrusion detection system using distributed ensemble learning for VANET,”
Electronics, vol. 9, no. 9, p. 1411, Sep. 2020.
[15] S. Gyawali, Y. Qian, and R. Q. Hu, “Machine learning and reputation
based misbehavior detection in vehicular communication networks,”
IEEE Trans. Veh. Technol., vol. 69, no. 8, pp. 8871–8885, Aug. 2020.

7671

[16] S. Tariq, S. Lee, and S. S. Woo, “CANTransfer: Transfer learning based
intrusion detection on a controller area network using convolutional
LSTM network,” in Proc. 35th Annu. ACM Symp. Appl. Comput.,
Mar. 2020, pp. 1048–1055.
[17] Y. Lu, X. Huang, Y. Dai, S. Maharjan, and Y. Zhang, “Federated learning
for data privacy preservation in vehicular cyber-physical systems,” IEEE
Netw., vol. 34, no. 3, pp. 50–56, May 2020.
[18] Q. Kong et al., “Privacy-preserving aggregation for federated learningbased navigation in vehicular fog,” IEEE Trans. Ind. Informat., vol. 17,
no. 12, pp. 8453–8463, Dec. 2021.
[19] Y. Lu, X. Huang, K. Zhang, S. Maharjan, and Y. Zhang, “Blockchain
empowered asynchronous federated learning for secure data sharing
in Internet of Vehicles,” IEEE Trans. Veh. Technol., vol. 69, no. 4,
pp. 4298–4311, Apr. 2020.
[20] H. Liu et al., “Blockchain and federated learning for collaborative
intrusion detection in vehicular edge computing,” IEEE Trans. Veh.
Technol., vol. 70, no. 6, pp. 6073–6084, Jun. 2021.
[21] S. Otoum, I. A. Ridhawi, and H. Mouftah, “Securing critical IoT infrastructures with blockchain-supported federated learning,” IEEE Internet
Things J., vol. 9, no. 4, pp. 2592–2601, Feb. 2022.
[22] J. Kang, Z. Xiong, D. Niyato, Y. Zou, Y. Zhang, and M. Guizani, “Reliable federated learning for mobile networks,” IEEE Wireless Commun.,
vol. 27, no. 2, pp. 72–80, Apr. 2020.
[23] H. B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. Y. Arcas,
“Communication-efficient learning of deep networks from decentralized
data,” in Proc. AISTATS, 2017, pp. 1273–1282.
[24] B. Brik, A. Ksentini, and M. Bouaziz, “Federated learning for UAVsenabled wireless networks: Use cases, challenges, and open problems,”
IEEE Access, vol. 8, pp. 53841–53849, 2020.
[25] Z. A. E. Houda, A. S. Hafid, and L. Khoukhi, “MiTFed: A privacy preserving collaborative network attack mitigation framework
based on federated learning using SDN and blockchain,” IEEE Trans.
Netw. Sci. Eng., vol. 10, no. 4, pp. 1985–2001, Jul./Aug. 2023, doi:
10.1109/TNSE.2023.3237367.
[26] H. Moudoud, S. Cherkaoui, and L. Khoukhi, “Towards a secure and
reliable federated learning using blockchain,” in Proc. IEEE Global
Commun. Conf. (GLOBECOM), Dec. 2021, pp. 1–6.
[27] Z. A. El Houda, H. Moudoud, B. Brik, and L. Khoukhi, “Securing federated learning through blockchain and explainable AI for robust intrusion
detection in IoT networks,” in Proc. IEEE INFOCOM Conf. Comput.
Commun. Workshops (INFOCOM WKSHPS), May 2023, pp. 1–6.
[28] Pysyft. Accessed: 2022. [Online]. Available: https://github.com/
OpenMined/PySyft
[29] MiniNet. Accessed: 2022. [Online]. Available: http://mininet.org
[30] N. Marir, H. Wang, G. Feng, B. Li, and M. Jia, “Distributed abnormal
behavior detection approach based on deep belief network and ensemble
SVM using spark,” IEEE Access, vol. 6, pp. 59657–59671, 2018.
[31] S. Rajagopal, P. P. Kundapur, and K. S. Hareesha, “A stacking ensemble
for network intrusion detection using heterogeneous datasets,” Secur.
Commun. Netw., vol. 2020, pp. 1–9, Jan. 2020.
[32] H. Zhang, J.-L. Li, X.-M. Liu, and C. Dong, “Multi-dimensional
feature fusion and stacking ensemble mechanism for network
intrusion detection,” Future Gener. Comput. Syst., vol. 122,
pp. 130–143, Sep. 2021. [Online]. Available: https://www.sciencedirect.
com/science/article/pii/S0167739X2100114X
[33] Z. Chkirbene, S. Eltanbouly, M. Bashendy, N. AlNaimi, and A. Erbad,
“Hybrid machine learning for network anomaly intrusion detection,”
in Proc. IEEE Int. Conf. Informat., IoT, Enabling Technol. (ICIoT),
Feb. 2020, pp. 163–170.
[34] Y. Yan, L. Qi, J. Wang, Y. Lin, and L. Chen, “A network intrusion
detection method based on stacked autoencoder and LSTM,” in Proc.
IEEE Int. Conf. Commun. (ICC), Jun. 2020, pp. 1–6.
[35] Y.-F. Hsu, Z. He, Y. Tarutani, and M. Matsuoka, “Toward an online
network intrusion detection system based on ensemble learning,” in
Proc. IEEE 12th Int. Conf. Cloud Comput. (CLOUD), Jul. 2019,
pp. 174–178.
[36] B. A. Tama, M. Comuzzi, and K.-H. Rhee, “TSE-IDS: A two-stage
classifier ensemble for intelligent anomaly-based intrusion detection
system,” IEEE Access, vol. 7, pp. 94497–94507, 2019.
[37] M. H. Kabir, M. S. Rajib, A. S. M. T. Rahman, Md. M. Rahman, and
S. K. Dey, “Network intrusion detection using UNSW-NB15 dataset:
Stacking machine learning based approach,” in Proc. Int. Conf. Advancement Electr. Electron. Eng. (ICAEEE), Feb. 2022, pp. 1–6.
[38] N. Moustafa, G. Misra, and J. Slay, “Generalized outlier Gaussian mixture technique based on automated association features for simulating
and detecting web application attacks,” IEEE Trans. Sustain. Comput.,
vol. 6, no. 2, pp. 245–256, Apr. 2021.

7672

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 7, JULY 2024

Zakaria Abou El Houda (Member, IEEE) received
the Ph.D. degree in computer science from the
University of Montreal, Montreal, QC, Canada, and
the Ph.D. degree in computer engineering from
the University of Technology of Troyes, Troyes,
France, in 2021. He is currently a Professor with the
Energy, Materials, and Telecommunications Center,
National Institute of Scientific Research (INRS),
Canada. He is also a member of the INRS-UQO
Joint Research Unit in Cybersecurity. Prior to joining INRS, he was a Research Scientist in various
institutions, contributing to significant research projects on the application of
machine learning for intrusion detection systems, and studying the explainability and robustness of these systems. His current research interests include
applied AI for intrusion detection systems, security in distributed/federated
machine learning, and blockchain for network security.

Bouziane Brik (Senior Member, IEEE) received
the Engineering degree (Hons.) in computer science
and the M.Sc. and Ph.D. degrees from Laghouat
University, Algeria, in 2010, 2013, and 2017, respectively. He is currently an Assistant Professor with
the Computer Science Department of Computing
and Informatics College, Sharjah University, United
Arab Emirates. Before joining Sharjah University,
he was an Assistant Professor with the DRIVE
Department, Bourgogne University, France. He was
a Post-Doctoral Researcher with the CESI School,
University of Troyes, and Eurecom Research Institute, France. He has
been (still) working on resources management and security challenges of
5G network slicing in the context of H2020 European projects, including
MonB5G, 5GDrones, InDiD, and 5G-INSIGHT. His research interests include
5G and beyond networks, explainable AI, and machine/deep learning for
wireless networks. He is an active member in many conferences organizing
committees, such as Globecom, WCNC, ICC, GIIS, EAI, and EAI CICom.
He actively organized different special issues in prestigious journals and
conference workshops.

Hajar Moudoud (Member, IEEE) received the
B.Eng. degree in software engineering from the
Mohammadia School of Engineers, Rabat, Morocco,
in 2018, the Ph.D. degree in computer engineering from the University of Sherbrooke, Canada,
and the Ph.D. degree in computer engineering
from the University of Technology of Troyes,
France, in 2022. Her research interests include
the security of the Internet of Things, applied
machine/deep learning for intrusion detection systems, and leveraging blockchain to enhance the
security of next-generation networks (5G and beyond/6G).

Lyes Khoukhi (Senior Member, IEEE) received
the Ph.D. degree in electrical and computer engineering from the University of Sherbrooke, Canada,
in 2006. From 2007 to 2008, he was a Post-Doctoral
Researcher with the Department of Computer
Science and Operations Research, University of
Montreal. Currently, he is a Full Professor with
GREYC CNRS, ENSICAEN, Normandie University. His current research topics are in the field
of cybersecurity, attack detection, and performance
evaluation in advanced networks, such as cloud
networking, 5G/SDN, the IoT/V2X, and CPS.
PAPER_TEXT
