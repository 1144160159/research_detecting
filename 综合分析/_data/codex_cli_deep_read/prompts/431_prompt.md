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
# [431] Fed-IoMT-Block: A Privacy-Preserving Framework for Secure Federated Learning in Consumer-Centric Internet of Medical Things
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
编号：431
题名：Fed-IoMT-Block: A Privacy-Preserving Framework for Secure Federated Learning in Consumer-Centric Internet of Medical Things
年份：2025
DOI：10.1109/tce.2025.3582794
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2025.3582794.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：联邦学习、隐私保护与分布式协同
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\431.txt
- 原始字符数：62354
- 本次发送字符数：62354
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 3, AUGUST 2025

8453

Fed-IoMT-Block: A Privacy-Preserving Framework
for Secure Federated Learning in Consumer-Centric
Internet of Medical Things
Arfat Ahmad Khan , Rakesh Kumar Mahendran, Fasee Ullah , Farman Ali , Norah Saleh Alghamdi ,
Ahmad Ali AlZubi , and Daehan Kwak , Senior Member, IEEE
Abstract—The rapid proliferation of the Internet of Medical
Things (IoMT) has enabled sophisticated, timely, and remote
healthcare monitoring by leveraging advanced networking technologies. However, despite ongoing research, the IoMT paradigm
still faces significant security and privacy challenges. To address
these, this study introduces Fed-IoMT-Block, an end-to-end
framework for securing IoMT devices. The framework first
authenticates IoMT entities using the Quantum Authentication
Protocol (QAP), which identifies communicating entities and
secures their exchange using unique quantum particles, providing stronger protection than conventional protocols. Once
authenticated, entities share data through federated learning,
leveraging the Attention Capsule Network (Att-CapsNet) and a
homomorphic algorithm. Network monitoring is then handled
by a machine learning agent, the Vulnerability Analysis Agent
(VAA), which inspects external traffic and classifies it using
the Light Gradient Boosting Machine (LGBM). The associated
risk is mathematically quantified based on multiple parameters.
Finally, role-based access control is enforced via a Flexible NeuroFuzzy Inference System (FNFIS) to prevent unauthorized access.
The proposed framework demonstrates notable improvements in
packet delivery, security, and scalability compared to existing
methods. These improvements include a 26% reduction in malicious traffic, 84.88% accuracy in disease severity detection, 12%
lower latency, and a high packet throughput ratio. This study
highlights the potential of federated learning and blockchain to
Received 28 January 2025; revised 22 March 2025 and 17 May 2025;
accepted 1 June 2025. Date of publication 24 June 2025; date of current
version 7 November 2025. This research was supported in part by the
Researchers Supporting Projects (PNURSP2025R40) at Princess Nourah bint
Abdulrahman University, Riyadh, Saudi Arabia, in part by the Ongoing
Research Funding program (ORF-2025-395), King Saud University, Riyadh,
Saudi Arabia, and in part by the Regional Innovation System & Education
(RISE) through the Seoul RISE Center, funded by the Ministry of Education
(MOE) and the Seoul Metropolitan Government (2025-RISE-01-018-01).
(Corresponding authors: Farman Ali; Daehan Kwak.)
Arfat Ahmad Khan is with the Department of Computer Science, College
of Computing, Khon Kaen University, Khon Kaen 40002, Thailand (e-mail:
arfatkhan@kku.ac.th).
Rakesh Kumar Mahendran is with the Department of Computer Science and
Engineering, Saveetha Engineering College, Chennai 602105, India (e-mail:
rakeshkumarmahendran@gmail.com).
Fasee Ullah is with the Department of Computing, Universiti Teknologi
PETRONAS, Seri Iskandar 32610, Malaysia (e-mail: fasee.ullah@utp.
edu.my).
Farman Ali is with the Department of Applied AI, School of Convergence,
College of Computing and Informatics, Sungkyunkwan University, Seoul
03063, South Korea (e-mail: farman0977@skku.edu).
Norah Saleh Alghamdi is with the Department of Computer Sciences,
Princess Nourah bint Abdulrahman University, Riyadh 11671, Saudi Arabia
(e-mail: nosalghamdi@pnu.edu.sa).
Ahmad Ali AlZubi is with the Department of Computer Science, King Saud
University, Riyadh 11451, Saudi Arabia (e-mail: aalzubi@ksu.edu.sa).
Daehan Kwak is with the Department of Computer Science and Technology,
Kean University, Union, NJ 07083 USA (e-mail: dkwak@kean.edu).
Digital Object Identifier 10.1109/TCE.2025.3582794

create secure, scalable, and privacy-preserving IoMT systems for
consumer healthcare.
Index Terms—Blockchain, federated learning, homomorphic
encryption, Internet of Medical Things (IoMT), intrusion detection systems (IDS), quantum authentication, risk assessment.

I. I NTRODUCTION
HE INTERNET of Things (IoT) is an emerging technology used for real-time monitoring, data transmission,
and various applications across sectors such as emergency
services, traffic congestion, industrial control, logistics, retail,
and smart cities [1], [2], [3]. Due to the significance of IoT,
its feasibility in medical applications for health monitoring has
led to a new intelligent paradigm in Healthcare 4.0, referred
to as the Internet of Medical Things (IoMT) [4], [5], [6], [7].
IoMT utilizes IoT-based smart medical devices or sensors
for continuous health monitoring of patients across various
rankings and gradings.
The patient health monitoring process in IoMT typically
consists of three methods [8]: (1) On-body medical sensors,
deployed on the patient’s body to monitor parameters such as
heart rate, respiratory rate, and temperature. (2) In-body sensors,
installed inside the body to monitor internal organs such as
the liver, kidneys, and heart using wireless endoscopy sensors.
(3) Off-body sensors, placed around the patient to monitor
physical activities such as postural movements or improper
seating positions on a sofa. Due to these diverse monitoring
applications, the proportion of IoT devices is projected to
increase by 50% by 2030, marking a 150% rise over current
levels [2], [9].
The key advantages of IoMT include cost reduction,
improved quality of life, and enhanced user experience [10], [11]. However, a major concern is its security and
privacy [12]. Communication among IoMT devices occurs
in a wireless environment, making them attractive targets
for attackers aiming to perform malicious actions that may
endanger human lives [13], [14]. Common threats include
eavesdropping, intentional delays in device detection capabilities, and Distributed Denial of Service (DDoS) attacks.
A DDoS attack is one of the widespread attacks that tends
to flood a legitimate server to prevent access by legitimate
users by consuming the entire bandwidth. By sending flooding
messages to the server, it appears that the server is not showing

T

c 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
1558-4127 
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

8454

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 3, AUGUST 2025

