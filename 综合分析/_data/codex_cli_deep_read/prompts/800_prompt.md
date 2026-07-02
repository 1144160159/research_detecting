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
# [800] SecureDyn-FL: A Robust Privacy-Preserving Federated Learning Framework for Intrusion Detection in IoT Networks
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
编号：800
题名：SecureDyn-FL: A Robust Privacy-Preserving Federated Learning Framework for Intrusion Detection in IoT Networks
年份：2025
DOI：10.1109/tnsm.2025.3647642
来源：IEEE Transactions on Network and Service Management
PDF：paper/10.1109_TNSM.2025.3647642.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：联邦学习、隐私保护与分布式协同、IoT、车联网、工业互联网与边缘安全
相关性：强相关，分数 14
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\800.txt
- 原始字符数：119823
- 本次发送字符数：119823
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
1742

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

SecureDyn-FL: A Robust Privacy-Preserving
Federated Learning Framework for Intrusion
Detection in IoT Networks
Imtiaz Ali Soomro , Hamood Ur Rehman Khan , Syed Jawad Hussain , Adeel Iqbal ,
Waqas Khalid , Member, IEEE, and Heejung Yu , Senior Member, IEEE

Abstract—The rapid proliferation of Internet of Things (IoT)
devices across domains such as smart homes, industrial control
systems, and healthcare networks has significantly expanded
the attack surface for cyber threats, including botnet-driven
distributed denial-of-service (DDoS), malware injection, and data
exfiltration. Conventional intrusion detection systems (IDS) face
critical challenges like privacy, scalability, and robustness when
applied in such heterogeneous IoT environments. To address
these issues, we propose SecureDyn-FL, a comprehensive and
robust privacy-preserving federated learning (FL) framework
tailored for intrusion detection in IoT networks. SecureDyn-FL is
designed to simultaneously address multiple security dimensions
in FL-based IDS: (1) poisoning detection through dynamic
temporal gradient auditing, (2) privacy protection against inference and eavesdropping attacks through secure aggregation,
and (3) adaptation to heterogeneous non-independent-andidentically-distributed (non-IID) data via personalized learning.
The framework introduces three core contributions: (i) a
dynamic temporal gradient auditing mechanism that leverages
Gaussian mixture models (GMMs) and Mahalanobis distance
(MD) to detect stealthy and adaptive poisoning attacks, (ii) an
optimized privacy-preserving aggregation scheme based on
transformed additive ElGamal encryption with adaptive pruning and quantization for secure and efficient communication,
and (iii) a dual-objective personalized learning strategy that
improves model adaptation under non-IID data using logitadjusted loss. Extensive experiments on the N-BaIoT dataset
under both IID and non-IID settings, including scenarios with
Received 10 October 2025; accepted 17 December 2025. Date of publication 23 December 2025; date of current version 15 January 2026. This
work was supported by the National Research Foundation of Korea (NRF)
grant funded by the Korea government (MSIT) (RS-2025-00514779, RS2025-02303435), by the Information Technology Research Center (ITRC)
support program (IITP-2023-RS-2022-00164800) supervised by the Institute
for Information & Communications Technology Planning & Evaluation (IITP).
The associate editor coordinating the review of this article and approving it
for publication was J.-H. Cho. (Imtiaz Ali Soomro and Adeel Iqbal contributed
equally to this work.) (Corresponding authors: Heejung Yu; Waqas Khalid.)
Imtiaz Ali Soomro and Syed Jawad Hussain are with the Department of
Computer Science, Sir Syed CASE Institute of Technology, Islamabad 44000,
Pakistan (e-mail: imtiaz.soomro@case.edu.pk; jawad.hussain@case.edu.pk).
Hamood Ur Rehman Khan is with the ECE Department, Habib University,
Karachi 75350, Pakistan (e-mail: hamood.rehman@sse.habib.edu.pk).
Adeel Iqbal is with the School of Computer Science and Engineering,
Yeunganam University, Gyeongsan 38541, South Korea (e-mail:
adeeliqbal@yu.ac.kr).
Waqas Khalid is with the Department of Electrical and Electronic
Engineering and the Next Generation Internet of Everything Laboratory,
University of Nottingham Ningbo China, Ningbo 315100, China (e-mail:
Waqas.Khalid@nottingham.edu.cn).
Heejung Yu is with the Department of Electronics and Information
Engineering, Korea University, Sejong 30019, South Korea (e-mail:
heejungyu@korea.ac.kr).
Digital Object Identifier 10.1109/TNSM.2025.3647642

up to 50% adversarial clients, demonstrate that SecureDyn-FL
consistently outperforms state-of-the-art FL-based IDS defenses.
It achieves up to 99.01% detection accuracy, a 98.9% F1-score,
and significantly reduced attack success rates across diverse
poisoning attacks, while maintaining strong privacy guarantees and computational efficiency for resource-constrained IoT
devices.
Index Terms—Security threats, intrusion detection system
(IDS), federated learning (FL).

I. I NTRODUCTION
HE RAPID expansion of the Internet has driven
large-scale connectivity, accelerating the deployment of
Internet of Things (IoT) devices [1], [2], [3], [4], [5], [6].
By 2025, IoT devices are expected to exceed 55.7 billion
globally [7]. Smart appliances and sensors produce massive
data streams but have limited computing power and minimal
security [8]. These vulnerabilities make them attractive targets
for cyber adversaries, as illustrated by the 2016 Mirai botnet
attack [9], which remains one of the most severe IoT security
incidents. Such events highlight the need for effective IoTspecific cybersecurity measures. Intrusion Detection Systems
(IDS), which analyze network traffic to identify threats, are
essential components for IoT defense [10].
Federated Learning (FL) offers a promising paradigm for
addressing the privacy and scalability limitations of centralized IDS [11]. In FL, clients collaboratively train a shared
model without exchanging raw data. Clients compute local
updates that are aggregated by a central server to form a
global model. This iterative process preserves privacy, reduces
communication overhead, and supports distributed intrusion
detection [12]. Recent FL-based IDS frameworks [13], [14]
leverage this approach to enhance scalability and privacy.
Despite these advantages, several deployment challenges
remain. IoT environments typically exhibit non-independentand-identically-distributed (non-IID) data, with clients
receiving heterogeneous mixes of benign and malicious
traffic. Such heterogeneity degrades global convergence and
detection performance [12], [15], [16]. FL is also vulnerable
to poisoning attacks: compromised clients can inject malicious
updates to bias or degrade the global model [17], [18]. The
lack of client supervision amplifies these threats [19], [20].
Adversaries can further exploit eavesdropping or man-in-themiddle (MITM) attacks [21], [22] to reconstruct local models

T

c 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
1932-4537 
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

SOOMRO et al.: SecureDyn-FL: A ROBUST PRIVACY-PRESERVING FL FRAMEWORK

and conduct inference attacks [23], [24], [25]. Gradient
manipulation techniques can bypass traditional defenses [26].
Privacy-preserving techniques such as differential privacy
(DP), secure multiparty computation (SMC), and homomorphic encryption (HE) have been proposed to mitigate these
threats [27], [28]. DP-based methods [29], [30] inject noise to
protect data but often degrade accuracy in dynamic or imbalanced settings. SMC approaches [31] prevent data leakage but
incur heavy computational and communication costs, unsuitable
for constrained devices. HE frameworks [32] ensure confidentiality but increase latency. Hybrid solutions [33], [34], [35]
aim to balance privacy and performance but face trade-offs.
Frameworks such as TrustFL [36] and SafeFL [37] advance
the field but have practical limitations: TrustFL depends on
trusted execution environments (TEEs), and SafeFL incurs
high computational overhead. Many poisoning defenses require
gradient access, which risks data leakage, and existing methods
struggle against encrypted poisoning attacks.
These limitations can be summarized as: (i) vulnerability
to poisoning and inference attacks, (ii) poor adaptation to
non-IID data and limited generalization to unseen intrusions,
and (iii) communication inefficiencies unsuitable for resourceconstrained devices. While recent zero-shot learning (ZSL)
advances [38] offer promising techniques for generalization,
further progress is needed to address these issues holistically.
This paper proposes SecureDyn-FL, a privacy-preserving
FL-based IDS tailored for heterogeneous IoT environments.
SecureDyn-FL addresses three core challenges: data heterogeneity, poisoning resilience, and communication security. A
model decoupling strategy separates shared feature extraction
from personalized classification, allowing local adaptation
while maintaining global robustness. A joint mini-batch logitadjusted and cross-entropy loss improves learning under
diverse distributions. Unlike standard aggregation methods,
which are vulnerable to label-flipping and model poisoning [39], [40], SecureDyn-FL maintains stable convergence
under heterogeneous and adversarial conditions.
SecureDyn-FL ensures secure communication by integrating homomorphic encryption with efficient privacy-preserving
mechanisms. This design enables encrypted computation
without compromising computational efficiency, thereby safeguarding both model parameters and sensitive data throughout
the training process. The framework is engineered for realworld deployment, delivering strong security guarantees,
robustness against adversarial behavior, and scalability across
large-scale distributed environments.
The main contributions are:
• Proposing SecureDyn-FL, integrating dynamic auditing,
encryption, and personalization to address heterogeneity,
poisoning, and communication security in FL-based IDS.
• Developing a Gaussian mixture model (GMM)-based
auditing mechanism using Mahalanobis distance (MD) to
detect stealthy and adaptive poisoning attacks.
• Designing a hybrid loss function that improves local
adaptation and global performance.
• Applying dynamic pruning and quantization to reduce
communication overhead without degrading accuracy or
privacy.

1743

•

Demonstrating strong cross-dataset generalization, maintaining high performance across N-BaIoT, and TONIoT
benchmarks.
• Achieving up to 99.01% overall accuracy and a 0.9893
F1-score on N-BaIoT under same-model poisoning, while
maintaining strong robustness across all attack settings,
consistently outperforming state-of-the-art defenses such
as FL Trust, Shield FL, and FL-Defender.
The remainder of this paper is structured as follows.
Section II presents the problem formulation and threat model.
Section III discusses the necessary background and related
concepts. Section IV introduces the overall SecureDyn-FL
framework and system workflow, while Section V details
the proposed model and defense mechanisms. Section VI
provides theoretical and security analysis. Section VII presents
the experimental setup and results. Section VIII offers a
comparative evaluation with existing state-of-the-art methods.
Section IX analyzes computational efficiency and scalability.
Finally, Section X concludes the paper and outlines future
research directions.
II. P ROBLEM F ORMULATION
In SecureDyn-FL models, a key focus is to secure the entire
FL pipeline, with a particular emphasis on the secure aggregation of model updates. Clients contribute encrypted gradients
to the FL server, bolstering data privacy by safeguarding
individual contributions from both external adversaries and
the server itself. Secure aggregation in SecureDyn-FL is
distinct from simply sending encrypted gradients; it involves
combining these gradients in a manner that prevents revealing
individual updates while still facilitating effective global model
training.
Given K clients with a dataset Di that may follow either
IID or non-IID data distributions, the goal is to collaboratively
train a global model M by minimizing the loss function L.
This must be achieved while ensuring data privacy, robustness
against adversarial attacks, and minimal computational overhead. The SecureDyn-FL framework F is designed to meet
the following objectives:
• Handle both IID and non-IID data distributions across
clients.
• Ensure data privacy by allowing clients to contribute to
M without exposing their individual data.
• Verify encrypted gradients gi = ∇(Di , M ) to detect
malicious attacks.
• Implement secure aggregation of verified gradients to
enhance model robustness against poisoning attacks.
• Maintain high performance of M for all clients, irrespective of data distribution variations.
• Minimize the overhead of encryption and gradient verification while optimizing cryptographic efficiency.
The adversarial attack problem in SecureDyn-FL is formulated as minimizing L(M ) under privacy, robustness, and
efficiency constraints, as expressed in Eq. (1).

min L(M ) =
M

1
K


N
i=1

L(Di , M )

(1)

1744

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

A. Threat Model

Fig. 1. Thread Model: Federated Learning-based Intrusion Detection System
(FL-IDS) in IoT networks with model inference and poisoning attacks.

When optimizing Eq. (1), the following constraints are
considered:
• The global model M is updated using verified gradients
gi after their computation.
• Gradients gi = ∇(Di , M ) for i = 1, . . . , K are
encrypted to preserve confidentiality.
• Performance constraints, such as data security, model
robustness, adaptability to IID and non-IID data, and
cryptographic efficiency, are satisfied.
The gradients are verified using a predefined verification
function Va(gi ), as defined in Eq. (2).

Va(gi ) =

benign if gi ∈ non-malicious
malicious otherwise

(2)

In Eq. (2) Va (gi ) denotes a binary auditing decision variable produced by the temporal gradient auditing mechanism.
A value of Va (gi ) = 1 indicates that the client update
gi is classified as benign and is therefore accepted for
aggregation, whereas Va (gi ) = 0 denotes that the update is
identified as malicious and consequently rejected. This explicit
interpretation improves the precision and interpretability of
the proposed formulation. This function evaluates gi against
expected non-malicious patterns, categorizing it accordingly.
Such a mechanism ensures only valid gradients contribute to
updating the global model M, thus enhancing its accuracy and
resilience in adversarial SecureDyn-FL scenarios. Based on
Eq. (2), the benign gradients are passed to the global model:

M =M −η×

1
K


×

K


Va(gi ) × gi

(3)

i=1

where η is the learning rate. The framework F also evaluates
accuracy, computation time, communication cost, and resource
utilization to ensure practical and efficient real-world deployment.

