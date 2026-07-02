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
# [640] DDoS Attack Detection in Business Blockchain Networks: A Review, Framework, and Challenges
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
编号：640
题名：DDoS Attack Detection in Business Blockchain Networks: A Review, Framework, and Challenges
年份：2025
DOI：10.1109/tnse.2025.3588625
来源：IEEE Transactions on Network Science and Engineering
PDF：paper/10.1109_TNSE.2025.3588625.pdf
已有粗分类：数据集、基准、综述与开源工具
二级关联：恶意流量、暗网与攻击检测、联邦学习、隐私保护与分布式协同
相关性：中相关，分数 7
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\640.txt
- 原始字符数：107020
- 本次发送字符数：107020
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
906

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 13, 2026

DDoS Attack Detection in Business Blockchain
Networks: A Review, Framework, and Challenges
Mengyuan Li , Jiewei Chen , Shaoyong Guo , Xuesong Qiu , Senior Member, IEEE, and Feng Qi

Abstract—With the rapid growth of the Internet of Things and
the increasing deployment of blockchain technology in critical
applications, distributed denial of service (DDoS) attacks pose a
significant threat to the security and availability of blockchain
networks. However, due to the lack of data sharing among different
business chains, existing attack detection systems fail to identify
global DDoS attack patterns. This leads to reduced detection accuracy and timeliness, as well as increased risks of false positives
and false negatives. Moreover, it prevents the implementation of
distributed collaborative defense mechanisms, allowing attackers
to bypass local defenses through cross-chain attacks.This paper
reviews the current state of DDoS attack detection in blockchain
networks and provides a preliminary look at the challenges facing
the field.To address these challenges, this paper proposes a new
intrusion detection system, BAFL, which utilizes supervision chain
and federated learning to detect DDoS attacks in blockchain network layer. We design a distributed DDoS architecture that utilizes
a supervised chain of directed acyclic graph (DAG) structures to
achieve trusted sharing of model parameters among client nodes
and record detected DDoS attacks. The system uses asynchronous
federated learning algorithm, weights the client model based on its
DDoS attack detection accuracy, and introduces a time attenuation
factor to reduce the influence of old model parameters on aggregation and accelerate model convergence. Through comprehensive
experiments on data sets such as CIC-DDoS2019, we demonstrated
that the accuracy of BAFL in detecting DDoS attacks is more than
99%, which is better than traditional methods, the accuracy is
increased by 2%, and the real-time detection delay is reduced by
half. The results highlight the robustness and scalability of BAFL,
making it a promising solution for protecting blockchain networks
from DDoS threats.
Index Terms—DDoS attack detection, federated learning,
blockchain, supervision chain.

I. RESEARCH BACKGROUND
HE Internet of Things (IoT) aims to enable smart manufacturing, smart factories and optimized communications
within the industrial ecosystem. Due to its ability to share data
efficiently and prevent data tampering, blockchain has been
widely applied in the IoT. The distributed ledger characteristic of blockchain allows data to be stored and shared across

T

multiple nodes, avoiding the bottlenecks in data management
and processing that occur in centralized architectures, and enhancing the system’s scalability and fault tolerance. Moreover,
the immutability and transparency of blockchain increase the
credibility of data, enabling IoT devices to establish a trust
mechanism, ensuring the authenticity and reliability of data, and
thus providing a solid foundation for the collaborative operation
of IoT devices. However, its interconnected nature and valuable
data make it vulnerable to cyber attacks, and without effective
protection strategy, the potential cost of cyber attacks will reach
$90 trillion by 2030. Major risks include malware proliferation
and downtime caused by DoS and DDoS attacks that exploit
system vulnerabilities.
Specifically, the extensive connectivity of IoT devices, which
often possess limited computational and storage capabilities and
weak security measures, provides attackers with abundant attack
vectors and diverse pathways to launch sophisticated and covert
DDoS attacks. The substantial data traffic generated by these
IoT devices not only facilitates the creation of false traffic surges
by attackers, thereby triggering DDoS attacks, but also poses a
threat to the normal operation of blockchain networks due to
potential data tampering or forgery. The decentralized nature
of blockchain networks further complicates the situation, as it
allows attackers to bypass traditional defense mechanisms by
exploiting vulnerabilities in smart contracts or by controlling
multiple nodes, while also dispersing attack traffic across numerous nodes to enhance attack stealth. Moreover, the increasing
reliance of critical applications on blockchain networks means
that DDoS attacks can not only paralyze these applications, causing significant societal and economic impacts, but also disrupt
data sharing mechanisms, affect data synchronization and verification, and potentially infringe upon user privacy. Finally, the
diversity of IoT devices and the complexity of data traffic present
significant challenges for DDoS attack detection, necessitating
the development of novel detection techniques and lightweight
defense mechanisms tailored to the IoT environment.

A. DDoS Attacks Detection in Business Blockchain Networks
Received 14 April 2025; revised 25 May 2025; accepted 6 July 2025. Date
of publication 14 July 2025; date of current version 21 November 2025. This
work was supported by the National Key R&D Program of China under Grant
2022YFB2703400. Recommended for acceptance by Dr. Liehuang Zhu. (Corresponding author: Shaoyong Guo.)
The authors are with the State Key Laboratory of Networking and Switching Technology, Beijing University of Posts and Telecommunications, Beijing
100876, China (e-mail: mengyuanli@bupt.edu.cn; chenjiewei@bupt.edu.cn;
syguo@bupt.edu.cn; xsqiu@bupt.edu.cn; qifeng@bupt.edu.cn).
Digital Object Identifier 10.1109/TNSE.2025.3588625

With the widespread application of blockchain technology in
fields such as finance and supply chain management, the risk
of DDoS attacks it faces has become increasingly prominent.
The decentralized nature of blockchain networks diversifies the
attack paths, enabling attackers to launch complex attacks by
exploiting consensus mechanisms and smart contracts, such as
transaction spamming and Sybil attacks. These attacks not only

2327-4697 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

LI et al.: DDoS ATTACK DETECTION IN BUSINESS BLOCKCHAIN NETWORKS: A REVIEW, FRAMEWORK, AND CHALLENGES

prolong transaction finalization times but also lead to a decrease
in network throughput and service performance. Therefore, researching effective DDoS attack detection methods is crucial for
ensuring the security and stability of blockchain networks [1].
DDoS attack detection methods in blockchain networks significantly differ from those in industrial settings, mainly in
terms of network characteristics, attack patterns, detection technologies, and application scenarios. The decentralized nature,
dynamic topology, and complex attack patterns (e.g., transaction
spamming and Sybil attacks) of blockchain networks increase
detection difficulty. In contrast, industrial networks’ hierarchical, fixed topology and relatively singular attack patterns (e.g.,
network-layer flooding attacks) make detection more focused on
device security and mitigation of common attacks. In terms of
detection technology, blockchain networks often employ deep
learning techniques (such as CNN and LSTM) and decentralized
federated learning to accommodate their high dynamism and
concurrency. Industrial networks, on the other hand, rely more
on traditional machine learning and statistical analysis methods.
Additionally, blockchain networks’ application scenarios (such
as finance and supply chain management) have extremely high
requirements for data real-time and security, necessitating rapid
identification and mitigation of attacks. Industrial networks,
however, place greater emphasis on the stability and reliability
of devices.These reasons lead us to the necessity of researching DDoS attack detection methods applicable to blockchain
networks.
In addition to localized DDoS attacks targeting individual
business chains, the existence of global DDoS attacks within
blockchain networks poses a significant threat. These global
attacks not only compromise the performance and security of
individual business chains but also have the potential to destabilize the entire blockchain network through cross-chain attacks.
The interconnected nature of blockchain networks means that an
attack on one chain can propagate to others, exploiting shared
nodes, protocols, and trust mechanisms to achieve a broader
disruption.
The current state of DDoS attack detection in blockchain
networks is characterized by a focus on local analysis. Existing
detection methods predominantly concentrate on analyzing network traffic data at individual nodes or within specific business
chains. While this approach can provide insights into localized
attack patterns, it falls short in capturing the full scope of global
attacks. The lack of comprehensive, cross-chain data sharing and
coordinated analysis mechanisms limits the ability to identify
and mitigate attacks that span multiple business chains. This
fragmented approach to detection creates vulnerabilities, as
attackers can exploit the isolation of individual chains to launch
coordinated attacks that evade local defenses and disrupt the
overall stability of the blockchain network.
To address these challenges, there is a pressing need for detection frameworks that can integrate data from multiple business
chains and perform global analysis. Such frameworks should
be capable of identifying attack patterns that transcend individual chains and coordinating defensive measures across the
entire network. This requires not only technical advancements
in data sharing and analysis but also the development of trust

907

mechanisms that ensure the integrity and confidentiality of
shared information. By adopting a holistic approach to DDoS
attack detection, blockchain networks can enhance their resilience and maintain the security and stability necessary for
their widespread adoption and operation.
B. Supervision Chain
Blockchain technology effectively addresses the issues of
data tampering and information silos prevalent in traditional
regulatory models through its immutable and distributed ledger
characteristics [2]. It ensures that once data is recorded, it
cannot be altered by employing cryptographic techniques and
consensus mechanisms. It also supports data sharing and verification across institutions, thereby enhancing the transparency
and credibility of regulatory processes. For example, in the
financial sector, blockchain can record detailed information
of financial transactions in real-time, helping regulatory authorities quickly detect and address violations while protecting investors’ interests. Meanwhile, the complete data history
recorded by blockchain supports comprehensive traceability,
facilitating post-event audits and investigations by regulatory
authorities, such as tracing the source of quality issues in supply
chain management. Moreover, blockchain supports dynamic
node participation and departure, thereby enhancing the system’s scalability and maintaining stability in the face of node
failures or network partitions. By ensuring real-time access to the
latest model parameters and detection results across all nodes,
it improves the timeliness of detection and facilitates rapid
information sharing. Therefore, blockchain technology can be
employed to construct a supervision chain for detecting DDoS
attacks within blockchain networks, ensuring data immutability
and traceability and guaranteeing data security and integrity.
The “supervision chain” is a core facility built on blockchain
technology, used for formulating and enforcing regulatory rules,
as well as verifying and auditing cross-chain data [3]. It is usually
controlled by regulatory authorities. It has a close relationship
with blockchain, inheriting characteristics such as immutability
and decentralization. It is a specific application of blockchain
technology in the regulatory field.The supervision chain works
in tandem with the business chain. The business chain serves
specific business scenarios and is responsible for recording and
processing business data. The supervision chain, on the other
hand, focuses on regulatory functions, ensuring the immutability
and traceability of attack data and the parameters of the model.
The business chain needs to meet regulatory requirements and
connect with the supervision chain to achieve business compliance.The supervision chain is also related to IoT devices. Data
generated by IoT devices is processed by the business chain
and is also a potential target for DDoS attacks. By regulating
the data of the business chain, the supervision chain indirectly
ensures the security of IoT device data, guards against DDoS
attacks on IoT devices, and ensures that IoT devices operate in a secure environment.In addition, the supervision chain
provides a reliable data-sharing and verification platform for
DDoS detection. Through technologies such as smart contracts,
it enables the automatic verification and sharing of attack data

908