online availability to legitimate users, and in this way, the
server’s services are hijacked.
According to a report by the International Medical
Cybersecurity Council (IMCC), nearly 70% of smart medical
devices are highly vulnerable to cyber-attacks due to the
lack of effective authorization and authentication mechanisms [15], [16], [17]. Additionally, IoMT systems face
challenges related to scalability and storage limitations, underscoring the need for extensive research in IoMT cybersecurity.
Authentication and authorization have been identified as
the primary security approaches in the literature to counter
cyber threats [18], [19]. Current research largely relies on
cryptographic algorithms such as Elliptic Curve Cryptography
(ECC) and the Digital Signature Algorithm (DSA). However,
these algorithms are often unsuitable for compact IoMT
devices due to their limited computational, storage, and
processing capacities, which ultimately compromises security [20]. Although technologies such as Artificial Intelligence
(AI) and blockchain have shown promise, their application
in Intrusion Detection and Prevention Systems (IDS/IPS) for
IoMT remains limited due to their high computational and
resource demands [21]. Moreover, AI models are susceptible
to insider threats, poisoning attacks, and fake malicious traffic.
To address scalability, flexibility, and security concerns,
cloud-based on-demand services have been adopted alongside
blockchain to ensure data integrity, tamper resistance, confidentiality, and immutability [22], [23]. However, their use
in IoMT environments has not been adequately explored for
comprehensive end-to-end authentication, authorization, model
protection, privacy, and network security. To bridge this gap, we
propose an end-to-end security strategy for IoMT applications
using Federated Learning (FL) and blockchain technologies.
The major security challenges addressed in state-of-the-art
research [2], [4], [7], [10], [13], [15], [22], [23], [24], [25] are
outlined below:
• Inadequate Smart Medical Device Validation: The authenticity and legitimacy of smart IoMT devices are typically
verified using IDs, passwords, and biometrics. However,
these methods fail to ensure full legitimacy, leaving
devices vulnerable to spoofing attacks.
• Lack of Risk Assessment: Security and privacypreserving strategies are weakened when risk assessment
is not performed, negatively affecting Quality of Service
(QoS) and network credibility.
• Significant Security Loopholes: Most existing work
emphasizes securing medical data via encryption and
federated learning to guard against external threats, but
offers limited analysis of malware targeting smart IoMT
devices.
Motivated by the above challenges, the proposed study aims
to enhance security and privacy in the IoMT environment by
designing a secure and private framework leveraging advanced
technologies. The novel contributions of this study are as
follows:
• This research study uses a federated machine learning
model to develop a novel security and privacy paradigm
for the heterogeneous IoMT devices environment by
incorporating communication and network security measures including Intrusion Detection Systems (IDS) and
risk assessment.

•

The adoption of the Quantum Authentication Protocol
(QAP), supported by blockchain, enhances IoMT security
and privacy beyond conventional cryptographic protocols.
• The integration of AI and homomorphic encryption
with federated learning offers additional privacy for data
auditing and integrity without requiring decryption or
cloud-side access to raw data.
• Performance evaluations show that the proposed FedIoMT-Block framework achieves high accuracy in
malicious device and attack detection, improved disease severity classification, and reduced latency with
higher packet throughput. The framework also effectively
defends against Man-in-the-Middle, DDoS, insider, and
poisoning attacks.
The remainder of this paper is organized as follows:
Section II presents a review of related work. Section III
describes the system model and prerequisites. Section IV
details the proposed processes with supporting pseudocode,
diagrams, and equations. Section V discusses the experimental setup, comparative analysis, and security evaluation.
Section VI concludes the paper.

II. L ITERATURE R EVIEW
This section reviews key shortcomings in state-of-the-art
efforts to secure the IoMT environment. It is organized into
three subsections to highlight existing gaps in the literature.
A. Blockchain Approaches for IoMT Security
Several studies have explored blockchain technology to
enhance IoMT device security. The edge computing and
blockchain approach by [26] reduces computation and latency
in data transmission using distributed edge servers, IoMT
devices, smart contract-based blockchains, and IPFS storage.
Data execution and offloading are managed via mobile devices
and Patient IDs. However, the involvement of multiple entities with different authentication and authorization processes
makes it unsuitable for resource-constrained devices.
The bidirectional Long Short-Term Memory (LSTM) and
smart contract-based blockchain method in [27] detects misbehavior in IoMT pancreas devices but does not account for the
computational burden on lightweight devices. Reference [28]
used blockchain to ensure secure communication and synchronization in critical medical infrastructure. A blockchain-based
access control method in [29] stores device data in digital
wallets using decentralized identity devices, later analyzed
in the fog layer. However, reliance on manual authentication based on credentials, roles, and attributes introduces
vulnerabilities.
The blockchain-based Covichain framework in [30] secures
IoMT data transfers for COVID-19 patients but incurs high
computation, processing, and storage costs due to IPFS.
Reference [31] addressed centralized storage limitations by
using distributed storage with ring-assisted access control
for authenticating patients, doctors, and nurses. However, the
study did not address cost concerns in the IoMT setting.
Reference [32] proposed a context-aware attribute-based
encryption scheme for secure IoMT data. However, its reliance

KHAN et al.: Fed-IoMT-Block: A PRIVACY-PRESERVING FRAMEWORK FOR SECURE FL

on cloud and fog servers, combined with blockchain and
biomedical sensors, results in high resource consumption.
B. Federated Learning Approaches for IoMT Security
Federated Learning (FL) has been integrated into healthcare
using blockchain, as demonstrated in [33]. A similar approach
in [34] incorporated enhanced secret sharing with FL. Here, user
authentication is handled via a dynamic hash function, with keys
shared using Elliptic Curve Cryptography (ECC)–also applied
in [35]. A dual-phase method combining privacy-preserving
techniques and FL blocks was proposed to address insider
and denial-of-service attacks. However, reliance on centralized
servers contradicts the decentralized nature of FL. Another
architecture with smart IoT devices, fog servers, and gateways
for encryption was presented in [36], demonstrating lower
communication costs than SPPDA and EHDA.
Blockchain has also been applied for data preprocessing [37].
A fraud detection model combining FL and blockchain was
introduced in [38], incorporating application and fog layers.
Reference [39] proposed a masking scheme using homomorphic
encryption in FL, applying a weighted average algorithm to
boost resiliency. Similarly, [40] employed two FL algorithms,
S-LMI and C-GMI, for data auditing and verification to
defend against poisoning attacks. Both use homomorphic hash
functions to download data from individual IoMT devices.
However, the scheme does not quantify cost complexity or
preemptively detect such attacks. A fuzzy ensemble-based
federated learning model was also introduced using temporal
convolutional networks (TCN), Long Short-Term Memory
(LSTM), and gated recurrent units (GRU) [41]. While cybersecurity and cost concerns are addressed, a hybrid FL-based
quantization framework was later proposed [42], [43], [44] to
improve protection against data leakage during transmission,
though cost complexity remains unaddressed. However, none of
these schemes fully exploit FL due to the high computational,
processing, and storage demands of IoMT devices.
C. Other Security Approaches for IoMT Security
The two-phase Secure-IoMT framework using multimodal
sensory signals was proposed in [45], comprising preprocessing, clustering, feature extraction, and classification.
However, it does not consider cost complexity. An AI-enabled
lightweight communication scheme using IPv6, ZigBee, BLE,
Z-Wave, and NFC was introduced in [46], but it lacks active
misbehavior detection.
A secure data aggregation scheme with an authentication
framework was proposed in [47], employing the HMAC
protocol for end-to-end authentication and using a fuzzybased delimiter for better resource use. Fuzzy-based Trust
Management (FTM) in [48] enhances device trustworthiness by identifying Sybil attacks and untrusted nodes.
Reference [49] applied Bayesian optimization and deep learning to reduce malicious access in IoMT environments.

8455

preserves patient privacy by avoiding disclosure of original
identities, while blockchain ensures transparency, integrity,
and immutability within the IoMT environment. The framework comprises three layers: IoMT Sensor Layer, Cloud
Layer, and Application Layer. The IoMT Sensor Layer
includes temperature sensors, heartbeat sensors, smart ECG
machines, and biosensors for continuous health monitoring. The Cloud Layer features a Trusted Authority
(TA), Vulnerability Analysis Agent (VAA), and Secure
Aggregator (SA) to authenticate devices, users, and doctors,
and to detect suspicious network activity. The Application
Layer consists of end users, doctors, and medical assistants who access patient data through an access control
mechanism.
A. Assumptions
The following assumptions are made in the proposed model:
• Malicious insiders: Suspicious digital sources offer various incentives to medical doctors, healthcare assistants,
and authenticators (TA, VAA, SA) to update components
of the existing system. These updates can be exploited,
potentially leading to system breaches caused by insider
threats and malicious attacks.
• The TA authenticates IoMT devices, users, and doctors.
The VAA monitors suspicious network behavior. The SA
manages global model aggregation in FL and handles
blockchain transactions and storage.
• Centralized cloud architecture does not hinder scalability,
as patient enrollment (i.e., IoMT devices) is limited based
on capacity.
• The blockchain is assumed resistant to 51% attacks due
to the low number of malicious insiders.
B. Design Goals
The proposed model aims to achieve the following:
• Security and Correctness: A secure TA ensures authenticity without compromising data integrity.
• Scalability: User interaction with the cloud is limited to
maintain scalability.
• Privacy and Transparency: Blockchain integration ensures
data privacy while supporting transparency.
• Integrity: Federated learning preserves the integrity of
sensed data against theft or tampering.
IV. F ED -I O MT-B LOCK M ODEL
The proposed Fed-IoMT-Block model consists of four
sequential steps: (1) Multi-Credential Quantum-based
Authenticity Verification, (2) Federated Learning-based
Sensed Data Sharing, (3) Machine Learning-Entrenched
Attack Detection & Risk Analysis, and (4) Adaptive Fuzzy
Role-based Access Control.
A. Multi-Credential Quantum-Based Authenticity Verification