This paper focuses on security and privacy threats in FL that
are exploitable by malicious users. Similar to [41], [42], [43],
and [44], we classify users into two categories: benign
or malicious, where malicious users (poisoners) may have
access to diverse local datasets. Although advanced adaptive
poisoning attacks exist, this study focuses on conventional
model poisoning threats to maintain a consistent basis for
comparison. We explicitly assume that users do not collude,
excluding user-user collusion from this scope. Additionally,
complex scenarios, such as server-client collusion or sophisticated adaptive attacks, are beyond the current focus. This
limitation ensures a fair comparison with [17], [42], [43], [45],
and [46], but also sets the stage for future research to extend
our model to these more intricate threats, including various
collusion scenarios and auditor threats. The threat model for
our FL-based IDS in IoT networks, accounting for both model
inference and poisoning attacks, is illustrated in Fig. 1. In this
setting, an honest-but-curious server may attempt to launch
model inversion or related inference attacks by exploiting
shared gradients to reconstruct sensitive local data, while malicious clients may perform targeted or untargeted poisoning
to degrade detection performance. SecureDyn-FL mitigates
these threats through additive homomorphic encryption, which
prevents the server from accessing raw gradients, and temporal
gradient auditing, which detects and filters abnormal client
updates before aggregation.
The specific threats and corresponding goals are:
1) Threat 1: The honest-but-curious (HBC) adversary: In
FL, the server has access to all local gradients and
ciphertexts and may act adversarially. The system operates on the assumption of this HBC behavior, but the
server could potentially launch privacy attacks, including
inferring the data privacy of users. The core threat lies in
adversaries seeking sensitive global model information
through data reconstruction or inference attacks.
Goal 1: Safeguard the confidentiality of local gradients.
Adversaries, including malicious servers, can exploit
shared gradients and global parameters to expose sensitive user data. Encrypting individual gradients before
server transmission provides some degree of confidentiality.
2) Threat 2: Inject poisonous gradients: Byzantine actors
can disrupt FL systems by submitting fraudulent gradients that mimic legitimate updates from heterogeneous
data, compromising model integrity.
Goal 2: Enhance the examination of encrypted gradients
to distinguish benign from malicious updates, strengthening resilience against poisoning attacks.
B. Design Goals
SecureDyn-FL aims to achieve the following design goals
to ensure high accuracy, robustness, privacy, and efficiency,
even under adversarial conditions:
1) Accuracy: Maintain high classification accuracy across
all clients, despite data imbalance, distribution skew,
or adversarial attacks. A dual-objective loss function

SOOMRO et al.: SecureDyn-FL: A ROBUST PRIVACY-PRESERVING FL FRAMEWORK

ensures dependable performance in both IID and nonIID settings.
2) Robustness: Ensure resilience against targeted and untargeted poisoning attacks, including adversaries who
change their strategies over time. This is achieved
through a dynamic temporal gradient auditing mechanism that tracks update behavior using GMM clustering
and MD.
3) Privacy: Sensitive data is protected during training and
communication using additive homomorphic encryption
based on a modified ElGamal scheme, enabling secure
gradient aggregation without exposing raw updates.
4) Adaptability: Support client-level personalization via
logit-adjusted loss, allowing local models to adapt to
diverse class distributions while contributing to global
learning, vital for heterogeneous IoT environments.
5) Efficiency in Communication and Computation:
Incorporate adaptive quantization and dynamic unstructured pruning to reduce overhead in low-power,
bandwidth-constrained devices while preserving model
quality.
III. L ITERATURE R EVIEW
The proliferation of IoT devices has generated massive
amounts of distributed data, necessitating learning frameworks
that preserve privacy while enabling effective model training.
FL has emerged as a promising decentralized paradigm,
allowing multiple edge devices to collaboratively train a global
model by exchanging only model parameters rather than raw
data. This approach significantly mitigates privacy risks and
communication overhead compared to centralized machine
learning models. Despite these advantages, FL remains highly
vulnerable to model poisoning and backdoor attacks, wherein
malicious clients manipulate local gradients to degrade or
subvert the global model. Fang et al. [17] conducted the first
systematic study of local model poisoning against Byzantinerobust FL methods. Their findings revealed that existing
defenses, which were assumed to be robust against Byzantine
failures, can be substantially compromised across multiple
real-world datasets, thereby exposing critical vulnerabilities in
federated optimization.
In response, researchers have proposed several defense
strategies to enhance the robustness of FL. Jebreel and
Domingo-Ferrer [47] introduced FL-Defender, which identifies
attack-related neurons by analyzing last-layer gradient behaviors and re-weights client updates based on worker-wise angle
similarity with PCA compression. Similarly, Gill et al. [48]
proposed FedDefender, leveraging differential testing on synthetic inputs and neuron activation fingerprinting to identify
backdoor-infected clients, achieving attack success rates as
low as 10%. Erbil and Gursoy [49] explored a clusteringbased defense using X-Means to isolate malicious updates
by selectively extracting indicative DNN parameters, yielding up to 95% true positive rates. To address large-scale
attacks, Zhang et al. [50] developed FLDetector, which detects
malicious clients by analyzing model-update inconsistencies
across iterations. Malicious participants are identified by their

1745

persistent deviation from expected update patterns, allowing
Byzantine-robust methods to effectively train accurate models
after removing compromised clients. Collectively, these methods reflect a growing body of work aimed at enhancing the
security of federated learning in distributed IoT environments.
IDSs play a crucial role in safeguarding IoT and industrial
IoT (IIoT) infrastructures against cyber threats. Traditional
centralized IDS approaches face significant challenges related
to data privacy, communication overhead, and real-time processing in distributed networks. FL-IDS has therefore emerged
as an effective solution, combining collaborative model training with privacy preservation. Bhavsar et al. [51] developed
an FL-IDS using logistic regression and CNN classifiers,
achieving 94–99% accuracy on NSL-KDD and Car-Hacking
datasets when deployed on low-power embedded devices
such as Raspberry Pi. Akinie et al. [52] proposed a hybrid
server–edge framework that reduced memory consumption by
42% and training time by 75%, while maintaining 99.2%
detection accuracy. Javeed et al. [53] combined CNN and
BiLSTM architectures within a zero-trust FL model to capture
spatial–temporal features, demonstrating strong performance
on CICIDS2017 and Edge-IIoTset datasets. Rashid et al. [54]
further achieved 92.49% accuracy on Edge-IIoTset, closely
approaching the performance of centralized machine learning
(93.92%), thus validating the effectiveness of FL for intrusion
detection without compromising privacy.
In IIoT environments, Ruzafa-Alcázar et al. [55] conducted
a comprehensive evaluation of differential privacy techniques
applied to FL-IDS, comparing FedAvg and Fed+ aggregation
methods on the TONIoT dataset under non-IID data distributions. Hamdi [56] advanced this line of work by combining
CNNs and Gated Recurrent Units with Isolation Trees for
anomaly detection, improving both real-time performance and
accuracy in non-IID settings. Similarly, Azeez et al. [57]
applied federated averaging on CICIDS2017, achieving 95.2%
accuracy, while Mahmud et al. [58] demonstrated over 90%
accuracy across multiple attack types, including DoS, DDoS,
and ransomware, in IoT networks. Abou El Houda et al. [59]
proposed an innovative approach that integrates secure aggregation protocols with blockchain technology to ensure both
data integrity and privacy. Their system employs multi-party
computation to prevent data exposure between participants and
uses blockchain to provide tamper-resistance, achieving high
detection accuracy on real-world IoT datasets. Collectively,
these studies demonstrate that FL-IDS offers a scalable,
privacy-preserving, and accurate intrusion detection mechanism for resource-constrained IoT environments.
Although FL inherently improves data privacy by avoiding raw data transmission, model updates themselves can
leak sensitive information. Moreover, defense mechanisms
against poisoning attacks must be designed carefully to
avoid privacy compromises. As a result, recent research has
focused on integrating advanced cryptographic techniques
into federated learning to achieve both security and privacy.
Yazdinejad et al. [60] proposed an internal auditing mechanism utilizing GMM and MD with additive homomorphic
encryption (AHE) to detect malicious encrypted gradients
while minimizing computational overhead. Miao et al. [61]

1746

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

introduced RFed, a dual-server framework that employs scaled
dot-product attention to achieve over 96% poisoning attack
failure rates without relying on strong assumptions, thereby
improving scalability and robustness. Wu et al. [62] developed
PBFL, integrating two-trapdoor fully homomorphic encryption with secure normalization and cosine similarity methods
to defend against poisoning while preventing privacy leakage during detection. Similarly, Ma et al. [43] proposed
ShieldFL, which uses two-trapdoor homomorphic encryption and secure cosine similarity measurements. ShieldFL
achieved 30%–80% accuracy improvements against state-ofthe-art poisoning attacks under both IID and non-IID data
conditions. These advances illustrate a growing emphasis on
privacy-preserving federated defense mechanisms, combining
cryptographic primitives with statistical detection techniques
to enable secure and practical FL deployment in large-scale
IoT and IIoT networks.
Privacy preservation in federated learning has been
extensively explored through cryptographic and statistical
techniques, including secure multiparty computation (SMC),
fully homomorphic encryption (FHE), differential privacy
(DP), and more recently, blockchain-based mechanisms. SMC
and FHE provide strong security guarantees by enabling
computations on encrypted data without exposing individual client updates. However, these approaches typically
incur significant computational and communication overhead,
limiting their scalability in resource-constrained IoT environments [27], [28]. DP techniques introduce calibrated noise to
model updates, effectively protecting individual data privacy
but often at the cost of reduced model utility and convergence performance, particularly in non-IID settings [33], [35].
To balance privacy and efficiency, hybrid approaches have
emerged that combine DP with SMC or homomorphic encryption, aiming to reduce overhead while maintaining strong
privacy guarantees. In parallel, blockchain-based frameworks
have been proposed to improve the integrity and auditability of
the aggregation process. By leveraging immutable ledgers and
decentralized consensus, blockchain can prevent tampering
and ensure trustworthy model updates without relying on
a fully trusted central server [37], [63], [64]. While these
methods offer promising privacy protection, most existing
solutions struggle to simultaneously ensure lightweight operation, robust poisoning defense, and high detection accuracy
in heterogeneous IoT deployments.
Existing federated learning-based IDS frameworks face
notable limitations in jointly addressing data heterogeneity,
adaptive poisoning resilience, and communication privacy
in realistic IoT environments. Current defenses often rely
on static detection mechanisms, trusted hardware, or heavy
cryptographic schemes, which either fail against stealthy
attacks or introduce prohibitive overhead in resource-constrained
settings. Moreover, non-IID data distributions significantly
hinder global model convergence and detection accuracy, a
challenge insufficiently addressed by prior works. To fill these
gaps, this paper proposes SecureDyn-FL, a federated intrusion
detection framework that integrates dynamic temporal gradient
auditing, lightweight privacy-preserving encryption, and personalized learning strategies. This holistic approach simultaneously

strengthens resilience against adaptive poisoning, enhances
privacy protection, and improves detection performance under
non-IID conditions, thereby advancing the state of the art
in secure and efficient FL-based intrusion detection for IoT
networks.
IV. W ORK F LOW
The SecureDyn-FL framework follows a structured
sequence of coordinated phases that together form an endto-end pipeline for secure, personalized, and robust intrusion
detection in federated IoT environments. Rather than treating each component in isolation, the workflow integrates
personalized learning, communication efficiency, and security mechanisms into a cohesive process. Client registration
establishes trust and tracking, personalized training ensures
adaptability to non-IID data, pruning and quantization reduce
communication cost, encryption protects updates during transmission, and temporal gradient auditing detects poisoning
attacks before aggregation. This high-level structure illustrates
how each stage contributes directly to the overarching IDS
goal: detecting malicious behavior while preserving data privacy and efficiency in federated settings.
The proposed SecureDyn-FL framework operates through a
sequence of coordinated phases to ensure secure, efficient, and
personalized FL for intrusion detection in IoT environments
as shown in Fig. 2. The system initializes the federated infrastructure by assigning unique identifiers and cryptographic key
pairs to each participating client. Simultaneously, a Central
Audit (CA) module prepares a tagging and update tracking
mechanism for later-stage gradient verification and poisoning
detection.
Each client performs personalized local training using
its non-IID data. The local model is decoupled into a
shared feature extractor and a private classifier. A dualloss strategy, comprising cross-entropy and mini-batch logit
adjustment, is used to enhance robustness against class imbalance and heterogeneous distributions. Following local training,
clients apply soft, unstructured L1-norm-based pruning with
a dynamically increasing pruning rate over rounds to reduce
computational and communication overhead while improving
privacy. Subsequently, clients quantize the pruned updates
using an adaptive quantization method. This involves computing a scale and zero-point to map real-valued updates
into a lower bit-width representation, reducing bandwidth
usage without sacrificing accuracy. These quantized updates
are then encrypted using the CKKS homomorphic encryption
scheme, enabling secure aggregation at the server without
decryption.
Before aggregation, a CA is conducted. The first phase
validates client identities and updates tags. The second phase
involves clustering using incremental GMMs, evaluating MD,
and verifying temporal trajectory consistency of updates. A
dynamic multi-threshold decision mechanism classifies client
updates as accepted, down-weighted, or rejected. Only verified
and reliable gradients proceed to the aggregation step. The
server aggregates the validated updates and constructs a
global model, which is redistributed to clients for the next

SOOMRO et al.: SecureDyn-FL: A ROBUST PRIVACY-PRESERVING FL FRAMEWORK

1747

Fig. 2. Flowchart of the SecureDyn-FL framework, including device initialization, local model training on clients, security measures (e.g., poisoned device
detection and central auditing), optimization (via weight pruning and quantization), privacy-preserving aggregation at the server, and performance evaluation
before deploying the global model.

training round. Clients integrate the updated model while
continuing to refine local classifiers. This workflow collectively
ensures secure communication, personalized learning, defense
against poisoning attacks, and robustness in heterogeneous IoT
environments.

V. P ROPOSED M ODEL
This section presents proposed SecureDyn-FL, a novel
personalized FL framework tailored for intrusion detection
in non-IID IoT environments. To address the vulnerabilities
of FL against poisoning attacks, we introduce a server-side
poisoned client detection mechanism before the global model
aggregation step of FL.