that has been detected, thereby enhancing the accuracy and
timeliness of DDoS detection and providing strong support for
the implementation of defense measures.
C. Introduction to This Work
In the current blockchain and federated learning (FL)
integrated architecture, the absence of real-time and reliable
data-sharing mechanisms between business chains restricts detection systems to local traffic monitoring. This makes identifying global DDoS attack patterns difficult, reducing detection
accuracy and timeliness, and increasing false positives and negatives. Data isolation between chains also hinders distributed
collaborative defense, as attackers can exploit information silos
for cross-chain attacks. The distributed nature of blockchain
networks diversifies attack paths, allowing attackers to exploit
consensus mechanism and smart contract vulnerabilities for
complex attacks that bypass traditional defenses. This further
complicates global attack pattern identification. Additionally,
conducting business processes and security monitoring on the
same blockchain limits system flexibility and results in suboptimal security performance. The significant differences in data
formats and structures between IoT business chains cause inconsistent feature extraction, affecting detection model accuracy
and generalization ability.
To address these issues, this paper proposes combining DAGstructured blockchain with federated learning for DDoS attack detection in IoT business chain networks. DAG-structured
blockchains offer high throughput and low latency, enabling
rapid recording of model parameters and attack events and
real-time sharing of model parameters and attack information.
Federated learning can integrate heterogeneous network traffic
information from different business blockchain networks for distributed detection while protecting the privacy of local network
traffic data. By using dynamic weight allocation and time decay
mechanisms, federated learning can improve detection accuracy
and model convergence speed. Therefore, this combination can
effectively address the challenges of DDoS attack detection
in blockchain networks and enhance the ability of blockchain
networks to resist DDoS threats.
The main contributions of this study are summarized as
follows:
1) We have conducted a comprehensive and in-depth investigation of DDoS attack detection methods in blockchain
networks, systematically summarized the widely adopted
technical means at present, and thoroughly analyzed the
key challenges and urgent problems currently faced in this
research area.
2) We propose a cross-chain supervision method called
BAFL, which is based on the DAG (Directed Acyclic
Graph) structure and employs a federated learning framework. This method analyzes heterogeneous network traffic
information from different business blockchain networks
and strictly protects the privacy of local network traffic data for each client node and the business chains
they supervise during the model training process. It also
utilizes smart contract technology to achieve automated
data verification and sharing within the supervision chain

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 13, 2026

based on the DAG structure. Given that DAG chains offer higher transaction throughput compared to traditional
blockchains, our method can reduce the latency of onchain data sharing and enable real-time sharing of model
parameters and attack cases among each client node.
3) We introduce a time decay mechanism for asynchronous
aggregation. When client nodes in federated learning
unexpectedly go offline due to crashes, this mechanism
reduces the impact of outdated model parameters on the
aggregation results, ensuring that the model training remains unaffected and thereby enhancing the scalability of
federated learning. Moreover, by leveraging blockchain
technology to record the update history of model parameters, we ensure the immutability and traceability of data.
When new clients join the federated learning training, they
can quickly synchronize with the latest model parameters
via the blockchain and thus participate in normal model
training.
4) To enhance the accuracy of the federated learning model
in DDoS detection, we have adopted a dynamic weight
assignment method. By assigning greater weights to nodes
with higher accuracy in each training round, we allow
models with better performance to have a larger proportion in the aggregation process. This approach not
only improves the accuracy of DDoS detection but also
reduces the number of rounds and time required for model
convergence.
The rest of this paper is organized as follows: Section II
presents DDoS detection methods in blockchain networks. Section III introduces the Challenges for DDoS attack detectionin
business blockchain networks. Section IV introduces the types
of DDoS attacks in blockchain networks. Section V describes
the system model and the details the scheme proposed in this
paper.In Section VI, we present experimental simulations. Finally, we conclude in Section VII. The structure of this paper is
illustrated in Fig. 1, and a detailed comparative analysis of the
related works is presented in Table I.

II. DDOS MITIGATION AND DETECTION METHODS IN
BLOCKCHAIN NETWORKS
A. Blockchain Technology-Based Mitigation Methods
Blockchain technology, with its characteristics of decentralization, immutability, and transparency, has demonstrated a
certain ability to mitigate Distributed Denial of Service (DDoS)
attacks. Through the recording and verification mechanisms of
the distributed ledger, blockchain can effectively identify and
block the propagation of malicious traffic, thereby reducing the
occupation and destruction of network resources by attacks.
Moreover, the consensus mechanism of blockchain can ensure
that nodes in the network reach a consistent identification and
response to attack behaviors, further enhancing the network’s
defensive capabilities [4], [5]. For example, several blockchainbased mitigation methods have been proposed, including decentralized Content Delivery Network(CDN) schemes [6], smart
contract-based attack information sharing [7], and blockchainSDN collaborative frameworks [8]. These methods leverage

LI et al.: DDoS ATTACK DETECTION IN BUSINESS BLOCKCHAIN NETWORKS: A REVIEW, FRAMEWORK, AND CHALLENGES

Fig. 1.

909

The structure of this paper.

blockchain’s inherent security features to enhance DDoS attack detection and mitigation. [9] systematically studied the
attack principles and defense strategies of blockchain from two
dimensions—blockchain hierarchical structure and attack association analysis—summarized blockchain attack clusters, and
constructed a relatively comprehensive distributed blockchain
security defense system.Several scholars have proposed DDoS
attack detection and mitigation schemes based on blockchain
and SDN. Co-IoT [10], on the other hand, utilizes SDN controllers to detect DDoS attacks in IoT devices and shares attack
information via Ethereum smart contracts to block malicious
traffic. The BloSS model is a collaborative threat informationsharing framework that integrates blockchain, smart contracts,
and software-defined networking (SDN). It utilizes IPFS to store
data and ensures data security through the use of blockchainbased hash values [11], [12], [13], [14], [15]. Additionally, the DefenseChain framework employs smart contracts to
detect and mitigate DDoS attacks, supporting dynamic strategy
updates and traffic redirection [16]. Other studies have explored
privacy-preserving mechanisms based on Bloom filters, systems
that encrypt IP lists using AES algorithms, and Ethereum-based
frameworks for verifying the integrity of IoT sensor data [17].
Although blockchain technology shows great potential in mitigating DDoS attacks, it still faces many challenges in the detection and defense of DDoS attacks, which limit its effectiveness.
Therefore, it is necessary to further enhance the DDoS attack
detection capabilities within blockchain networks. For example,
to maintain the consistency of model parameters across different
nodes, it is necessary to overcome the synchronization delay that
may be caused by the blockchain consensus mechanism, which

directly affects the efficiency of model updates. Moreover, after
detecting an attack, the system needs to take defensive measures
quickly, but communication latency and node response time in
distributed systems may hinder the timely implementation of
defensive measures.
B. Traditional Detection Methods
Traditional DDoS attack detection methods in blockchain networks mainly include machine learning-based techniques and
defense mechanisms that leverage blockchain characteristics.
Traditional methods include machine learning-based anomaly
detection [18], fee-based mempool optimization [19], and collaborative anomaly detection frameworks [20]. These methods leverage various algorithms and optimization strategies to
enhance detection accuracy and efficiency. [21]analyzes the
behavior of the Ethereum network under low-cost DDoS
attacks and proposes using machine learning techniques, such
as decision trees and random forests, to detect such attacks.
These approach can effectively identify DDoS attacks and other
abnormal behaviors, and further determine the type of attack
through clustering analysis. Some research focus on the issue
of DDoS attack detection in Blockchain-IoT systems and propose distributed detection frameworks based on fog computing
and machine learning. [22] presents a distributed framework
that integrates IPFS and optimized feature selection, employing
Random Forest (RF) and XGBoost algorithms, and is suitable for smart contract-based Blockchain-IoT systems. [23] is
based on heterogeneous ensemble learning (AdaBoost and Random Forest) and virtual-reality parallel blockchain technology,

910

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 13, 2026

TABLE I
A COMPARISON OF RELATED WORKS

optimizing detection performance for DDoS attack detection
in blockchain networks. [24] designs a fog computing-based
distributed intrusion detection system, using RF and XGBoost
algorithms for distributed detection, emphasizing low latency
and efficient detection, and is suitable for Blockchain-IoT

networks. Although these traditional methods can detect and
mitigate DDoS attacks to some extent, they usually rely on specific network features or the performance of machine learning
models, and may need further optimization and improvement
when facing complex attack scenarios.

LI et al.: DDoS ATTACK DETECTION IN BUSINESS BLOCKCHAIN NETWORKS: A REVIEW, FRAMEWORK, AND CHALLENGES

911

TABLE I
(CONTINUED)

These methods have achieved certain effects in early attack
detection. However, in the complex blockchain network environment, their accuracy and real-time performance are limited.
First, attackers can exploit the blockchain consensus mechanism
to transmit redundant data, and hide DDoS attack traffic in
redundant P2P traffic through protocol obfuscation or mutation flooding mechanisms, reducing the accuracy of statistical

detection methods. Second, the consensus mechanism in
blockchain processes the traffic load information sent by all
miner nodes. Attackers can encapsulate and transmit rumorbased DDoS attack traffic containing disguised load information [5], further reducing the accuracy of statistical detection
methods [20]. Moreover, these methods may face performance
bottlenecks when dealing with high-dimensional data. On the

912

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 13, 2026

TABLE I
(CONTINUED)

one hand, the blockchain network layer has various consensus
mechanisms (such as PoW, PoS, DPoS, Byzantine fault tolerance, etc.), and the diversity of underlying traffic protocols
(such as RLPx, GHOST, Gossip, DEVp2p, Strata, Gnutella, etc.)
increases the dimensionality of non-linear features of traffic data
and the complexity of classification output of DDoS detection
models. This weakens the model’s generalization ability for
DDoS traffic. What’s more, the characteristics of rumor-based

attack traffic in the blockchain network layer are very similar to
those of normal network traffic, making it difficult to distinguish
the core features of mixed DDoS attack traffic through machine
learning methods.
C. Deep Learning- Based Detection Methods
Deep learning demonstrates significant advantages in detecting DDoS attacks due to its powerful capability of extracting

LI et al.: DDoS ATTACK DETECTION IN BUSINESS BLOCKCHAIN NETWORKS: A REVIEW, FRAMEWORK, AND CHALLENGES

913

TABLE I
(CONTINUED)

high-dimensional features. It can automatically identify subtle
patterns and features associated with attacks from complex
network traffic data, thereby enabling more accurate attack
detection and classification [25], [26]. [27]proposes a deeplearning-based method for detecting DDoS attacks in bitcoin
ecosystem by collecting blocks and transaction data from the

Bitcoin network, extracting statistical features, reducing feature
dimensions using Principal Component Analysis (PCA), and
ultimately predicting and detecting DDoS attacks with a MultiLayer Perceptron (MLP) neural network.A blockchain-based
DDoS mitigation method is proposed in [28], which reduces
signaling complexity and enables multiple autonomous systems

914

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 13, 2026

TABLE I
(CONTINUED)

to share hardware resources and defense capabilities. It also
integrates a deep learning DDoS detection system to identify
and block only the specific malicious traffic, instead of blocking
all traffic to the victim. In addition, in the field of AI detection
of DDoS attacks, current research and practice tend to adopt
centralized training and detection strategies. A DDoS attack
detection method based on a cross-multi-layer convolutional