III. S YSTEM M ODEL
This section outlines the proposed IoMT security framework, which integrates blockchain and federated learning
technologies, as shown in Figure 1. Federated learning

The proposed Quantum Authentication Protocol (QAP) is
based on the Greenberger–Horne–Zeilinger (GHZ) quantum
state, a fundamental concept in quantum communication theory. The protocol involves three major entities: cloud-based

8456

Fig. 1.

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 3, AUGUST 2025

Overall architecture of the proposed Fed-IoMT block.

blockchain as a conventional participant, TA, and clients (i.e.,
IoMT devices, doctors, and healthcare assistants). The TA
and clients possess quantum capabilities enabling trustworthy
authentication.
The blockchain is considered an honest entity, while the
TA and clients are classified as partially honest. The primary
advantage of QAP is its zero-loss, noise-free authentication
process, ensuring high security. The proposed QAP consists
of two phases, outlined below:
Phase 1: Enrollment
Step 1: In the initial phase, the TA, clients Cl, including
IoMT devices Dn = {D1 , D2 , . . . , Dn }, doctors docn =
{doc1 , doc2 , . . . , docn }, and healthcare assistants han =
{ha1 , ha2 , . . . , han }, are registered with their secret credentials
(Z) onto the blockchain B. The representation of Z within the
blockchain is formulated as follows:

⎧
ZTA0 = {ZTA01 , ZTA02 , . . . , ZTA0R }
⎪
⎪
⎨
ZD1 = {ZD11 , ZD12 , . . . , ZD1N }
B←
Z
⎪ doc2 = {Zdoc21 , Zdoc22 , . . . , Zdoc2N }
⎪
⎩
Zha3 = {Zha31 , Zha32 , . . . , Zha3N }

(1)

where, ZD1j , Zdoc2j , and Zha3j ∈ {0, 1} for (j = 1, 2, . . . , N),
and ZTA0j ∈ {0, 1} for (j = 1, 2, . . . , R). The secret credential
Z consists of its ID, password, biometrics, and assigned roles.
Step 2: Upon successful registration, an authentication token
is issued to the TA and clients. The representation of Step 2
is as follows:
B → ATok [D, doc, ha]

(2)

where ATok denotes the authenticity token, serving as
a credential for clients to initiate the authentication
process.

KHAN et al.: Fed-IoMT-Block: A PRIVACY-PRESERVING FRAMEWORK FOR SECURE FL

Phase 2: Authenticity Verification
Step 3: The clients initiate authentication by submitting
ATok to the TA. Upon receiving the clients’ ATok tokens, the
TA generates random quantum sequences of R(N + 1) GHZ
quantum states, formulated as follows:

⎧
√1 |STA SD . . . SD 
|G

=
1
⎪
⎪ 
2
 01 11 
n1
 
⎪
⎪
⎪
⊕
1
S
⊕
1
.
.
.
SDn1 ⊕ 1 
+|
S
TA
D
⎪
01 
11
⎪
⎨ |G  = √1 |S
2
TA Sdoc12 . . . Sdocn2 
2
 02


 

(3)
⎪
+| STA02 ⊕ 1 Sdoc12 ⊕ 1 . . . Sdocn2 ⊕ 1 
⎪
⎪
⎪
⎪
|G3  = √1 |STA03 Sha21 . . . SDn3 
⎪
⎪
2



 
⎩ 
+| STA03 ⊕ 1 Sha21 ⊕ 1 . . . Shan3 ⊕ 1 
where TA0n , D1n , doc2n , ha3n represent the (N + 1) quantum
particles of the nth GHZ state.
Step 4: After generating the random quantum sequences,
the TA splits the GHZ sequences into ordered sequences:
STA0 , SD1 , Sdoc2 , Sha3 . The TA then generates quantum
decoy photons {|0, |1, |+, |−} and inserts them into
the ordered sequences. The TA retains STA0 and provides
SD1 , Sdoc2 , Sha3 to the clients.
Step 5: Upon receiving the ordered sequences Seq =
{SD1 , Sdoc2 , Sha3 }, the clients perform quantum operations,
specifically GNZ and XOR operations, on the quantum decoy
photons. This process is formulated as follows:



(4)
Seq = GNZ SD1 ⊕ GNZ Sdoc2 ⊕ GNZ Sha3

Cl Seq → TA
(5)
Step 6: Upon receiving Seq from the clients, the TA
performs the same operations as in Step 5 to retrieve the
original sequences. The correctness of the sequences is verified
by computing the error between the original sequences held
by the TA and those received from the clients. The error
computation is formulated as follows:
Err = Seq − Seq

(6)

In the above equation, a threshold value (Th) is set by the
blockchain to verify client authenticity. If the computed error
is greater than or equal to the threshold, the client is considered
malicious; otherwise, the client is considered legitimate. The
formulation for authenticity verification is expressed as:
TA =

Discarded,
if Err ≥ Th
Authenticated, otherwise

(7)

Similarly, clients compute the error for the TA and publish the
results to the blockchain.
Step 7: The blockchain determines the final decision regarding whether the communication between the clients and the
TA is legitimate or malicious. The results are securely stored
as blocks within the blockchain.
B. Federated Learning-Based Sensed Data Sharing
Only authenticated IoMT devices are allowed to participate in the IoMT environment, specifically the authenticated
patients’ IoMT devices for sensing. To enhance user privacy, the proposed framework employs federated learning and
homomorphic encryption. For each round r, IoMT devices

8457

acquire a global model from the cloud server, train and encrypt
their local models, compute decryption dividends, and perform
secure aggregation. This process is repeated until convergence
is achieved. A detailed explanation of the proposed FL-based
data-sharing process is provided below.
First, the server initializes the public key parameters for
each IoMT device based on its authenticity d(∀, δ, ϒ, η, ),
where  is a random vector,  ← U(T∀D ), ϒ and η represent
the error distribution over T, δ denotes the key distribution
parameter, and ∀ is the modulus of ciphertext. Based on the
public key parameters, each IoMT device Dj generates a secret
key seckj ← δ, from which the public key is computed as
Pkj = −seckj ·  + ej (mod ∀). Using this, all authenticated
IoMT devices compute the collaborative public key as follows:
n

Pk =

n

Pkj =
j=1



− seckj ·  +

j=1

n

ej (mod ∀)

(8)

j=1

Once the collaborative public key is computed, for each
round r, every IoMT device Dj downloads the current weights
of the global model wet from the cloud server. Using these
weights, each device generates a local model by employing
the Att-CapsNet algorithm. The integration of a squeezeand-excitation block into a conventional CapsNet serves as
an attention mechanism that enhances the learning of global
feature representations. This incorporation addresses dimensionality challenges, resulting in improved channel weight
estimation.
Local Model Generation: Initially, the sensed data from
the IoMT devices are fed into the convolutional layers of the
Att-CapsNet. In these layers, local features are extracted using
convolutional kernels of size 3 × 3 with a stride of one.
The extracted feature maps are then passed to the squeezeexcitation layer. The squeeze-excitation network consists of
two key operations: squeeze and excitation, which extract
global features.
The squeeze operation extracts features to generate the
feature map, while the excitation operation determines the
channel weights based on the computed feature maps. The
formulation of the squeeze-excitation operation is as follows:
H
 