A. System Architecture Overview
The architecture consists of four key entities:
• Clients (IoT Devices): Distributed nodes that locally train
on non-IID data while preserving data privacy.
• Central Auditor: A trusted party responsible for client
registration, key distribution, secure aggregation, model
auditing, and dissemination.
• Communication Network: Secure channels through which
encrypted updates and models are exchanged.
• Audit Table Repository: A secure, encrypted ledger
storing client-specific encrypted updates and behavioral
metadata for auditing.
The architecture supports secure model updates, client personalization, encryption-enabled communication, and integrity
verification, without revealing sensitive client information or
raw data.

B. Registration Phase
The device registration and authentication process
comprises four main phases: registration, login, key exchange,
and authentication. During registration, each device is enrolled
with the certification authority (CA), which assigns a unique
tag identity (TID) and generates a secret value (HSV)
based on the device’s MAC address. A hashed identity
(HID) is derived and stored securely to prevent duplicate
registrations [65], [66]. In the login phase, the device submits
its HID for server validation, followed by the exchange
of masked random values to reconstruct shared secrets.
In the key exchange phase, both parties derive a 128-bit
session key through random number operations and bitwise
transformations, ensuring confidentiality. Finally, mutual
authentication is achieved using HMAC-SHA256 over session
keys, IP addresses, and nonces, securing the communication
channel against MITM attacks. For a detailed algorithm,
mathematical derivations, and message exchanges, the reader
is referred to [67].
C. Proposed Method: Multi-Objective Personalized
Federated Learning
To tackle the challenges introduced by statistical heterogeneity (i.e., non-IID data distributions) in FL, we propose a
multi-objective personalized FL (MO-PFL) framework. This
approach adopts a decoupled dual-classifier strategy coupled
with a tailored multi-objective loss function. Our architecture
enables client-level personalization while preserving alignment
with the global learning objective. As shown in Fig. 3, the
model consists of a shared feature extractor and two decoupled classifiers: a personalized classifier tuned to the local
distribution and a global classifier synchronized across clients.

1748

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

Fig. 3. System model of proposed SecureDyn-FL framework. The architecture integrates multiple defense mechanisms, including quantization, mean-based
parameter clipping, and dynamic unstructured model pruning, followed by encrypted local training. The FL model is decoupled into a shared feature extractor
and dual classifiers (global and personalized) enabling multi-objective optimization. A trusted auditor monitors the training pipeline to detect adversarial threats
such as data/model poisoning and eavesdropping. Secure aggregation ensures the integrity and privacy of the global model.

glob

D. Model Architecture
Consider a client k ∈ {1, 2, . . . , K } with local
k
sampled from a possibly non-IID
dataset Dk = {(xi , yi )}ni=1
distribution Dk . The local model comprises:
• A shared feature extractor: f : Rd → Rp
pers
• A personalized classifier: hk
: Rp → R|C |
glob
: Rp → R|C |
• A global classifier: hk
For input x on client k, the model produces:
pers

ŷ pers = hk

(f (x)),

glob

ŷ glob = hk

(f (x))

(4)

The extractor f is globally shared and updated via the
pers
remains private to each
FedAvg algorithm [11], while hk

client for local adaptation. The global classifier hk
periodically synchronized across clients.

is

E. Multi-Objective Loss Formulation
To balance personalization and global generalization, we
define a composite loss function:
a) Global Cross-Entropy Loss: This loss ensures consistency across clients by training the global classifier:




⎛

LCE y, ŷ glob = − log⎝



⎞
exp ŷyglob

⎠
glob
y  ∈C exp ŷy 

(5)

SOOMRO et al.: SecureDyn-FL: A ROBUST PRIVACY-PRESERVING FL FRAMEWORK

glob

where C is the label space and ŷy 
is the output logits
for class y  . y glob as the predicted label generated by the
global classifier on each client. This value is utilized in
the computation of the global cross-entropy loss to ensure
alignment between local and global objectives during federated
training.
b) Logit-Adjusted Personalization Loss: To handle the local
objective of the client and learn the personalized model for
each client, we apply a logit-adjusted cross-entropy loss to the
personalized classifier:


⎞
⎛
pers
exp ŷy
+ τ log αyk


pers
 ⎠ (6)

= − log⎝ 
LLA y, ŷ
pers
k
y  ∈C exp ŷy  + τ log αy 

where αyk is the normalized frequency of class y in client k. It
is dynamically recalculated at the mini-batch level, enabling
real-time adaptation to batch-wise label skew. The temperature
parameter τ regulates the intensity of the logit adjustment.
c) Mitigating Non-IID Challenges: Beyond addressing
class imbalance, the proposed dual-objective formulation plays
a crucial role in mitigating the adverse effects of non-IID data
distributions commonly observed in IoT environments. The
global cross-entropy loss LCE enforces alignment with the
global decision boundary by optimizing shared representations
collaboratively across clients, ensuring that local models do
not drift too far from the global objective. Meanwhile, the
logit-adjusted personalization loss LLA dynamically reweights
logits based on local class priors, which counteracts the bias
introduced by label distribution skew and stabilizes local
training. By jointly optimizing these objectives, the model
achieves a balance between local specialization and global
consistency, reducing client-drift and improving the robustness
of aggregation under heterogeneous non-IID settings.
F. Optimization and Gradient Flow
The total loss for each client is:


Ltotal = LCE y, ŷ glob +λ


Global objective

LLA (y, ŷ pers )



(7)

Personalization objective

1) Backward Pass:
hkpers is updated using ∇LLA
glob
is updated using ∇LCE
• hk
• f is updated using ∇f (LCE + LLA )
•

G. Federated Training Protocol
Each local training round on client k proceeds through the
following steps:
1) Forward Pass: The client computes intermediate features
using the shared feature extractor:
z = f (x)

(8)

These features are passed to both classifiers:
ŷ pers = hkpers (z),

ŷ glob = hkglob (z)

(9)

Here, ŷ pers reflects the personalized inference tailored to
local data, while ŷ glob contributes to the globally shared
model.

1749

2) Loss Computation: The total loss is formulated as a
weighted sum of the global cross-entropy loss and the
logit-adjusted personalization loss:


Ltotal = LCE y, ŷ glob + λLLA (y, ŷ pers ) (10)
The parameter λ balances the trade-off between global
consistency and local adaptation.
3) Backpropagation: Gradients are computed and applied
separately:
hkpers ← hkpers − η∇h pers LLA
k

hkglob ← hkglob − η∇h glob LCE
k

f ← f − η∇f (LCE + LLA )

(11)

The feature extractor f receives a combined gradient
from both loss terms, enabling it to capture features that
support both global generalization and local personalization.
H. Quantization and Pruning
During local model training, we employed a pruning technique to iteratively remove less important weights or gradients
from model updates. Specifically, clients perform soft unstructured pruning based on the L1 norm, which creates a sparse
model and makes the FL training process more efficient. The
pruning process is guided by a dynamically updated pruning
rate pt , which increases over the communication rounds,
allowing more aggressive pruning as the training progresses.
After pruning, clients send their pruned updates to the server,
which aggregates them using FedAvg to generate the global
model. This pruning technique not only reduces the model size
and computational costs, but also makes the training process
more resistant to inference attacks.
By progressively increasing the pruning rate, communication efficiency improves throughout the rounds. As clients
share a sparsified model with the server, the transmitted
model is no longer the full model, limiting the information
available to potential attackers. The sparsity introduced by
pruning constrains the parameter space, significantly reducing
the chances of reverse engineering or inferring sensitive data.
This reduction in exposed parameters inherently enhances
privacy protection, making it more difficult for adversaries to extract meaningful insights about the underlying
data.
The pruning rate pt is updated iteratively using Eq. (12):




t − teﬀ
· ptarget − p0 + p0 (12)
pt = max 0,
ttarget − teﬀ
where pt is the pruning rate at round t, teﬀ is the effective
round when pruning starts, ttarget is the target round when the
target pruning rate is reached, p0 is the initial pruning rate, and
ptarget is the target pruning rate. This pruning rate increases
gradually from the initial value to the target value, ensuring
that the pruning is progressively applied more aggressively as
training progresses.

1750

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

Each weight xi (k ) is mapped to a discrete value x̄i (k ) using
the following stochastic quantization rule:

xi (N )−T (l)
t+1
t+1
t
 mi
(13) QN (xi (N )) = T (l + 1) with probability T (l+1)−T (l) ,
Δwp,i = Δwi
T (l )
otherwise .
where  represents the element-wise product, and mit is the
This rule assigns xi (N ) to the quantization level T (l +
local pruning mask identifying pruned weights at communi- 1) with a probability proportional to its distance from T (l ),
t+1
is then quantized ensuring minimal distortion. The quantized output x̄ (N ) takes
cation round t. This pruned update Δwp,i
i
and sent to the server for aggregation.
a discrete value from the set as shown in Eq. (18).
We also used a layer-wise clipping technique based on
dynamic mean to help reduce inconsistencies during the
(18)
{r1 , r1 + ΔN , r1 + 2ΔN , . . . , r2 − ΔN , r2 }
training process. The clipping factor controls the clipping
The key novelty of AQ lies in its ability to dynamiparameter, dynamically adjusting the clipping based on layercally
adjust quantization levels based on the communication
wise updates, rather than using a static clipping method.
resources
of each device. Devices with limited bandwidth
This approach ensures that each layer’s updates are clipped
can
use
fewer
quantization levels (smaller N), while devices
according to their specific dynamics, leading to more stable
with
higher
bandwidth
can use more levels (larger N). This
and efficient training. After the local model updates are
t+1
adaptive
approach
ensures
that the communication overhead
to
computed, each client clips its own model update Δwi
is
minimized
without
compromising
model accuracy. AQ is
avoid instability before sending it to the server. The clipping
scalable
to
large
IoT
networks
with
diverse
device capabilities,
for client i’s model update is applied using Eq. (14):
making it suitable for real-world deployments.


t+1
t+1
(14)
=
clip
Δw
,
−α
·
μ
,
α
·
μ
ΔwC
i
i
i
,i
I. Additive ElGamal Encryption Based on Discrete
where μi is the mean of the absolute values of the elements Logarithm
of client i’s model update, calculated as:
After completing the quantization process, each client
encrypts the quantized model updates using the PRKG algon

1 
rithm. However, to facilitate secure aggregation in the FL
t+1 
(15)
μi =
Δwi,j

environment, it is essential to endow the ElGamal crypn
j =1
tosystem with additive homomorphic properties. By default,
t+1
The clipping function clip(Δwi , a, b) ensures that the the ElGamal cryptosystem supports multiplicative homomorphism, that is,
values of Δwit+1 are constrained within the range [−α·μi , α·
μi ], thereby limiting the impact of extreme values.
(19)
Enc(m1 ) · Enc(m2 ) = Enc(m1 · m1 ),
Next, each client performs adaptive quantization (AQ),
a novel technique designed to address the communication but it does not naturally support additive operations. To achieve
overhead challenges in FL for resource-constrained IoT envi- additive homomorphism necessary for FL model aggregation,
ronments. AQ scheme allows devices to dynamically adjust Zhu et al. [68] introduced a secure transformation technique
their quantization levels based on their available communi- based on the Cramer transformation, enabling additive homocation resources. Unlike traditional quantization methods that morphism over ElGamal-encrypted data.
The transformation works by converting the original plainenforce a uniform strategy across all devices, AQ accounts
text
m to an exponentiated form m  = g m mod p, thereby
for device heterogeneity, enabling efficient on-device training
mapping the message space into Zp . The transformed ElGamal
while maintaining model accuracy.
scheme
then facilitates additive homomorphism as demonThe AQ scheme employs a K-level quantizer, where K
strated
in
Eq. (20):
represents the number of distinct values to which each weight
can be mapped. For each device i ∈ N , the model updates
Enc(m1 ) · Enc(m2 ) = g m1 y r1 · g m2 y r2
xi are quantized to reduce their size before transmission. We
= g m1 +m2 y r1 +r2 mod p (20)
assume that the elements of xi fall within the range [r1 , r2 ].
The quantization process is defined as follows: - The range
Although this transformation enables additive homomor[r1 , r2 ] is partitioned into N contiguous intervals with equal phism, it significantly increases the computational burden of
probability. - The threshold value separating the l-th and encryption and decryption, primarily due to the necessity
(l + 1)-th intervals is given by Eq. (16).
of discrete logarithm recovery. Zhu et al. employed bruteAfter applying pruning to the model updates at each client,
t+1
is computed as:
the pruned local update Δwp,i

T (l ) = r1 + l · ΔN

(16)

where ΔN is the quantization interval, calculated using
Eq. (17).
ΔN =

r2 − r1
N −1

(17)

force search and logarithmic recovery techniques to retrieve
plaintexts, which are computationally intensive.
To ensure privacy during the federated learning process,
SecureDyn-FL employs a post-Cramer transformed additive
ElGamal encryption scheme, enabling additive homomorphism while maintaining computational efficiency. This allows
encrypted local model updates to be aggregated on the server

SOOMRO et al.: SecureDyn-FL: A ROBUST PRIVACY-PRESERVING FL FRAMEWORK

without decryption, thereby preventing information leakage
to both external adversaries and honest-but-curious servers.
Unlike differential privacy, which introduces noise and can
negatively impact utility, this encryption mechanism preserves
the exact model updates, thus avoiding accuracy degradation during aggregation. The approach balances privacy and
performance, offering a practical alternative to DP or fully
homomorphic encryption, which often impose significant computational costs. The process involves the following steps:
First, select two large, distinct prime numbers pp and
qp of equal bit-length, and compute n = pp · qp and
λ = lcm(pp − 1, qp −1) , ensuring that n 2 < p. Then, choose
a generator gp ∈ Z∗n 2 such that


gcd L(gpλ mod n 2 ), n = 1,
(21)
where the function L(x ) = x −1
n denotes the L-function used
in the Paillier cryptosystem. With this setup, the message m
is transformed into m  = gpm mod n 2 , and the encryption
scheme is expressed as:
c := c1 = g r

mod p,

c2 = gpm

mod n 2 · y r

mod p(22)