neural network is proposed in [29], targeting DDoS attacks in
the blockchain network layer. The method extracts robust features of attack traffic through cross-layer convolution operations
with L2 regularization. It employs a stacked sparse autoencoder
based on Kullback-Leibler divergence for feature encoding to
reduce redundancy and prevent overfitting. Moreover, it optimizes model parameters using an improved stochastic gradient

LI et al.: DDoS ATTACK DETECTION IN BUSINESS BLOCKCHAIN NETWORKS: A REVIEW, FRAMEWORK, AND CHALLENGES

descent (ISGD) algorithm to accelerate convergence.However,
these centralized approach has several limitations in the context
of blockchain networks.
Specifically, the limited computing resources of centralized
detection organizations make it difficult to process large-scale
network traffic data quickly and efficiently, which can lead to
insufficient response speed to attacks. A centralized approach
can also raise the risk of privacy breaches during the transmission of network traffic, as a large amount of data needs to be
transferred across the network, increasing the possibility of data
interception and abuse.

915

central server resources, mainly because resource-constrained
edge devices cannot provide sufficient computing and storage
capabilities to support large-scale model aggregation and optimization. Second, the failure of the central server may lead to the
interruption of collaborative training, which in turn affects the
stability and reliability of the entire federated learning system.
In addition, as the number of participating devices increases,
the scalability of the system and communication bottlenecks
are becoming more and more prominent. These problems not
only increase communication overhead but also may lead to
a significant increase in training delays, thus posing a severe
challenge to real-time performance and efficiency.

D. Privacy-Preserving Detection Methods
At present, in the field of network attack detection, the
research of privacy protection methods has made remarkable
progress. With the rapid development of network technology
and the increasing awareness of data privacy, how to protect
user privacy while detecting network attacks has become an
urgent problem to be solved. In recent years, researchers have
proposed a variety of privacy protection methods to address this
challenge.Specific methods include vehicular network security
frameworks combining blockchain and deep learning [30], federated learning-based anomaly detection [31], and blockchainenabled federated deep learning frameworks [32]. These methods enhance privacy protection and detection performance by
integrating advanced cryptographic and machine learning techniques. Meanwhile, [33] also proposed the PEFL framework,
which employs perturbation encoding and long short-term memory autoencoders to protect privacy and designs the FedGRU algorithm for intrusion detection. [34] proposed the P2TIF framework to protect confidential information in IIoT environments
and identify cyber threats. It includes a blockchain module to
ensure secure communication of data and a deep learning module
that uses DVAE technology to resist inference attacks, followed
by threat detection using A-DGRNN.
In recent years, IDS based on federated learning (FL) have
attracted widespread attention [35]. FL, as a distributed machine
learning approach, eliminates the need for sharing data samples
and emphasizes data heterogeneity, availability, and privacy protection while reducing model bias, making it a highly promising
solution for IIoT [36]. FL also provides a distributed framework that ensures privacy protection and promotes collaboration
among multiple parties, enabling iterative training of machine
learning models for IoT applications.
A blockchain-based DDoS attack detection framework using FL is proposed in [37]. It detects DDoS attacks in a distributed environment through data preprocessing (including data
validation, feature selection, and normalization), local model
training (using LSTM models and the Adam optimization algorithm), and model aggregation (employing centralized or
distributed federated learning techniques). This framework aims
to improve detection efficiency and accuracy while adapting to
the distributed nature of blockchain networks.
However, these methods are facing several challenges in
practical applications. First, in the process of detecting DDoS
attacks on blockchain networks, it is not easy to find suitable

E. Blockchain Technology-Based Detection Methods
DDoS detection methods integrated with blockchain technology are gradually becoming a research direction.The decentralized and tamper-proof characteristics of blockchain provide new
ideas for attack detection. For instance, blockchain-based smart
contracts can establish a trust mechanism among distributed
detection nodes, thereby enhancing the robustness of detection.
In addition, blockchain technology can also be utilized to store
attack features and historical data.For example [38] further
discusses the application of blockchain in IoT, safeguarding
device data through hash values and timestamps, and enabling
the recovery to a secure state after network intrusions. [39] proposed a blockchain-based Link-Flooding Attack(LFA) detection
scheme, which deploys blockchain technology on routers and
servers within and around the protected area to record and share
traceroute information, thereby achieving efficient detection of
LFA.
Current researchers have proposed various approaches that
integrate blockchain and machine learning techniques for detecting and defending against DDoS attacks. On one hand, traditional machine learning methods such as K-Nearest Neighbors
(KNN), decision trees, and random forests have been demonstrated to effectively detect DDoS attacks [40]. Blockchain technology is utilized for securely storing blacklisted IP addresses,
and smart contracts are employed to automatically block and
unblock attack traffic. On the other hand, deep learning models
like LSTM are applied to analyze network traffic from IoT edge
devices, combining blockchain technology to achieve mechanisms for attack detection and defense [41]. Researchers in [42]
have proposed a blockchain-based distributed machine learning
framework that leverages collaboration among edge nodes and
incentive mechanisms through smart contracts to enhance the
efficiency of DDoS attack detection and model optimization
capabilities. [43] introduces a DDoS detection framework
integrating blockchain, smart contracts, and fuzzy neural networks. It protects privacy by hosting collaborators on private
blockchains and avoids data sharing among them. The fuzzy
neural network within the smart contract detects abnormal data,
and the results are uploaded to a public blockchain for access by
all collaborators, demonstrating high detection accuracy and recall rates. [45] presents a blockchain-supported adaptive DDoS
detection and classification method. By integrating multiple
deep learning models (GRU, CNN, LSTM, DNN, and SVM) and

916

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 13, 2026

introducing a dynamic weight adjustment mechanism, it significantly enhances the performance of DDoS attack detection and
classification. [44] proposes a blockchain-supported SoftwareDefined Networking (SDN) framework (BSDN-HMTD). It employs deep learning techniques to detect DDoS attacks and
strengthens network security and robustness through user authentication, flow validation, and dynamic Moving Target Defense (MTD) techniques.
However, in distributed systems such as blockchain networks,
although the integration of blockchain and machine learning
shows great potential in detecting DDoS attacks, it also faces
many challenges. On the one hand, the transaction processing
speed and storage capacity of blockchain are limited. In the
scenario of high-traffic DDoS attacks, it may not be able to
process and store a large amount of attack data in time, thereby
increasing detection latency. On the other hand, machine learning models need to be updated regularly to adapt to new attack
patterns. In distributed systems, how to efficiently update and
synchronize model parameters is an urgent problem to be solved.
In addition, real-time detection of DDoS attacks requires the
system to respond quickly, but the transaction confirmation time
and data synchronization time of blockchain may have a negative
impact on the system’s real-time performance.

III. CHALLENGES FOR DDOS ATTACK DETECTION IN
BUSINESS BLOCKCHAIN NETWORKS
A. Insufficient Data Monitoring Coverage
1) The Decentralization Dilemma of DDoS Attack Detection
in Blockchain Networks: In blockchain networks, the distributed
architecture, while offering the advantages of decentralization
and tamper resistance, also presents significant challenges for the
detection of DDoS attacks. Given the extensive and independent
distribution of nodes within blockchain networks, malicious traffic can easily be concealed within legitimate network flows, making it extremely difficult to distinguish between malevolent and
benign traffic. This obfuscation not only increases the complexity of detection but also leads to a higher rate of false positives,
thereby compromising the accuracy and reliability of detection
systems. Moreover, the decentralized nature of blockchain networks further restricts the application of traditional centralized
detection methods. In a decentralized environment, the absence
of a unified control center to coordinate and implement detection strategies renders traditional single-point-based detection
technologies inapplicable to blockchain networks. For instance,
attackers can exploit the anonymity of blockchain nodes to
launch attacks simultaneously from multiple nodes, thereby
concealing their true identities and attack trajectories. This
anonymity significantly diminishes the effectiveness of traditional tracking and identification methods when confronting
DDoS attacks in blockchain networks, making it difficult to
accurately locate the attack sources and implement effective
defensive measures. Therefore, designing efficient, accurate,
and adaptable DDoS attack detection mechanisms within the
distributed environment of blockchain networks has become an
urgent issue in the field of blockchain security research.

2) Non-IID Data Distribution and Data Heterogeneity: In
blockchain networks, data typically exhibit Non-IID (nonindependent and identically distributed) characteristics, with
significant differences in the data distributions across various
nodes. This data distribution characteristic poses substantial
challenges for traditional machine learning models based on
centralized training, as they often assume that data are IID.
As a result, the generalization capability of detection models is
compromised. For example, in blockchain networks, different
nodes may process different types of transactions or traffic,
leading to increased diversity in attack features.
The data distribution characteristics in blockchain networks
show significant Non-IID features, which pose severe challenges
to traditional machine learning models. Specifically, there are
considerable differences in the data distributions across different
nodes. These differences are not only reflected in the volume
of data but also in the type, structure, and feature distribution
of the data. For instance, some nodes may primarily handle
high-frequency transaction data, while others may focus on
smart contract execution or cross-chain interactions. This diverse data distribution makes it difficult for machine learning
models based on centralized training to adapt effectively, as
these models typically assume that data are IID and thus fail
to fully account for data heterogeneity and complexity during
the training process.
Moreover, the Non-IID data distribution characteristic further
weakens the generalization capability of detection models. In
blockchain networks, different nodes may face different types
of attacks. For example, some nodes may be more susceptible
to DDoS attacks, while others may face the risk of smart contract vulnerability exploitation. The diversity of attack features
increases the complexity of detection models, making it difficult
for a single centralized model to capture all potential attack
patterns. For instance, an attack feature present on one node
may not exist on another node or may appear in a different form.
This heterogeneity in data and attack features requires detection
models to have stronger adaptability and generalization capability in order to maintain high accuracy and low false-positive
rates across different data distributions and attack scenarios.
Therefore, designing machine learning models that can adapt to
Non-IID data distributions within the distributed environment
of blockchain networks has become an important research topic
in the field of blockchain security. This not only requires the
development of new algorithms to handle data heterogeneity but
also necessitates exploring how to achieve collaborative training
and optimization of models within a distributed architecture,
thereby enhancing the overall performance and reliability of
detection models.
B. The Real-Time and Scalability Challenges of DDoS
Detection in Large-Scale Blockchain Networks
With the continuous expansion of the business chain network
scale, DDoS attack detection systems are facing increasingly
stringent requirements for real-time performance and scalability. In large-scale network environments, the volume of traffic
data grows exponentially, and detection models must efficiently

LI et al.: DDoS ATTACK DETECTION IN BUSINESS BLOCKCHAIN NETWORKS: A REVIEW, FRAMEWORK, AND CHALLENGES

process and analyze vast amounts of data within an extremely
short period of time to minimize detection latency and ensure
that attacks are identified and responded to in a timely manner.
Meanwhile, the dynamic nature of the supervision chain, such as
the frequent addition and exit of nodes, further complicates the
detection system and poses significant challenges to its real-time
performance and adaptability. In the actual deployment and
application of supervision chains, the performance bottlenecks
of blockchain technology have become a key obstacle to their
large-scale application.
Specifically, limitations in transaction processing speed and
storage capacity severely restrict the operational efficiency and
scalability of supervision chain. On the one hand, although the
consensus mechanism of blockchain ensures the security and
immutability of data, it often comes at the cost of transaction processing speed. For example, when dealing with high-throughput
network traffic data, the low transaction speed of blockchain can
lead to data backlogs, preventing real-time attack detection and
recording, thereby affecting the timeliness of detection. On the
other hand, as the volume of regulatory data continues to rise,
the storage capacity of blockchain is also reaching its limits.
Distributed ledgers need to store large amounts of historical
data, which not only increases the storage burden on nodes but
also may cause network congestion and synchronization delays,
thereby affecting the overall system’s operational efficiency.
Therefore, how to optimize the performance of blockchain while
retaining its security and decentralization characteristics to meet
the needs of large-scale applications has become one of the core
issues that urgently need to be solved in the current research
field of supervision chain.