1
Qc = Seq ℵp = H×W

W

ℵp (j, i)

(9)

j=1 i=1

Sc = Exi(Q, W) = (A(Q, W)) = (W2 ϕ(W1 Q)) (10)


yp = scale ℵp , Scp = Scp · ℵp
(11)
From equations (9)–(11), ℵp represents the pth feature map,
W2 and W1 denote the dimensionality weights, Sc represents
the channel weight, and Qc denotes the statistical representation of the channel. The generated feature maps from the
squeeze-excitation layer are then passed to the primary capsule
layer, where they are transformed into primary capsules. The
capsules store a large amount of information in vector format.
These vector-formatted capsules are subsequently provided as
inputs to the digit capsule layer, which produces the final
output.

8458

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 3, AUGUST 2025

The digit capsule layer incorporates a squashing function to
facilitate vector-directed routing. The routing process between
the jth and ith capsules is formulated as follows:
ℵi|j = Wji ℵj

(12)

Sci =

(13)

∂ji ℵi|j
j
2

oi = 1+ScSci 2 ·
i

Sci
Sci

(14)

From Equations (12)–(14), Wji represents the matrix weight
emphasizing the relationship between the jth and ith capsules,
∂ji denotes the connection coefficient, and Oi refers to the
output squashing function that provides the sensed results
of individual patients. Once the local model is derived after
several epochs, IoMT devices provide the weights of each
j
individual local model as wet , j ∈ 1, 2, . . . , n.
Encrypting the Local Model Weights: The plaintext input
j
for wet is represented as fj ∈ T. Let  = [0] and Pk =
Pk[0]. The samples from the public key parameters are given
Di
i
as ϑ Di ← δ, and eD
0 , e1 ← ϒ. The ciphertext for the local
model is computed as follows:


Di
Di
i
CpTDi = ϑ Di · Pk + fj + eD
,
ϑ
·

+
e
0
1 (mod ∀) (15)
From the above equation, each IoMT device shares the
Di
i
encrypted local model CpTDi = (CpTD
0 , CpT1 ) with the
cloud server.
Perform Homomorphic Operation: Homomorphic verification protects cloud-stored data from cyberattacks and
enables data auditing without downloading the entire
encrypted dataset. To improve verification, homomorphic verification incorporates non-malleability and Context Binding.
Non-malleability protects legitimate ciphertext from generation or modification by attackers, while Context Binding
prevents fake data auditing at the cloud server. Once the server
receives the encrypted local model weights from all IoMT
devices, it performs homomorphic encryption operations by
summing all the weights. The formulation of the homomorphic
operation on the local model weights is as follows:
⎞
⎛
N

CpTsum =

CpT

Di

=⎝

N

N

i
CpTD
0 ,

i⎠
CpTD
1

Algorithm 1 FL-Based Data Sharing
Input: Authenticated IoMT devices Di
Output: Aggregated Sensed Model with new model weight wet+1
1: Initialize collaborative Pk (8)
2: for every round r → Dj do
3:
Every Dj [get(wet )] from the cloud server
// Local Model Generation //
4:
Sensed results → AttCapsNet[Conv(3 × 3)]
5:
AttCapsNet[Conv(3 × 3)] extracts local features Lfea
6:
Lfea → Seq(.)Exi(.) for Scp · ℵp (9)–(11)
7:
ℵp → primary capsules for vector format conversion
8:
OP (primary capsules) → Digit capsules (12)–(14))
j
9:
Assign weight for every IoMT local model wet
// Encrypt Local Model Weights //
j
10:
Represent wet to plaintext form fj ∈ T
11:
With public-key parameters compute CpTDi (15) to cloud server
// Perform Homomorphic Operation //
12:
Apply HE CpTsum on CpTDi (16)
13:
CpTsum → Di for computing decryption dividends (17)
// Secure Global Aggregation //
14:
Decryption dividends → Cloud server
15:
Perform secure local model aggregation (18)
16:
Assign a new global model weight wet+1 (19)
17:
Run until max r met
18: end for

secure aggregation to obtain the plaintext. The formulation for
secure aggregation is as follows:
N

N

fj ≈ CpTsum0 +
i=1

Di (mod ∀)

(18)

i=1


From the above equation, the cloud server decrypts N
i=1 fj to
compute the average local weights and obtain the new global
model weight wet+1 for further rounds.
N
j

wet+1 = N1

wet

(19)

j=1

The communication rounds continue until the desired convergence is met. The pseudocode for Federated Learning-based
data sharing is given in Algorithm 1.
C. Machine Learning-Entrenched Attack Detection and Risk
Analysis

(17)

The Vulnerability Analysis Agent (VAA) in the cloud server
monitors the communication between IoMT devices and the
cloud server. Continuous monitoring is enabled by observing
the behaviors of IoMT devices and network traffic to the cloud
server. Specifically, the behavior of IoMT devices is captured
by computing both direct and indirect trust measures. Network
flows are analyzed by examining flow and packet features.
1) Behavioral Analysis: For each IoMT device Dj in each
communication round r, the VAA computes direct and indirect
trust (dirtru ) and (indirtru ), respectively. dirtru is computed by
analyzing the past behaviors of a particular IoMT device. The
formulation of dirtru is as follows:

dirtru Dj = Z · y
(20)

Secure Global Aggregation: Upon receiving all decryption
dividends from IoMT devices, the cloud server performs

where Z represents the past behavior of device Dj , and y
denotes the current behavior monitored by the VAA. Indirect
trust, indirtru , is computed as follows:

j=1

j=1

j=1


 
= CpTsum0 , CpTsum1 (mod ∀)

(16)

where CpTsum is the sum of homomorphic operations of
ciphertexts.
Decryption Dividends Computation: The homomorphically encrypted ciphertext sum is distributed to all IoMT
devices to compute the decryption dividends, which are then
sent back to the cloud server. The formulation for decryption
dividends is as follows:
Di = secki · CpTsum1 + e∗j =
N 

i
ϑi ·  + eD
+ e∗1 (mod ∀)
seckj ·
1
j=1

KHAN et al.: Fed-IoMT-Block: A PRIVACY-PRESERVING FRAMEWORK FOR SECURE FL

8459

Algorithm 2 Packet Flow Analysis

Algorithm 3 LGBM-Based Device Classification

1: BEGIN
// Extracting source and destination port details //
2: SRC_Port ← Packet.Header.Source_Port
3: DEST_Port ← Packet.Header.Destination_Port
// Identifying transport layer protocol //
4: Protocol ← Packet.Header.Transport_Protocol
// Extracting IP addresses //
5: SRC_IP ← Packet.Header.Source_IP
6: DEST_IP ← Packet.Header.Destination_IP
// Monitoring packet exchange statistics //
7: CNT ← Compute_Byte_Packet_Count(Packet)
// Calculating inter-packet arrival time //
8: IPkt ← Compute_Inter_Packet_Time(Cloud_Server, Device)
9: END

Input: Tr(Dj ), Ntrm
Output: Classification Result (Normal or Malicious)
1: for all Dj do
2:
Set training samples: {(a1 , b1 ), (a2 , b2 ), L, (an , bn )}
 (23)
3:
Perform Loss Minimization: F(a)
4:
Determine Iterative Function (24)
5:
Provide Final Classification: FU (a) (25)
6:
Provide results: ωu (a) (26)
7: end for
8: for all Malicious Dj do
9:
Analyze Risk(Dj ) (27)
10:
Formulate Risk Impact: Imp(Dj ) (28)
11:
Formulate Risk Likelihood: lik(Dj ) (29)
12:
Calculate: Overall Risk ← Imp(Dj ) × lik(Dj )
13:
if Risk score > 90 then
14:
Critical Impact
15:
else if Risk score ≥ 70 and < 90 then
16:
High Impact
17:
else if Risk score ≥ 60 and < 70 then
18:
Moderate Impact
19:
else if Risk score ≥ 20 and < 60 then
20:
Low Impact
21:
else
22:
Negligible Impact
23:
end if
24: end for

