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
# [438] Federated Malware Detection in Flying Ad Hoc Drone Networks Using Hybrid Convolutional Learning and Adaptive Optimization
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
编号：438
题名：Federated Malware Detection in Flying Ad Hoc Drone Networks Using Hybrid Convolutional Learning and Adaptive Optimization
年份：2025
DOI：10.1109/tce.2025.3618628
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2025.3618628.pdf
已有粗分类：IoT、车联网、工业互联网与边缘安全
二级关联：联邦学习、隐私保护与分布式协同、入侵检测与网络异常检测
相关性：强相关，分数 12
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\438.txt
- 原始字符数：90776
- 本次发送字符数：90776
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

9993

Federated Malware Detection in Flying Ad Hoc
Drone Networks Using Hybrid Convolutional
Learning and Adaptive Optimization
Abdulwahab Ali Almazroi

Abstract— The growing use of drones in edge computing,
primarily within Flying Ad Hoc Networks (FANETs), has raised
pressing security concerns, particularly in detecting malware
within decentralized and privacy-sensitive environments. Traditional intrusion detection systems often fall short in these
settings, struggling to meet the demands of limited computational
power, non-IID data distributions, and the need to preserve
local information. In response to these challenges, we propose
F-ResDenseEffiNet, a novel federated deep learning framework
that uniquely integrates ResNet, DenseNet, and EfficientNet. This
architectural combination, not previously explored in FL-based
malware detection, enables residual learning, feature reuse, and
compound scaling, resulting in accurate and lightweight detection
suitable for UAV platforms. To further improve convergence and
adaptability in heterogeneous data settings, we introduce AGRO,
an Adaptive Gorilla–Rabbit Optimization algorithm, which balances exploration and exploitation more effectively than standard
optimizers such as Adam or RMSProp. Comprehensive experiments on four diverse intrusion detection datasets, DBMD24
(drone-malware), CICIDS2017, NSL-KDD, and KDDCup99—
representing both traditional and UAV-relevant traffic patterns,
showcase the model’s strong performance, achieving an average
detection accuracy of 97.9%, a threat identification rate of 99.7%,
a decision confidence of 98.6%, and an overall classification quality of 98.7%. Additional evaluations, including ablation studies,
statistical tests, fairness analysis, and architectural interpretability, further confirm the scalability, reliability, and suitability
of the proposed framework for real-time drone-based anomaly
detection.
Index Terms— Federated learning, malware detection, drone
networks, hybrid deep learning, edge security.

I. I NTRODUCTION

T

HE Internet is essential in contemporary life, particularly with the rise of Internet-enabled technologies like
IoT [1]. IoT technology, which connects devices over the web,
has improved living, working, and learning experiences. IoD
stands for Internet of Drones, an extension of IoT [2]. Using
IoD for UAV deployment is essential due to its “layered network control architecture” [3], [4]. Drones, UAVs, and FANET
are synonymous in this work. Network security research is
Received 7 April 2025; revised 23 May 2025, 5 August 2025,
and 1 September 2025; accepted 1 October 2025. Date of publication
7 October 2025; date of current version 8 December 2025. The authors extend
their appreciation to the Deputyship for Research & Innovation, Ministry of
Education in Saudi Arabia for funding this research work through the project
number MoE-IF-UJ-R2-22-04100409-1.
The author is with the College of Computing and Information Technology at
Khulais, Department of Information Technology, University of Jeddah, Jeddah
21959, Saudi Arabia (e-mail: aalmazroi@uj.edu.sa).
Digital Object Identifier 10.1109/TCE.2025.3618628

crucial due to the prevalence of the Internet and advanced
communication technologies. Data and network security need
IDSs and firewalls. NIDS monitors all network traffic for
malicious activity. In the last decade, communications and
network technologies have rapidly expanded network size
and data sharing, making new threats more challenging to
detect. A compromise at a single node might impact an
organization’s data. The US Department of Transportation
assessed the viability of civil GPS spoofing, including drone
interference [6]. Signatures, anomalies, and specifications can
trigger IDSs. Anomaly-based methods involve knowledge,
machine learning, and statistics. Detecting abnormal intrusions
involves comparing traffic data to a model of ordinary operation [7], [8]. Machine-learning anomaly detection systems
enhance performance by refining models based on observed
patterns. Signature-driven identification compares current data
to threat trends and eliminates false alarms, but requires
regular signature updates [9].
Machine learning algorithms dominate this article. They
work better than non-machine learning ones because they
learn and teach. Drone networks require reliable intrusion
detection. Researchers suggest using deep learning (DL) and
machine learning (ML) to extract meaningful data from large
datasets [10]. Network security uses ML and DL approaches to
learn from network data and distinguish between normal and
unusual activities. Unlike feature engineering-based machine
learning, deep learning can immediately learn complex features from raw data. Over time, researchers have created
ML and DL-based NIDS risk identification algorithms. NIDS
must cope with increased security concerns and network
traffic. According to [11] and [12], the agent monitors the
network, while the analysis engine and response module detect
attacks and report findings. Despite improvements, standard
NIDSs are inadequate for IoT’s complex network layers due
to the critical applications of drone operations and security
considerations. The addition of UAVs introduces complexity,
necessitating enhanced intrusion detection.
This study presents a federated deep learning framework
designed explicitly for malware detection within the Internet of
Drones (IoD) environment. At its core is a hybrid model called
F-ResDenseEffiNet, which integrates the strengths of ResNet,
DenseNet, and EfficientNet to achieve high detection accuracy
while staying within the computational and energy constraints
of UAV platforms. Each drone is equipped with a lightweight
version of the model that operates independently to identify

1558-4127 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

9994

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

local threats in real time. Meanwhile, a central base station
aggregates insights across the network to coordinate a broader,
swarm-wide response. What sets this approach apart from
traditional IoT-based solutions is its alignment with the operational realities of drone systems—limited bandwidth, high
mobility, and strict privacy requirements. By leveraging federated learning, the model avoids transmitting raw data, keeping
sensitive information on each drone while still enabling collaborative intelligence. To further address the challenges of
uneven data distribution and sporadic connectivity standards
in Flying Ad Hoc Networks (FANETs), the system incorporates AGRO (Adaptive Gorilla–Rabbit Optimization). This
dual-phase optimization method ensures stable and efficient
learning. Evaluations across four benchmark datasets confirm
that the proposed method delivers strong performance and
real-world viability for secure, real-time anomaly detection in
drone networks.
Research Aim: The primary focus of this research is to
design a privacy-preserving federated deep learning model
capable of detecting malware efficiently in real-time UAV
network environments. The proposed solution is designed to
respect privacy constraints while maintaining high detection
accuracy, efficient resource utilization, and scalability across
distributed UAV systems.
Research Questions:
• RQ1: What design considerations are necessary to optimize deep hybrid models for malware classification on
drones with limited processing capabilities?
• RQ2: How can federated learning be leveraged to enable
secure and collaborative model training in drone environments, particularly under non-IID data conditions?
• RQ3: Which optimization strategies are most effective
for accelerating convergence and improving accuracy in
decentralized UAV systems facing unreliable communication and dynamic topologies?
Significance: These research questions address core challenges in securing the Internet of Drones (IoD). As drones
increasingly support critical missions in areas such as logistics, monitoring, and defense, there is a pressing need for
lightweight, adaptable, and privacy-aware cybersecurity frameworks. Meeting these demands will help ensure resilient
operations and safeguard sensitive data in complex, real-world
deployment scenarios.
Key Contributions: The principal contributions of this
research are outlined below:
1) In this research, we introduce a federated learning framework that can detect anomalies in FANETs, flying ad hoc
networks that utilise drones in real-time. This system
features asynchronous training, adherence to stringent
data privacy standards, and optimisation for deployment
on edge-level platforms. The proposed method ensures
improved scalability and resilience in decentralised UAV
settings, in contrast to centralised FL-CNN-based systems.
2) A hybrid deep learning model, termed FResDenseEffiNet, is introduced by integrating the
residual feature propagation capabilities of ResNet, the

dense connectivity principles of DenseNet, and the
compound scaling efficiency of EfficientNet. Unlike
prior approaches such as [30] that rely on graph neural
networks in combination with convolutional models,
this architecture is meticulously optimized to achieve
high inference accuracy while maintaining compatibility
with the constrained computational profile of drone
hardware.
3) A novel optimization method, Adaptive Gorilla–Rabbit
Optimization (AGRO), is proposed to improve convergence dynamics under non-IID data settings. This
algorithm uniquely merges exploratory behavior inspired
by gorilla search heuristics with the fast convergence
traits observed in rabbit-based dynamics. It is especially
well-suited for federated learning contexts characterized
by unstable network connectivity and heterogeneous
client data, as frequently encountered in aerial communication networks.
4) The efficacy and generalizability of the framework
are demonstrated through extensive validation across
four benchmark intrusion detection datasets: DBMD24,
CICIDS2017, NSL-KDD, and KDDCup99. These
datasets represent a broad spectrum of real-world
malware behaviors and attack scenarios, enabling comprehensive evaluation under diverse conditions.
5) A thorough experimental analysis is conducted, encompassing ablation studies, statistical hypothesis testing,
fairness assessments, and hyperparameter sensitivity
evaluations. The proposed system consistently delivers
an average detection accuracy of 98.9 percent, underscoring its robustness, adaptability, and practical utility
for real-time malware detection in UAV-based surveillance and monitoring operations.
The structure of this article is organized to guide the reader
through each stage of the research. The second section looks
at the works that are most closely related. In Section III,
the suggested organization is summed up. Section IV outlines the experiments and assessment criteria employed, and
Section V analyzes and comments on the simulation results.
Section 6 concludes the study and provides ideas for future
projects.
II. R ELATED W ORK
Recent breakthroughs have significantly enhanced malware
detection capabilities within IoT and drone-based networks,
leveraging deep learning and edge intelligence. Traditional
methods, which often depend on centralized architectures,
struggle to address critical concerns such as data privacy, communication overhead, and deployment scalability. In response
to these limitations, A decentralized solution that allows
remote nodes to learn together without exchanging raw data
is Federated Learning (FL) [13]. This section reviews both
federated and non-federated approaches, analyzing each study
in terms of its objectives, core methodology, performance
achievements, and constraints, with a focus on their applicability to secure, privacy-aware, and resource-constrained drone
environments.