917

IV. ATTACK TYPE
This section introduces the types of DDoS attacks in
blockchain networks.

A. DDoS Attack in Blockchain Data Layer
DDoS attacks on the blockchain data layer are malicious
activities that interfere with data storage and integrity by sending
a large number of invalid or low-value transactions, injecting
false data, and generating invalid blocks. These actions consume the storage and computing resources of nodes, leading to
decreased network performance and difficulties in confirming
normal transactions.

B. DDoS Attack in Blockchain Network Layer
The Blockchain Network Layer DDoS attack model focuses
on the blockchain network layer, specifically using blockchain’s
P2P (peer-to-peer) architecture for attacks. Attackers exploit
vulnerabilities in P2P file sharing systems to access targeted
objects through large numbers of normal users, or to disconnect some nodes from each other in an anonymous P2P network, thereby compromising the integrity and availability of
the blockchain networks. This kind of attacks can cause the
blockchain networks to fork, delay or fail transactions, affecting
the decentralized nature of the blockchain and the trust mechanism.

C. DDoS Attacks in Consensus Layer
C. The Tradeoff Between Privacy and Supervision
The application of the supervision chain in network security needs to not only meet the regulatory authorities’ requirements for data transparency and traceability but also protect
the data privacy of network participants. However, finding a
balance between these two aspects is a significant challenge
faced by the supervision chain. On the one hand, regulatory
authorities need to obtain sufficient information to identify and
prevent cyberattacks, ensuring the safety and stability of the network environment. For example, when detecting DDoS attacks,
the supervision chain needs to record detailed characteristics of
the attack traffic for tracing and analysis. On the other hand, the
data privacy of network participants must not be overlooked.
Although blockchain technology provides a certain level of privacy protection through encryption mechanisms, excessive data
sharing may lead to the leakage of users’ sensitive information
in some cases. Therefore, designing mechanisms that can satisfy
regulatory needs while protecting privacy is an urgent issue that
needs to be addressed in the practical application of the supervision chain. This requires not only technological innovation,
such as the application of privacy-preserving technologies like
zero-knowledge proofs and homomorphic encryption, but also
in-depth exploration at the legal and policy levels to ensure the
compliance and acceptability of the supervision chain.

DDoS attacks at the consensus layer of blockchain typically
occur by manipulating the consensus mechanism. Attackers may
control a large number of nodes (e.g., by launching a 51% attack)
or generate a large number of invalid blocks and transactions,
thereby preventing the network from reaching consensus. This
can lead to delayed transaction confirmations or even transaction
rollbacks. Such an attack not only disrupts the stability and
consistency of the network but also may affect the decentralized
nature of the entire blockchain network, enabling attackers to
manipulate transaction records or prevent the confirmation of
legitimate transactions.

D. DDoS Attacks in Application Layer
DDoS attacks at the application layer of blockchain typically occur by launching a large number of requests against
blockchain application programming interfaces (APIs) or smart
contracts. Attackers exploit the openness and accessibility of
these interfaces to send a vast number of malicious requests,
which consume the computational resources and bandwidth
of the application layer, leading to slow service responses or
even system crashes. This type of attack not only increases
the execution latency of smart contracts but also may prevent
users from accessing blockchain applications normally, thereby
severely affecting user experience and application availability.

918

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 13, 2026

E. DDoS Attacks in Protocol Layer
DDoS attacks at the protocol layer of blockchain typically
exploit vulnerabilities or weaknesses in the blockchain protocol.
Attackers may send a large number of maliciously constructed
protocol messages to interrupt or disrupt communication between nodes, thereby undermining the normal synchronization
and data transmission of the network. For example, attackers can
exploit vulnerabilities in the P2P protocol to send a large number
of forged node discovery or block propagation requests. When
nodes process these invalid requests, they consume a significant
amount of resources, which may ultimately prevent them from
functioning properly and even lead to network partitioning. This
type of attack directly affects the underlying communication
mechanism of the blockchain network, posing a threat to the
stability and security of the entire network.
F. DDoS Attacks in Node Layer
DDoS attacks at the node layer of blockchain typically occur
by focusing attacks on specific nodes. Attackers may overwhelm
the target nodes with massive malicious traffic or generate a large
number of spurious requests, thereby exhausting the resources
of the target nodes (such as CPU, memory, and bandwidth).
This prevents the nodes from processing legitimate transactions
or communicating normally with other nodes. Such an attack
not only degrades the performance of the nodes but also may
cause them to crash or become isolated, thereby affecting the
decentralized nature and overall stability of the entire blockchain
network.
G. DDoS Attacks in Smart Contract
The DDoS attack model against smart contracts targets
blockchain-IoT systems based on smart contracts, specifically
exploiting the automated nature of smart contracts. Attackers
could exploit vulnerabilities in smart contracts or clog up the
network by sending a large number of illegal requests, making
it impossible for smart contracts to properly execute or process
legitimate transactions. Such attacks can result in the failure
of smart contract execution, affect the business processes of
blockchain-IoT systems, and may even lead to financial losses.
V. METHOD
In this part, we will introduce the following aspects: the design
of the model architecture as well as the workflow, network traffic
preprocessing technology and the training method of the model.
A. Model Architecture
Our method consists of several entities: supervision chain,
clients, and business network. In our federated learning framework, model aggregation is performed by supervision chain,
which includes a leader node and several follower nodes. Follower nodes establish communication connections with client.
clients are not only used to upload and update parameters during
model training, but also used to analyze network traffic generated
by the business networks during model detection and record it

on the blockchain as transactions. The leader node is responsible
for verifying transactions and proposing new blocks. And help
maintain the consistency of model parameters across nodes of
the Directed Acyclic Graph (DAG) supervision chain, coordinating parameter aggregation and model updates throughout the
federated learning process. Leveraging the high throughput and
efficiency inherent to DAG-structured blockchains, the supervision chain is capable of rapidly recording model parameters and
vast numbers of detected DDoS attack events. This enables a
more agile and responsive detection mechanism, enhancing the
overall security and robustness of the system.
1) Workflow of DDoS Attack Detection Model: The workflow of this model is shown in Fig. 2:
i) Each client in business chain have a labeled data set and a
set of business blockchain nodes that it monitors.
ii) Each client in business chain uses local datasets for training.
iii) Each client in business chain completes the current round
of training and obtains the local model data.
iv) The client in business chain that completes this training
round will upload the local model data to the expected follower
node on the supervision chain, and the follower node will record
the model parameters as transactions on the supervision chain
through “Data Upload”smart contract.
v) The leader node obtains the aggregation model through our
proposed aggregation algorithm by reading and analyzing the
model parameters of the clients node received on the supervision
chain. The leader node records the aggregated model parameters
on the DAG ledger through a “Data Upload” smart contract and
shares them with the follower nodes. You can see the details in
Algorithm 1.
vi) The followers node reads the aggregated model parameters
through the “Data Query” smart contract from DAG ledger,
sends them to the corresponding clients, and updates the model
parameters of the clients.
vii) After multiple rounds of training, the classification accuracy of the model reached a reasonable standard, and the
model training was completed. Each client node will collect
the network traffic of its assigned business blockchain nodes
through the traffic collection device, and analyze these traffic to
detect potential DDoS attacks.
viii) The client saves the latest network traffic check result.
This information is not only used to update local training
datasets, It is also uploaded via the client node to its corresponding follower node on the DAG blockchain and stored on the
DAG chain as transactions through smart contracts called “data
uploads,” sharing information on discovered attack behavior
with other nodes.
Follower nodes in the supervision chain are responsible for
updating model parameters during the federated learning process. They record the network traffic generated by the business
blockchain nodes as transactions on the supervision chain ledger.
These follower nodes interact with the supervision chain leader
and client nodes in the business chain. They obtain locally
trained model parameters from the client nodes in the business
chain and upload them to the leader node, which aggregates
these parameters using the proposed asynchronous federated
learning algorithm. The follower nodes ensure that only model

LI et al.: DDoS ATTACK DETECTION IN BUSINESS BLOCKCHAIN NETWORKS: A REVIEW, FRAMEWORK, AND CHALLENGES

Fig. 2.

919

Working process of BAFL DDoS attack detection system.

parameters are shared, not the raw network traffic data from
the business chains, thereby protecting the data privacy of the
business chains.
Client nodes corresponding to the business chain monitor and
collect network traffic data from the business blockchain nodes.
They preprocess this data and use it to train local models. These
client nodes send their locally trained model parameters to the
supervision chain for aggregation and further processing. Meanwhile, they also receive updated global model parameters from
the supervision chain to continue training in subsequent rounds.
After training is completed, the client nodes corresponding to the
business chain act as regulators to conduct security monitoring
of the business chains they oversee.
Our aggregation node of federated learning consist of a DAG
structured blockchain, and the implementation of consensus
relies on the process of selecting and confirming transactions
among the nodes in the DAG network, where the tips transaction
block refers to the most recent collection of transactions that have
not yet been confirmed by subsequent transactions. Nodes reach
a consensus by selecting the Tips trading block with the highest
credibility that satisfies a particular selection algorithm, such as
the highest transaction fees or the greatest network influence,
and these choices reflect a common recognition of transaction order and validity in the network. As more transactions
join, they reference these Tips trading blocks, gradually building an interdependent network structure to achieve a common

understanding of the history and current status of the transaction.
This graph-based structure allows transactions to be confirmed
in a non-linear manner, improving the throughput of the system
and enabling a decentralized consensus mechanism through the
joint selection and confirmation of Tips trading blocks by nodes
in the network.
The DAG structure supports the parallel confirmation of multiple transactions, effectively avoiding the sequential processing
bottleneck in traditional blockchains. Its throughput increases
linearly with the number of nodes, making it suitable for largescale networks. Meanwhile, DAG’s efficient transaction recording capability, such as processing thousands of transactions per
second, reduces the latency of uploading model parameters and
attack events to the blockchain, thereby supporting real-time
detection and response.
In the process of model aggregation, the aggregator determines the weight of the parameter in the model aggregation
according to the old and new degree of the parameter transmitted
by the client and the accuracy rate of the client model. In the
process of the first aggregation, the aggregator first aggregates
the collected client parameters to obtain the pre-aggregation
model of the round and its accuracy, and then compares the
model accuracy of each client with it. When the accuracy
of the pre-aggregation model is high, the parameters of the
pre-aggregation model dominate; otherwise, the parameters of
the client model dominate. As the result, the older the client

920