This modified ciphertext structure retains additive homomorphism, enabling secure aggregation in FL. Upon
decryption using ElGamal, the transformed message m  = gpm
mod n 2 is obtained. The original plaintext m is recovered
through the expression:


L gpm mod n 2
 mod n
m=  λ
(23)
L gp mod n 2
Therefore, if two clients u1 and u2 share the public parameters (gp , n, λ), they can independently decrypt the ciphertext
and retrieve the plaintext m. The complete encryption, homomorphic addition, and decryption process is summarized in
Algorithm 1.
J. Central Auditor Protocol
The CA module includes three phases: Phase 1 generates
keys and IDs as described in section, Phase 2 detects and
filters poisoning gradients, and Phase 3 aggregates gradients,
as discussed below.
K. Phase 1: System Initialization
The audit module initializes the federated system by performing the following tasks:
• Generates pair-keys (public-private) K = (pk , qk ) for
each user n, where n ∈ N and |N | = N .
• Assigns a unique tag ID {TID1 , TID2 , . . . , TIDn } to
each user.
• Constructs the Update_Table that includes tuples
(TID , Table_Tag) to facilitate CA on the user side.
L. Phase 2: Dynamic Temporal Gradient Auditing
The original Phase 2 auditing mechanism, which relied
on static clustering via GMM and MD filtering, exhibited
vulnerabilities under realistic FL conditions, particularly in the
presence of non-IID user data and adaptive adversaries. Static

1751

Algorithm 1 Post-Cramer Transformation Based Encryption
and Decryption
Encryption: Encpk (m) → m
1: Convert plaintext m to m  = gpm mod n 2 using postCramer transformation.
2: Compute ciphertext:
c1 = g r mod p
c2 = gpm mod n 2 · y r mod p
m = c1 , c2 
Homomorphic Addition: m1  · m2  = m1 + m2 
m
1: Let m1  = c11 = g r1 mod p, c12 = gp 1 mod n 2 ·
r
1
y mod p
m
2: Let m2  = c21 = g r2 mod p, c22 = gp 2 mod n 2 ·
r
2
y mod p
3: Compute:
c1 = g r1 +r2 mod p
c2 = gpm1 +m2 mod n 2 · y r1 +r2 mod p
m1 + m2  = c1 , c2 
Decryption: Decsk (m) → m
1: Compute:
p
gpm mod n 2 = gcxr2 mod
mod p =
2: Apply L-function: L(x ) = x −1
n
3: Recover plaintext:

gpm mod n 2 ·y r
mod p
g xr

L(g m mod n 2 )

m = L(gpλ mod n 2 ) mod n
p

clustering at each round caused instability in detection, while
single-round MD evaluation failed to account for temporal
variations. To overcome these limitations, we propose an
improved Phase 2 auditing strategy that integrates incremental
GMM updating, temporal trajectory consistency analysis, and
dynamic multi-threshold gradient filtering.
At each communication round t, the auditor receives
encrypted gradients from users. Instead of reinitializing clustering, the GMM parameters, denoted by θt , are updated
incrementally by blending the previous round’s parameters
θt−1 with the newly estimated parameters θnew as follows:
θt = αθt−1 + (1 − α)θnew ,

(24)

where α ∈ (0, 1) is the forgetting factor controlling the
influence of historical information. This incremental updating
allows the clustering model to adapt gradually to evolving data
distributions without overreacting to local fluctuations, thereby
improving robustness in non-IID environments.
Following clustering, the MDMDi (t) for each user’s gradient is computed relative to the mean and covariance of
its assigned cluster. To capture user behavior over time, we
introduce a trajectory consistency analysis by tracking the
variation in MD values across consecutive rounds. Specifically,
for each user i, the trajectory consistency score is defined as
Δ MDi = | MDi (t) − MDi (t − 1)|.

(25)

A small Δ MDi suggests stable gradient behavior consistent
with benign updates, while large variations may indicate
adversarial manipulation or instability.

1752

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

To further enhance detection, a dynamic multi-threshold
filtering mechanism is employed, maintaining three adaptively
updated thresholds:
• a gradient magnitude threshold derived from the historical
distribution of benign gradient norms
• a MD threshold TMD defined as
TMD = k × σnormal ,

(26)

where k is a sensitivity constant and σnormal is the
standard deviation of MD values from benign users,
• a trajectory consistency threshold based on the empirical
distribution of Δ MDi values.
Gradients are filtered according to their compliance with
these thresholds: those satisfying all thresholds are accepted,
those moderately deviating are down-weighted, and those
significantly deviating are rejected.
Through this integrated dynamic auditing process, the model
not only filters out obvious malicious gradients but also
mitigates the impact of stealthy or slowly-drifting adversarial
updates.
M. Phase 3: Byzantine-Resilient Gradient Aggregation
Once the Update_Table is populated, the auditor transfers
it to the server:
• The server and auditor interact to ensure Byzantinetolerant aggregation.
• For each communication round, the server applies a
robust aggregation function to the filtered gradients.
• The global model is updated with the aggregated results,
reinforcing reliability and resistance to Byzantine attacks
in the FL environment.
N. Adversarial Resilience Analysis
SecureDyn-FL is designed to withstand multiple types of
adversarial behaviors that typically arise in federated learning,
including both data/model poisoning attacks and inferencebased privacy attacks such as model inversion.
• Resilience to Poisoning Attacks: In federated intrusion
detection, malicious clients may attempt to manipulate
global model behavior by injecting carefully crafted
updates, either to reduce overall detection performance
(untargeted poisoning) or to deliberately misclassify
specific attack types (targeted poisoning). SecureDynFL mitigates these threats through its temporal gradient
auditing mechanism, which leverages an incremental GMM
and MD trajectory scoring. By continuously modeling
the distribution of benign gradient patterns over time, the
auditor can detect deviations that are subtle or adaptive in
nature—such as attacks that gradually poison the model
over multiple rounds—without requiring labeled attack
examples. Abnormal updates are flagged and removed prior
to aggregation, ensuring that malicious contributions have
minimal impact on the global model.
• Resilience to Model Inversion Attacks: In addition to
malicious clients, federated learning is vulnerable to
honest-but-curious servers that attempt to reconstruct
clients’ local data from shared gradients using model

inversion techniques. In SecureDyn-FL, this class of
attacks is neutralized through the use of additive homomorphic encryption, which ensures that local model
updates are encrypted before transmission and remain
encrypted throughout the aggregation process. As a
result, the server never observes raw gradient information,
making inversion or membership inference attempts
infeasible. Under the adopted cryptosystem, the probability of successful gradient reconstruction is negligible
without the private keys of the participating clients.
• Complementary Protection: By jointly integrating temporal gradient auditing and encryption, SecureDyn-FL
provides defense in depth against heterogeneous adversarial strategies. While encryption protects against
server-side inference and eavesdropping, auditing detects
and filters malicious client behavior. This complementary design enhances the overall robustness of federated
intrusion detection systems in realistic IoT environments,
where both privacy breaches and active poisoning threats
may co-occur.
VI. T HEORETICAL A NALYSIS
Secure training in SecureDyn-FL consists of three key
phases: users’ local training, auditor training, and robust
aggregation. Below, we present the theoretical foundations of
each phase, supported by lemmas and theorems to ensure both
correctness and security.
A. Users’ Local Training
In this phase, we assume that the proportion of malicious
users does not exceed 50%. During training round t, every
user ntx , where x ranges from 1 to m, obtains the encrypted
t pk , encrypts it using their public key pk,
global model M
and trains a local model to compute the gradient vector gtx .
To improve the update process, we apply Stochastic Gradient
Descent (SGD) with momentum, incorporating past gradients
through an exponential decay factor ∂ (0 < ∂ < 1):

∂ t−l glx .
(27)
gx ∼
l∈[0,t]

As shown in prior work (e.g., [41]), momentum accelerates convergence, reduces variance, and enhances robustness,
helping mitigate poisoning attacks in federated training.
B. Auditor Training
The auditor identifies malicious gradients using GMM and
MD. The process involves the following steps:
• Collecting labeled data containing benign gradients gi
and malicious gradients gi∗ .
• Extracting and normalizing features Xi for consistent
scaling.
• Dividing the data into training (Dtrain ) and validation
(Dval ) sets.
• Training a GMM using Expectation-Maximization [42]
to estimate parameters for benign and malicious clusters,
initially setting k = 2 clusters [6].

SOOMRO et al.: SecureDyn-FL: A ROBUST PRIVACY-PRESERVING FL FRAMEWORK

•

Iteratively adjusting the number of clusters using the
Bayesian information criterion (BIC) to adapt to the
gradient distribution and minimize misclassifications.
This dynamic clustering approach ensures effective adaptation to encrypted gradient distributions, reducing false
positives, particularly in environments with predominantly
benign users.
C ORRECTNESS
Correctness ensures the accurate sharing of encrypted gradients and effective auditing to filter out malicious contributions.
Lemma 1: Upon receiving user updates via the audit table
φ, the server employs these updates to refine the global model.
The incremented version of the global model is derived from
the equation:

1 
1 − Mkti φt + Mkti φτki .
N
N

φτ +1 =

(28)

i=1

Here, φτ +1 represents the updated audit table at the subsequent time step, N stands for the total number of users, Mkti
is the model from the i-th user, and φτki denotes the i-th user’s
entry in the audit table at time step τ .
Lemma 2: The CA holds the security property, such as
pair keys (pk , qk ), and learns nothing about private data like
gradients and the aggregation results.
Lemma 3: AHE ensures the confidentiality of both the user
and server sides since user i encrypts its gradients denoted by
xim . Then, each user sends Enc(σim ).
Lemma 4: The cryptosystem is clear by defining a random
value as r, r = ab to have two prime factors of equal size
a and b and letting c ∈ Z and k1 , k2 ∈ Z×
r . It is possible
to compute Enc(k1 + k2 ) using only the public key and the
Encryption Enc(k1 ), Enc(m2 ). Additionally, Enc(m ×k1 ) can
be calculated given a constant m.
Under Lemmas 1 and 2, the audit protocol enables the
Updated_Table to carry user gradients for the aggregation
process. The Updated_Table is populated by users (Ui ⊆ U )
at round t, with gradients reflecting diverse data quality and
distributions. Trustworthy auditors and user compliance with
the workflow, absence of malicious activity, ensure correct
gradient vector W aggregation.
Theorem 1 (Robustness Against Malicious Gradients via
Auditability - IID): Based on Lemma 1 and the participation of registered users as (Ui ⊆ U , i ∈ N ), we have
{U1 , U2 , . . . , Un }, that j ⊆ Ui ⊆ U denotes users that send
malicious gradients. The assumption is |j | ≤ n/2 , and the
auditor traces users based on the audit protocol to find the
adversarial users. Our proposed model checks the gradient
distribution and behavior for all users to remove the effect of
adversary user participation and obtain robustness. Therefore,
the auditor can confirm user k and calculate that the gradient
gk is valid. Adversarial users who send malicious updates will
have their ID revoked. We can guarantee to reduce their effect
on them.
In this regard, based on proof of Lemma 1, the symbol
Ui Ui+1 represents users who uploaded data in round t, but
some users may still inject false data in round t + 1 in the

1753

IID setting. Thus, each user holds a local gradient denoted as
xn (where n ∈ U ). According to Lemma 2, the auditor can
obtain the following expression:
W pk =

n


W i pk =

i=1

n


W i pk .

(29)

i=1

Here, W represents the aggregated encrypted gradients, and
W i represents
the encrypted gradient from the i-th user. The

symbol ni=1 denotes the product operator, indicating that
the encrypted gradients from all users are multiplied together.
Likewise, ni=1 represents the summation operator, indicating
that the encrypted gradients from all users are summed
together. It is important to note that the encrypted gradients
have been received confidentially and can be expressed as
W = ni=1 Wi (see Lemma 3).
In the following round, the auditor computes the GMM for
gradients, then tracks wt+1 with the MD, using the parameters
provided by every user in round t + 1,
wt+1 ←

t
u⊂Ut wu
M
t
u mk

(30)

to track benign and adversaries. The assumption is that there
are fewer than half the users who are adversaries U2t ; hence,
the mean of each cluster is expected to correspond to the
similarity value of at least one benign user.
The auditor first calculates the covariance matrix for cluster
the variance and correlation structure and then applies MD to
detect injected false data (see Audit section V-B). Therefore,
w i , w j , w z , i , j , z ∈ FM (i , z ∈ [1, N ], j ∈ [1, N /2]) are
gradients corresponding to the similarity position of benign
users and adversaries. According Lemma 4, benign users
gradients, w i , w z ∈ FM satisfies:
w i + w z ≡ xit + yzt

(mod mt )

(31)

While gradients of adversarial users w j ∈ FM cannot satisfy
Eq. (3). Note that t = {1, 2, . . . , k }, xit , t is an element in the
Pi ’s original gradient Wi .
Theorem 2: The proposed scheme is secure in terms of user
gradient confidentiality.
Proof: In SecureDyn-FL, privacy leakage mainly occurs in
the following three scenarios:
1) Gradient transmission process
2) Poisoning detection process
3) Key leakage
1. Gradient Transmission Security: SecureDyn-FL
employs Elgamal encryption technology to protect the gradient information submitted by users during transmission.
This security framework ensures that sensitive information
exchanged between participants is not accessible to unauthorized adversaries. Furthermore, since the keys are generated
in a distributed manner, no single entity within the system has
complete knowledge of the key information.
Mathematically, for an adversary to access user data without
the private key, they would need to solve the discrete logarithm
problem:
Given(g, g x mod p), ﬁnd x

(32)

1754

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

where g is a generator of the multiplicative group, p is
a large prime, and x is the private key. This problem is
computationally infeasible for sufficiently large parameters.
2. Poisoning Detection Privacy: To safeguard privacy
during poisoning detection, SecureDyn-FL uses one-time pad
encryption for gradients, which provides perfect secrecy when:
c =m ⊕k

(33)

where c is the ciphertext, m is the plaintext gradient, and k is
the random mask. The masks are generated by CPC members
through (T, n)-threshold secret sharing, ensuring that:
|S | < T ⇒ Pr[reconstruct k ] = negligible