ALMAZROI: FEDERATED MALWARE DETECTION IN FLYING AD HOC DRONE NETWORKS

To detect intrusions in IoT networks, [14] developed a deep
learning model that incorporated CNNs and LSTM networks.
The method’s accuracy rate of 96.2% and F1-score of 0.965 on
the IoT-23 dataset were promising. Still, it was only suitable
for centralised processing, which rendered it ineffective for
distributed applications like drone swarms, where privacy is
essential. A strategy presented in [15] utilized time-window
embeddings in conjunction with a feedforward neural network
and a transformer encoder to identify anomalies in smart
homes enabled by the Internet of Things. On the Aposemat
IoT-23 dataset, the system achieved an F1-score of 0.937.
Despite its strong results, the model was developed for centralized environments and lacked flexibility for deployment in
decentralized aerial systems. In [16], a lightweight ensemblebased model was proposed for botnet detection across multiple
IoT datasets, including IoT-23. It achieved a binary classification accuracy of 97.9%. While computationally efficient,
the method does not support federated learning and has not
been validated in dynamic drone networks with real-time
constraints. A GRU-based botnet detection model presented
in [17] demonstrated exceptional accuracy of 99.89% on IoT23. Although effective, the model’s reliance on centralized
learning hinders its suitability for decentralized drone-based
ecosystems where privacy and on-device inference are
critical.
A notable federated learning-based approach was proposed
in [18], utilizing depthwise separable CNNs to detect traffic
anomalies in IoT networks. The model demonstrated strong
performance, achieving 98.52% accuracy for binary classification and 97.73% for multiclass scenarios on the IoT-23 dataset.
While this work highlights the privacy benefits of FL, it does
not address key deployment challenges often encountered in
drone networks, such as vulnerability to adversarial attacks
or unstable connectivity. As outlined in the foundational
study by [13], federated learning is particularly well-suited
for decentralized and privacy-sensitive environments, such as
UAV swarms, where sharing raw data is restricted due to
bandwidth constraints and security concerns. Their insights
into communication efficiency, heterogeneity handling, and
privacy-preserving strategies directly support our decision to
adopt FL as the backbone of our malware detection framework
in Flying Ad Hoc Networks (FANETs).
In [19], conventional classifiers like Random Forest, MultiLayer Perceptron, and Gradient Boosting were applied to the
IoT-23 dataset, with Random Forest yielding the best result
at 98.6% accuracy. The study, however, remained centralized and did not account for edge-device constraints or the
privacy-preserving benefits of FL. A temporal model named
ADEPT was introduced in [20] for phase-wise attack detection, achieving 99% accuracy and an F1-score of 0.99 using
NSS and IoT-23 datasets. Despite its effectiveness, the absence
of federated capabilities limits its relevance for drone-based
distributed learning environments. A federated CNN-LSTM
architecture was implemented in [21] and [22] to detect
wormhole attacks across distributed nodes using the IoT23 dataset. The model preserved privacy and achieved 96%
accuracy, although its vulnerability to adversarial attacks and
poisoned updates was not addressed.

9995

The study in [23] and [24] compared centralized and federated versions of SVM and LSTM models on the VirusTotal
dataset. The federated LSTM variant achieved the highest
accuracy at 91.67%, striking a balance between privacy and
performance. However, it lacked mechanisms to handle noisy
or non-IID client data, an essential factor in drone applications.
In [25], a federated framework utilizing both supervised and
unsupervised models was applied to the N-BaIoT dataset for
malware detection. It maintained strong accuracy, exceeding
97%, while preserving user privacy. Yet, the study did not
consider heterogeneous data distributions across clients—a
realistic challenge in drone swarms. A comparative evaluation in [26] used over 87,000 Android applications from
the Opera Mobile Store to test centralized and federated
SVM models. Although the federated model had slightly
lower accuracy (93.45%) compared to centralized (94.05%),
it outperformed in precision and recall. However, it lacked
hybrid deep learning components that could further enhance
detection capabilities. In [27], a federated malware detection
model based on the “Less is More” framework was evaluated
on the MaMaDroid dataset, which included 200 users. The
model achieved an F1-score of 95%. While privacy-aware, the
method required significant preprocessing and lacked deeper
neural architectures for feature extraction. The FedHGCDroid
framework in [28] introduced a federated approach that integrates Convolutional Neural Networks (CNNs) with Graph
Neural Networks (GNNs) for malware detection. Evaluated
on the Androzoo dataset, it achieved a notable accuracy of
91.3% and demonstrated effective adaptability across distributed clients. Deploying it on drone platforms with limited
resources may be challenging due to its relatively high processing requirements, despite its performance.
Incorporating generative adversarial networks for Android
malware detection via federated learning was part of the
Fed-IIoT architecture in [29]. With a performance reaching
93.24% accuracy on the Genome dataset, the system showed
promise; however, training instability due to GANs and the
presence of non-IID data pose implementation challenges. The
authors of [30] introduced FedMalDE, a federated learning
framework that use a Subgraph Aggregated Capsule Network
(SACN), in an effort to enhance malware detection. The model
attained a remarkable F1-score of 97.64% when evaluated on
datasets like DREBIN and AndroZoo. However, its reliance
on graph-based structures adds computational complexity,
which could hinder real-time implementation in drone systems where low latency and resource efficiency are critical.
In [28], a comparison of tree-based classifiers such as Random
Forest, CatBoost, and LightGBM was conducted using the
CIC-MalMem-2022 dataset. Random Forest achieved nearperfect accuracy, but the centralized framework lacks support
for federated inference or secure edge deployment. A hybrid
ML-DL approach was proposed in [31], combining SMOTE
and XGBoost for intrusion detection across CIC-MalMem2022 and KDDCUP-99. Achieving 100% accuracy, the system
performed well but lacked any distributed training or data
protection capabilities.
An evaluation of clustering and classification techniques,
including AdaBoost, K-means, and DBSCAN, was performed

9996

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

TABLE I
S UMMARY OF R ECENT L ITERATURE C ATEGORIZED BY M ODEL AND D EPLOYMENT S TRATEGY

in [32], with AdaBoost achieving 99.99% accuracy on CICMalMem-2022. Though effective, these models were not
adapted for federated training or collaborative learning scenarios. The extended CNN model introduced in [33] focused on
detecting memory-resident malware, reporting 99% detection
accuracy and 83% accuracy in malware type classification on CIC-MalMem-2022. Despite a solid performance,
its centralized structure prevents practical application in
privacy-sensitive drone operations. Finally, the study in [34]
employed metaheuristic algorithms, including Particle Swarm
Optimization (PSO), Binary Bat Algorithm (BBA), and Mayfly
Algorithm (MA), for feature selection in malware detection.
Combined with classifiers such as SVM and Random Forest,
the framework achieved approximately 99% accuracy on CICMalMem-2022. However, its lack of federated capabilities
restricts use in distributed or privacy-critical systems.
The need to include privacy-preserving methods in both
federated and decentralised intrusion detection systems has
been highlighted in recent research. For example, [35] presents

research that utilises the Laplace mechanism and statistical
metrics, such as information value and weight of evidence,
to develop a differential privacy strategy for deep neural networks. A significant trade-off between privacy and
usefulness is maintained. At the same time, this strategy
successfully preserves both numerical and categorical sensitive
data. Despite its effectiveness in privacy preservation, the
model’s lack of emphasis on real-time processing and resource
optimization limits its suitability for UAV-based deployment.
Similarly, the research in [36] proposes an advanced TBMFCC-based multifuse feature extraction framework aimed
at classifying emergency vehicle sounds. By combining signal
augmentation techniques with a Multi-Stacked CNN and an
Attention-enhanced BiLSTM network, the model achieves a
high classification accuracy of 98.66%. Although not directly
related to malware detection, the study offers valuable insights
into handling data imbalance and extracting rich temporalspatial features—strategies that can be adapted to drone-based
threat identification systems. In another contribution, [37]

ALMAZROI: FEDERATED MALWARE DETECTION IN FLYING AD HOC DRONE NETWORKS

presents a hybrid privacy-preserving model that merges statistical transformations with a privacy-chain-based homomorphic
encryption scheme. Applied across diverse datasets, including
lung cancer and bank marketing data, the model demonstrates
high classification accuracy while protecting user-sensitive
information. However, the encryption process incurs significant computational overhead, which can pose practical
limitations for deployment in low-power, real-time UAV environments.
Another study focused on strengthening the security
of drone and Internet of Drones (IoD) environments
through advanced intrusion and malware detection techniques.
To enhance anomaly detection in drone-to-drone and drone-tobase station communications, the Cross-Layer Convolutional
Attention Network (CLCAN) was proposed in the research
by [38]. This network utilises contextual attention, multiscale convolutional layers, and dynamic feature fusion. Their
approach reported detection accuracy below 96% on real drone
communication datasets. Work presented in [39] explored
artificial intelligence–based methods for malware detection
in drone communication, proposing a hybrid model with
feature selection (Hybrid with FS). Although it improved performance, accuracy remained around 80%, underscoring the
need for more robust solutions. A ConvLSTM-based approach
was examined in [40], where the method was validated
across benchmark datasets such as KDDCup99, NSL-KDD,
CICIDS2017, and WSN-DS, achieving performance slightly
below 96% across different attack categories. The identification of Denial of Service (DoS) attacks in Internet of
Things (IoT) settings was examined by [41], who also detailed
the advantages and disadvantages of UAV intrusion detection
systems that utilise machine learning. Research from these
studies indicates that drone security solutions powered by
AI have considerable potential. Still, they also have specific
common problems, such as reliance on datasets and limited attack coverage. Building on these insights, our work
introduces a federated hybrid deep learning framework that
not only strengthens malware detection in drone networks
but also demonstrates consistent generalization across diverse
benchmark datasets (NSL-KDD, KDDCup99, CICIDS2017).
Although earlier studies have made meaningful contributions to the development of federated learning frameworks
and malware detection methods, many still overlook the
unique combination of challenges that arise in practical dronebased environments. Many existing models rely on single-path
architectures, such as CNNs or LSTMs, and often do not
leverage hybrid designs or adaptive tuning techniques. Furthermore, only a few approaches have been tested under
drone-specific conditions such as limited connectivity, exposure to adversarial threats, or real-time processing constraints
on lightweight hardware. To address these limitations, the
proposed F-ResDenseEffiNet model combines the strengths
of ResNet, DenseNet, and EfficientNet to create a compact
yet powerful architecture tailored for UAV platforms. The
AGRO algorithm complements this—a hybrid Gorilla–Rabbit
optimization strategy—that enhances convergence and generalization, particularly under the non-IID data and intermittent
communication settings typical in federated UAV networks.