model parameters, the smaller the proportion in the aggregation
process, we implemented this by introducing a time factor. This
is described in detail in the part C of Section V.
The time factor indicates that in the maximum experimental
time range, the longer the time delay, the smaller the time factor,
resulting in a smaller model proportion. If the delay exceeds the
maximum delay range, the client model can be ignored.
During the training of the DDoS attack detection model,
clients in federated learning only upload model parameters to the
server, without transmitting raw training data. This mechanism
ensures the privacy of the network traffic data in business chains,
as different business chains are monitored by separate clients and
data between chains are isolated from each other. Moreover, we
have automated the processes of data verification and sharing
through the use of smart contracts, thereby further enhancing the
security and trustworthiness of the data. In the actual deployment
scenarios of supervision chains, smart contracts are designed to
permit only specific nodes to access and process data. Under
this architecture, only regulatory authorities and certain business
chain nodes are able to obtain certain sensitive data, thereby realizing a precise and meticulous access control mechanism. For
example, in the IoT environment, the data generated by devices
may contain users’ private information. Through blockchain
technology and smart contracts, the privacy of this data can
be ensured during transmission and processing, preventing data
leakage and misuse.
In the actual deployment scenarios of supervision chains,
smart contracts are designed to permit only specific nodes to
access and process data. Under this architecture, only regulatory
authorities and certain business chain nodes are able to obtain
certain sensitive data, thereby realizing a precise and meticulous
access control mechanism.
This approach of combining the DAG structure with federated
learning not only enhances the performance and efficiency of
BAFL but also strengthens data privacy protection and model robustness, making it a powerful solution for protecting blockchain
networks from DDoS attacks. It is particularly effective in
processing large-scale, dynamically changing network data,
providing high-precision, low-latency detection results. Firstly,
from the perspective of data privacy protection, federated learning effectively safeguards data privacy by sharing only model
parameters instead of raw data. The supervision chain of the
DAG structure further ensures the immutability and traceability
of these parameters, thereby enhancing the credibility of data
privacy protection. Secondly, in terms of efficient data sharing
and synchronization, the efficiency of the DAG structure enables
rapid uploading and synchronization of model parameters. This
is especially crucial for handling high-traffic network data, as
the DAG structure can process thousands of transactions per
second, significantly reducing the latency of data uploading
and synchronization. Moreover, regarding model robustness and
scalability, the asynchronous nature of federated learning makes
the model training process more flexible, better able to handle
client failures and network latency. The supervision chain of the
DAG structure ensures real-time updating and sharing of model
parameters, thereby enhancing model robustness and scalability.
Finally, in the aspect of real-time detection and response, this

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 13, 2026

Fig. 3.

The process of data preprocessing.

combination enables BAFL to quickly update and synchronize
model parameters, ensuring the timeliness of detection results.
Thus, when dealing with dynamically changing network traffic
data, it can more promptly respond to potential DDoS attacks.
B. Real-Time Network Traffic Preprocessing
Network traffic comprises data transfers between endpoints.
Because the communication channel is shared, packets from
different data flows are multiplexed, or split for transmission, for
the purpose of transmission. This suggests that handling traffic
for a live presentation to an NIDS is quite different from handling
a static dataset that contains all of the flows [46].
We use tool designed in paper [46] to develop our online
detection, which divides the traffic flows into sub-flows based on
time frames and transforms them into array-like data structures
taken from network traffic traces of a dataset.
Network traffic consists of data flows between ends,as shown
in Fig. 3. Due to the shared nature of communication links,
packets from different data streams are multiplexed, resulting in
packets from the same data stream being separated for transmission. This means that real-time traffic is being processed.
In the feature extraction stage,given a traffic tracking file from
the data set and a predefined time window with a length of t
seconds, collect all packets (pk1, pk2, . . .) from the file with
the capture time between t0, the capture time of the first packet,
and time[t0 + t]. The algorithm extracts f attributes from each
packet.
In the data preprocessing stage,the attributes of packets belonging to the same bidirectional communication stream are
grouped in chronological order to form a matrix of shape width
and length [n, f ], where f is the number of features and n is
the maximum number of packets collected for each stream in
the time window during the parsing process. Streams greater
than n are truncated, while shorter streams are filled with zeros
at the end of the next stage after normalization. In the time
window [t0 + t, t0 + 2t], etc.The same operation is repeated for
the packet until the end of the file. The output of this process can
be viewed as a two-dimensional array of samples E. A row in
the array represents a sample of the packet captured in the same

LI et al.: DDoS ATTACK DETECTION IN BUSINESS BLOCKCHAIN NETWORKS: A REVIEW, FRAMEWORK, AND CHALLENGES

Fig. 4.

921

BAFL training procedure.

time window, while a column represents a sample of the packet
belonging to the same bidirectional stream.
In the normalization and filling stage, each attribute value is
normalized to a scale [0,1], and the sample is filled with zero,
so the fixed length of each sample is n, because a sample with a
fixed length is the requirement that CNN can learn on a complete
sample set. Each non-empty element of array E is a compact
graphical representation of a sample. Within each E element,
the colored rows are the packet in the form of f standardized
attributes, while the white rows represent zero padding.
Each E is labeled by matching its stream identifier id with the
label provided by the original dataset. This also means that the
value of the label is constant along each column of the array E.
In the input layer,each traffic stream is reshaped in seconds
into a two-dimensional matrix of packet characteristics, enabling
CNNS to learn correlations between packets of the same stream.
This first layer takes a flow flow represented by a matrix of size
n × f as the input to the neural network.
Each input matrix is operated by a convolution layer with k
convolution nuclei, each of size h × f , where h is the length of
each convolution kernel. Our neural network model is trained to
classify network traffic.
C. Model Training
We randomly and evenly distributed the preprocessed data to
each client p, allowing local data on different clients to cover
different feature spaces or categories. Clients with higher accuracy may have learned more generalizable features or their local
data distributions may be closer to the global task requirements.
By assigning higher weights to models with higher accuracy and
introducing a temporal factor to reduce the aggregation weights
of outdated models, we can accelerate the convergence of the
global model and potentially enhance its performance across the
overall data distribution.The asynchronous federated learning
algorithm based on accuracy is shown in Algorithm 1.
As for each client p, we divide the collected attack network
traffic data into training set and test set.After receiving the data,
the client uses the CNN model for training. The trained client
sends the model parameters w, model accuracy acc, and losses

to its corresponding follower node, which packages this information into the transaction and uploals it to the DAG blockchain
for data sharing.
The leader node reads the model parameters of follower nodes
that have completed the current theoretical training from the
DAG chain. According to the accuracy of the client model
corresponding to each follower node, the leader node weights
the parameters so that the model parameters of the client with
higher training accuracy account for a larger proportion in the
aggregation. After the leader node aggregates these parameters,
it packages the aggregated parameters w into a transaction
and publishes it on the DAG blockchain, sharing the model
parameter information with the follower nodes, who send these
parameters to the client for the next round of training.The BAFL
training procedure is shown in Fig. 4.
1) Local Model Training: The training sample is evenly distributed to each client, and the number of client is P . After
receiving the training samples sent by the training data memory,
we randomly divided the training samples into P parts and
gave them to each client. After each follower node receives the
training sample Dtp = (dk, np −1 , . . ., dk, np ), using the t round of
training assigned to its own data.
We collect real-time network traffic data from a blockchain
network, pre-process it, and apply it as input to our convolutional neural network (CNN) model to facilitate online attack
detection. Traffic data is divided into two categories: malicious
(DDoS attack) traffic and benign traffic. We aim to optimize the
CNN model to reduce complexity and computation time so that
the model can be effectively deployed on resource-constrained
devices. In order to achieve this goal, we design a lightweight
supervised learning system, the core of which is a well-designed
CNN for efficient attack detection.
The structure of our neural network is shown in Fig. 5:
Input layer: We build a spatial representation in which every
traffic stream is transformed into a two-dimensional packet
characteristic matrix in a matter of seconds. To make it possible
for the CNN to discover correlations between the same stream’s
packets. As a result, a flow stream represented by a matrix f
of size n × f is fed into this first layer. F is made up of n
distinct package vectors, therefore F = pkt1, . . ., pktn. where

922

Fig. 5.

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 13, 2026

The structure of our neural network.

each packet vector has a length of f = 11 features and pktn is
the n TH packet in a stream.
CNN layer: As shown in Fig. 5, each input matrix F is
operated by a convolution layer, in which the size of k filters
is h × f , and h is the length of each filter. In our model,
we set k = 64 to make the data features pass through multiple channels, so that the characteristics of DDoS attacks can
be extracted more comprehensively. Each filter, also known
as the kernel or sliding window, performs convolution with
step 1 to extract and learn local features that contain useful
information for detecting DDoS and benign flows. Each filter
generates an activation map of magnitude (n − h + 1) × k, such
that ak = ReLU (Conv(F )Wk , bk ), where Wk and bk are the
weight and bias parameters of the KTH filter learned during the
training phase. We add BatchNorm2d after the convolutional
layer of the convolutional neural network for data normalization
processing, so that the data will not cause unstable network
performance due to large data before Relu. We then use the
corrected linear activation function ReLU (x) = max0, x. All
activation graphs are stacked to create an activation matrix A of
size (n − h + 1) × k, which gives us A = [a1 |. . .|ak ].
Average pooling layer: We use an average pooling method
where we sample down the first dimension of A, which represents the time nature of the input. A pool of size m produces an output matrix of size ((n − h + 1)/m) × k containing the maximum m activation for each learning filter,
such that c0 = [avg1 |. . .|avgk ]. In this way, the dimensionality of the training data is reduced, the redundant information
is removed, the features are compressed, the network complexity is simplified, the computation is reduced, the memory consumption is reduced, and too much high-dimensional
information is avoided. c0 then flattens to generate a onedimensional feature vector v that will be input to the detection
layer.
Detection layer: v is input to a linear fully connected layer.
The main function of the Linear fully connected layer is to map
the feature space computed from the previous layer to the sample
label space. That is, the feature representation is integrated into
one value, which has the advantage of reducing the influence

of feature positions on classification results and improving the
robustness of the entire network. This output x is passed to the
S-type activation function such that σ(x) = 1/(1 + e−x ). This
limits activation to a value between 0 and 1, thus returning the
probability p ∈ [0, 1] that a given stream becomes a malicious
DDoS attack. If p > 0.5, the traffic is DDoS.Otherwise, the
traffic is benign.
When the local model is trained for the second time or more,
we optimize the parameters of the local model based on the local
model trained in the current round. Construction loss function
 np
t−1
l(yi , ŷp,i
) + Ω (fpt )
(1)
Lpt = i=1
It is minimized to represent the predicted value when the locally
trained model p trains the sample in the round of t training
After the training is completed, the parameters of CNN network
parameter will be sent to the server.Regularized term Ω(fpt )
controls model complexity and prevents overfitting and weight
decay.
2) Aggregation Process: After the local training model completes the rth round of training, clients send its rth round of
training parameters wrp and rth round of accuracy accpr to the
leader node to train the global model. The leader node uses
fedprox aggregation algorithm to get the preliminary aggregation parameters of round r wrp . We set the difference between
the time when the server receives the data from client p and the
time when client p sends the r round of model parameters to the
server as tpr , the longest waiting time of the server is maxt, and
the calculation formula of the time-weighted parameter of client
p ctpr is as follows

(1 − (tpr − maxt) /maxt) /100 + C, 0 < tpr < maxt
p
ctr =
0, otherwise
(2)
Here C is the adjustment parameter. The leader node then
recalculates the aggregate parameters by determining how accurate each client’s model parameter is compared to client’s
accuracy. When the accuracy of the client’s model is higher,
the model parameters of client will play a dominant role in
the adjustment process of the aggregation parameters, and the