(34)

for any subset of colluding parties S.
3. Key Security: The PRKG key generation in SecureDynFL uses Shamir’s secret sharing where:
f (x ) = s + a1 x + · · · + aT −1 x T −1 mod p

(35)

and shares are (xi , f (xi )). The secret s (private key) can only
be recovered when:
s=

T

i=1

f (xi )

T

j =1
j =i

xj
xj − xi

(36)

which requires at least T participants for successful reconstruction.
By analyzing these three aspects, including secure gradient
transmission via Elgamal encryption, privacy-preserving poisoning detection using one-time pads with threshold masks,
and robust key management through PRKG, we conclude
that SecureDyn-FL effectively protects the confidentiality of
gradient information.
Theorem 3 (Robustness Against Malicious Gradients via
Auditability - non-IID): According to Theorem 1, there is a
subset of user gradients donated by (Hi ⊆ U , i ∈ [N /2])
that lie on the boundary of gradient similarities, as indicated
by Eq. (2). This implies that users i ∈ Di possess non-IID
data. However, the auditor must distinguish between legitimate
users and adversaries, introducing gradient drift. Thus, in the
t-th round, the auditor leverages the gradient of the global
∗
from the previous round to analyze the current
model wt−1
∗
= (wt − wt−1 )/ε,
behavior of the gradient wt , where wt−1
and ε represents the direction of the global model gradient
(Lemma 4).
Consequently, the auditor approximates the benign gradient
∗
= (wt − wt−1 )/ε.
update in the t-th round as w
t∗ ≈ wt−1
In a gradient drift attack, the direction of the gradient ε does
not converge, as the attacker can use an inappropriate scaling
factor ε to amplify fake local model updates, ensuring their
magnitudes are no smaller than those from genuine users. The
attacker i sends a fake gradient as wt∗i = −ε(wt − wt−1 ).
VII. E XPERIMENTAL A NALYSIS
This section presents the experimental evaluation of
the proposed SecureDyn-FL framework using the N-BaIoT
TONIoT dataset. We compare its performance against several

state-of-the-art methods to assess its effectiveness under varying data distribution and poisoning attack scenarios. Details
of the experimental environment, dataset preparation, and data
distribution strategies are provided below.
A. Experimental Environment
All experiments were conducted using the PyTorch framework. The client-side evaluations were performed on a
machine equipped with an Intel Core i7-10750H CPU @
2.60 GHz and 64 GB of RAM.
B. Dataset Description
To rigorously evaluate the performance and generalizability
of the proposed framework, two widely recognized benchmark datasets were employed: the N-BaIoT dataset [69] and
the TONIoT dataset [70]. The N-BaIoT dataset comprises
network traffic traces generated by nine commercially available IoT devices that were intentionally compromised using
the Mirai and BASHLITE malware families. In total, the
dataset contains more than 70 million traffic records, each
represented by a 115-dimensional feature vector derived from
statistical characteristics of network flows. This dataset is
designed to support binary classification tasks—differentiating
benign from malicious traffic—while also offering ten distinct
attack sub-categories corresponding to various manifestations
of the underlying malware.
The TONIoT dataset, on the other hand, encompasses a
diverse spectrum of IoT-related cyberattacks alongside legitimate traffic instances. It integrates telemetry and network data,
annotated with 46 labeled features that capture relevant behavioral attributes. Unlike N-BaIoT, the TONIoT dataset frames
the detection problem as a multi-class classification task,
aiming to distinguish between normal activity and multiple
heterogeneous attack types. This combination of datasets
enables a comprehensive and robust evaluation across both
binary and multi-class intrusion detection scenarios, reflecting
realistic IoT network environments.
To provide a clear and structured overview of the data
employed in this study, Tables I and II summarize the distribution of samples across the attack categories for the
TONIoT and mini-N-BaIoT datasets, respectively. The tables
have been designed with consistent formatting to facilitate
straightforward comparison between the two datasets. While
the TONIoT dataset reflects realistic network conditions with
significant class imbalance across multiple attack categories,
the mini-N-BaIoT dataset is more balanced, containing evenly
distributed samples across various Mirai and BASHLITE
attack subtypes.
The mini-N-BaIoT dataset was partitioned into training
and testing subsets using a 70:30 split. The training data
was distributed among participating clients in the FL setup,
while the testing data was centrally used to evaluate the
performance of the aggregated model. To simulate a realistic
FL environment with a large number of participants, the
training dataset was further divided among 20 clients. This
client-simulation strategy is widely adopted in FL literature to

SOOMRO et al.: SecureDyn-FL: A ROBUST PRIVACY-PRESERVING FL FRAMEWORK

TABLE I
D ISTRIBUTION OF T RAINING AND T EST S AMPLES ACROSS ATTACK
C ATEGORIES IN THE TONIoT DATASET

1755

TABLE III
H YPERPARAMETERS

TABLE II
D ISTRIBUTION OF S AMPLES ACROSS ATTACK C ATEGORIES IN THE
M INI -N-BA I OT DATASET

mirrors real-world traffic imbalances where benign traffic is
more prevalent and not all devices experience attacks.
D. Poisoning attack setting

mimic decentralized data scenarios. The key hyperparameters
used in our experiments are summarized in Table III.
C. Data Distribution Scenarios
To investigate the robustness of the proposed framework
under heterogeneous conditions, we implemented three distinct
data distribution settings across the 20 clients. The scenarios
are designed to simulate both IID and non-IID data distributions, as described below:
• Non-IID Scenario 1: The client data is sampled using a
Dirichlet distribution with concentration parameter η =
0.1, inducing high heterogeneity across clients.
• Non-IID Scenario 2: Half of the clients are assigned
only benign traffic samples, while the remaining half
receive only attack samples. This setup reflects practical
conditions where some IoT devices may never be compromised.
• IID Scenario: Each client receives a balanced dataset
composed of 50% benign and 50% attack samples,
ensuring uniform data distribution across all clients.
In both the IID and Non-IID Scenario 1, each client is
allocated exactly 1000 samples to ensure consistency in local
training workloads. In Non-IID Scenario 2, clients with only
benign samples are assigned 500 samples, while those with
only attack data are assigned 1000 samples. This variation

To evaluate the performance of our approach, we simulate
a range of model poisoning attacks using encrypted local
gradients. These simulations examine varying degrees of
adversarial presence, represented by different attack ratios, α,
which we set at 10%, 20%, 30%, and 50%. In evaluating
FL, similar to the assessment of related work based on [43],
the number of users is related to the number of classes in
each dataset to provide IID and non-IID settings. For the
N-BaIoT dataset, 20 users participated, and the attack aims to
transform instances from Class 9 to Class 11. In addition to
the above configurations, we establish a baseline model representing a poisoned SecureDyn-FL system without any defense
mechanisms or central audit. This baseline model serves as
a comparison point, illustrating the enhanced effectiveness of
our proposed approach in defending against various model
poisoning attacks.
E. Accuracy, Robustness, & Malicious Alarm Analysis
In model poisoning, adversaries aim to optimize
arg max Ht (w − w ∗ ),
i∈[1,n]

(37)

where H is a vector representing the model’s direction
changes, w is the pre-attack model, and w ∗ is the poisoned
model in targeted and untargeted attacks. Our evaluation
metrics for targeted attacks include Attack Class Accuracy,
which measures testing performance on the targeted labels, and
Benign Class Accuracy, which evaluates learning performance
on non-source and non-target labels. These metrics are crucial
for detecting potential auditing failures and unintended adverse
effects on the FL system. Additionally, Overall Accuracy represents the average classification performance across all labels,

1756

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

providing a comprehensive view of the defense mechanisms’
effectiveness against poisoning attacks. The Malicious Alarm,
assessed using the Receiver Operating Characteristic (ROC)
curve, reflects the capability of defense algorithms to accurately identify malicious activities within the FL environment.
It is important to note that Overall Accuracy may differ from
the combined Attack Class and Benign Class accuracies due
to the impact of various attack and defense strategies. For
untargeted attacks, we focus on evaluating Overall Accuracy
and the Malicious Alarm metrics.
F. Accuracy Evaluation Under Targeted and Untargeted
Attacks With Baseline Model
Table VIII presents a comparative analysis of the baseline and the proposed model under targeted and untargeted
poisoning attacks, considering both non-IID and IID data
distributions with a fixed attack rate of 50%.
Under the non-IID setting, the baseline model shows poor
performance across all metrics. For targeted attacks, it records
a Tacc of 0.015, an Oacc of 0.94, and an F1-score of 0.04.
In untargeted attacks, the baseline improves slightly, with
Tacc = 0.782, Oacc = 0.761, and F1-score of 0.62. In
contrast, the proposed model shows substantial performance
gains. For targeted attacks, it achieves a Tacc of 0.995, Oacc
of 0.992, and an F1-score of 0.89. During untargeted attacks,
it maintains strong results with Tacc = 0.989, Oacc =
0.967, and F1-score of 0.84, highlighting its robustness against
adversarial threats under data heterogeneity.
Under the IID setting, where training data is evenly distributed among clients, the baseline model still underperforms.
For targeted attacks, it yields a Tacc of 0.049, an Oacc of
0.60, and an F1-score of 0.47. In untargeted attacks, the
results slightly improve, with Tacc = 0.58, Oacc = 0.52,
and an F1-score of 0.55. The proposed model, however,
consistently outperforms the baseline. For targeted attacks, it
achieves a near-perfect Tacc of 0.997, Oacc of 0.995, and
F1-score of 0.98. In untargeted attacks, it delivers Tacc =
0.992, Oacc = 0.991, and F1-score of 0.96. These results
confirm the proposed model’s robustness and generalizability
across both homogeneous and heterogeneous data distributions, establishing its efficacy in defending FL systems against
diverse poisoning threats.
G. Robustness and Auditing Evaluation
1) a) RTAnonIID : Robustness to Targeted Attacks (NonIID): The robustness of the proposed model under targeted
attacks with non-IID data is evaluated in Fig. 9, where
performance is analyzed across varying attack rates from
10% to 50%. The results reveal that the model consistently
maintains high accuracy levels, with minimal degradation
despite increased attack intensity. This consistency underscores the model’s ability to sustain reliable performance even
in adversarial environments, thereby confirming its robustness
to targeted poisoning in non-IID scenarios.
b) RUTAnonIID : Robustness to Untargeted Attacks (NonIID): As shown in Fig. 10, the proposed model also exhibits
high resilience against untargeted attacks under non-IID data

Fig. 4.

Analyzing malicious alarms on IID data.

settings. Across varying attack rates and user distributions,
the accuracy remains stable and robust. This reinforces
the model’s capacity to mitigate the effects of non-specific
adversarial disruptions, preserving its integrity and predictive
performance.
c) RTAIID : Robustness to Targeted Attacks (IID): To evaluate robustness under IID data conditions, the model is exposed
to targeted attacks across varying attack rates, as shown in
Fig. 8. The proposed method consistently maintains stable
accuracy, demonstrating resilience against adversarial intensities. These results underscore its effectiveness in protecting
FL systems under homogeneous data distributions, ensuring
robust defense even when the training process is explicitly
targeted.
d) RUTAIID : Robustness to Untargeted Attacks (IID): The
model’s performance under untargeted attacks with IID data
is illustrated in Fig. 11. Despite the uniform distribution
of training data, which typically increases vulnerability, the
proposed approach sustains high accuracy levels across a wide
range of adversarial configurations. These results confirm the
model’s reliability and adaptability in diverse deployment environments, supporting its utility in real-world FL applications.
e) Model Auditing (MA) Evaluation: The CA of the
proposed model is assessed through ROC analysis, focusing
on its ability to detect both falsely labeled malicious and clean
users. As shown in Figs. 4 and 5, the ROC curves for both IID
and non-IID scenarios on the KDDCup dataset exhibit superior
characteristics compared to baselines. The proposed model
achieves the highest average ROC, demonstrating not only
strong classification performance but also effective auditing
functionality. These findings highlight that the robustness
and precision of the CA module significantly contribute to
the overall reliability of the model, ensuring comprehensive
protection against FL poisoning threats.

SOOMRO et al.: SecureDyn-FL: A ROBUST PRIVACY-PRESERVING FL FRAMEWORK

Fig. 5.

Analyzing malicious alarms on non-IID data.

1757

Fig. 6. Accuracy convergence comparison on the mini-N-BaIoT dataset
between SecureDyn-FL and representative SOTA FL-based IDS methods. Synthetic convergence curves are based on reported final accuracies.
SecureDyn-FL achieves both faster convergence and higher final accuracy.

VIII. C OMPARISON W ITH S TATE - OF - THE -A RT R ESEARCH
In this section, we comprehensively evaluate the robustness of our proposed SecureDyn-FL framework against
poisoning attacks on non-IID data distributions and compare it with several state-of-the-art methods, including
FedAvg, coordinate-wise median, trimmed mean, multiKrum, and FL-Defender. Furthermore, additional comparisons
with advanced schemes such as Trimmed Means [17], FLDefender [47], FedAvg [11], FLTrust, and ShieldFL [43] are
also provided to demonstrate the superiority of our model
under various data settings and attack types.
Beyond these baseline defenses, we also compare
SecureDyn-FL with representative state-of-the-art FL-based
IDS frameworks from the literature, including RuzafaAlcázar et al. (DP-based Industrial IoT), Bhavsar et al.
(Transportation FL-IDS), Friha et al. (FELIDS), and PEIoTDS (N-BaIoT).
A. Comparative Accuracy Analysis With SOTA FL-IDS
To comprehensively evaluate the effectiveness of
SecureDyn-FL, we conducted comparative analyses against
several representative state-of-the-art (SOTA) FL-based
intrusion detection frameworks on both the mini-N-BaIoT
and TONIoT datasets. Figures 6 and 7 illustrate the accuracy
convergence behavior of all methods across training rounds.
On the mini-N-BaIoT dataset Figure 6, SecureDyn-FL
demonstrates consistently faster convergence and achieves
the highest final accuracy among all compared methods.
Specifically, SecureDyn-FL attains a final accuracy of approximately 99.5%, surpassing Bhavsar et al. (97%), Friha et al.
(96%), PEIoT-DS (95%), and Ruzafa-Alcázar et al. (93%).
These results highlight the model’s ability to learn efficiently
in a relatively balanced and less diverse IoT network environment.