9997

An aggregated summary of the existing literature is provided
in Table I, while a detailed comparative analysis focusing on
key differentiators such as federated capability, drone compatibility, optimization mechanisms, and resilience to non-IID
conditions is presented in Table II.
III. P ROPOSED S YSTEM M ODEL
The proposed system is structured around a well-defined
design cycle comprising six interconnected stages. The process begins with the collection of data from drone-mounted
sensors and network traffic sources, capturing key operational
and environmental variables, including IP addresses, packet
contents, GPS coordinates, and surrounding conditions. Once
gathered, the raw data is preprocessed to ensure quality—this
involves cleaning, normalization, and addressing any missing
values, making the data reliable and ready for analysis.
In the third stage, feature engineering is applied to extract
insightful attributes, such as traffic volume, packet flow length,
and variations in packet size—features that are crucial for
identifying malware patterns. Statistical and machine learning
techniques are employed in a hybrid feature selection strategy,
which is utilised in the fourth phase to identify the most
crucial features. The data will be simplified, and the model’s
performance will be improved.
The next step is to feed the ResDenseEffiNet classifier
the cleaned-up dataset. This solution enables multiple drones
to train together in a federated learning context without
exchanging raw data, thereby respecting user privacy and
reducing transmission costs. Step six involves introducing
the Adaptive Gorilla-Rabbit Optimisation (AGRO) approach
to finish optimising the model’s hyperparameters. AGRO
excels in providing constant and fast convergence, even in the
most challenging circumstances, such as FANETs’ notoriously
non-iid data and intermittent network connections.
The hybrid ResDenseEffiNet model serves as the core
intelligence of the system, offering a carefully crafted balance between architectural depth, representational power, and
computational efficiency. By integrating ResNet’s residual
learning, DenseNet’s feature reuse, and EfficientNet’s compound scaling, the model achieves high detection accuracy
while minimizing the computational demands on onboard
UAV hardware. Empirical evaluations indicate that the model
requires approximately 305 MFLOPs per inference and occupies 14.2 MB of memory, well within the operational
limits of embedded systems such as the NVIDIA Jetson
Nano and Qualcomm Flight RB5. When compared to established lightweight models like MobileNetV2 (238 MFLOPs,
13.6 MB) and SqueezeNet (833 MFLOPs, 4.8 MB), ResDenseEffiNet achieves a consistent 6–9% improvement in
accuracy, with only a marginal increase in inference latency
(62 ms versus 49 ms). This performance-to-resource trade-off
makes the model a viable and deployable solution for real-time
malware detection in UAV environments.
Importantly, only the trained ResDenseEffiNet model is
deployed on drones for inference tasks, while the federated
training process is executed asynchronously across distributed
edge nodes. This separation ensures that drones are not burdened with training overhead during active operation, thereby

9998

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

TABLE II
C OMPARATIVE A NALYSIS OF E XISTING M ETHODS AND P ROPOSED F RAMEWORK

preserving responsiveness and maintaining a practical balance
between processing cost and real-time detection performance.
To assess its robustness, the model was validated across
four well-known intrusion detection datasets—DBMD24 [42],
CICIDS2017 [44], NSL-KDD, and KDDCup 99 [43]—
covering a wide range of cyberattack scenarios and network
behaviors. As illustrated in Figure 1, the proposed architecture
supports distributed analysis, where individual drones detect
local anomalies. At the same time, the base station aggregates
updates to maintain global security awareness across the
network.

TABLE III
S UBSET OF K EY F EATURES F ROM E ACH C ATEGORY

A. Stage 1: Dataset Description
This study’s dataset is built to help detect malware by
analyzing ambient variables, network traffic, data from drone
GPS and sensors, and metrics for malware identification.
Drone operations and possible cyber risks are both modeled in
this dataset. The “Drone-based Malware Detection (DBMD)”
dataset [42], available on Kaggle at [29], was used to acquire
the data. The dataset comprises 54 attributes and 200,000
records, derived from four distinct categories. Some of the
attributes are shown in Table III. The dataset used in this
study is publicly available. It is intended solely to advance
research in secure drone communication and malware detection. Nevertheless, as with many cybersecurity datasets, there
is a potential for misuse if not properly applied. Therefore, its
use should remain strictly within the bounds of ethics and the
law.
1) Derived Features: We created various additional characteristics from the current ones to strengthen the dataset and
raise the efficiency of the malware detection algorithms. These
generated characteristics find further trends and connections in
the data. The derived features are described in Table IV.
B. Stage 2: Data Preprocessing
The first and foremost stage in preparing data for training
machine learning algorithms is data preparation. Preprocessing
can ensure the integrity and consistency of raw input fields and
prepare them for better model performance(iterative & more
accurate results). The drone-based malware detection dataset
was preprocessed with the following steps [45]:

Handling Missing Values: The first step in maintaining a
clean dataset is to replace any missing values. When numerical
characteristics had missing values, the mean of that feature
was used to fill them in, ensuring the data remained normally
distributed. The distribution of categorical characteristics was
maintained by imputing missing values using the mode.
Normalization and Standardization The numerical characteristics were standardized and normalized to guarantee their
equal scale. Algorithms that depend on distance measurements
rely on this stage. Min-max scaling normalized features to [0,
1] and StandardScaler to zero-average and zero-deviation. The
process of standardization and normalization can be stated as
follows:
X − X min
X max − X min
X −µ
′′
x =
σ
x′ =

(1)
(2)

ALMAZROI: FEDERATED MALWARE DETECTION IN FLYING AD HOC DRONE NETWORKS

9999

Fig. 1. Proposed drones-malware detection framework in a federated architecture, showing local client model updates from UAVs and global aggregation at
the server using FedAvg.

TABLE IV
D ERIVED F EATURES W ITH F ORMULAS AND D ESCRIPTIONS

feature, ensuring the accurate interpretation of the categorical
data by the model.
Feature Extraction: We derived more temporal characteristics from the timestamp feature—day, month, year, hour, and
minute—to capture temporal trends that are perhaps significant
for malware identification. This phase adds more finely-tuned
temporal information to augment the dataset.
Anomaly Detection and Removal: To increase the model’s
resilience, anomalies were found and eliminated. Particularly
suited for high-dimensional datasets, we used the Isolation
Forest method. This method selects a feature randomly and
then uses the feature’s highest and lowest values to determine
a split value. The anomaly is scored using the number of splits
needed to separate a point. A point A has an anomaly score
computed as [45]:
F(L(A))

score(A) = 2− G(M)

In terms of the feature, σ stands for the average and µ
for the variance; X min and X max represent the minimum and
maximum values, respectively.
Categorical Variables Encoding: To make the dataset
more suitable for training models, one-hot encoding was
used to convert the categorical variables into a numerical
form. Without assuming any ordinal connection, this approach
generates binary columns for every category in a categorical

(3)

The expected route length of point A is represented by
F(L(A)). In contrast, the average path length of an unsuccessful search inside a Binary Search Tree is denoted by G(M).
Augmentation of Data The problem of class imbalance
was addressed by using the Synthetic Minority Over-sampling
Technique (SMOTE), which is particularly useful for underrepresented groups. By generating supplementary synthetic
samples through interpolation between existing minority class
occurrences, SMOTE contributes to data collection equalisation in several ways. Due to this enhanced distribution, the
model can learn more efficiently from all classes, including
those that are typically disregarded. The SMOTE method
was employed to address the prevalent problem of class
imbalance in malware detection, which occurs when certain

10000

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

types of attacks occur much less frequently than others.
By extrapolating from existing cases, this method generates
synthetic examples of the minority class, contributing to a
more balanced dataset. As a result, the model becomes better
equipped to recognize underrepresented attack patterns, leading to improved detection performance across all classes.
Correlation Analysis and Feature Reduction: To improve
model efficiency and reduce redundancy, we extracted characteristics that were highly correlated with each other. For
any set of two qualities where the correlation coefficient was
more than 0.9, we removed one from consideration after
computing the correlation matrix. This stage ensures that the
dataset is compact and free from multicollinearity, which could
compromise model performance.
Temporal Feature Smoothing: We employed smoothing
methods, such as exponential and rolling averages, to enhance
the temporal properties of the data. These methods make the
patterns more apparent to the model by reducing background
noise and highlighting underlying trends. When a rolling
average is used to smooth out a temporal characteristic Z ,
the result is [47]:
Z′ =

1
W

W
−1
X

Z T −J

(4)

J =0

where W represents the size of the window, J denotes the
index, and T signifies the current time point.
By implementing these preprocessing steps, we have
successfully achieved a state where the data is pristine, standardized, enhanced with additional attributes, and free from
irregularities and duplications. This extensive preprocessing
pipeline established a solid base for efficient feature engineering and model training, ultimately improving the performance
of our drone-based malware detection models.
C. Stage 3: Feature Selection
Building an accurate and efficient machine-learning model
for drone-based malware detection depends critically on feature selection. Selecting the most relevant features will help
reduce the dataset’s dimensionality, enhance model performance, and prevent overfitting. To find the most essential
characteristics in our work, we combined embedding techniques with filter approaches, specifically tailored to our
situation.
D. Filter Methods
Filter techniques evaluate the inherent characteristics of features without using any learning approach, thereby determining their importance. These techniques provide a reasonable
starting point for features and are computationally effective.
Mutual Information: We assessed feature and target variable dependence using mutual information. This metric helps
identify relevant characteristics for malware detection by capturing the degree of knowledge gained about one variable
through another [47].


XX
P(ξ, θ )
I(4; 2) =
(5)
P(ξ, θ ) log
P(ξ ) · P(θ)
ξ ∈4 θ ∈2