n

1
indirtru Dj = nr
Fe[Di ] → Dj

(21)

i=1

where nr denotes the number of feedbacks obtained about the
behavior of device Dj , and Fe[Di ] represents the feedback from
device Di regarding device Dj . Finally, the overall trust value
is computed by summing dirtru and indirtru as follows:


Tr = dirtru Dj + indirtru Dj

(22)

2) Network Traffic Analysis: Simultaneously, the flows
from IoMT devices Dj , as well as external malicious devices,
are analyzed by considering several features. The features
extracted in the proposed work are listed below and also
described in Algorithm 2:
• SRC_Port: The source port extracted from the packet
header; used by the sending peer.
• DEST_Port: The destination port from the packet header;
used by the receiving peer.
• Protocol Used: Specifies the transport layer protocol in
use (e.g., UDP, TCP).
• DES_IP: The destination IP address of the receiving peer.
• SRC_IP: The source IP address of the transmitting peer.
• CNT: Represents the number of bytes or packets
exchanged during a defined time interval.
• IPkt: The inter-packet arrival time, indicating the time
between packets during flow exchange between the cloud
server and devices.
By obtaining these features, the analysis is performed
using several feature aggregation techniques, such as packet
and byte counts over a particular second, standard deviation
computation for flow, bytes, and packets, and standard deviation measures among byte-to-duration counts. The analyzed
network traffic for all devices is represented as Ntrm =
{Ntr1 , Ntr2 , . . . , Ntrm }.
3) LGBM-Based Risk Analysis and Prevention: The
LGBM is a powerful machine-learning classifier for complex decision-making situations. The proposed method
trains the classifier using trust and traffic analysis results
from the devices. The training set is represented as
{(a1 , b1 ), (a2 , b2 ), L, (an , bn )}, where the given data samples
are represented as a, and the labels for classification are
represented as b. The goal of the Light Gradient Boosting
Machine is to minimize the loss function during classification.

The loss can be minimized using F(a), which is formulated
as follows:
 = arg min εa,b [L(b, F(a))]
F(a)
F

(23)

From the above equation, the iterative function of the LGBM
can be used to minimize the loss function as follows:
Fu (a) = Fu−1 (a) + αu

u (a)

(24)

where u defines the number of iterations,
 u (a) denotes the
decision tree base, and αu = arg minα ni=1 L(bi , Fu−1 (ai ) +
α u (ai )). From this equation, the final classification model for
the LGBM is obtained by combining the weights as follows:
FU (a) =

U
u=1

αu

u (a)

(25)

The maximized iteration number is denoted by U, and the
final classification from the base decision tree u (a) can be
formulated as follows:
u (a)

=

Normal Dj if condition
Malicious Dj otherwise

(26)

From the classifier results, normal Dj values are accepted,
while malicious Dj values are subjected to risk analysis.
The pseudocode defining the operation of the LGBM device
classification and risk analysis is shown in Algorithm 3.
To analyze the risk of any IoMT device Dj , the formulation
is defined as follows:
 
 
 
(27)
Risk Dj = Imp Dj × lik Dj
where Imp(Dj ) defines the impact of risk and lik(Dj ) defines
the likelihood of the risk. The impact of risk is determined
based on metrics such as device security, considering whether
an attack compromises confidentiality, integrity, or availability,
the type of protocol used, the network type, and the number
of heterogeneous IoMT devices involved.

8460

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 3, AUGUST 2025

TABLE I
S ECURITY R ISK A NALYSIS FOR I O MT D EVICES

 
 
    
Imp Dj = sec Dj + CIA Dj + Pro Dj
 
 
+ NT Dj + Het Dj /5

Algorithm 4 Role-Based Access Control
(28)

where sec(Dj ), CIA(Dj ), Pro(Dj ), NT(Dj ), and Het(Dj ) denote
the security, CIA, protocol used, network type, and number
of heterogeneous devices, respectively. The likelihood of risk
can be formulated as follows:
 
 
 
    
lik Dj = RF Dj + His Dj + Sec Dj + Lay Dj /4 (29)
where RF(Dj ) represents the risk factor, His(Dj ) denotes
the history of attacks encountered by the IoMT device,
Sec(Dj ) refers to the sector type, and Lay(Dj ) represents the
proposed IoMT layer, which is more prone to cyber-attacks.
Accordingly, the risk level is classified into five categories:
critical impact, high impact, moderate impact, low impact, and
negligible impact. Table I presents the risk impact analysis of
the IoMT devices in the proposed environment, with a detailed
description available in Algorithm 3.
D. Adaptive Fuzzy Role-Based Access Control

Input: Client Roles {Ro(Dn ), Ro(docn ), Ro(han )}
Output: FNFIS Access Rules 1 or 0
1: Initialize the Roles and Authenticity of Cl
2: Pass Ro(Cl) → fuzzification layer (30)
3: Set the FNFIS Gaussian Function f (x) (31)
4: OpiI → Inference Layer to determine weights (32)
5: Normalize Wei in the normalization layer (33)
6: Defuzzify the normalized weights in the de-fuzzification layer (34)
7: Obtain overall output OpiV (35)
8: Generate Fuzzy Rules from OpiV
9: if Ro(Cl) = Ac(res) then
10:
Allowed = 1
11: else
12:
Denied = 0
13: end if

From the above equation, the weight of a neuron is denoted
by Wei . The weights from the inference layer are normalized
in the normalization layer, which is formulated as follows:
Wei
OpiIII = Wei = 
,
i Wei

∀i = 1, 2, 3

(33)

Access control is provided for IoMT users, doctors, and
healthcare assistants in cloud applications using the Flexible
Neuro-Fuzzy Inference System (FNFIS), based on the roles
assigned during the authentication stage. For instance, doctors
interpret and provide results for IoMT users, IoMT users
view the final results provided by doctors, and healthcare
assistants manage IoMT users’ requests without compromising
their privacy. Entities that comply with role-based policies are
granted access; otherwise, access is denied.
The roles of the entities are input to the FNFIS, which
consists of five layers: fuzzification, inference, normalization,
defuzzification, and output. The entity roles are represented
as Ro = {Ro(Dn ), Ro(docn ), Ro(han )}. The output of the
fuzzification layer is expressed as follows:
⎧
⎨ Ai (x), ∀i = 1, 2
OpiI = Bi−2 (x), ∀i = 3, 4
(30)
⎩
Ci−4 (x), ∀i = 5, 6

From the above equation, the normalized weight is denoted by
Wei . The normalized weights are defuzzified in the defuzzification layer, formulated as follows:

From the above equation, the fuzzy membership function is
denoted by , and the linguistic variables are denoted by Ai ,
Bi , and Ci . The proposed FNFIS uses a Gaussian function,
formulated as follows:


(x − B)2
f (x) = A · exp −
(31)
2C2

where 1 denotes access granted and 0 denotes access denied.
Specifically, if the client roles and their access requests Ac(res)
match, access is granted (1); otherwise, it is denied (0). The
pseudocode for the FNFIS-assisted role-based access control
is provided in Algorithm 4.

where A, B, and C denote the membership parameters of the
FNFIS. These parameters are provided to the inference layer,
which produces the output as follows:

V. E XPERIMENTAL R ESULTS

OpiII = Wei = Ai (x) · Bi (x) · Bi (x),

∀i = 1, 2, 3 (32)

OpiIV = Wei fi = Wei · (Pi x + Qi y + Si z)

(34)

where P, Q, and S denote the subsequent fuzzy parameters
that provide the defuzzified output. The overall output from
the output layer is formulated as follows:

Wei fi
i
Wei fi = i
(35)
OpV = f (x, y, z) =
i
i Wei
The final output from the output layer provides access rules
for clients based on their designated roles in Boolean format.
The formulation of the access rules is as follows:
RULE(FNFIS) =

1, if Ro(Cl) = Ac(res)
0, if Ro(Cl) = Ac(res)

(36)