On the more challenging TONIoT dataset Figure 7,
which exhibits greater heterogeneity, class imbalance, and a
broader range of attack scenarios, all methods show slightly
lower final accuracies and slower convergence. Nonetheless,
SecureDyn-FL maintains a distinct advantage, converging
faster and reaching a final accuracy of approximately 98.6%.
In contrast, Bhavsar et al., Friha et al., PEIoT-DS, and RuzafaAlcázar et al. achieve 95.0%, 94.2%, 93.5%, and 92.0%
respectively. This performance gap underscores SecureDynFL’s robustness in more realistic and complex IoT intrusion
detection scenarios.
Taken together, these results demonstrate not only the
superior detection performance of SecureDyn-FL under federated learning settings but also its strong generalizability
across datasets of varying complexity. While many existing
frameworks exhibit significant performance drops when transitioning from simpler to more heterogeneous data distributions,
SecureDyn-FL consistently maintains high accuracy and rapid
convergence. This indicates that the proposed framework
can adapt effectively to diverse IoT environments without
extensive reconfiguration or accuracy degradation.
Moreover, by integrating additive homomorphic encryption and temporal gradient auditing, SecureDyn-FL provides
enhanced privacy protection without compromising model
performance. Unlike approaches based on differential privacy—
which often trade off utility for privacy—or those that expose raw
gradients to the server, SecureDyn-FL achieves strong privacy
guarantees and robustness concurrently.
B. Scenario 1: Dirichlet Non-IID Data Distribution
In the first scenario, non-IID data was generated using a
Dirichlet distribution with a concentration parameter η = 0.1,
simulating a highly imbalanced client data distribution. In

1758

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

resilience to backdoor-style threats. Overall, these results
highlight the effectiveness of SecureDyn-FL in maintaining
detection performance even under severe non-IID conditions
and adversarial settings.
C. Scenario 2: Clients With Missing Attack Labels

Fig. 7.
Accuracy convergence comparison on the TONIoT dataset
between SecureDyn-FL and representative SOTA FL-based IDS methods.
Despite increased dataset heterogeneity, SecureDyn-FL maintains superior
convergence speed, accuracy, and generalizability.
TABLE IV
P RIVACY ATTACK R ESULTS : G RADIENT I NVERSION AND M EMBERSHIP
I NFERENCE

the absence of poisoning, all methods demonstrated strong
performance, with the proposed model achieving the highest
accuracy 0.9842 and F1-score 0.9801, albeit with a slight
performance dip (1̃%) compared to IID settings.
As shown in Table VI, the proposed method consistently
outperforms existing defense strategies under all poisoning
attack scenarios, maintaining high classification accuracy and
very low attack success rates (ASR). For instance, under
benign label-flipping attacks, while other methods like FedAvg
and FL-Defender suffer ASRs of 0.0185 and 1.0000 respectively, the proposed model limits the ASR to just 0.0072. Even
in the combined label-flipping attack, where methods such as
Shield FL and FL trust show degraded performance e.g., ASR
of 0.0345 and 0.5034 respectively. The proposed model retains
a strong F1-score of 0.9645 and limits ASR to 0.0512.
Under model-scaling attacks, traditional defenses like
FedAvg and trimmed mean drop to 45.12% accuracy and F1score of 0.6414, exposing them to high false alarm rates. In
contrast, the proposed method remains robust, with accuracy
at 97.07% and F1-score of 0.9695, while maintaining ASR
at a minimal 0.0568. A similar trend is observed under the
same-model poisoning attack, where the proposed method
delivers the best results across all metrics—97.01% accuracy,
0.9708 F1-score, and only 0.0402 ASR—demonstrating its

The second scenario simulates a more realistic IoT environment, where attack samples are absent from half of the clients.
This setup reflects practical federated deployments, where not
all edge devices observe malicious behavior, resulting in sparse
and partially distributed attack data.
As shown in Table VII, the proposed method consistently
achieves the highest performance across all metrics, even outperforming FedAvg, which traditionally handles IID settings
well. In the absence of attacks, the proposed model attains
98.40% accuracy and 0.9838 F1-score, shows its ability to
preserve model quality without any degradation.
Under benign label-flipping attacks, the proposed method
limits the attack success rate (ASR) to a mere 0.0061, whereas
all other baselines—including Shield FL, FL Trust, and FLDefender—fail completely, recording an ASR of 1.0000.
Similarly, under attacks where malicious labels are flipped to
benign, the proposed model maintains high accuracy 0.9814,
F1-score 0.9775, and the lowest ASR 0.0738, while FL Trust
and Shield FL show significant degradation in both accuracy
and F1 performance.
In combined label-flipping scenarios, most methods see a
marked drop, with trimmed mean and FL-Defender yielding
F1-scores of 0.6381 and 0.6378 respectively, also ASRs
exceeding 0.5. The proposed model, in contrast, delivers a high
F1-score of 0.9762, accuracy of 0.9698, and an ASR of only
0.0421.
For model-scaling attacks, which often lead to oversuppression of legitimate updates, methods like FedAvg and
Shield FL fall to 47.06% accuracy and F1-scores near 0.64,
misclassifying most benign data. However, the proposed
method effectively mitigates these attacks, achieving 98.23%
accuracy, 0.9725 F1-score, and a low ASR of 0.0341. Even in
same-model poisoning, where poisoned updates are identical
across clients, the proposed method again stands out, achieving
the highest accuracy 99.01%, F1-score 0.9893, and the lowest
ASR 0.0405 among all tested methods.
Interestingly, as shown in Tables VI and VII, the FedAvg
baseline demonstrates relatively strong performance in certain
experimental settings, in some cases approaching the accuracy
of more robust aggregation methods. This behavior can be
explained by the moderate adversarial participation ratios and
data distributions used in these scenarios, where the majority
of clients provide benign updates. Under such conditions,
FedAvg’s simple averaging can still yield a stable and accurate
global model because the impact of malicious gradients is
statistically diluted by the dominant benign contributions.
Moreover, FedAvg often exhibits fast initial convergence in
clean settings, which can temporarily narrow the performance
gap with more advanced defense mechanisms. However, as
adversarial intensity or data heterogeneity increases, FedAvg
lacks the necessary resilience and its performance degrades

SOOMRO et al.: SecureDyn-FL: A ROBUST PRIVACY-PRESERVING FL FRAMEWORK

significantly compared to SecureDyn-FL, as shown in the
higher attack ratios and non-IID settings.
SecureDyn-FL successfully defended against all poisoning
strategies in this challenging non-IID setting, preserving high
accuracy and maintaining a low ASR, confirming its strong
resilience under data heterogeneity and sparsity.

1759

TABLE V
D ETECTION D ELAY C OMPARISON B ETWEEN S ECURE DYN -FL AND
FL-BASED I OT IDS F RAMEWORKS

D. Privacy Evaluation Against Inference Attacks
To complement the theoretical privacy guarantees of
SecureDyn-FL, we conduct experimental validation against
two common privacy attacks in federated learning: gradient
inversion and membership inference.
For gradient inversion, we apply the attack method to both
FedAvg and SecureDyn-FL. In FedAvg, where the server has
access to raw model updates, the attacker can successfully
reconstruct client-side input features with high visual and
numerical similarity. In contrast, SecureDyn-FL employs additive homomorphic encryption before gradient transmission,
which prevents the server from observing raw gradients. As
a result, reconstruction attempts produce only random noise,
indicating that no meaningful information can be recovered.
For membership inference, we evaluate the attack accuracy against both FedAvg and SecureDyn-FL. While FedAvg
exhibits elevated inference accuracy, indicating information
leakage through gradient updates, SecureDyn-FL achieves
attack performance close to random guessing, confirming that
encrypted gradients significantly reduce leakage.
Table IV summarizes the results of the gradient inversion
and membership inference attacks conducted on the FedAvg
baseline and the proposed SecureDyn-FL framework. For the
gradient inversion attack, we use the Structural Similarity
Index Measure (SSIM) between the original client data and
the reconstructed data to quantify the extent of information
leakage. Higher SSIM values indicate more successful reconstruction and thus greater privacy risk.
As shown in the table, FedAvg exhibits a high SSIM score
(0.78), demonstrating that the server can effectively reconstruct
sensitive client data when raw gradients are exposed. In
contrast, SecureDyn-FL achieves a very low SSIM score
(0.07), indicating that gradient inversion produces only random
noise due to the use of additive homomorphic encryption,
which prevents the server from observing raw updates.
For membership inference, we report the attacker’s classification accuracy in determining whether a given data sample
was part of the training set. FedAvg shows high inference
accuracy (0.82), implying considerable leakage through gradients, whereas SecureDyn-FL achieves near-random inference
accuracy (0.51), effectively mitigating membership inference
attacks.
These results provide quantitative evidence that SecureDynFL offers stronger privacy protection than standard FL
methods, complementing the theoretical security analysis
presented earlier.
E. Efficiency Evaluation
In addition to accuracy and privacy assessments, we evaluate
the efficiency of SecureDyn-FL in terms of detection delay
and communication overhead. Detection delay refers to the

average time required for the global model to correctly detect
an intrusion after its occurrence in the federated training
process. Lower detection delay is critical for timely response
in IoT environments.
We compare the detection delay of SecureDyn-FL against
FedAvg and representative FL-based IoT IDS frameworks.
As shown in Table V, SecureDyn-FL achieves a significantly
lower detection delay while maintaining high accuracy. This
efficiency improvement is attributed to the framework’s temporal gradient auditing, which accelerates the detection of
poisoned updates, and dynamic pruning and quantization,
which reduce communication overhead and enable faster
model updates.
Table V summarizes the detection delay of SecureDyn-FL
compared to FedAvg and representative FL-based IoT IDS
frameworks. Detection delay measures the average time taken
by each method to correctly detect an intrusion event after
it occurs, which is a critical efficiency metric for real-time
intrusion detection in IoT networks.
As shown in the table, SecureDyn-FL achieves the lowest
detection delay (2.14 s), significantly outperforming FedAvg
and other FL-based IDS frameworks. This improvement is
attributed to two key design features of SecureDyn-FL: (1)
the temporal gradient auditing mechanism, which rapidly
identifies and filters malicious updates, thereby allowing the
model to respond more quickly to new attack patterns, and
(2) the dynamic pruning and adaptive quantization strategies,
which reduce communication overhead and accelerate the
overall training process.
These results demonstrate that SecureDyn-FL not only
delivers superior accuracy and privacy protection but also
achieves high efficiency, making it practical for real-world
IoT intrusion detection deployments where rapid response is
essential.
IX. C OMPLEXITY & C OMPUTATIONAL A NALYSIS
We provide a detailed computational and communication complexity analysis of SecureDyn-FL, quantifying
overhead at the client, server, and auditor, and showing that
redundancy-aware optimizations, pruning, and quantization
enable deployment in resource-constrained IoT environments.
The analysis is structured by system entities, including client
devices, the central server, and the trusted auditor, and parameterized by the number of participating clients C and model
dimensionality ω. Special attention is given to the optimization
mechanisms, particularly gradient redundancy elimination,
which significantly reduces repetitive computations and
transmissions. These enhancements promote scalability and

1760

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

TABLE VI
P ERFORMANCE OF D EFENSE M ETHODS U NDER D IFFERENT P OISONING ATTACKS (S CENARIO 1)

TABLE VII
P ERFORMANCE OF D EFENSE M ETHODS U NDER D IFFERENT P OISONING ATTACKS (S CENARIO 2)

computational efficiency, thus enabling deployment in largescale and resource-constrained IoT environments. Empirical
evidence is provided to support the efficacy of these strategies
in mitigating overhead while preserving model accuracy in
adversarial conditions. Furthermore, the proposed encryption
scheme is evaluated against contemporary privacy-preserving
alternatives.

A. Computational Overhead at Client Devices
For each client cj , the dominant computational cost stems
from encrypting local updates, which scales with the input
dimension γ. Across all C clients, the cumulative encryption
cost is O(γC log2 C ) . The communication complexity comprises uploading encrypted model parameters and participating
in the initial registration phase, totaling O(ωC + 2C ). These

SOOMRO et al.: SecureDyn-FL: A ROBUST PRIVACY-PRESERVING FL FRAMEWORK

1761

TABLE VIII
P ERFORMANCE C OMPARISON U NDER TARGETED AND U NTARGETED P OISONING ATTACKS FOR IID AND N ON -IID S ETTINGS

Fig. 8.

Targeted Attack under IID.

Fig. 10.

Untargeted-non-IID.

Fig. 9.

Targeted Attack under non IID.

Fig. 11.

Untargeted-IID.

costs are effectively mitigated by redundancy-aware optimizations, which reduce the volume of redundant data transmitted
from client to server.

B. Auditor’s Computational and Communication Cost
The Auditor’s primary tasks include anomaly detection
using GMM and MD, incurring a computational cost of

1762

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

TABLE IX
C OMPUTATIONAL C OST B EFORE AND A FTER A DVERSARIAL C LIENT R EMOVAL

TABLE X
C OMMUNICATION OVERHEAD B EFORE AND A FTER A DVERSARIAL C LIENT R EMOVAL

TABLE XI
C RYPTOGRAPHIC O PERATION T IMES ACROSS K EY S IZES