The reciprocal information between the feature set 4 and
the class label set 2 is represented by I(4; 2) in this version.
The joint probability of witnessing feature ξ together with
class θ is denoted by the term P(ξ ), and the marginal probabilities of the feature and class, respectively, are denoted by
P(θ ). This metric measures how much a feature’s information
helps clarify its associated class name, shedding light on the
feature’s categorization importance.
E. Stage 4: Embedded Methods
Embedded approaches choose features throughout the
model-training process. These techniques offer a reasonable
balance between performance and computational cost, and are
less computationally demanding than wrapper techniques.
Tree-Based Methods: Feature selection is an inherent part
of tree-based algorithms like Random Forest since these
algorithms consider feature relevance when splitting nodes.
Random Forest was used to determine the most essential
features for reducing impurities. determines the significance
of features in Random Forest cite38:
Fk =

M
X

1G m (k)

(6)

m=1

in where Fk stands for the feature’s significance, M for the
total number of trees, and 1G m (k) for the feature’s importance
in tree m.
F. Hybrid Feature Selection Approach
We combined the filtering and embedding methods into a
single feature selection strategy that leveraged their strengths.
The following is the procedure to do it:
1) Initial Filtering: After initial feature filtering using
mutual information, keep only the features with high
scores.
2) Embedded Method Validation: By looking at feature
significance ratings, Random Forest can verify that the
characteristics you’ve chosen are solid and relevant.
One way to mathematically characterize the hybrid feature
selection strategy is as follows:
Hk = α · I (A; B) + β · Fk

(7)

The hybrid feature significance score for feature k, with
weights allocated to the mutual information and Random
Forest important scores, respectively, and β for the feature.
By integrating these approaches, we found a substantial
collection of characteristics that our drone-based malware
detection algorithm uses for prediction. This combined method
improves model performance while decreasing computational
complexity by selecting relevant and efficient characteristics.
G. Stage 5: ResDenseEffiNet Architecture
This section introduces the ResDenseEffiNet model,
a hybrid deep learning architecture for detecting malware in
drone-based edge systems. ResNet, DenseNet, and EfficientNet are used together to extract rich, hierarchical features
effectively. The approach utilizes a federated learning (FL)

ALMAZROI: FEDERATED MALWARE DETECTION IN FLYING AD HOC DRONE NETWORKS

10001

enhances learning efficiency. The output of the q-th dense
block is formulated as:
ψq = ϒq ([ξ1 , ξ2 , . . . , ξq−1 ])

(9)

The output of the k-th earlier layer is represented as ξk , and
[·] indicates channel-wise concatenation. The functions ϒq (·)
that make up the transformation include batch normalisation,
ReLU activation, and convolution. The model can efficiently
reuse features and maintain concise representations with this
arrangement.
3) Scalable Efficiency via EfficientNet: EfficientNet components utilize compound scaling to optimize performance and
resource utilization. This approach coordinates network depth,
breadth, and input resolution using scaling factors. Rather
than increasing these dimensions independently, the model
scales them proportionally to maintain a balanced architecture.
This strategy allows the model to achieve higher accuracy
without significantly increasing computational demands. The
relationship between these scaled dimensions is expressed as:
depth = µ · α s ,
Fig. 2.

Federated ResDenseEffiNet architecture.

architecture to facilitate collaborative training without requiring the sharing of client data, enabling real-time, privacy-aware
learning across multiple drones. The model input, λ ∈
R H ×W ×C , is a drone-acquired image or telemetry tensor with
height H , width W , and C channels. The following specialised
blocks handle this input. Figure 2 shows the internal layered
architecture of Federated ResDenseEffiNet.
1) Residual Learning via ResNet: To overcome typical
challenges, such as vanishing gradients in deep neural networks, the model integrates residual learning blocks inspired
by the ResNet architecture. These blocks are built to learn the
differences—or residuals—between the input and the desired
output, effectively enhancing the model’s ability to train deeper
layers. Instead of learning the complete transformation, the
network focuses on what needs to change from the input,
allowing for more stable and efficient learning. The output
from a residual block can be mathematically expressed as:
χ = F (λ, {i }) + λ

(8)

The input feature map is denoted by λ in this formula; the
residual function F (·) includes the activation, batch normalisation, and convolution layers, and {i } are the learnable
weights of the convolutional filters. The network can concentrate on learning differences compared to the input with
the help of the residual connection, which promotes practical
training.
2) Dense Feature Reuse via DenseNet: Following the residual stage, the output is processed through a series of densely
connected layers based on the DenseNet architecture. In this
configuration, each layer is directly connected to every previous layer, allowing the model to reuse features efficiently
and promote richer information flow. This dense connectivity
strengthens feature propagation, minimizes redundancy, and

width = ν · β s ,

resolution = ρ · γ s
(10)

The fundamental values of depth, breadth, and resolution are
µ, ν, and ρ, respectively, in this equation. With α, β, and γ
as scaling factors and s as a compound coefficient, the growth
rate is determined. Improving accuracy while maintaining
resource efficiency, this strategy ensures balanced growth of
the network across multiple dimensions.
4) End-to-End Model Architecture: The data flow in
the ResDenseEffiNet model is organized into a systematic
pipeline. Initially, the input tensor λ is processed through
residual blocks that capture high-level variations. This output is then passed through densely connected layers that
aggregate features from previous stages, enhancing representation quality. Next, EfficientNet modules refine the extracted
features by applying scalable transformations. Then, a fully
connected layer receives the feature map that has had its
dimensions reduced via global average pooling. Utilising a
softmax activation function yields the most accucategorisationation. According to mathematical definitions, this whole
transformation process is:
χ = σ (8 (GAP (S (D (F (λ))))))

(11)

The F (·) represents the residual module, D(·) the dense module, S(·) the EfficientNet module, GAP(·) the fully connected
layer, and σ (·) the softmax activation function that generates
the final class probabilities.
5) Stage 5: Federated Learning Integration: To facilitate collaborative intelligence across a network of drones,
the proposed F-ResDenseEffiNet model is deployed within
a federated learning framework. In this setup, each drone
functions as an autonomous client, training the model on
its own locally collected telemetry and network traffic data.
By routinely communicating just the learned model parameters
to a central server, privacy concerns are effectively eliminated.
This server takes drone data contribution into consideration by
weighting average client updates using the FedAvg algorithm.
The initialization and transmission of a global model ω0 to

10002

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

the clients by the central server initiates the training process. The international model is improved by aggregating
the new weights ωr from each drone after local training.
This approach ensures privacy-preserving collaboration and
maintains learning consistency even under non-identical data
distributions and limited communication bandwidth conditions
commonly encountered in Flying Ad Hoc Network (FANET)
environments.
ωt+1 =

M
X
mr
r =1

m

· ωr

(12)

With M standing for the number of client devices and m r for
the local data stored
client r , the total dataset for federated
Pby
M
training is m =
r =1 m r . The central server updates the
global model parameters and sends them to all clients as ωt+1
after update aggregation. Until the model reaches stability and
convergence, the update-and-distribute cycle is repeated.
6) Loss Function and Optimization: Reducing the discrepancy between the predicted class probabilities and the
ground-truth labels is the primary objective during training.
An accurate assessment of the model’s performance across
multiple categories is achieved by using the multi-class categorical cross-entropy loss. The loss function helps the model
improve its predictions over time by retaliating significant
differences between the actual and anticipated values. The loss
is defined mathematically as:
J =−

T X
C
X

ya,b · log( ŷa,b )

(13)

a=1 b=1

A binary indication of the right class is ya,b , the projected
probability for group b is ŷa,b , the total number of training
samples is T , and the number of output classes is C. To modify
the model’s parameters, the Adam optimizer is used. This
method enables the dynamic modification of learning rates by
using first- and second-moment estimates of gradients. The
updated rule is defined as:
b
gk
φk+1 = φk − τ · p
b
hk + ζ

TABLE V
S UMMARY OF M ATHEMATICAL S YMBOLS U SED IN R ES D ENSE E FFI N ET

(14)

A small constant ζ is added for numerical stability, the
bias-corrected first and second moment estimates are b
gk and
b
h k , the learning rate is τ , and the parameter set at iteration k
is φk . The suggested ResDenseEffiNet model amalgamates the
benefits of federated neural architectures with residual, dense,
and scalable neural designs. This integration enhances the
system’s adaptability, efficiency, and security for edge-based
intelligence in IoT applications by supporting accurate and
privacy-conscious malware detection in drone contexts.
To improve clarity, all mathematical symbols used in Equations (8)–(14) are summarized in Table V.
7) Stage 6: Hyperparameter Optimization: A hybrid
swarm-based optimization method called Adaptive
Gorilla–Rabbit Optimization (AGRO) is introduced
to fine-tune the hyperparameters of the Federated
ResDenseEffiNet model. The term “AGRO” reflects its
inspiration from two biological behaviors: the gorilla
embodies broad and dominant search abilities, ideal for

exploring global parameter spaces, while the rabbit represents
speed and agility, enabling precise local refinements. Through
the integration of these additional approaches, AGRO achieves
a harmonious equilibrium in the optimisation process, striking
a balance between exploration and exploitation. This
dual-mode mechanism enhances convergence speed and
leads to more reliable hyperparameter selection under varied
training conditions. In this model, d represents the number
of parameters being tuned, and vi ∈ Rd represents a possible
collection of hyperparameters for each agent in the population.
The efficacy of every remedy is evaluated by comparing the
cross-validated classification performance of the matching
hyperparameter-trained F-ResDenseEffiNet model.
AGRO uses AGTO-inspired movement rules to emphasise
exploration early in the search. The equation states that each
agent adjusts its location depending on population mobility
and the best-known solution:


(t+1)
(t)
(t)
(15)
vi
= v(t)
g + η1 · H − η2 · vi
(t)

In the formula, vg represents the current global best solution, H(t) models the group’s collective direction, and η1 and
η2 are random values (0, 1) that determine the effect of each
component on the new position. This approach enables the
program to explore diverse locations. The emphasis moves to
exploitation throughout training. Localised search driven by
ARO helps the top-performing half refine their rankings. Each
chosen agent’s position is refined as:


(t+1)
(t)
(t)
vi
= vi + η3 · sin(2π · η4 ) · v(t)
(16)
g − vi
In this case, η3 controls update intensity, whereas η4 simulates rabbit foraging adaptability and evasiveness by a sinusoidal function. This exploitation stage thoroughly explores