This section presents the experimental and implementation
analyses of the proposed Fed-IoMT-Block framework, offering
both quantitative and qualitative insights. It consists of three
supplementary sections, each described in detail below:

KHAN et al.: Fed-IoMT-Block: A PRIVACY-PRESERVING FRAMEWORK FOR SECURE FL

8461

TABLE II
S IMULATION S ETTINGS

Fig. 2.

Number of IoMT devices vs malicious traffic.
TABLE III
M ALICIOUS T RAFFIC R ATE ( BPS ) FOR I O MT D EVICES

A. Simulation Setup
The simulation setup for the proposed Fed-IoMT-Block
framework is detailed in this section. The framework was
implemented using Python 3.8.2 on Windows 11, with 8GB
of RAM, 500GB HDD storage, and an AMD Ryzen 5 5600H
microprocessor with Radeon Graphics at 3.30 GHz. Table II
lists the simulation parameters of the proposed method.
The heterogeneous nature of IoMT devices includes onbody, in-body, and off-body sensing devices, which are used
to monitor respiratory rate, heart rate, blood pressure, temperature, internal organs such as the kidneys, and the physical
postural movements of the patient, respectively. The sensory
data generated by these devices require different transmission
speeds and bandwidths to be periodically sent to medical
doctors.
B. Comparative Analysis
This section focuses on the comparative analysis of
the proposed Fed-IoMT-Block with existing frameworks,
including the Fortified Chain [31], Fed-IoMT [38], and ASCPIoMT [46]. The performance metrics used for quantitative
analysis include Malicious Traffic (bps), Detection Accuracy
(%), Attack Detection Accuracy (%), and Throughput (Mbps).
A detailed explanation of the comparative metrics is provided
below.
1) Malicious Traffic Analysis: Malicious traffic is defined
as traffic initiated or imposed by malicious users/entities in
the IoMT environment, attempting to take over legitimate
resources in an untrusted environment. Figure 2 compares
malicious traffic in the proposed Fed-IoMT-Block framework with existing methods based on the number of IoMT
devices. It is observed that the malicious traffic generated
by attackers is lower in the proposed framework than in
existing solutions. The primary reason for this reduction
is that the proposed framework filters such traffic early
by performing authentication using the QAP protocol. The
QAP utilizes multiple authentication metrics, including ID,
password, biometrics, and user roles, to establish a robust
authentication policy. Additionally, quantum communication
helps prevent communication-related attacks commonly found
in conventional cryptography-based authentication methods.

In contrast, existing methods such as the Fortified Chain,
Fed-IoMT, and ASCP-IoMT either rely on conventional
cryptography-based authentication or lack efficient authentication mechanisms, resulting in higher malicious traffic
rates. The quantitative analysis in Figure 2 shows that as the
number of IoMT devices increases to a maximum of 100, the
proposed Fed-IoMT-Block achieves a lower malicious traffic
rate of 38 bps. In comparison, the existing solutions, including Fortified Chain, Fed-IoMT, and ASCP-IoMT, experience
higher rates of 41 bps, 45 bps, and 48 bps, respectively.
Similarly, when the number of IoMT devices is at a minimum
of 10, the proposed Fed-IoMT-Block records 13 bps, while
Fortified Chain, Fed-IoMT, and ASCP-IoMT record 15 bps,
18 bps, and 20 bps, respectively. Table III presents the detailed
comparison.
2) Detection Accuracy Analysis: Detection accuracy is the
proportion of true positives to the sum of true positives and
true negatives. In our work, we define detection accuracy as
the correct identification of disease by heterogeneous IoMT
devices, as follows.
TP
× 100
(37)
DetAcc =
TP + TN
Figure 3 shows detection accuracy in relation to disease severity. The graphical analysis indicates that detection accuracy
increases as disease severity increases.
The proposed Fed-IoMT-Block achieves improved detection
accuracy by utilizing an advanced AI model for disease
detection called Att-CapsNet. This model outperforms the
conventional CNN algorithm and ensures higher detection
accuracy. In contrast, existing works such as Fortified Chain,
Fed-IoMT, and ASCP-IoMT achieve lower detection accuracy due to their reliance on conventional machine learning
classifiers. The numerical results show that the detection
accuracy of the proposed Fed-IoMT-Block increases to 98%

8462

Fig. 3.

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 3, AUGUST 2025

Disease severity vs detection accuracy.

Fig. 4.

TABLE V
ATTACK D ETECTION ACCURACY (%) FOR I O MT D EVICES

TABLE IV
D ETECTION ACCURACY (%) FOR I O MT D EVICES

when disease severity reaches its maximum of 100. However,
existing solutions achieve detection accuracy rates of 91%,
82%, and 72%, respectively. Similarly, when disease severity is
a minimum of 10, the detection accuracies of the proposed and
existing methods are 70%, 63%, 55%, and 40%, respectively.
Table IV provides a better representation of the detection
accuracy.
3) Attack Detection Accuracy Analysis: Attack detection
accuracy is defined as the proportion of legitimate sample
counts in the environment to the number of malicious samples,
as described below:
No. of Legitimate Samples
× 100
(38)
AttDec =
No. of Malicious Samples
Figure 4 shows that the proposed Fed-IoMT-Block achieves a
higher attack detection accuracy rate than existing methods.
The primary reason for this improved detection rate is the
incorporation of a VAA, which continuously monitors external attacks. In addition, the proposed framework employs a
blockchain-based role-based access control method, further
strengthening the security of the Fed-IoMT-Block model.
Quantitative analysis indicates that when the number of
malicious IoMT devices increases to a maximum of 50, the
proposed Fed-IoMT-Block detects attacks at a higher rate
of 99%, whereas existing solutions achieve lower detection
rates of 86%, 83%, and 79%, respectively. Similarly, when
the number of malicious IoMT devices is as low as 10,
the proposed framework achieves a higher attack detection
accuracy of 65%, while existing solutions achieve detection
rates of 60%, 53%, and 40%, respectively. Table V shows
the attack detection accuracy of the proposed Fed-IoMT-Block
framework compared to existing state-of-the-art schemes,
achieving a higher attack detection accuracy.
4) Throughput Analysis: Throughput is defined as the number of packets successfully transmitted from the source to the

Malicious IoMT devices vs attack detection accuracy.

Fig. 5.

Latency vs throughput.

destination in the IoMT environment. Figure 5 shows that as
latency increases, throughput decreases because it is inversely
proportional to latency. The proposed framework achieves
better throughput, even as latency increases. The primary
reason for this higher throughput rate is that the proposed
framework incorporates federated learning technology into the
IoMT environment, ensuring data privacy that helps resist
communication-related attacks and protect model privacy. In
contrast, existing solutions such as Fortified Chain, Fed-IoMT,
and ASCP-IoMT have limited data privacy measures, resulting
in lower throughput.
Based on the numerical analysis, the proposed framework
achieves a higher throughput rate of 12 Mbps when latency
increases to a maximum of 1.6 seconds. For the same latency,
the throughput achieved by Fortified Chain, Fed-IoMT, and
ASCP-IoMT is 11 Mbps, 10.5 Mbps, and 10 Mbps, respectively. Similarly, when latency is a minimum of 0.2 seconds,
the proposed framework achieves a throughput of 23 Mbps,
while existing solutions achieve 22 Mbps, 21 Mbps, and
20 Mbps, respectively.

KHAN et al.: Fed-IoMT-Block: A PRIVACY-PRESERVING FRAMEWORK FOR SECURE FL

8463

TABLE VI
A LGORITHM F UNCTIONS AND C OST C OMPLEXITY IN THE P ROPOSED F ED -I O MT-B LOCK F RAMEWORK

C. Security Analysis

D. Research Findings