O(CGδ + C γ log γ), where G represents the number of
Gaussian clusters and δ the feature space dimensionality.
Communication overhead arises from interaction with both
server and clients, expressed as O(R(Ψ + C )), where R
is the number of audit rounds, Ψ ≤ Θ is the number of
gradient evaluations, and Θ is the total reliability checks.
Selective auditing, enabled by our optimization framework,
reduces both computation and communication loads without
sacrificing detection performance.
C. Server-Side Complexity Analysis
The central server aggregates encrypted updates from all
clients with a computational complexity of O(ωC log C ) . Its
communication cost is defined as O(Φ + CV ), where Φ and
V represent interactions with the Auditor and clients, respectively. The Auditor filters malicious or redundant updates
before aggregation, thus reducing the server’s computational
load and expediting training convergence. Quantitative gains
in efficiency following adversarial user elimination are summarized in Tables IX and X. The Auditor’s overhead is shown
to be minimal, especially in low-threat environments, making
it a justifiable trade-off for enhanced system resilience.
D. Cryptographic Cost and Execution Time
Given the security limitations of legacy key sizes in Paillierbased cryptosystems, this work adopts larger keys conforming
to current security standards. The trade-off between computational cost and security is carefully balanced. As key length
increases, encryption latency and memory consumption rise,

as demonstrated in Table XI. Furthermore, as the number of
encrypted gradient elements increases, computational overhead
scales accordingly. Thus, the model dynamically tunes key size
and batch size to balance privacy with performance, ensuring
robust security with feasible latency.
E. Scalability to Large-Scale IoT Deployments
The proposed framework is primarily designed for cross-silo
FL environments, where the number of clients is relatively
small and each participant possesses sufficient computational
resources. Accordingly, our experiments consider 20 clients, all
of which participate in every communication round. However, in
practical large-scale IoT deployments, where thousands of edge
devices may be involved, this full participation model becomes
infeasible due to increased communication overhead and
computational burden on the central server. In such scenarios,
the server must wait for all clients to upload their local models
before aggregation. This dependency introduces a bottleneck,
especially if some clients are slow (i.e., stragglers) or unable
to complete their local training within the prescribed time. To
address these challenges, a *client selection mechanism* can
be integrated, wherein only a randomly chosen subset of clients
participates in each communication round. This approach,
widely adopted in FL literature, significantly reduces server load
and improves training efficiency. Furthermore, to mitigate the
issue of straggling clients, the system can incorporate timeout
strategies to exclude delayed responses from the aggregation
process. Such client drop strategies prevent indefinite server
blocking and maintain the momentum of the learning process.

SOOMRO et al.: SecureDyn-FL: A ROBUST PRIVACY-PRESERVING FL FRAMEWORK

Both client selection and straggler mitigation are active areas
of research in scalable federated learning, and extending our
framework to support these mechanisms is a promising avenue
for future work.
F. Incorporating Recent Advances in Neural Architectures
Selecting an appropriate neural network architecture is
crucial for optimizing the performance of IDS. In this study,
we employ a one-dimensional convolutional neural network
(1D-CNN) as the local model due to its proven efficacy in
modeling time-series and sequential data typical in network
traffic analysis. While our current model achieves competitive
detection performance, exploring advanced neural architectures could further enhance its predictive capability. Recent
studies have demonstrated the effectiveness of hybrid architectures in capturing both spatial and temporal dependencies
in sequential data. For instance, the work in [71] proposed
a deep spatiotemporal model that integrates two-dimensional
CNNs with Long Short-Term Memory (LSTM) networks. In
this hybrid model, CNNs extract spatial features while LSTMs
model temporal correlations, thereby improving detection
performance on sequential datasets. Similarly, the approach
in [72] introduced a differentially private tensor-based recurrent neural network tailored for IoT environments. This model
not only demonstrated robust detection capabilities but also
ensured privacy preservation through the integration of differential privacy mechanisms. Both aforementioned models were
deployed in decentralized settings and demonstrate significant
potential for adaptation to FL scenarios. Incorporating such
architectures into our federated intrusion detection framework
could yield enhanced performance and improved privacy
guarantees. Future research can focus on the integration and
empirical evaluation of these advanced models within the
federated IDS paradigm.
X. C ONCLUSION
In this study, we proposed SecureDyn-FL, a robust FLbased IDS designed to tackle the challenges of poisoning
attacks and non-IID data distributions in IoT environments.
Our empirical findings confirm that malicious clients can
significantly degrade the performance of federated IDS models, with the impact being more severe under non-IID data
settings, a scenario commonly encountered in real-world IoT
deployments due to data heterogeneity and imbalance. To
mitigate these challenges, we introduced a personalized FL
approach that enables local model customization, allowing
each client to adapt to its unique data distribution while still
contributing to the global model. This enhances resilience
against performance degradation caused by non-IID data.
Additionally, we implemented a server-side malicious client
detection mechanism that uses anomaly detection to identify
and exclude adversarial updates, protecting the global model
from poisoning attacks. Extensive experiments on the N-BaIoT
dataset confirm the effectiveness of SecureDyn-FL. Evaluated
using metrics such as accuracy, F1-score, and detection rate,
our approach consistently outperforms state-of-the-art baseline
methods under both IID and non-IID conditions. Notably,

1763

SecureDyn-FL shows strong robustness against poisoning
attacks, including label-flipping and model update poisoning,
while maintaining high detection performance. These results
highlight its practical value for secure and scalable intrusion
detection in heterogeneous IoT networks.
Future work will explore advanced neural architectures
(e.g., graph neural networks and attention mechanisms) to
capture IoT data complexities, scalable client selection strategies (e.g., reinforcement learning methods), and enhanced
attack detection techniques incorporating differential privacy
and secure multi-party computation. In addition, we recognize that blockchain and distributed ledger technologies
(DLTs) can provide immutable logging of model updates,
decentralized trust management, and verifiable audit trails.
Integrating such mechanisms with SecureDyn-FL represents a
promising direction to further strengthen the trustworthiness
and accountability of federated learning in IoT networks.
Collectively, these efforts aim to improve the adaptability,
robustness, and transparency of SecureDyn-FL in large-scale
federated environments.
R EFERENCES
[1] M. Shahjalal et al., “Enabling technologies for AI empowered 6G
massive radio access networks,” ICT Exp., vol. 9, no. 3, pp. 31–355,
Jun. 2023.
[2] H. Yu, H. Lee, and H. Jeon, “What is 5G? Emerging 5G mobile services
and network requirements,” Sustainability, vol. 9, no. 10, p. 1848, 2017.
[3] Y. B. Zikria, H. Yu, M. K. Afzal, M. H. Rehman, and O. Hahm,
“Internet of Things (IoT): Operating system, applications and protocols
design, and validation techniques,” Future Gener. Comput. Syst., vol. 88,
pp. 699–706, Nov. 2018.
[4] M. A. Siddiqi, H. Yu, and J. Joung, “5G ultra-reliable lowlatency communication implementation challenges and operational
issues with IoT devices,” Electronics, vol. 8, no. 9, p. 981,
2019.
[5] I.-G. Lee, D. B. Kim, J. Choi, H. Park, S.-K. Lee, J. Cho, and H. Yu,
“WiFi halow for long-range and low-power Internet of Things: System
on chip development and performance evaluation,” IEEE Commun.
Mag., vol. 59, no. 7, pp. 101–107, Jul. 2021.
[6] A. Musaddiq, Y. B. Zikria, O. Hahm, H. Yu, A. K. Bashir, and
S. W. Kim, “A survey on resource management in IoT operating
systems,” IEEE Access, vol. 6, pp. 8459–8482, 2018.
[7] J. Hojlo, “Future of industry ecosystems: Shared data and insights.” IDC.
2021. [Online]. Available: https://www.idc.com/resource-center/blog/
[8] Q.-U.-A. Arshad, W. Z. Khan, F. Azam, M. K. K. Khan, H. Yu, and
Y. B. Zikria, “Blockchain-based decentralized trust management in IoT:
systems, requirements and challenges,” Complex Intell. Syst., vol. 9,
pp. 6155–6176, 2023.
[9] M. Antonakakis et al., “Understanding the Mirai botnet,” in
Proc. 26th USENIX Security Symp. (USENIX Security), 2017,
pp. 1093–1110.
[10] J. Wu et al., “An intelligent IoT intrusion detection system using
Heinit-WGAN and SSO-BNMCNN based multivariate feature analysis,”
Engineering Applications of Artificial Intelligence, vol. 127, Jan. 2024,
Art. no. 107132.
[11] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. y Arcas,
“Communication-efficient learning of deep networks from decentralized
data,” in Proc. Artif. Intell. Stat., 2017, pp. 1273–1282.
[12] S. Agrawal et al., “Federated learning for intrusion detection system:
Concepts, challenges and future directions,” Comput. Commun.,
vol. 195, pp. 346–361, Nov. 2022.
[13] O. Friha, M. A. Ferrag, L. Shu, L. Maglaras, K.-K. R. Choo,
and M. Nafaa, “FELIDS: Federated learning-based intrusion detection
system for agricultural Internet of Things,” J. Parallel Distrib. Comput.,
vol. 165, pp. 17–31, Jul. 2022.
[14] V. Kelli, V. Argyriou, T. Lagkas, G. Fragulis, E. Grigoriou, and
P. Sarigiannidis, “IDS for industrial applications: A federated learning
approach with active personalization,” Sensors, vol. 21, no. 20, p. 6743,
2021.

1764

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

[15] M. A. Ferrag, O. Friha, L. Maglaras, H. Janicke, and L. Shu,
“Federated deep learning for cyber security in the Internet of Things:
Concepts, applications, and experimental analysis,” IEEe Access, vol. 9,
pp. 138509–138542, 2021.
[16] V. Mothukuri, R. M. Parizi, S. Pouriyeh, Y. Huang, A. Dehghantanha,
and G. Srivastava, “A survey on security and privacy of federated learning,” Future Gener. Comput. Syst., vol. 115, pp. 619–640,
Feb. 2021.
[17] M. Fang, X. Cao, J. Jia, and N. Gong, “Local model poisoning attacks to
{Byzantine-Robust} federated learning,” in Proc. 29th USENIX Security
Symposium (USENIX Security), 2020, pp. 1605–1622.
[18] Y. Chang, K. Zhang, J. Gong, and H. Qian, “Privacy-preserving
federated learning via functional encryption, revisited,” IEEE Trans. Inf.
Forensics Security, vol. 18, pp. 1855–1869, 2023.
[19] V. Rey, P. M. S. Sánchez, A. H. Celdrán, and G. Bovet, “Federated
learning for malware detection in IoT devices,” Comput. Netw., vol. 204,
Feb. 2022, Art. no. 108693.
[20] Z. Zhang, Y. Zhang, D. Guo, L. Yao, and Z. Li, “SecFedNIDS: Robust
defense for poisoning attack against federated learning-based network
intrusion detection system,” Future Gener. Comput. Syst., vol. 134,
pp. 154–169, Sep. 2022.
[21] J. Bae, W. Khalid, A. Lee, H. Lee, S. Noh, and H. Yu, “Overview of RISenabled secure transmission in 6G wireless networks,” Digit. Commun.
Netw., vol. 10, pp. 1553–1565, Dec. 2024.
[22] M. R. A. Ruku, M. Ibrahim, A. Badrudduza, I. S. Ansari, W. Khalid, and
H. Yu, “Effects of co-channel interference on RIS empowered wireless
networks amid multiple eavesdropping attempts,” ICT Exp., vol. 10,
pp. 491–497, Jun. 2024.
[23] C. Xu and G. Neglia, “What else is leaked when eavesdropping federated
learning?” in Proc. CCS Workshop Privacy Preserving Mach. Learn.
(PPML), 2021, pp. 1–11.
[24] I. Driouich, C. Xu, G. Neglia, F. Giroire, and E. Thomas, “A novel
model-based attribute inference attack in federated learning,” in Proc.
FL-NeurIPS-Federated Learn. Recent Adv. New Challenges Workshop
Conjunction NeurIPS, 2022, pp. 1–21.
[25] L. Wang, S. Xu, X. Wang, and Q. Zhu, “Eavesdrop the composition proportion of training labels in federated learning,” 2019,
arXiv:1910.06044.
[26] W. Wan, J. Lu, S. Hu, L. Y. Zhang, and X. Pei, “Shielding federated
learning: A new attack approach and its defense,” in Proc. IEEE Wireless
Commun. Netw. Conf. (WCNC), 2021, pp. 1–7.
[27] G. Xu et al., “Hercules: Boosting the performance of privacy-preserving
federated learning,” IEEE Trans. Dependable Secure Comput., vol. 20,
no. 5, pp. 4418–4433, Sep./Oct. 2023.
[28] L. Zhao, Q. Wang, Q. Zou, Y. Zhang, and Y. Chen, “Privacy-preserving
collaborative deep learning with unreliable participants,” IEEE Trans.
Inf. Forensics Security, vol. 15, pp. 1486–1500, 2019.
[29] G. Chandu, T. Karthik, and B. Parag, “Federated learning for distributed
IoT security: A privacy-preserving approach to intrusion detection,”
IEEE Access, vol. 13, pp. 135863–135875, 2025.
[30] J. Li, X. Tong, J. Liu, and L. Cheng, “An efficient federated learning
system for network intrusion detection,” IEEE Syst. J., vol. 17, no. 2,
pp. 2455–2464, Jun. 2023.
[31] F. Liu, Z. Zheng, Y. Shi, Y. Tong, and Y. Zhang, “A survey on federated
learning: A perspective from multi-party computation,” Front. Comput.
Sci., vol. 18, no. 1, 2024, Art. no. 181336.
[32] Y. Guo et al., “Efficient and privacy-preserving federated learning based
on full homomorphic encryption,” 2024, arXiv:2403.11519.
[33] A. G. Sébert, R. Sirdey, O. Stan, and C. Gouy-Pailler, “Protecting data
from all parties: Combining FHE and DP in federated learning,” 2022,
arXiv:2205.04330.
[34] G. Xu, G. Li, S. Guo, T. Zhang, and H. Li, “Privacy-preserving
decentralized deep learning with multiparty homomorphic encryption,”
2022, arXiv:2207.04604.
[35] S. Sav, A. Diaa, A. Pyrgelis, J.-P. Bossuat, and J.-P. Hubaux,
“Privacy-preserving federated recurrent neural networks,” 2022,
arXiv:2207.13947.
[36] X. Zhang, F. Li, Z. Zhang, Q. Li, C. Wang, and J. Wu, “Enabling
execution assurance of federated learning at untrusted participants,” in
Proc. IEEE Conf. Comput. Commun., 2020, pp. 1877–1886.
[37] T. Gehlhar, F. Marx, T. Schneider, A. Suresh, T. Wehrle, and H. Yalame,
“SAFEFL: MPC-friendly framework for private and robust federated
learning,” in Proc. IEEE Security Privacy Workshops (SPW), 2023,
pp. 69–76.
[38] M. Asif et al., “Advanced zero-shot learning (AZSL) framework for
secure model generalization in federated learning,” IEEE Access, vol. 12,
pp. 184393–184407, 2024.