ALMAZROI: FEDERATED MALWARE DETECTION IN FLYING AD HOC DRONE NETWORKS

interesting areas of the search space, accelerating convergence to the optimal solution. AGRO successfully navigates
the high-dimensional hyperparameter space of deep learning
models by alternating between AGTO for broad exploration
and ARO for concentrated exploitation. AGRO runs locally at
each client in federated learning, allowing personalised model
adjustment without sharing raw data. In F-ResDenseEffiNet,
this protects privacy while enhancing model accuracy and
generalization across dispersed devices. Algorithm 1 describes
the tuning procedure for the proposed federated framework.
Algorithm 1 Federated Training of F-ResDenseEffiNet With
AGRO-Based Hyperparameter Tuning
1: Input: Initial global model ω0 ; number of participating
clients M; number of AGRO iterations K ; local datasets
D1 , . . . , D M
2: Output: Final optimized global model ωT
3: The central server initializes the global model ω0 and
distributes it to all clients
4: for each communication round t = 0 to T − 1 do
5:
for each client r = 1 to M in parallel do
6:
Each client generates a population of candidate
N
hyperparameter vectors {vri }i=1
7:
for each AGRO optimization step k = 1 to K do
8:
Evaluate the performance of each candidate vri
using local dataset Dr
9:
Identify the best-performing candidates to be used
in the exploitation phase
10:
Perform AGTO-based position updates to promote
broad exploration
11:
Apply ARO-based refinement to selected candidates for localized improvement
12:
end for
13:
Select the optimal hyperparameter configuration vr∗
based on AGRO results
14:
Train the F-ResDenseEffiNet model locally on Dr
using vr∗ and obtain updated weights ωr
15:
end for
16:
The server collects all local model updates and computes the new global model:
ωt+1 =

M
X
mr
r =1

m

· ωr

The updated global model ωt+1 is broadcast back to all
clients
18: end for
19: return The final global model ωT after T rounds of
training
17:

H. Performance Evaluation Metrics
Several performance measures are used to determine how
well and quickly the suggested ResDenseEffiNet model can
find malware on drones. These measurements accurately represent the model’s ability to detect malware while minimizing
both false positives and false negatives. Accuracy, Precision,

Fig. 3.

10003

Performance evaluation metrics.

memory, F1-score, ROC-AUC, and computing speed were the
primary measures used to evaluate the study’s performance.
Figure 3 describes the performance metrics for evaluation.
Real-time drone models need computing efficiency and
precision. Minimising inference time and memory utilisation
are critical for achieving real-time responses and running
models on resource-limited devices, such as drones. Model
complexity, including the number of parameters and layers,
affects both training and inference delays; therefore, complexity and performance must be balanced. This is supplemented
by the Detection Effectiveness Index (DEI) for intrusion detection systems. In dynamic contexts like UAV networks, DEI
utilizes Accuracy, Precision, Recall, and F1-Score to evaluate
a model’s detection capabilities, as shown in Equation 17.
DEI = α · Accuracy+β · Precision+γ · Recall+δ · F1-Score
(17)
The weights allocated to each measure, representing their
relative relevance in the context of the particular application,
are α, β, γ , and δ. The system’s priorities under evaluation
may dictate adjustments to these weights.
IV. S IMULATION R ESULTS
This section evaluates the F-ResDenseEffiNet model with
AGRO optimisation approach in a federated learning configuration. A complete assessment is provided. Four popular
intrusion detection datasets—DBMD24, CICIDS2017, NSLKDD, and KDDCup99—were distributed among clients to
emulate real-world, decentralized drone scenarios. Python and
TensorFlow 2.x were used to implement all models on a workstation with 32GB of RAM. The training approach included
60 epochs per client, a 10−4 to 10−2 learning rate, and
32 to 128 batch sizes. Accuracy, precision, recall, F1-score,
convergence behaviour, and model stability are evaluated.
Statistical tests, sensitivity analysis, ablation experiments, and
fairness assessments verified the framework’s generalisation
and resilience across multiple network circumstances.
Figure 4 shows accuracy trends for four clients processing different datasets (DBMD, CICIDS2017, NSL-KDD, and
KDDCup99) during 90 communication rounds in a federated
learning scenario. Increasing communication leads to sustained
accuracy gains, reaching high levels exceeding 97% for all
customers. The use of multiple line styles and markers helps
distinguish each client’s trajectory. The model’s client-wide
performance consistency proves its generalisation of heterogeneous data. This graphic shows that the F-ResDenseEffiNet
model can withstand divergence in federated settings due to
local data distributions and separate optimisations. Collaborative training, fairness, and synchronisation need client-wise

10004

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

Fig. 6. Comparative impact of optimization algorithms on training efficiency
and model stability.
Fig. 4.

Accuracy of client-wise over communication rounds.

Fig. 5.

Model accuracy and loss over epochs.

accuracy monitoring. The figure shows that, across various
network behaviors and attack characteristics, the suggested
technique enables decentralized training without sacrificing
detection performance.
The development of training and validation accuracy, as well
as loss across 60 epochs, is shown in Figure 5. By the
last epoch, the model improves in both measures, with loss
decreasing to 0.02 and accuracy reaching 98%. Both error
minimisation and performance improvement are seen in the
dual-axis format. The alignment of the accuracy curve between
training and validation shows the model’s capacity to generalise across unseen data. The optimisation technique decreases
variance, since minor oscillations before epoch 30 are followed
by steady convergence. Verifying model convergence, learning
dynamics, and training stability requires this figure. It shows
that AGRO-based parameter adjustment and hybrid design
allow effective learning across epochs. Both loss and accuracy
curves support the model’s architecture, showing that it can
achieve optimal operational capacity without overfitting or
underfitting during training.
Table VI presents a detailed performance comparison
between the proposed F-ResDenseEffiNet + AGRO model and
20 baseline methods across four widely used intrusion detection datasets: DBMD, CICIDS2017, NSL-KDD, and KDDCup
99. To ensure fairness, models marked with an asterisk (*)
were re-implemented and evaluated under a consistent federated learning configuration, which included five clients, a batch
size of 64, 10 communication rounds, and a learning rate
of 0.001. The performance results for the remaining models
were drawn directly from their original publications. Across all
datasets, our proposed model demonstrates consistently supe-

Fig. 7. Client-level influence on federated learning dynamics and divergence
behavior.

rior results, with accuracy, precision, and F1-scores exceeding
96.5%. Notably, on the DBMD dataset, it reaches an accuracy
of 98.7%, showcasing its strong alignment with drone-based
anomaly detection tasks. Compared to traditional models like
CNN + LSTM and GRU, F-ResDenseEffiNet + AGRO offers
an improvement of nearly 8%. Although federated approaches
such as FedGAN and FedMalDE show moderate gains over
centralized baselines, they still do not match the performance
of our hybrid framework. These findings underline the model’s
robustness, adaptability, and effectiveness in handling diverse
intrusion patterns across heterogeneous environments.
In Figure 6, five optimisation methods—Adagrad, Adam,
RMSProp, SGD, and AH-GTO—are compared based on
accuracy, convergence time, and stability score. The best
optimizer is the AH-GTO, with 98.7% accuracy, 35-second
convergence, and 98% stability. SGD, the slowest and least
stable optimizer, exhibits larger convergence delays and poorer
performance. This comparison shows that the suggested optimiser increases accuracy, convergence, and consistency across
iterations. This figure must be shown to support tweaking
the F-ResDenseEffiNet model using AH-GTO. From harmonized measurements, the graph illustrates how numerous
optimizers affect federated model training, particularly in
resource-constrained drone contexts where stability and speed
are crucial.
Figure 7 shows how client contributions affect model divergence in federated learning. The volume of data and the
relevance of updates for each client impact the global model.
Client 3 has the lowest contribution (0.20) and divergence
(0.07), whereas Client 2 contributes the most (0.28) and

ALMAZROI: FEDERATED MALWARE DETECTION IN FLYING AD HOC DRONE NETWORKS

10005

TABLE VI
P ERFORMANCE C OMPARISON (M EAN ± S TANDARD D EVIATION ) OF F-R ES D ENSE E FFI N ET + AGRO AGAINST BASELINE M ETHODS ON F OUR
DATASETS , I NCLUDING P -VALUES FOR S TATISTICAL S IGNIFICANCE

diverges the most (0.11). This inverse contribution-divergence
relationship shows local data heterogeneity and learning
dynamics. Both indicators are readily visible on the dualaxis visualisation, making client-specific implications easier
to understand. Understanding model consistency among participants, fairness, and adaptive weighting or client selection
depends on this figure. Personalised learning should not
degrade global models or cause instability in collaborative
contexts; hence, divergence must be monitored when client
data distributions are non-identical.
The
deployment
feasibility
of
the
proposed
F-ResDenseEffiNet model was assessed using an edge-level
UAV computing platform—specifically, the NVIDIA Jetson
Nano. The model has a compact footprint of 14.2 MB
and performs inference with approximately 305 million
floating-point operations (MFLOPs) per forward pass.
It achieves an average latency of 62 milliseconds per
sample, which comfortably meets the real-time processing
requirements of drone-based applications. When compared to
other lightweight models, such as MobileNetV2 (13.6 MB,
238 MFLOPs, 49 ms) and SqueezeNet (4.8 MB, 833 MFLOPs,
42 ms), F-ResDenseEffiNet offers superior detection accuracy
while maintaining a moderate computational overhead. These
results demonstrate that the model strikes a practical balance
between performance and resource efficiency, making it
well-suited for federated learning scenarios in UAV networks
where hardware constraints are a critical consideration.
Ablation analysis on the DBMD dataset reveals the performance effect of F-ResDenseEffiNet + AGRO architecture
and optimization components (Table VII). Backbones such as
ResNet, DenseNet, and EfficientNet achieve 80%–83% accuracy, while their combinations further improve this accuracy.
Combining all three networks without AGRO or federated
learning improves performance to 87.6%. Federated integra-

TABLE VII
A BLATION S TUDY OF F-R ES D ENSE E FFI N ET + AGRO C OMPONENTS ( ON
DBMD DATASET )