This section presents a security analysis of the proposed
countermeasures. Below are the cyber-attacks that were
resisted by the proposed method:
• Man-in-the-Middle Attack (MITM): The proposed work
mitigates this MITM attack by adopting quantum
technology-based authentication, named QAP, which
overcomes the problems of conventional cryptography
algorithms.
• DDoS Attacks: The Distributed Denial of Service (DDoS)
attack floods legitimate servers to prevent access from
legitimate users. DDoS attacks are overcome in the
proposed environment by utilizing VAA, which analyzes
the risk of external traffic to enable better attack detection
accuracy.
• Insider Attacks: The proposed architecture consists of
three layers including the IoMT Sensors Layer, the
Cloud Layer, and the Application Layer. Each layer
includes various sensing devices and healthcare personnel. Although these layers are partially secured,
they remain vulnerable to compromise. Insider attacks
may exploit vulnerabilities through phishing, malware,
DoS, and DDoS attacks, leading to the deletion or
corruption of sensory data stored on local machines.
These incidents are often attributed to human error
or hardware/software failures. Any TA, VAA, or SA
can be compromised by such attacks and may exhibit
Byzantine failures to conceal the loss or corruption of
data from medical professionals. Furthermore, insider
threats may also involve reassigning stored data to a new
user’s storage location, effectively removing the original
data. To address these challenges, the proposed work
adopts role-based access control using FNFIS, which
restricts privileged access and effectively mitigates insider
threats.
• Model Poisoning Attacks: Model poisoning attacks are
common in federated learning environments, manipulating the federated learning model to bypass the global
model. The proposed work resists model poisoning
attacks by adopting homomorphic encryption, which
successfully prevents such attacks.
• Cryptographic Attacks: In conventional IoMT environments, systems are highly vulnerable to cryptographic
attacks, where conventional cryptographic methods are
easily spoofed. The proposed work addresses this issue
by adopting a quantum-based authentication method that
resists both conventional and recent cryptographic attacks
to a greater extent.

The proposed method adopts Fed-IoMT-Block by utilizing
blockchain and federated learning technologies. Further, the
comparative results show that the proposed work outperforms
other methods. The cost complexities of the proposed algorithms align with the multiple QAP systems in Figure 1, as
depicted in Table VI.
VI. C ONCLUSION
The poor security measures and heterogeneity issues in
IoMT devices present challenges in the IoMT environment.
The proposed Fed-IoMT-Block framework addresses these
challenges by adopting a three-layered approach, consisting
of an IoMT sensor layer, a cloud layer, and an application
layer. The authenticity of IoMT clients is validated using the
QAP protocol, based on several metrics such as ID and biometrics. Only authenticated IoMT device results are securely
communicated using heterogeneous federated technology with
homomorphic encryption through Att-CapsNet. Meanwhile,
external network traffic is analyzed using the LGBM algorithm
based on several metrics.
The implemented algorithm classifies traffic into normal
and malicious categories. Based on these classifications, a risk
assessment is performed using various mathematical analyses. Finally, role-based access control is implemented based
on the roles registered during the registration phase in the
application layer. This role-based access control mechanism
prevents malicious unauthorized access and ensures end-toend security. The performance results demonstrate that the
proposed model outperforms existing models. This work will
be further enhanced by introducing a stronger encryption
algorithm, protection mechanisms against potential cyberattacks, energy consumption considerations, and real-world
testing.
R EFERENCES
[1] L. D. Xu, Y. Lu, and L. Li, “Embedding blockchain technology into
IoT for security: A survey,” IEEE Internet Things J., vol. 8, no. 13,
pp. 10452–10473, Jul. 2021.
[2] D. C. Nguyen, M. Ding, P. N. Pathirana, A. Seneviratne, J. Li, and
H. V. Poor, “Federated learning for Internet of Things: A comprehensive
survey,” IEEE Commun. Surveys Tuts., vol. 23, no. 3, pp. 1622–1658,
3rd Quart., 2021.
[3] F. Ali et al., “Type-2 fuzzy ontology–aided recommendation systems
for IoT-based healthcare,” Comput. Commun., vol. 119, pp. 138–155,
Apr. 2018.
[4] A. Aslam and E. Curry, “A survey on object detection for the Internet
of Multimedia Things (IoMT) using deep learning and event-based
middleware: Approaches, challenges, and future directions,” Image Vis.
Comput., vol. 106, Feb. 2021, Art. no. 104095.

8464

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 3, AUGUST 2025

[5] V. Malamas et al., “Risk assessment methodologies for the Internet of
Medical Things: A survey and comparative appraisal,” IEEE Access,
vol. 9, pp. 40049–40075, 2021.
[6] W. Cai et al., “Hierarchical domain adaptation projective dictionary pair
learning model for EEG classification in IoMT systems,” IEEE Trans.
Comput. Social Syst., vol. 10, no. 4, pp. 1559–1567, Aug. 2023.
[7] T. Zhu, L. Kuang, J. Daniels, P. Herrero, K. Li, and P. Georgiou, “IoMTenabled real-time blood glucose prediction with deep learning and edge
computing,” IEEE Internet Things J., vol. 10, no. 5, pp. 3706–3719,
Mar. 2023.
[8] J. Liu, F. Miao, L. Yin, Z. Pang, and Y. Li, “A noncontact
ballistocardiography-based IoMT system for cardiopulmonary health
monitoring of discharged COVID-19 patients,” IEEE Internet Things J.,
vol. 8, no. 21, pp. 15807–15817, Nov. 2021.
[9] P. V. Paul and R. Saraswathi, “The Internet of Things—A comprehensive
survey,” in Proc. Int. Conf. Comput. Power Energy Inf. Commun.
(ICCPEIC), Mar. 2017, pp. 1–7.
[10] S. Bharati, P. Podder, M. R. H. Mondal, and P. K. Paul, Applications
and Challenges of Cloud Integrated IoMT. Cham, Switzerland: Springer
Int., Oct. 2020, pp. 67–85.
[11] R. Dwivedi, D. Mehrotra, and S. Chandra, “Potential of Internet of
Medical Things (IoMT) applications in building a smart healthcare
system: A systematic review,” J. Oral Biol. Craniofacial Res., vol. 12,
no. 2, pp. 302–318, Mar. 2022.
[12] P. Singh, K. J. Devi, H. K. Thakkar, M. Bilal, A. Nayyar, and D. Kwak,
“Robust and secure medical image watermarking for edge-enabled
e-Healthcare,” IEEE Access, vol. 11, pp. 135831–135845, 2023.
[13] R. Hireche, H. Mansouri, and A.-S. K. Pathan, “Security and privacy
management in Internet of Medical Things (IoMT): A synthesis,” J.
Cybersecurity Privacy, vol. 2, no. 3, pp. 640–661, Aug. 2022.
[14] S. Tarikere, I. Donner, and D. Woods, “Diagnosing a healthcare
cybersecurity crisis: The impact of IoMT advancements and 5G,” Bus.
Horizons, vol. 64, no. 6, pp. 799–807, Nov. 2021.
[15] S. Razdan and S. Sharma, “Internet of Medical Things (IoMT):
Overview, emerging technologies, and case studies,” IETE Tech. Rev.,
vol. 39, no. 4, pp. 775–788, May 2021.
[16] R. K. Mahendran and P. Velusamy, “A secure fuzzy extractor based biometric key authentication scheme for body sensor network in Internet of
Medical Things,” Comput. Commun., vol. 153, pp. 545–552, Mar. 2020.
[17] T. S. Enamamu, Intelligent Authentication Framework for Internet
of Medical Things (IoMT). Cham, Switzerland: Springer Int., 2022,
pp. 97–121.
[18] N. Naren et al., “IoMT and DNN-enabled drone-assisted COVID-19
screening and detection framework for rural areas,” IEEE Internet Things
Mag., vol. 4, no. 2, pp. 4–9, Jun. 2021.
[19] Z. Ghaffar, W.-C. Kuo, K. Mahmood, T. Tariq, A. K. Bashir, and
M. Omar, “A machine learning attack resilient and low-latency authentication scheme for AI-driven patient health monitoring system,” IEEE
Commun. Stand. Mag., vol. 8, no. 3, pp. 36–42, Sep. 2024.
[20] S. Yu and K. Park, “SALS-TMIS: Secure, anonymous, and lightweight
privacy-preserving scheme for IoMT-enabled TMIS environments,”
IEEE Access, vol. 10, pp. 60534–60549, 2022.
[21] S. Y. Siddiqui et al., “IoMT cloud-based intelligent prediction of breast
cancer stages empowered with deep learning,” IEEE Access, vol. 9,
pp. 146478–146491, 2021.
[22] J. Almalki et al., “Enabling blockchain with IoMT devices for
Healthcare,” Information, vol. 13, no. 10, p. 448, Sep. 2022.
[23] K. K. Kamarajugadda, P. Movva, M. N. Raju, S. A. Kant, and
S. Thatavarti, IoMT With Cloud-Based Disease Diagnosis Healthcare
Framework for Heart Disease Prediction Using Simulated Annealing
With SVM. Cham, Switzerland: Springer Int., 2021, pp. 115–126.
[24] Q. Pan, J. Wu, A. K. Bashir, J. Li, W. Yang, and Y. D. Al-Otaibi,
“Joint protection of energy security and information privacy for energy
harvesting: An incentive federated learning approach,” IEEE Trans. Ind.
Informat., vol. 18, no. 5, pp. 3473–3483, May 2022.
[25] A. D. Aguru et al., “Reliable-RPL: A reliability-aware RPL protocol
using trust-based blockchain system for Internet of Things,” IEEE Trans.
Rel., early access, Dec. 16, 2024, doi: 10.1109/TR.2024.3508652.
[26] D. C. Nguyen, P. N. Pathirana, M. Ding, and A. Seneviratne,
“BEdgeHealth: A decentralized architecture for edge-based IoMT
networks using blockchain,” IEEE Internet Things J., vol. 8, no. 14,
pp. 11743–11757, Jul. 2021.
[27] S. Rahmadika, P. V. Astillo, G. Choudhary, D. G. Duguma, V. Sharma,
and I. You, “Blockchain-based privacy preservation scheme for misbehavior detection in lightweight IoMT devices,” IEEE J. Biomed. Health
Inform., vol. 27, no. 2, pp. 710–721, Feb. 2023.