LI et al.: DDoS ATTACK DETECTION IN BUSINESS BLOCKCHAIN NETWORKS: A REVIEW, FRAMEWORK, AND CHALLENGES

Algorithm 1: Asynchronous Federated Learning Algorithm
Based on Accuracy.
for each round r = l, 2,... do
Leader node executes:initialize wrp
get ctpr ←− tpr
for each client p, in parallel do
p
←− ClientU pdate(p, wrp ),calculate accpr+1
wr+1
if accpr > accpr+1 then
p
p
wr+1
= wrp × (1 − ctpr ) + wr+1
× ctpr
else
p
p
= wr+1
× (1 − ctpr ) + wrp × ctpr
wr+1
end if
end for
Calculate the aggregation parameters:
p
wr+1 ← FedProx all wr+1
Follower node update(p,wrp )://Executed on client k
for each local epoch do
batches ←−data split into batches
for Batch b In Batches do
wrp ←− wrp − η∇Lpt (wrp , b)
end for
end for
end for
return wrp , accpr ;

model parameters after the update of the r round clientp are
p
p
= wr+1
× (1 − ctpr ) + wrp × ctpr . On the contrary, when
wr+1
the aggregation model accuracy of the leader node is higher, the
aggregation model parameters of the leader node will dominate
the aggregation parameter adjustment process, and the model
p
= wrp ×
parameters after the r round client p update are wr+1
p
p
p
(1 − ctr ) + wr+1 × ctr . After calculating the new weighted
parameters of all client, perform the next aggregation to obtain
the final aggregation parameters and send them to supervision
chain.
Clients may encounter various faults or anomalies during the
model training process, such as operating system failures, memory overflows, and insufficient storage space. These technical
issues may cause clients to fail temporarily or permanently,
thereby affecting the continuity and stability of the federated
learning process. In addition, the uneven quality of network
connections between clients makes the inconsistency of data
transfer rates a key issue. Factors such as network latency, bandwidth limitations, and unstable connections may cause some
clients to be less efficient than others in sending or receiving
model updates. This instability of clients can lead to failures at
any time, preventing the aggregation model from obtaining the
latest parameter updates in a timely manner, which in turn affects
the real-time and accuracy of model training. Secondly, some
clients may achieve higher accuracy than the leading node during
training, while others do not. In this case, traditional aggregation
methods may mask the advantages of these high-performing
models.
To address these challenges, this study introduces a time decay
parameter and proposes an innovative method. This method

923

TABLE II
HYPERPARAMETER SETTING

effectively reduces the impact of outdated model parameters
on the current training process, thereby enabling asynchronous
federated learning. This strategy not only accelerates the speed
of model aggregation but also enhances the robustness of the
model training process. Even if some clients fail, model training
can still continue and can quickly integrate the latest parameter
updates from different clients, ensuring the continuity and efficiency of the training process and maintaining high quality and
efficiency. In addition, to fully leverage the high-performing follower nodes, our leader node performs a secondary adjustment
of the model parameters based on the accuracy of each client
after the initial aggregation in each round, further speeding up
the aggregation process.
VI. EXPERIMENT AND EVALUATION
In this study, our core objective was to conduct a comprehensive performance evaluation of our proposed BAFL approach.
Specifically, this evaluation aims to explore the performance of
the BAFL approach on several key dimensions.First, the accuracy of its global model in identifying DDoS attacks.Secondly,
its robustness is tested in the face of different proportions of node
failures.Thirdly, the convergence rate in the federated learning
process is evaluated. Finally, the scalability of the system when
processing large-scale data is evaluated. Through these comprehensive tests, we aim to gain a deeper understanding of the
effectiveness and potential of the BAFL approach in practical
applications.
Our model was trained on a personal computer configured
with 13th Gen Intel(R) Core(TM) i9-13900HX,and CUDA 11.6
version.The parameter Settings in this study are detailed in
Table II. All experimental results are based on the statistical
average of 10 independent repeated experiments.
This model is validated with normal blockchain network
traffic data and recent datasets CIC-DDoS2019 provided
by the Canadian Institute for Cybersecurity of the UNB,
Canada [47]. [47] consist of several days of network activity,
normal and malicious, including DDoS attacks. The dataset is
publicly available in the form of traffic traces in pcap format
including full packet payloads, plus supplementary text files containing the labels and statistical details for each traffic flow.The
attack types in CIC-DDoS2019 DDoS shown in Table III.
These datasets encompass both normal network traffic and
a variety of DDoS attack traffic, such as IRC-based botnet

924

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 13, 2026

TABLE III
CIC-DDOS2019 DDOS ATTACK TYPES

Fig. 6.
ods.

Accuracy and loss of our model BAFL compared to traditional methand diverse traffic features, are processed by time-window-based
division and merging, all of which contribute to the evident
heterogeneity of the data.
A. The Performance of the Global Model to Identify DDoS
Attacks

attacks and HTTP DDoS attacks utilizing LOIC and HOIC
tools. They also feature a diverse range of traffic characteristics spanning the network, transport, and application layers,
including packet length, protocol type, TCP flags, and window
size. These datasets exhibit non-independent and identically
distributed (non-i.i.d.) characteristics: attack traffic significantly
differs from normal traffic in terms of features (e.g., higher
packet rates and more concentrated IP address distributions in
attack traffic), and different types of DDoS attacks also possess
distinct traffic features (e.g., differences between network-layer
and application-layer attacks). Moreover, the datasets are divided into time windows, and the traffic features within each
window may vary due to the influence of network conditions,
user behavior, and attack activities.
When these non-i.i.d. datasets are distributed across different
clients, heterogeneity arises primarily due to the diversity of data
distributions, the variety of data features, and the imbalance of
data volumes. In the context of DDoS attack detection in service
chain networks, the significant differences in features (such as
packet rates and IP address distributions) between different types
of attack traffic and normal traffic contribute to the diversity of
data distributions. Additionally, variations in network environments across organizations, data collection time windows, and
the volume of data provided by each client further exacerbate the
diversity of data features and the imbalance of data volumes. The
datasets used in the paper, which include multiple attack types

Classification performance of BAFL models is measured in
Precision, recall rate and F1-score. In machine learning and
statistics, Precision, Recall, and F1-score are three important
metrics for evaluating the performance of classification models,
especially in binary classification problems. Here’s what each
means:
Loss function (loss): The loss function measures the difference between the model’s predicted value and the actual value. It
is an objective function in the process of model optimization and
is used to guide the adjustment of model parameters to minimize
prediction errors. Different machine learning tasks use different
loss functions, and our classification task uses cross entropy loss.
Accuracy (acc): Accuracy refers to the proportion of all
predictions in the model that are correct.
Precision: The accuracy rate refers to the proportion of the
positive class that the model predicts is actually positive.
Recall rate: The recall rate refers to the proportion of positive
class samples correctly identified by the model to all actual
positive class samples.
F1-score: The F1-score is a harmonic average of accuracy
and recall, and it tries to find a balance between the two metrics.
When the accuracy and recall rate are equal, the F1-score reaches
the maximum.
These metrics provide a comprehensive assessment of the
model’s performance, especially if the sample of positive and
negative categories is unbalanced.
In this part, we used Fedprox-BAFL, Fedavg-BAFL, Fedavg,
Fedprox and other methods to train the global model until
the model converged. Our model underwent 20 iteration of
aggregation during training. To evaluate the performance of
these methods, we compared their Acc and Loss values over
different iterations. The experiment was performed 10 times per
experiment through the collaborative participation of 20 clients
to ensure statistical significance of the results, and average
indicators are reported in this section.
As shown in Fig. 6 and Table IV, under the same number of
iterations, Fedprox-BAFL and Fedavg-BAFL models, through

LI et al.: DDoS ATTACK DETECTION IN BUSINESS BLOCKCHAIN NETWORKS: A REVIEW, FRAMEWORK, AND CHALLENGES

925

TABLE IV
MODEL PERFORMANCE COMPARISON

our quadratic aggregation algorithm, give greater weight to
the model parameters of clients with higher accuracy during
model aggregation, which makes our model more accurate than
FEDAVG and FEDPROX,showing higher accuracy and lower
losses. In particular, the acc of Fedprox-BAFL and FedavgBAFL models has reached convergence at the 8th and 9th
iterations, and the convergence time is 69.3 s and 92.05 s, respectively. Acc converges at the 18th and 19th iterations of Fedprox
and Fedavg, which are 184.583 s and 249.02 s, respectively.
Similarly, the loss values of Fedprox-BAFL and Fedavg-BAFL
models converged at the 8th and 9th polymerization, while
Fedprox and Fedavg converged at the 16th and 18th polymerization, respectively. Compared with FEDAVG and FEDPROX,
the improved model FedPROX-BAFL and FeDAVG-BAFL also
achieved higher scores in Precision, Recall and F1-score.
Further, considering that the data set contains multiple attack
types, Fedprox-BAFL method shows better performance than
Fedavg-BAFL in heterogeneous data detection. Specifically,
under the same number of iterations, Fedprox-BAFL method
not only has higher accuracy and lower loss, but also has faster
convergence of accuracy and loss value. These results show
that the Fedprox-BAFL method can effectively improve the
performance and convergence rate of the model when dealing
with data sets containing multiple attack types.
The above experiments show that BAFL employs a dynamic
weight allocation mechanism, assigning different weights based
on the detection accuracy of client models. Models with better
performance have a larger proportion in the aggregation process, thereby enhancing the accuracy of the global model.The
Fedprox-BAFL method can more effectively utilize the
parameters of high-precision models when dealing with complex
datasets containing various types of attacks, thereby enhancing
the overall performance of the model. Additionally, BAFL introduces a temporal decay factor, which reduces the impact of old
model parameters on the aggregation results. This enables the
model to quickly adapt to new data distributions and accelerates
the convergence process.When processing dynamically changing network traffic data, the temporal decay factor can ensure
that the model does not overly rely on old and potentially outdated parameters, thereby maintaining the real-time and accurate
nature of the model.
B. Robustness
In this study, we aim to evaluate the performance of the
proposed Fedprox-BAFL model in the face of node failure.
Specifically, we randomly suspended the training of some clients
to simulate mid-process client failures. We introduced random
node failures in the 2nd to 5th rounds of model training, and

Fig. 7.

Accuracy and loss of ther model when 20% of clients are down.

Fig. 8.

Accuracy and loss of ther model when 40% of clients are down.

Fig. 9.

Accuracy and loss of ther model when 60% of clients are down.

compared and analyzed the performance of Fedprox-BAFL,
Fedavg-BAFL, Fedavg, Fedprox models under different proportions of fault nodes (20%, 40%, 60% and 80%). As shown in
Figs. 7–10, node failures lead to fluctuations in the accuracy and
loss values of all models, and such fluctuations are aggravated
as the proportion of faulty nodes increases. In addition, the
increase in the number of faulty nodes also prolongs the number
of iterations and the time required for model convergence.
In the presence of node failures, the aggregation process
is affected by the uneven distribution of data. In federated
learning, each node may have different data distributions. If
the failure of some nodes leads to the loss of key data, the
distribution of remaining data may be changed, thus affecting

926

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 13, 2026

TABLE V
MODEL PERFORMANCE COMPARISON WHEN 20% OF CLIENTS ARE DOWN