tion without AGRO boosts accuracy to 91.4%. The optimiser
contributes to the centralised version with AGRO’s 94.1%.
Finally, backbone fusion, adaptive optimisation, and federated
training work together to provide the most accurate model at
98.7%. Each model design option is justified and quantified
in this table to determine performance.
To assess whether the F-ResDenseEffiNet model can be
practically deployed on drones with limited computational
resources, we tested its performance on an edge-grade
device—specifically, the NVIDIA Jetson Nano (4GB RAM).
The model demonstrated an average inference time of approximately 42 milliseconds per sample, used around 17.6 MB
of memory, and operated with approximately 2.1 million
parameters and 92 MFLOPs. Although the architecture combines multiple deep learning backbones, it remains lightweight

10006

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

TABLE VIII
C OMPARISON OF O PTIMIZATION M ETHODS FOR
H YPERPARAMETER T UNING

Fig. 8. ROC curves on DBMD dataset for federated and non-federated
malware detection models.
TABLE IX
M ULTI -TASK C LASSIFICATION P ERFORMANCE OF F-R ES D ENSE E FFI N ET
+ AGRO ACROSS B ENCHMARK DATASETS

Fig. 9.

ROC of F-ResDenseEffiNet on the CICIDS2017 dataset.

due to EfficientNet’s compound scaling and the incorporation
of dropout layers, which reduce complexity. These results
confirm that the model can run efficiently on embedded
drone hardware, making it well-suited for real-time intrusion
detection in Flying Ad Hoc Network (FANET) environments
where fast, low-power inference is essential.
ROC curves of 17 malware detection models are shown
in Figures 8 and 9, comparing their performance on the
DBMD and CICIDS 2017 datasets. With an AUC of 0.98,
F-ResDenseEffiNet exhibits good classification sensitivity and
specificity. With AUC values between 0.85 and 0.89, GRU,
CNN+LSTM, and Ensemble Learning compete with baselines. Random Forest and metaheuristic hybrids have low
detection capability, but FedMalDE and FedGAN generalise better under privacy-preserving restrictions. The ROC
curves illustrate model performance across all false positive
rates, revealing trade-offs between sensitivity and false alarm
rates. This graphic illustrates the comparative resilience and
superiority of the suggested model against network threats.
It facilitates objective model selection for federated drone
security systems and visualizes model behavior in real-world
attack scenarios.
AGRO was used to optimize learning rate, dropout rate,
batch size, and weight decay to improve model performance.
The best results were obtained after iterative adjustment with

a learning rate of 0.001, a dropout rate of 0.3, a batch
size of 64, and a weight decay factor of 0.0001. These
values offered the most effective balance between fast convergence, high detection accuracy, and reliable generalization
across the diverse and decentralized client environments in the
federated setting. The table VIII compares the performance
of several hyperparameter optimisation methods on the FResDenseEffiNet architecture. Adaptive Hybrid Golden-Tiger
Optimisation (AH-GTO) outperforms all other algorithms
in terms of accuracy (98.7%), convergence time (42.6s),
and cross-run stability (97.9%). The competing methods,
ESOA and MGO, have reasonable accuracy but exhibit more
extended convergence periods and poorer consistency. With
accuracy under 93%, FOX and GJO are less sturdy. The
unoptimised model has the lowest accuracy (87.6%) and
consistency. These findings support the use of AH-GTO for
accurate, fast, and repeatable training convergence across
heterogeneous federated clients.
The proposed model is evaluated in Table IX for its
ability to perform classification tasks, including malicious payload identification, attack type prediction, sandbox analysis,

ALMAZROI: FEDERATED MALWARE DETECTION IN FLYING AD HOC DRONE NETWORKS

10007

TABLE X
F EDERATED P ERFORMANCE E VALUATION ACROSS D ISTRIBUTED C LIENTS
U SING F-R ES D ENSE E FFI N ET + AGRO

Fig. 11.
Confusion matrix of F-ResDenseEffiNet on the CICIDS2017
(Benchmark dataset).

Fig. 10.

Confusion matrix of F-ResDenseEffiNet on the DBMD dataset.

and signature matching, on four benchmark datasets. The
F-ResDenseEffiNet + AGRO model performs well on the
DBMD dataset, with F1-scores over 98.7% across all tasks.
The model performs over 93% across all measures on
CICIDS2017, NSL-KDD, and KDDCup99 datasets. The
model’s robust generalisation for varied malware-related
subtasks and appropriateness for real-world cybersecurity
deployments with single and multi-output prediction targets
are confirmed by these findings.
Table X displays the federated performance of the FResDenseEffiNet + AGRO model across four clients, each
with a unique benchmark dataset. All clients performed well in
categorization, with Client 1 (DBMD) achieving an excellent
accuracy of 98.7%. Clients with 96.5% to 97.9% accuracy
show similar findings. The proposed architecture is resilient
in heterogeneous federated contexts, adapting to different data
distributions while maintaining optimal detection effectiveness
without compromising client-level privacy or training convergence.
The confusion matrix for the DBMD dataset analysed
using the proposed F-ResDenseEffiNet is shown in Figure 10.
Over 41,300 samples were tested, and the matrix accurately
classified five main malware types. Small off-diagonal pieces
indicate misclassifications, whereas diagonal dominance suggests accurate predictions. For all classes, false positives and
negatives are < 5, indicating robust model calibration. Drone
cybersecurity requires well-separated malware and benign
classes to prevent false warnings. The approach effectively
separates difficult categories, such as botnets and DDoS, well.

Fig. 12. Confusion matrix of F-ResDenseEffiNet on the NSL-KDD (Benchmark dataset).

This chart illustrates label-wise performance and demonstrates
that the classifier generalizes successfully across varied drone
communication settings without class bias.
The confusion matrix of F-ResDenseEffiNet, as tested
on the CICIDS2017 dataset, is shown in Figure 11.
Benign, DDoS/DoS, Brute-force/Phishing, Botnet, and Malware (Other) were previously 14 distinct traffic classes in
CICIDS2017; however, these were merged into five larger categories to better reflect our focus on malware detection: Web
Attacks, Infiltration, DoS Hulk, FTP-Patator, SSH-Patator,
Botnet ARES, and others. Results show good categorisation
performance, with most samples correctly classified and few
cross-category misclassifications. For example, the model’s
ability to distinguish between Botnet and DDoS traffic demonstrates its effectiveness in handling various types of attacks.
Moreover, the results indicate that the proposed model is valid
for both datasets, explicitly focusing on drones, and serves
as a well-established benchmark. Depicting its versatility and
reliability in many circumstances for detecting intrusions and
viruses.

10008

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

TABLE XII
FAIRNESS E VALUATION IN F EDERATED L EARNING C LIENTS

Fig. 13.
Confusion matrix of F-ResDenseEffiNet on the KDDCup99
(Benchmark dataset).
TABLE XI
AVERAGE S TATISTICAL A NALYSIS R ESULTS

Figure 12 shows the confusion matrix of F-ResDenseEffiNet
on the NSL-KDD dataset. We include this benchmark to
demonstrate how the proposed method performs on a classic
intrusion detection dataset beyond our main drone-oriented
scenarios. NSL-KDD uses the standard five-class taxonomy:
Normal, DoS, Probe, R2L (Remote to Local), and U2R (User
to Root). The clear diagonal structure of the matrix indicates
that the majority of records are correctly classified, with
only a small number of misclassifications. Some confusion is
expected between closely related categories, such as R2L and
U2R; however, the overall false-positive and false-negative
rates remain very low. These findings suggest that the
model transfers well to legacy benchmarks, reinforcing its
robustness and adaptability across diverse intrusion detection
environments.
The confusion matrix for KDDCup99 is shown in Figure 13,
which demonstrates the performance of F-ResDenseEffiNet on
a highly benchmarked intrusion dataset. The classifier achieves
over 8,240 correct predictions per class, despite the dataset facing challenges related to age and imbalance. There are hardly
any values outside the diagonal; in fact, there are no more
than seven misclassified cases in the whole matrix. Classical
intrusion recordings often include noisy and highly redundant
feature spaces, which the model can adjust to, as shown in this
figure. The matrix shows that the federated model can maintain
accuracy even when faced with varied clients’ limited label
distributions, thanks to its balanced sensitivity and specificity.
In Table XI, the F-ResDenseEffiNet + AGRO framework
is statistically compared to different benchmark models using
various hypothesis testing methods. The metrics include Pearson’s, Spearman’s, and Kendall’s correlation coefficients for

monotonic and linear correlations, as well as parametric and
non-parametric tests such as the Chi-Squared test, Student’s
t-test, ANOVA, and Kruskal-Wallis test. The suggested model
surpasses all baselines in each statistical test, with strong
correlation (Pearson’s = 0.94) and excellent agreement in
ranking measures (Spearman’s = 0.91, Kendall’s = 0.89).
It also has the most significant impact in group comparison tests, such as ANOVA (0.92) and Kruskal-Wallis (0.91),
demonstrating steady, statistically substantial gains across runs
and datasets. The model’s resilience and dependability make it
suitable for federated malware classification in heterogeneous
drone-Internet of Things (IoT) scenarios.
The assessment of fairness among participating clients in
the federated learning setup utilising the F-ResDenseEffiNet
+ AGRO model is shown in Table XII. Four criteria about
fairness are included in the evaluation: accuracy variance,
participation rate, Kullback-Leibler (KL) divergence for data
skew, and client contribution ratings. The local models are
converging uniformly among customers, since the accuracy
variance is continuously low (mean = 0.38%). Minimal data
skew values (mean KL divergence = 0.15), indicating that the
data is evenly distributed throughout the nodes. To guarantee
that all customers are fairly exposed to worldwide updates,
we ask that they maintain full involvement (100%) throughout
the training process. Normalised aggregate weights, from
which contribution scores are calculated, show a low standard
deviation (0.03) and a balanced distribution around a mean
of 0.25, indicating a proportionate effect without client dominance. The proposed federated framework must treat diverse
clients fairly to be deployed in real-world decentralized drone
and IoT systems, and these fairness statistics demonstrate that
it does just that.
Figure 14 presents the 3D sensitivity analysis of the FResDenseEffiNet + AGRO model, illustrating how learning
rates and batch sizes impact classification accuracy. The surface map shows a peak performance zone at 0.001 learning
rate and 64 batch size, when the model achieves 98.7%
accuracy. Due to instability and underfitting in particular areas,
performance gradually declines for both minimal and high
learning rates, as well as small batch sizes. Larger batch sizes
and moderate learning rates provide more consistent results,
indicating the model’s resilience to mini-batch granularity