[28] Y. Liu, G. Shan, Y. Liu, A. Alghamdi, I. Alam, and S. Biswas,
“Blockchain bridges critical national infrastructures: E-healthcare data
migration perspective,” IEEE Access, vol. 10, pp. 28509–28519, 2022.
[29] H. Saidi, N. Labraoui, A. A. A. Ari, L. A. Maglaras, and J. H. M. Emati,
“DSMAC: Privacy-aware decentralized self-management of data access
control based on blockchain for health data,” IEEE Access, vol. 10,
pp. 101011–101028, 2022.
[30] S. L. T. Vangipuram, S. P. Mohanty, and E. Kougianos, “CoviChain:
A blockchain based framework for nonrepudiable contact tracing in
healthcare cyber-physical systems during pandemic outbreaks,” SN
Comput. Sci., vol. 2, no. 5, p. 346, Jun. 2021.
[31] B. S. Egala, A. K. Pradhan, V. Badarla, and S. P. Mohanty, “Fortifiedchain: A blockchain-based framework for security and privacy-assured
Internet of Medical Things with effective access control,” IEEE Internet
Things J., vol. 8, no. 14, pp. 11717–11731, Jul. 2021.
[32] B. Annane, A. Alti, and A. Lakehal, “Blockchain based context-aware
CP-ABE schema for Internet of Medical Things security,” Array, vol. 14,
Jul. 2022, Art. no. 100150.
[33] A. Rehman, S. Abbas, M. Khan, T. M. Ghazal, K. M. Adnan, and
A. Mosavi, “A secure healthcare 5.0 system based on blockchain
technology entangled with federated learning technique,” Comput. Biol.
Med., vol. 150, Nov. 2022, Art. no. 106019.
[34] W. Liu, Y. Zhang, G. Han, J. Cao, H. Cui, and D. Zheng, “Secure and
efficient smart healthcare system based on federated learning,” Int. J.
Intell. Syst., vol. 2023, no. 1, pp. 1–12, Jan. 2023.
[35] B. D. Deebak and S. O. Hwang, “Federated learning-based lightweight
two-factor authentication framework with privacy preservation for
mobile sink in the social IoMT,” Electronics, vol. 12, no. 5, p. 1250,
Mar. 2023.
[36] P. K. Bhansali, D. Hiran, and K. Gulati, “Secure data collection and
transmission for IoMT architecture integrated with federated learning,”
Int. J. Pervasive Comput. Commun., vol. 20, no. 4, pp. 564–577,
May 2022.
[37] T. Hai, J. Zhou, S. R. Srividhya, S. K. Jain, P. Young, and S. Agrawal,
“BVFLEMR: An integrated federated learning and blockchain technology for cloud-based medical records recommendation system,” J. Cloud
Comput., vol. 11, no. 1, p. 22, Jul. 2022.
[38] A. Lakhan et al., “Federated-learning based privacy preservation and
fraud-enabled blockchain IoMT system for Healthcare,” IEEE J. Biomed.
Health Inform., vol. 27, no. 2, pp. 664–672, Feb. 2023.
[39] L. Zhang, J. Xu, P. Vijayakumar, P. K. Sharma, and U. Ghosh,
“Homomorphic encryption-based privacy-preserving federated learning
in IoT-enabled healthcare system,” IEEE Trans. Netw. Sci. Eng., vol. 10,
no. 5, pp. 2864–2880, Sep. 2023.
[40] S. Niu, X. Zhou, N. Wang, W. Kong, and L. Chen, “Secure and verifiable
federated learning against poisoning attacks in IoMT,” Comput. Elect.
Eng., vol. 122, Mar. 2025, Art. no. 109900.
[41] W. Jiang et al., “Fuzzy ensemble-based federated learning for EEGbased emotion recognition in Internet of Medical Things,” J. Ind. Inf.
Integr., vol. 44, 2025, Art. no. 100789.
[42] M. Narula, J. Meena, and D. K. Vishwakarma, “Federated workloadaware quantized framework for secure learning in data-sensitive
applications,” Future Gener. Comput. Syst., vol. 168, Jul. 2025,
Art. no. 10777.
[43] M. Kumar, S. K. Singh, and S. Kim, “Hybrid deep learningbased cyberthreat detection and IoMT data authentication model in
smart healthcare,” Future Gener. Comput. Syst., vol. 166, Mar. 2025,
Art. no. 107711.
[44] A. Hussain et al., “Ensuring zero trust IoT data privacy: Differential
privacy in blockchain using federated learning,” IEEE Trans. Consum.
Electron., vol. 71, no. 1, pp. 1167–1179, Feb. 2025.
[45] S. A. Wagan et al., “A fuzzy-based duo-secure multi-modal framework
for IoMT anomaly detection,” J. King Saud Univ. Comput. Inf. Sci.,
vol. 35, no. 1, pp. 131–144, Jan. 2023.
[46] M. Wazid et al., “ASCP-IoMT: AI-enabled lightweight secure communication protocol for Internet of Medical Things,” IEEE Access, vol. 10,
pp. 57990–58004, 2022.
[47] M. Azeem et al., “FoG-oriented secure and lightweight data aggregation
in IoMT,” IEEE Access, vol. 9, pp. 111072–111082, 2021.
[48] A. Almogren, I. Mohiuddin, I. U. Din, H. Almajed, and N. Guizani,
“FTM-IoMT: Fuzzy-based trust management for preventing Sybil
attacks in Internet of Medical Things,” IEEE Internet Things J., vol. 8,
no. 6, pp. 4485–4497, Mar. 2021.
[49] J. Nayak, S. K. Meher, A. Souri, B. Naik, and S. Vimal, “Extreme
learning machine and Bayesian optimization-driven intelligent framework for IoMT cyber-attack detection,” J. Supercomput., vol. 78, no. 13,
pp. 14866–14891, Apr. 2022.
PAPER_TEXT