TABLE VI
MODEL PERFORMANCE COMPARISON WHEN 40% OF CLIENTS ARE DOWN

TABLE VII
MODEL PERFORMANCE COMPARISON WHEN 60% OF CLIENTS ARE DOWN

Fig. 10.

Accuracy and loss of ther model when 80% of clients are down.

the performance of the model in each iteration. The instability
of model updating is also a key factor. Model updating depends
on the data and computing power of each node, and node failure
may cause the updating process to become unstable, especially
when the number of nodes is small, and the update of a single
node has a more significant impact on the global model. In
addition, node failure may change the communication mode of
the network, affect the uploading and downloading efficiency
of model parameters, and then affect the convergence speed
and stability of the model. In some federated learning settings,
the nodes involved in training are randomly selected, so the
randomness of the faulty nodes can result in different nodes
participating in each training, which can also lead to fluctuations
in model performance. The problem of data loss also cannot be
ignored. The faulty node may contain important training data,
and its absence will lead to incomplete information during model
training, thus affecting model performance. Node failures also
reduce data diversity and reduce the generalization ability of
the model, which in turn affects the performance of unseen
data.

Fig. 11.

Convergence time.

During the training process, Fedprox and Fedavg models
showed obvious performance degradation after node failure, and
slowly resumed training after node recovery. As can be seen
from Tables V–VIII and Figs. 7–11, when acc converges, the
number of iteration has reached 17 and 18, and the required
time is 210.4 seconds and 219.6 seconds, respectively. Due to
the introduction of a time attenuation factor in our model, which
can effectively eliminate the influence of the old parameters
of the long-failed nodes, the acc and loss of Fedprox-BAFL
and Fedavg-BAFL only fluctuate slightly when the nodes fail,
and the training will resume quickly after the nodes return to
normal. Acc reached convergence in the 10th and 11th iteration,
with times of 81.56 seconds and 95.56 seconds, respectively.
In contrast, our proposed BAFL algorithm exhibits smaller
fluctuations in the case of node failure and can reach convergence
more quickly. It can be seen from the data in the above figure and

LI et al.: DDoS ATTACK DETECTION IN BUSINESS BLOCKCHAIN NETWORKS: A REVIEW, FRAMEWORK, AND CHALLENGES

927

TABLE VIII
MODEL PERFORMANCE COMPARISON WHEN 80% OF CLIENTS ARE DOWN

table that the convergence time and iteration times of the model
increase correspondingly with the increase of the proportion
of faulty nodes. From the perspective of model performance,
the performance indexes of Fedprox-BAFL and Fedavg-BAFL,
such as acc, loss, precision, recall and F1-score, did not decrease
significantly in the case of node failure compared with the
case without fault. Fedprox and Fedavg models show obvious
performance degradation after node failure.
The temporal decay factor employed by the BAFL model
demonstrates remarkable efficacy in mitigating the potential
interference of old parameters from long-term offline nodes
on current model training. Even if some clients remain offline
for extended periods, their old parameters are unlikely to exert
a significant negative impact on the ongoing model training
process. For instance, when 20% of the nodes fail, the accuracy and loss value of the BAFL model only exhibit minor
fluctuations, and once the faulty nodes return online, the model
can swiftly resume its normal training trajectory. Moreover,
the BAFL model relies on an asynchronous federated learning
algorithm, which endows clients with the flexibility to update
model parameters at different time points. This feature not only
enhances the adaptability of the model training process but
also effectively ensures the continuity and stability of model
training in the face of client failures. Even if some clients
are unable to update parameters in a timely manner due to
failures, other clients can still continue to advance the model
training, thereby ensuring the robustness of the model’s overall
performance.
C. Stable Performance of BAFL
In the previous part, we described in detail the experimental
setup of collaborative participation in 20 clients. However,
these experimental results are not sufficient to reveal the stable
performance of BAFL (Blockchain-assisted Federated
Learning) in larger alliances. To address this research gap,
we introduced new clients to simulate the scenario where
new business chains join the supervision chain and are
allocated corresponding monitoring nodes and clients by the
supervision chain. This part expands the assessment of BAFL
performance to cover a range of growing league sizes from 5 to
80 clients, and quantifies key performance metrics, including
F1-score, time per round of aggregation, and total time to
convergence. Specifically, we randomly suspended the training
of some clients to simulate mid-process client failures, and
introduced new clients to simulate the scenario where new
business chains join the supervision chain and are allocated
corresponding monitoring nodes and clients by the supervision
chain.

Fig. 12.

The scalability of the Fedprox-BAFL.

For models with different number of clients, the experiment
was repeated for 10 times, and the average trend of their F1
scores and convergence time was shown in Fig. 12. When the
number of clients is small, the overall convergence time of the
BAFL model is longer and the F1-score is relatively low. As
the number of nodes increases, the model is able to process
more data in parallel, which may speed up the training process.
The addition of clients provides a more representative sample,
which enhances the generalization of the model and improves
the F1-score. When the number of clients increased to 20, the
model showed the shortest convergence time. The different
data perspectives provided by the new clients helped reduce
the model’s dependence on specific data biases, and enhanced
the consistency and performance of the model on different data
subsets, thus promoting the stability of F1-score. As the number
of clients further increases, although the model’s F1-score shows
some stability, the network communication overhead increases
due to the need for more communication to aggregate model
updates. As the number of clients increases, so does the amount
of data that needs to be transferred between the server and
the client, which can lead to higher communication costs per
training round, potentially slowing down training. In situations
where bandwidth is limited or communication costs are high,
the increase in communication overhead may further reduce
the training speed and prolong the convergence time of the
model, while the F1-score of the BAFL model fails to improve
further.
Within the BAFL framework, the adoption of a DAG structured supervision chain enables efficient recording of model
parameters and detected DDoS attack events. The DAG structure
supports parallel confirmation of multiple transactions, thereby
effectively circumventing the performance bottlenecks caused

928

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 13, 2026

by sequential processing in traditional blockchains and significantly enhancing system throughput. For instance, in the scenario where the number of clients increases, the DAG structure
demonstrates higher processing efficiency, capable of rapidly
handling and synchronizing model parameters, which in turn
accelerates the model training process. Moreover, BAFL has
automated data validation and sharing through smart contracts,
ensuring the security and credibility of data. This mechanism
allows newly joined clients to quickly synchronize the latest
model parameters and seamlessly participate in model training.
After joining, new clients can rapidly obtain the latest model
parameters through the supervision chain, thereby substantially
reducing initialization time and improving overall training efficiency.
VII. CONCLUSION
We summarize the research status and problems of DDoS
attack detection in blockchain networks, and propose a new
method to detect DDoS attacks in blockchain networks by
integrating FL with the supervision chain. The proposed system, BAFL, leverages the decentralized and secure nature of
blockchain technology to enhance the efficiency and robustness
of DDoS attack detection while preserving the privacy of local
node data. Through the use of a Directed Acyclic Graph (DAG)structured supervision chain, BAFL ensures secure and transparent sharing of model parameters among distributed nodes.
Additionally, the asynchronous federated learning algorithm,
augmented with a time decay factor, optimizes the aggregation
process by reducing the impact of outdated model parameters,
thereby accelerating convergence and improving detection accuracy. The experimental results show that the accuracy of our
proposed detection algorithm reaches more than 99%, showing
excellent robustness and scalability. Compared to traditional
DDoS attack detection algorithms, our solution can improve
detection accuracy by 2% and reduce real-time detection latency
to half of the industry’s current methods.
REFERENCES
[1] S. Wani, M. Imthiyas, H. Almohamedh, K. M. Alhamed, S. Almotairi,
and Y. Gulzar, “Distributed denial of service (DDoS) mitigation using
blockchain—A comprehensive insight,” Symmetry, vol. 13, no. 2, 2021,
Art. no. 227.
[2] Y. Xu, H. Wang, and J. Zeng, “Scope: A cross-chain supervision scheme
for consortium blockchains,” in Proc. Int. Conf. Inf. Commun. Secur., 2023,
pp. 553–570.
[3] X. Liang, J. Chen, R. Du, and T. Zhao, “Surveillant: A supervision mechanism between blockchains for efficient cross-chain verification,” KSII Trans. Internet Inf. Syst., vol. 16, no. 8, pp. 2507–2528,
2022.
[4] A. R. Jamader, P. Das, and B. R. Acharya, “BCIoT: Blockchain based
DDoS prevention architecture for IoT,” in Proc. IEEE Int. Conf. Intell.
Comput. Control Syst., 2019, pp. 377–382.
[5] M. Mirkin, Y. Ji, J. Pang, A. Klages-Mundt, I. Eyal, and A. Juels, “BDoS:
Blockchain denial-of-service,” in Proc. ACM SIGSAC Conf. Comput.
Commun. Secur., 2020, pp. 601–619.
[6] K. Kim, Y. You, M. Park, and K. Lee, “DDoS mitigation: Decentralized
CDN using private blockchain,” in Proc. IEEE 10th Int. Conf. Ubiquitous
Future Netw., 2018, pp. 693–696.
[7] Z. Abou El Houda, A. S. Hafid, and L. Khoukhi, “Cochain-SC: An
intra-and inter-domain DDoS mitigation scheme based on blockchain
using SDN and smart contract,” IEEE Access, vol. 7, pp. 98893–98907,
2019.