ALMAZROI: FEDERATED MALWARE DETECTION IN FLYING AD HOC DRONE NETWORKS

Fig. 14. 3D Sensitivity analysis of the proposed F-ResDenseEffiNet + AGRO
model across varying learning rates and batch sizes.

during federated training. The hyperparameter tweaking assistance in this figure is crucial for efficient model deployment
in resource-constrained federated systems.
Overall, the proposed F-ResDenseEffiNet + AGRO framework demonstrates consistent and superior performance across
all evaluated datasets and metrics. It maintains an average
accuracy of 97.6%, showing minimal variation across different clients and classification tasks. This strong performance
is driven by the integration of hybrid deep learning backbones, the privacy-preserving nature of federated learning, and
the adaptive hyperparameter tuning provided by the AGRO
algorithm. In addition to accuracy, the model’s reliability and
stability are further supported by thorough statistical analysis
and fairness evaluations, highlighting its practical readiness
for deployment in real-world drone-based intrusion detection
environments.
A. Novel Insights From Implementation
Beyond reporting accuracy, precision, and other metrics,
the implementation of the proposed F-ResDenseEffiNet model
with AGRO optimisation revealed several novel insights that
add both scientific value and practical relevance. First, testing
across four heterogeneous datasets, DBMD, CICIDS2017,
NSL-KDD, and KDDCup99, showed that the framework
maintains high accuracy and stable convergence in federated
settings, even when clients rely on a mix of modern and
legacy benchmarks. This demonstrates that the model is not
restricted to a specific environment but can generalise across
diverse network behaviours and attack patterns. Second, the
Adaptive Gorilla–Rabbit Optimisation (AGRO) consistently
outperformed standard optimisers such as SGD, RMSProp,
and Adam, delivering faster convergence and greater stability across runs. These improvements are especially valuable
in resource-constrained UAV and IoD environments, where
reducing communication overhead and energy consumption is
critical.
Third, client-level analysis revealed a vital trade-off: clients
contributing larger updates also exhibited higher divergence

10009

from the global model. This highlights the need for adaptive
weighting or dynamic participation strategies to ensure fairness
and prevent instability in decentralised UAV systems. Fourth,
ablation experiments confirmed the importance of combining
all three design choices: backbone fusion, federated training, and adaptive optimisation. Each component improved
accuracy on its own, but their integration provided the most
significant performance gains, validating the hybrid design of
the proposed framework.
Fifth, edge-level deployment tests on an NVIDIA Jetson Nano confirmed that the model can run in real time
with low latency and modest memory usage. This shows
that the framework is not only accurate in theory but
also practical for mission-critical drone operations in realworld settings. Finally, re-simulated confusion matrices from
benchmark datasets provided stronger interpretability. While
older datasets, such as NSL-KDD, remained challenging
in fine-grained categories like R2L and U2R, the model
performed exceptionally well on modern threats, clearly distinguishing categories like DDoS and Botnet in CICIDS2017.
This indicates that the architecture is well-suited for contemporary malware scenarios while remaining compatible with
older benchmarks.
Taken together, these insights demonstrate that the proposed
framework advances the state of the art by offering more than
just high detection rates; it also delivers fairness, scalability,
deployment feasibility, and interpretability, making it a practical solution for federated security in drone and IoD networks.
B. Limitations and Validity of Experimental Results
Although the F-ResDenseEffiNet framework has achieved
promising results across multiple benchmark intrusion detection datasets, several limitations must be acknowledged to
contextualize the findings. First, the datasets utilized—such as
DBMD24 and CICIDS2017—are comprehensive and widely
accepted, yet they do not entirely reflect the real-world conditions of drone-based environments. Live FANET operations
often encounter challenges such as intermittent connectivity,
adversarial interference, and unpredictable traffic behaviors
that are difficult to replicate in fully controlled benchmark
scenarios. Second, while the framework’s computational performance has been validated on edge-level hardware, such as
the NVIDIA Jetson Nano, its suitability for ultra-lightweight
microcontrollers remains untested. This can present challenges
for large-scale deployments in drone fleets, particularly those
with severe power and memory limitations.
Third, the Adaptive Gorilla–Rabbit Optimization (AGRO)
algorithm, though effective in accelerating convergence and
improving generalization, can exhibit sensitivity to its initial
parameter configuration. This could lead to suboptimal performance if not carefully tuned for different deployment contexts,
especially in environments characterized by high client variability or fluctuating communication bandwidth. Finally, the
federated learning setup was simulated under realistic yet
synthetic non-IID data distributions. While the design aimed
to mimic operational diversity, actual drone deployments can
introduce further heterogeneity and unpredictability that warrant live validation.

10010

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

Despite these constraints, the experimental setup, including
extensive cross-dataset testing, ablation studies, fairness evaluation, and statistical analysis, provides a sound and reliable
basis for assessing the model’s effectiveness under structured
conditions. Future work will focus on deploying the system in
physical drone networks to evaluate performance under actual
environmental dynamics.
V. C ONCLUSION
This study introduces F-ResDenseEffiNet, a federated deep
learning framework designed to detect malware in drone
networks while safeguarding data privacy. By combining the
strengths of ResNet, DenseNet, and EfficientNet, the model
effectively captures both spatial and semantic patterns while
maintaining computational efficiency for edge-based environments. Leveraging federated learning, the system allows
decentralized drones to collaboratively train a shared model
without exchanging sensitive raw data, ensuring both scalability and privacy across distributed clients. To further
enhance learning performance, an advanced dual-phase optimization technique—AGRO (Adaptive Hybrid Gorilla–Rabbit
Optimization)—is employed, which balances exploration and
exploitation to support faster and more stable convergence.
Experiments conducted on four well-established intrusion
detection datasets—DBMD24, CICIDS2017, NSL-KDD, and
KDDCup99—demonstrated consistently high accuracy, precision, recall, and F1 Scores, all exceeding 98.5%. Ablation
studies, statistical analysis, sensitivity assessments, and fairness evaluations illustrate the framework’s resilience and
flexibility in many operating settings. Beyond detection accuracy, we also explored practical aspects of real-world UAV
deployment. Although federated learning helps reduce bandwidth by transmitting only model updates, it still introduces
trade-offs in energy usage and communication load. Our
evaluations indicate that, with a moderate batch size of 64 and
an update frequency of once every 10 epochs, each communication round consumes less than 1.5 MB of bandwidth and
approximately 3–5% of a drone’s battery capacity. The use
of EfficientNet scaling and flexible communication intervals
helps to keep these overheads manageable. Nonetheless, for
mission-critical or large-scale drone swarms, further refinements, such as energy-aware client selection, compressed
update strategies, or adaptive scheduling, are necessary.
While the proposed system performs well in aerial drone
environments, its hybrid complexity can limit its deployment
in highly constrained edge settings. Moreover, its applicability
to other domains such as smart grids or healthcare IoT remains
to be fully validated. Future research will focus on enhancing adversarial robustness, minimizing the model footprint
for ultra-lightweight deployment, and evaluating cross-domain
generalizability in diverse federated environments. Overall, the
results affirm F-ResDenseEffiNet + AGRO as a reliable, scalable, and privacy-conscious foundation for advanced malware
detection in decentralized drone-based networks.
R EFERENCES
[1] A. Derhab et al., “Internet of drones security: Taxonomies, open
issues, and future directions,” Veh. Commun., vol. 39, Feb. 2023,
Art. no. 100552.

[2] O. I. Falowo, M. Ozer, C. Li, and J. B. Abdo, “Evolving malware
and DDoS attacks: Decadal longitudinal study,” IEEE Access, vol. 12,
pp. 39221–39237, 2024.
[3] F. Xu, H.-C. Yang, and M.-S. Alouini, “Energy consumption minimization for data collection from wirelessly-powered IoT sensors:
Session-specific optimal design with DRL,” IEEE Sensors J., vol. 22,
no. 20, pp. 19886–19896, Oct. 2022, doi: 10.1109/JSEN.2022.3205017.
[4] F. Xu et al., “Multi-UAV assisted mixed FSO/RF communication network for urgent tasks: Fairness oriented design with DRL,” IEEE Trans.
Veh. Technol., vol. 74, no. 1, pp. 1736–1741, Jan. 2025.
[5] F. Basholli, A. Daberdini, and A. Basholli, “Detection and prevention
of intrusions into computer systems,” Adv. Eng. Days (AED), vol. 6,
pp. 138–141, May 2023.
[6] D. P. Srirangam, K. Hemalatha, A. Vajravelu, and N. A. Kumar, “Safety
and security issues in employing drones,” in Wireless Networks: Cyber
Security Threats and Countermeasures. Cham, Switzerland: Springer,
2023, pp. 103–131.
[7] T. Radivilova et al., “Statistical and signature analysis methods of
intrusion detection,” Inf. Secur. Technol. Decentralized Distrib. Netw.,
vol. 2022, pp. 115–131, Jul. 2022.
[8] S. Huang, C. Sun, and D. Pompili, “Meta-ETI: Meta-reinforcement
learning with explicit task inference for AAV-IoT coverage,” IEEE
Internet Things J., vol. 12, no. 13, pp. 23852–23865, Jul. 2025, doi:
10.1109/JIOT.2025.3553808.
[9] Y. Guo, “A review of machine learning-based zero-day attack detection: Challenges and future directions,” Comput. Commun., vol. 198,
pp. 175–185, Jan. 2023.
[10] A. A. Almazroi and N. Ayub, “Enhancing smart IoT malware detection:
A GhostNet-based hybrid approach,” Systems, vol. 11, no. 11, p. 547,
Nov. 2023.
[11] D. Lee, S. Malacarne, and E. Aune, “Explainable time series anomaly
detection using masked latent generative modeling,” Pattern Recognit.,
vol. 156, Dec. 2024, Art. no. 110826.
[12] Y. Abbas, A. A. Alarfaj, E. A. Alabdulqader, A. Algarni, A. Jalal,
and H. Liu, “Drone-based public surveillance using 3D point clouds
and neuro-fuzzy classifier,” Comput., Mater. Continua, vol. 82, no. 3,
pp. 4759–4776, 2025.
[13] T. Li, A. K. Sahu, A. Talwalkar, and V. Smith, “Federated learning:
Challenges, methods, and future directions,” IEEE Signal Process. Mag.,
vol. 37, no. 3, pp. 50–60, May 2020.
[14] P. Sinha, D. Sahu, S. Prakash, T. Yang, R. S. Rathore, and V. K. Pandey,
“A high performance hybrid LSTM CNN secure architecture for IoT
environments using deep learning,” Sci. Rep., vol. 15, no. 1, p. 9684,
Mar. 2025.
[15] L. Sana et al., “Securing the IoT cyber environment: Enhancing intrusion
anomaly detection with vision transformers,” IEEE Access, vol. 12,
pp. 82443–82468, 2024.
[16] R. Esmaeilyfard, Z. Shoaei, and R. Javidan, “A lightweight and efficient
model for botnet detection in IoT using stacked ensemble learning,” Soft
Comput., vol. 29, no. 1, pp. 1–13, Jan. 2025.
[17] R. Jablaoui and N. Liouane, “Network security based combined CNN–
RNN models for IoT intrusion detection system,” Peer-Peer Netw. Appl.,
vol. 18, no. 3, p. 129, May 2025.
[18] Q. Xin, Z. Xu, L. Guo, F. Zhao, and B. Wu, “IoT traffic classification and
anomaly detection method based on deep autoencoders,” Appl. Comput.
Eng., vol. 69, no. 1, pp. 64–70, Jul. 2024.
[19] P. Kairouz et al., “Advances and open problems in federated learning,”
Found. Trends Mach. Learn., vol. 14, no. 1, pp. 1–210, 2021.
[20] C. Yanmin, A. Sarkar, J. M. Zain, A. Bhar, A. Noorwali, and
K. M. Othman, “Leveraging LSTM and GRU-based deep neural coordination in intelligent transportation to strengthen security in the Internet
of Vehicles,” Int. J. Mach. Learn. Cybern., vol. 16, no. 4, pp. 1–37,
Apr. 2025.
[21] J.-J. Xiong and Y. Chen, “RBFNN-based parameter adaptive sliding
mode control for an uncertain TQUAV with time-varying mass,” Int. J.
Robust Nonlinear Control, vol. 35, no. 11, pp. 4658–4668, Jul. 2025,
doi: 10.1002/rnc.7932.
[22] M. Alshehri et al., “Unmanned aerial vehicle based multi-person detection via deep neural network models,” Frontiers Neurorobotics, vol. 19,
Apr. 2025, Art. no. 1582995.
[23] B. S. Purkayastha, M. M. Rahman, and M. Shahpasand, “Android
malware detection using machine learning and neural network: A hybrid
approach with federated learning,” in Proc. 7th Int. Conf. Adv. Commun.
Technol. Netw. (CommNet), Dec. 2024, pp. 1–5.