[39] B. Biggio, B. Nelson, and P. Laskov, “Poisoning attacks against support
vector machines,” 2012, arXiv:1206.6389.
[40] E. Bagdasaryan, A. Veit, Y. Hua, D. Estrin, and V. Shmatikov, “How
to backdoor federated learning,” in Proc. Int. Conf. Artif. Intell. Stat.,
2020, pp. 2938–2948.
[41] G. Xu, H. Li, S. Liu, K. Yang, and X. Lin, “VerifyNet: Secure
and verifiable federated learning,” IEEE Trans. Inf. Forensics Security,
vol. 15, pp. 911–926, 2019.
[42] X. Liu, H. Li, G. Xu, Z. Chen, X. Huang, and R. Lu, “Privacyenhanced federated learning against poisoning adversaries,” IEEE Trans.
Inf. Forensics Security, vol. 16, pp. 4574–4588, 2021.
[43] Z. Ma, J. Ma, Y. Miao, Y. Li, and R. H. Deng, “ShieldFL: Mitigating
model poisoning attacks in privacy-preserving federated learning,” IEEE
Trans. Inf. Forensics Security, vol. 17, pp. 1639–1654, 2022.
[44] X. Cao, M. Fang, J. Liu, and N. Z. Gong, “FLtrust: Byzantine-robust
federated learning via trust bootstrapping,” 2020, arXiv:2012.13995.
[45] P. Blanchard, E. M. El Mhamdi, R. Guerraoui, and J. Stainer, “Machine
learning with adversaries: Byzantine tolerant gradient descent,” in Proc.
Adv. Neural Inf. Process. Syst., vol. 30, 2017, pp. 1–11.
[46] S. Shen, S. Tople, and P. Saxena, “AUROR: Defending against poisoning
attacks in collaborative deep learning systems,” in Proc. 32nd Annu.
Conf. Comput. Security Appl., 2016, pp. 508–519.
[47] N. M. Jebreel and J. Domingo-Ferrer, “FL-Defender: Combating targeted attacks in federated learning,” Knowl.-Based Syst., vol. 260,
Jan. 2023, Art. no. 110178.
[48] W. Gill, A. Anwar, and M. A. Gulzar, “FedDefender: Backdoor attack
defense in federated learning,” in Proc. 1st Int. Workshop Dependability
Trustworthiness Safety-Critical Syst. Mach. Learned Components, 2023,
pp. 6–9.
[49] P. Erbil and M. E. Gursoy, “Defending against targeted poisoning attacks
in federated learning,” in Proc. IEEE 4th Int. Conf. Trust, Privacy
Security Intell. Syst. Appl. (TPS-ISA), 2022, pp. 198–207.
[50] Z. Zhang, X. Cao, J. Jia, and N. Z. Gong, “FLDetector: Defending federated learning against model poisoning attacks via detecting malicious
clients,” in Proc. 28th ACM SIGKDD Conf. Knowl. Disc. Data Min.,
2022, pp. 2545–2555.
[51] M. H. Bhavsar, Y. B. Bekele, K. Roy, J. C. Kelly, and D. Limbrick, “FLIDS: Federated learning-based intrusion detection system using edge
devices for transportation IoT,” IEEe Access, vol. 12, pp. 52215–52226,
2024.
[52] R. Akinie, N. K. Gyimah, M. Bhavsar, and J. Kelly, “Fine-tuning
federated learning-based intrusion detection systems for transportation
IoT,” in Proc. SoutheastCon, 2025, pp. 1155–1161.
[53] D. Javeed, M. S. Saeed, M. Adil, P. Kumar, and A. Jolfaei, “A federated
learning-based zero trust intrusion detection system for Internet of
Things,” Ad Hoc Netw., vol. 162, Sep. 2024, Art. no. 103540.
[54] M. M. Rashid, S. U. Khan, F. Eusufzai, M. A. Redwan, S. R. Sabuj,
and M. Elsharief, “A federated learning-based approach for improving
intrusion detection in Industrial Internet of Things networks,” Network,
vol. 3, no. 1, pp. 158–179, 2023.
[55] P. Ruzafa-Alcázar et al., “Intrusion detection based on privacypreserving federated learning for the industrial IoT,” IEEE Trans. Ind.
Informat., vol. 19, no. 2, pp. 1145–1154, Feb. 2023.
[56] N. Hamdi, “Federated learning-based intrusion detection system for
Internet of Things,” Int. J. Inf. Security, vol. 22, no. 6, pp. 1937–1948,
2023.
[57] S. D. Azeez, M. Ilyas, and I. M. Bako, “Federated learning for privacypreserving intrusion detection in IoT networks,” in Proc. Int. Congr.
Human-Comput. Interact. Optim. Robot. Appl. (HORA), 2024, pp. 1–7.
[58] S. A. Mahmud, N. Islam, Z. Islam, Z. Rahman, and S. T. Mehedi,
“Privacy-preserving federated learning-based intrusion detection technique for cyber-physical systems,” Mathematics, vol. 12, no. 20, p. 3194,
2024.
[59] Z. Abou El Houda, H. Moudoud, and L. Khoukhi, “Secure and efficient
federated learning for robust intrusion detection in IoT networks,” in
Proc. IEEE Global Commun. Conf., 2023, pp. 2668–2673.
[60] A. Yazdinejad, A. Dehghantanha, H. Karimipour, G. Srivastava, and
R. M. Parizi, “A robust privacy-preserving federated learning model
against model poisoning attacks,” IEEE Trans. Inf. Forensics Security,
vol. 19, pp. 6693–6708, 2024.
[61] Y. Miao et al., “RFED: Robustness-enhanced privacy-preserving federated learning against poisoning attack,” IEEE Trans. Inf. Forensics
Security, vol. 19, pp. 5814–5827, 2024.
[62] J. Wu, F. Luo, T. Sun, H. Wang, and W. Zhang, “Privacy-preserving
federated learning scheme with mitigating model poisoning attacks:
Vulnerabilities and countermeasures,” 2025, arXiv:2506.23622.

SOOMRO et al.: SecureDyn-FL: A ROBUST PRIVACY-PRESERVING FL FRAMEWORK

[63] S. Sav et al., “Poseidon: Privacy-preserving federated neural network
learning,” 2020, arXiv:2009.00349.
[64] A. Salam, M. Abrar, F. Ullah, I. A. Khan, F. Amin, and
G. S. Choi, “Efficient data collaboration using multi-party privacy
preserving machine learning framework,” IEEE Access, vol. 11,
pp. 138151–138164, 2023.
[65] Z. Ashraf, Z. Mahmood, and M. Iqbal, “Lightweight privacy-preserving
remote user authentication and key agreement protocol for nextgeneration IoT-based smart healthcare,” Future Internet, vol. 15, no. 12,
p. 386, 2023.
[66] I. A. Soomro, H. Ur-Rehman Khan, S. J. Hussain, Z. Ashraf,
M. M. Alnfiai, and N. N. Alotaibi, “Lightweight privacy-preserving
federated deep intrusion detection for industrial cyber-physical system,”
J. Commun. Netw., vol. 26, no. 6, pp. 632–649, 2024.
[67] Z. Ashraf, A. Sohail, and M. Yousaf, “Robust and lightweight symmetric
key exchange algorithm for next-generation IoE,” Internet Things,
vol. 22, Jul. 2023, Art. no. 100703.
[68] H. Zhu, R. Wang, Y. Jin, K. Liang, and J. Ning, “Distributed additive
encryption and quantization for privacy preserving federated deep
learning,” Neurocomputing, vol. 463, pp. 309–327, Nov. 2021.
[69] Y. Meidan et al., “N-BaIoT—Network-based detection of IoT botnet
attacks using deep autoencoders,” IEEE Pervasive Comput., vol. 17,
no. 3, pp. 12–22, Jul.–Sep. 2018.
[70] A. Alsaedi, N. Moustafa, Z. Tari, A. Mahmood, and A. Anwar,
“Ton_IoT telemetry dataset: A new generation dataset of IoT and
IIoT for data-driven intrusion detection systems,” IEEE Access, vol. 8,
pp. 165130–165150, 2020.
[71] S. Tsokov, M. Lazarova, and A. Aleksieva-Petrova, “A hybrid spatiotemporal deep model based on CNN and LSTM for air pollution prediction,”
Sustainability, vol. 14, no. 9, p. 5104, 2022.
[72] J. Feng, L. T. Yang, B. Ren, D. Zou, M. Dong, and S. Zhang,
“Tensor recurrent neural network with differential privacy,” IEEE Trans.
Comput., vol. 73, no. 3, pp. 683–693, Mar. 2024.

Imtiaz Ali Soomro received the B.E. degree
in telecommunications from Hamdard University,
Islamabad, Pakistan, in 2010, and the M.S. degree in
electrical engineering with a specialization in telecom and networking from COMSATS University,
Islamabad, in 2012. He is currently pursuing the
Ph.D. degree in electrical and computer engineering
with the Sir Syed CASE Institute of Technology,
Islamabad. His research interests are focused on the
application of Federated Learning for IoT, wireless
networks, and cybersecurity, particularly on privacypreserving technologies and secure communication in distributed systems. He
is also an IEEE Member, actively contributing to the research community
through his innovative work in machine learning, IoT, and cybersecurity.

Hamood Ur Rehman Khan received the B.S.
degree in electronics engineering from the Ghulam
Ishaq Khan Institute of Technology in 2000, the M.S.
degree in electrical engineering from the University
of Michigan in 2005, and the Ph.D. degree in
electrical engineering from the King Fahd University
of Petroleum and Minerals in 2019. He was a
Senior Member Technical Staff with the Center
for Advanced Research and Engineering (CARE),
jointly holding appointment as an Adjunct Professor
with the Computer Science Department, Sir SyedCASE-Institute of Technology. At CARE, he has led projects ranging from IoT
Platform-as-a-Service systems, cyber-security products, and advanced VLSIbased AI platforms for Large Language Model inference. He is currently
an Assistant Professor with the ECE Department, Habib University, teaching
various courses pertaining to electrical and computer engineering majors,
including, computer architecture, signals and systems, digital communications,
and statistical inference. From 2000 to 2003, he was with Avaz Networks
Inc., Mountain View, CA, USA, as a Senior VLSI Design Engineer, working
on high-density Voice over IP System-on-Chips for gateway media switches.
His primary research interests are information theory, signal processing, and
PHY layer communications for networked systems like WSNs and IoTs.

1765

Syed Jawad Hussain recevied the Ph.D. degree
in computer science from Massey University, New
Zealand, focusing on developing high-definition
video quality experience models. He is a Professor
and Dean, Faculty of Computing, Sir Syed CASE
Institute of Technology, Islamabad, Pakistan. He has
extensive experience in academia and industry, having held various leadership roles, including Head of
Department positions at institutions in Pakistan and
abroad. He has worked on numerous research and
consultancy projects, focusing on machine learning,
data security, and multimedia communications. He has published extensively
in prestigious journals and conferences, contributing significantly to the field
of computer science. His research interests include multimedia communication
networks, machine learning, quality of service, quality of experience, data and
network security, and statistical modeling.

Adeel Iqbal received the bachelor’s degree from
the Federal Urdu University of Arts, Sciences
and Technology, Islamabad, and the master’s
and Ph.D. degrees in electrical engineering from
COMSATS University Islamabad. He is an Assistant
Professor with the School of Computer Science and
Engineering, Yeungnam University, South Korea. He
specializes in electrical engineering. His research
encompasses next-generation cellular networks, such
as cognitive radio, IoT, D2D, and vehicular systems,
along with work in WSNs, machine learning, image
processing, and green and renewable energy.

Waqas Khalid (Member, IEEE) received the B.S.
degree in electronics engineering from the GIK
Institute of Engineering Sciences and Technology,
Khyber Pakhtunkhwa, Pakistan, in 2011, the M.S.
degree in information and communication engineering from Inha University, Incheon, South Korea,
in 2016, and the Ph.D. degree in information
and communication engineering from Yeungnam
University, Gyeongsan, South Korea, in 2019. He is
currently an Assistant Professor with the Department
of Electrical and Electronic Engineering, University
of Nottingham Ningbo China, Ningbo, China. Previously, he served as
a Research Professor with the Institute of Industrial Technology, Korea
University, Sejong, South Korea, where he was also the recipient of a National
Research Foundation of Korea Research Grant from June 2022 to May 2025.
His research interests include physical layer modeling, signal processing,
and emerging technologies for 5G/6G networks, including reconfigurable
intelligent surfaces, physical-layer security, non-orthogonal multiple access,
UAV communications, and IoTs.

Heejung Yu (Senior Member, IEEE) received the
B.S. degree in radio science and engineering from
Korea University, Seoul, South Korea, in 1999, and
the M.S. and Ph.D. degrees in electrical engineering from the Korea Advanced Institute of Science
and Technology, Daejeon, South Korea, in 2001
and 2011, respectively. From 2001 to 2012, he
was with the Electronics and Telecommunications
Research Institute, Daejeon, and from 2012 to 2019,
he was with Yeungman University, Gyeongsan,
South Korea. He is currently a Professor with the
Department of Electronics and Information Engineering, Korea University,
Sejong, South Korea. His research interests include statistical signal processing and communication theory.
PAPER_TEXT