[8] B. Rodrigues, T. Bocek, and B. Stiller, “Multi-domain DDoS mitigation
based on blockchains,” in Proc. Secur. Netw. Serv. All-Connected World:
11th IFIP WG 6.6 Int. Conf. Auton. Infrastructure, Manage., Secur., Zurich,
Switzerland, 2017, pp. 185–190.
[9] T. G. Hua, H. Y. Han, and C. X. Feng, “Research progress on attack
and defense techniques in block-chain system,” J. Softw., vol. 32, no. 5,
pp. 1495–1525, 2021.
[10] Z. Abou El Houda, A. Hafid, and L. Khoukhi, “Co-IoT: A collaborative DDoS mitigation scheme in IoT environment based on
blockchain using SDN,” in Proc. IEEE Glob. Commun. Conf., 2019,
pp. 1–6.
[11] B. Rodrigues, E. Scheid, C. Killer, M. Franco, and B. Stiller, “Blockchain
signaling system (BLOSS): Cooperative signaling of distributed denialof-service attacks,” J. Netw. Syst. Manage., vol. 28, no. 4, pp. 953–989,
2020.
[12] B. Rodrigues and B. Stiller, “Cooperative signaling of DDoS attacks in
a blockchain-based network,” in Proc. ACM SIGCOMM Conf. Posters
Demos, 2019, pp. 39–41.
[13] B. Rodrigues, S. Trendafilov, E. Scheid, and B. Stiller, “SC-Flare: Cooperative DDoS signaling based on smart contracts,” in Proc. IEEE Int. Conf.
Blockchain Cryptocurrency, 2020, pp. 1–3.
[14] A. Gruhler, B. Rodrigues, and B. Stiller, “A reputation scheme for
a blockchain-based network cooperative defense,” in Proc. IFIP/IEEE
Symp. Integr. Netw. Serv. Manage., 2019, pp. 71–79.
[15] C. Killer, B. Rodrigues, and B. Stiller, “Security management and visualization in a blockchain-based collaborative defense,” in Proc. IEEE Int.
Conf. Blockchain Cryptocurrency, 2019, pp. 108–111.
[16] S. Purohit, P. Calyam, S. Wang, R. Yempalla, and J. Varghese, “DefenseChain: Consortium blockchain for cyber threat intelligence sharing
and defense,” in Proc. IEEE 2nd Conf. Blockchain Res. Appl. Innov. Netw.
Serv., 2020, pp. 112–119.
[17] L.-Y. Yeh, J.-L. Huang, T.-Y. Yen, and J.-W. Hu, “A collaborative DDoS
defense platform based on blockchain technology,” in Proc. IEEE 12th
Int. Conf. Ubi-Media Comput., 2019, pp. 1–6.
[18] S. Sayadi, S. B. Rejeb, and Z. Choukair, “Anomaly detection model
over blockchain electronic transactions,” in Proc. IEEE 15th Int. Wireless
Commun. Mobile Comput. Conf., 2019, pp. 895–900.
[19] M. Saad, M. T. Thai, and A. Mohaisen, “Poster: Deterring DDoS attacks
on blockchain-based cryptocurrencies through mempool optimization,” in
Proc. Asia Conf. Comput. Commun. Secur., 2018, pp. 809–811.
[20] T. Idé, “Collaborative anomaly detection on blockchain from noisy sensor
data,” in Proc. IEEE Int. Conf. Data Mining Workshops, 2018, pp. 120–127.
[21] J. E. A. Sousaet al., “Fighting under-price dos attack in ethereum with
machine learning techniques,” ACM SIGMETRICS Perform. Eval. Rev.,
vol. 48, no. 4, pp. 24–27, 2021.
[22] P. Kumar, R. Kumar, G. P. Gupta, and R. Tripathi, “A distributed framework
for detecting DDoS attacks in smart contract-based blockchain-iot systems by leveraging fog computing,” Trans. Emerg. Telecommun. Technol.,
vol. 32, no. 6, 2021, Art. no. e4112.
[23] B. Jia and Y. Liang, “Anti-D Chain: A lightweight DDoS attack detection
scheme based on heterogeneous ensemble learning in blockchain,” China
Commun., vol. 17, no. 9, pp. 11–24, 2020.
[24] R. Kumar, P. Kumar, R. Tripathi, G. P. Gupta, S. Garg, and M. M.
Hassan, “A distributed intrusion detection system to detect DDoS attacks
in blockchain-enabled IoT network,” J. Parallel Distrib. Comput., vol. 164,
pp. 55–68, 2022.
[25] M. Mittal, K. Kumar, and S. Behal, “Deep learning approaches for detecting DDoS attacks: A systematic review,” Soft Comput., vol. 27, no. 18,
pp. 13039–13075, 2023.
[26] M. A. Al-Shareeda, S. Manickam, and M. A. Saare, “DDoS attacks
detection using machine learning and deep learning techniques: Analysis
and comparison,” Bull. Elect. Eng. Inform., vol. 12, no. 2, pp. 930–939,
2023.
[27] U.-J. Baek, S.-H. Ji, J. T. Park, M.-S. Lee, J.-S. Park, and M.-S. Kim,
“DDoS attack detection on bitcoin ecosystem using deep-learning,” in
Proc. 20th Asia-Pacific Netw. Operations Manage. Symp., 2019, pp. 1–4.
[28] M. Essaid, D. Kim, S. H. Maeng, S. Park, and H. T. Ju, “A collaborative
DDoS mitigation solution based on ethereum smart contract and RNNLSTM,” in Proc. 20th Asia-Pacific Netw. Operations Manage. Symp., 2019,
pp. 1–6.
[29] Q.-Y. Dai, B. Zhang, and S.-Q. Dong, “A DDoS-attack detection method
oriented to the blockchain network layer,” Secur. Commun. Netw., vol.
2022, no. 1, 2022, Art. no. 5692820.
[30] R. Kumar, P. Kumar, R. Tripathi, G. P. Gupta, and N. Kumar, “P2SF-IoV:
A privacy-preservation-based secured framework for Internet of Vehicles,”
IEEE Trans. Intell. Transp. Syst., vol. 23, no. 11, pp. 22571–22582,
Nov. 2022.

LI et al.: DDoS ATTACK DETECTION IN BUSINESS BLOCKCHAIN NETWORKS: A REVIEW, FRAMEWORK, AND CHALLENGES

[31] V. Mothukuri, P. Khare, R. M. Parizi, S. Pouriyeh, A. Dehghantanha,
and G. Srivastava, “Federated-learning-based anomaly detection for IoT
security attacks,” IEEE Internet Things J., vol. 9, no. 4, pp. 2545–2554,
Feb. 2022.
[32] D. Hamouda, M. A. Ferrag, N. Benhamida, and H. Seridi, “PPSS: A
privacy-preserving secure framework using blockchain-enabled federated
deep learning for industrial IoTs,” Pervasive Mobile Comput., vol. 88,
2023, Art. no. 101738.
[33] P. Kumar, G. P. Gupta, and R. Tripathi, “PEFL: Deep privacy-encodingbased federated learning framework for smart agriculture,” IEEE Micro,
vol. 42, no. 1, pp. 33–40, Jan./Feb. 2021.
[34] P. Kumar, R. Kumar, G. P. Gupta, R. Tripathi, and G. Srivastava, “P2TIF:
A blockchain and deep learning framework for privacy-preserved threat
intelligence in industrial IoT,” IEEE Trans. Ind. Informat., vol. 18, no. 9,
pp. 6358–6367, Sep. 2022.
[35] M. A. Ferrag, O. Friha, L. Maglaras, H. Janicke, and L. Shu, “Federated deep learning for cyber security in the Internet of Things: Concepts, applications, and experimental analysis,” IEEE Access, vol. 9,
pp. 138509–138542, 2021.
[36] B. Jia, X. Zhang, J. Liu, Y. Zhang, K. Huang, and Y. Liang, “Blockchainenabled federated learning data protection aggregation scheme with differential privacy and homomorphic encryption in IIoT,” IEEE Trans. Ind.
Informat., vol. 18, no. 6, pp. 4049–4058, Jun. 2022.
[37] C. Xu et al., “A federated learning architecture for blockchain DDoS attacks detection,” IEEE Trans. Serv. Comput., vol. 17, no. 5, pp. 1911–1923,
Sep./Oct. 2024.
[38] R. K. Sharma and R. S. Pippal, “Malicious attack and intrusion prevention
in IoT network using blockchain based security analysis,” in Proc. IEEE
12th Int. Conf. Comput. Intell. Commun. Netw., 2020, pp. 380–385.
[39] W. Cao, Y. Huang, D. Li, F. Yang, X. Jiang, and J. Yang, “A
blockchain based link-flooding attack detection scheme,” in Proc. IEEE
4th Adv. Inf. Manage., Commun., Electron. Automat. Control Conf., 2021,
pp. 1665–1669.
[40] D. Manikumar and B. U. Maheswari, “Blockchain based DDoS mitigation
using machine learning techniques,” in Proc. IEEE 2nd Int. Conf. Inventive
Res. Comput. Appl., 2020, pp. 794–800.
[41] M. Chen, X. Tang, J. Cheng, N. Xiong, J. Li, and D. Fan, “A DDoS attack
defense method based on blockchain for IoTs devices,” in Proc. Artif.
Intell. Secur.: 6th Int. Conf., Hohhot, China, 2020, pp. 685–694.
[42] M. Singh, G. S. Aujla, A. Singh, N. Kumar, and S. Garg, “Deeplearning-based blockchain framework for secure software-defined industrial networks,” IEEE Trans. Ind. Informat., vol. 17, no. 1, pp. 606–616,
Jan. 2021.
[43] X. Han, R. Zhang, X. Liu, and F. Jiang, “Biologically inspired smart
contract: A blockchain-based DDoS detection system,” in Proc. IEEE Int.
Conf. Netw., Sens. Control, 2020, pp. 1–6.
[44] P. Ramadass et al., “BSDN-hmtd: A blockchain supported SDN framework
for detecting DDoS attacks using deep learning method,” Egyptian Inform.
J., vol. 27, 2024, Art. no. 100515.
[45] X. Li et al., “An adaptive DDoS detection and classification method in
blockchain using an integrated multi-models,” Comput., Mater. Continua,
vol. 77, no. 3, pp. 3265–3288, 2023.
[46] R. Doriguzzi-Corin, S. Millar, S. Scott-Hayward, J. Martinez-del Rincon,
and D. Siracusa, “Lucid: A practical, lightweight deep learning solution
for DDoS attack detection,” IEEE Trans. Netw. Service Manag., vol. 17,
no. 2, pp. 876–889, Jun. 2020.
[47] M. C. P. Saheb, M. S. Yadav, S. Babu, J. J. Pujari, and J. B. Maddala, “A
review of DDoS evaluation dataset: Cicddos2019 dataset,” in Proc. Int.
Conf. Energy Syst., Drives Automat., 2021, pp. 389–397.

Mengyuan Li received the B.S. degree from
Zhengzhou University, Zhengzhou, China, in 2019.
She is currently working toward the Ph.D. degree in
information and communication engineering from the
Beijing University of Posts and Telecommunications,
Beijing, China. Her research interests include network security, artificial intelligence, federated learning, anomaly detection, and blockchain.

929

Jiewei Chen received the B.S. degree in information
and computing science from the Minzu University
of China, Beijing, China, in 2019. She is currently
working toward the Ph.D. degree in information and
communication engineering from the Beijing University of Posts and Telecommunications, Beijing,
China. Her research interests include federated learning, large foundation model, edge computing, and
Internet of Things.

Shaoyong Guo is currently a Professor with the
School of Computer Science, Beijing University of
Posts and Telecommunications, Beijing, China. His
research interests include DPU, blockchain application technology, and edge intelligence. He has
achieved innovative results such as power communication network convergence control model and
method, network data trusted sandbox privacy sharing
service mechanism and technology, and edge security
protection technology and mechanism in an open
network environment. He is also undertaking many
key research and development projects and fund projects, and contributed to a
number of pioneering standards proposals in ITU-T. The systems and devices
developed by him have large-scale application. He was the recipient of the
National Science Fund for Excellent Young Scholars in 2023, Second Prize
of Science and Technology Progress Award of Beijing Municipality, Henan
Province, and Jiangsu Province, and the Second Prize of Science and Technology
Progress Award of Chinese Institute of Electronics.

Xuesong Qiu (Senior Member, IEEE) received the
Ph.D. degree in communication and information
systems from the Beijing University of Posts and
Telecommunications, Beijing, China, in 2000. He is
currently a Professor and the Ph.D. degree Supervisor
with the State Key Laboratory of Networking and
Switching Technology, Beijing University of Posts
and Telecommunications. He has authored about 100
SCI/EI index papers. He presides over a series of Key
Research Projects on Network and Service Management, including the projects supported by the National Natural Science Foundation and the National HighTech Research and
Development Program of China.

Feng Qi is currently a Professor with the State Key
Laboratory of Networking and Switching Technology, Beijing University of Posts and Telecommunications, Beijing, China, and a Researcher with
Peng Cheng Laboratory, Shenzhen, China. His research interests include communications software,
network management, and business intelligence. He
has won two National Science and Technology
Progress Awards. He has also written more than 10
ITU-T international standards and industry standards.
He was the Vice Chairman of ITU-T Study Group 4
and Study Group 12.
PAPER_TEXT