ALMAZROI: FEDERATED MALWARE DETECTION IN FLYING AD HOC DRONE NETWORKS

[24] G. Xu, L. Lei, Y. Mao, Z. Li, X.-B. Chen, and K. Zhang, “CBRFL: A
framework for committee-based Byzantine-resilient federated learning,”
J. Netw. Comput. Appl., vol. 238, Jun. 2025, Art. no. 104165.
[25] A. A. Almazroi and N. Ayub, “Deep learning hybridization for improved
malware detection in smart Internet of Things,” Sci. Rep., vol. 14, no. 1,
p. 7838, Apr. 2024.
[26] A. A. Alshdadi, A. A. Almazroi, N. Ayub, M. D. Lytras, E. Alsolami,
and F. S. Alsubaei, “Big data-driven deep learning ensembler for DDoS
attack detection,” Future Internet, vol. 16, no. 12, p. 458, Dec. 2024.
[27] T. Landman and N. Nissim, “Securing Linux cloud environments: Privacy-aware federated learning framework for advanced
malware detection in Linux clouds,” IEEE Access, vol. 13,
pp. 30377–30394, 2025.
[28] A. A. Alshdadi et al., “Federated deep learning for scalable and privacypreserving distributed denial-of-service attack detection in Internet of
Things Networks,” Future Internet, vol. 17, no. 2, p. 88, Feb. 2025.
[29] Z. Çiplak, K. Yıldız, and Ş. Altınkaya, “FEDetect: A federated learningbased malware detection and classification using deep neural network
algorithms,” Arabian J. Sci. Eng., vol. 50, no. 19, pp. 1–28, Oct. 2025.
[30] R. Bhavani and V. Sankaradass, “FedL_DBNFSpinalNet based malware
detection in IoT devices,” Int. J. Mach. Learn. Cybern., vol. 16, nos. 7–8,
pp. 1–19, Aug. 2025.
[31] G. Sun, G. Zhu, D. Liao, H. Yu, X. Du, and M. Guizani, “Cost-efficient
service function chain orchestration for low-latency applications in NFV
networks,” IEEE Syst. J., vol. 13, no. 4, pp. 3877–3888, Dec. 2019.
[32] F. S. Alsubaei, A. A. Almazroi, W. S. Atwa, A. A. Almazroi, N. Ayub,
and N. Z. Jhanjhi, “BERT ensemble based MBR framework for Android
malware detection,” Sci. Rep., vol. 15, no. 1, p. 14027, Apr. 2025.
[33] P. Hao, Z. Yan, and H. Wen, “Privacy-preserving NILM:
A self-alignment source-aware domain adaptation approach,”
IEEE Trans. Instrum. Meas., vol. 74, pp. 1–12, 2025, doi:
10.1109/TIM.2025.3542871.
[34] M. Zhang, E. Wei, R. Berry, and J. Huang, “Age-dependent differential
privacy,” IEEE Trans. Inf. Theory, vol. 70, no. 2, pp. 1300–1319,
Feb. 2024, doi: 10.1109/TIT.2023.3340147.
[35] G. S. Kumar, K. Premalatha, G. U. Maheshwari, P. R. Kanna, G. Vijaya,
and M. Nivaashini, “Differential privacy scheme using Laplace mechanism and statistical method computation in deep neural network for
privacy preservation,” Eng. Appl. Artif. Intell., vol. 128, Feb. 2024,
Art. no. 107399.
[36] T. M. Nithya, P. Dhivya, S. N. Sangeethaa, and P. R. Kanna, “TBMFCC multifuse feature for emergency vehicle sound classification
using multistacked CNN—Attention BiLSTM,” Biomed. Signal Process.
Control, vol. 88, Feb. 2024, Art. no. 105688.
[37] G. S. Kumar, K. Premalatha, G. U. Maheshwari, and P. R. Kanna, “No
more privacy concern: A privacy-chain based homomorphic encryption scheme and statistical method for privacy preservation of user’s
private and sensitive data,” Expert Syst. Appl., vol. 234, Dec. 2023,
Art. no. 121071.

10011

[38] M. Aldossary, I. Alzamil, and J. Almutairi, “Enhanced intrusion detection in drone networks: A cross-layer convolutional attention approach
for drone-to-drone and drone-to-base station communications,” Drones,
vol. 9, no. 1, p. 46, Jan. 2025.
[39] A. Kumar, V. Kumar, M. Kumar, and R. Sharma, “AI techniques for
malware detection in drone communication and security,” Int. J. Environ.
Sci., vol. 11, no. 3s, pp. 411–424, 2025.
[40] A. Alzahrani, “Novel approach for intrusion detection attacks
on small drones using ConvLSTM model,” IEEE Access,
vol. 12, pp. 149238–149253, 2024, doi: 10.1109/ACCESS.2024.
3471806.
[41] A. Alsumayt et al., “Detecting denial of service attacks (DoS) over the
Internet of Drones (IoD) based on machine learning,” Sci, vol. 6, no. 3,
p. 56, Sep. 2024.
[42] S. Sikandar, “Drone-based malware detection (DBMD) [data set],” Kaggle, 2024, doi: 10.34740/KAGGLE/DSV/9045375. [Online]. Available:
https://www.kaggle.com/datasets/nasirayub2/drone-based-malware-dete
ction-dbmd
[43] H. A. A. Hassan, “Exploring lightweight deep learning techniques for
intrusion detection systems in IoT networks: A survey,” J. Electr. Syst.,
vol. 20, no. 4, pp. 1944–1958, Apr. 2024.
[44] R. R. R. Robinson, K. P. A. Madhav, and C. Thomas, “Improved
minority attack detection in intrusion detection system using efficient
feature selection algorithms,” Expert Syst., vol. 41, no. 7, pp. e1354–6,
Jul. 2024.
[45] A. Tawakuli, B. Havers, V. Gulisano, D. Kaiser, and T. Engel, “Survey:
Time-series data preprocessing: A survey and an empirical analysis,” J.
Eng. Res., vol. 13, no. 2, pp. 674–711, Jun. 2025.
[46] J. Jose and J. E. Judith, “Unveiling the IoT’s dark corners: Anomaly
detection enhanced by ensemble modelling,” Automatika, vol. 65, no. 2,
pp. 584–596, Apr. 2024.
[47] Y. Wang et al., “Deeply integrated autoencoder-based anomaly detection and critical parameter identification for unmanned aerial vehicle
actuators,” IEEE Sensors J., vol. 24, no. 15, pp. 24905–24920,
Aug. 2024.
[48] Y. Mao et al., “A novel mooring system anomaly detection framework
for SEMI based on improved residual network with attention mechanism and feature fusion,” Rel. Eng. Syst. Saf., vol. 245, May 2024,
Art. no. 109970.
[49] Q. Liu and C. Wang, “Deep network with double reuses and convolutional shortcuts,” IET Comput. Vis., vol. 18, no. 4, pp. 512–525,
Jun. 2024.
[50] M. Fraccaroli, A. Bizzarri, P. Casellati, and E. Lamma, “Exploiting
CNN’s visual explanations to drive anomaly detection,” Int. J. Speech
Technol., vol. 54, no. 1, pp. 414–427, Jan. 2024.
[51] S. Bacha, A. Aljuhani, K. B. Abdellafou, O. Taouali, N. Liouane,
and M. Alazab, “Anomaly-based intrusion detection system in IoT
using kernel extreme learning machine,” J. Ambient Intell. Humanized
Comput., vol. 15, no. 1, pp. 231–242, Jan. 2024.
PAPER_TEXT
