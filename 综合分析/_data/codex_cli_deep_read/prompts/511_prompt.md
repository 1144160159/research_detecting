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
# [511] Q-P2FL: Quantum-Enhanced Federated Edge Intelligence for Privacy-Preserving Adversarial Attack Detection on Consumer Edge Devices
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
编号：511
题名：Q-P2FL: Quantum-Enhanced Federated Edge Intelligence for Privacy-Preserving Adversarial Attack Detection on Consumer Edge Devices
年份：2025
DOI：10.1109/tce.2025.3571352
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2025.3571352.pdf
已有粗分类：联邦学习、隐私保护与分布式协同
二级关联：恶意流量、暗网与攻击检测、IoT、车联网、工业互联网与边缘安全
相关性：中相关，分数 7
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\511.txt
- 原始字符数：50390
- 本次发送字符数：50390
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
4914

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 2, MAY 2025

Q-P2FL: Quantum-Enhanced Federated Edge
Intelligence for Privacy-Preserving Adversarial
Attack Detection on Consumer Edge Devices
Farhan Ullah , Nazeeruddin Mohammad , Member, IEEE, Leonardo Mostarda , Member, IEEE,
Diletta Cacciagrano , and Yue Zhao

Abstract—The rapid expansion of smart consumer environments is facilitated by device-to-device communication, which
generates considerable quantities of data and improves the
user experience. While this data provides useful insights, it
is also subject to malicious cyberattacks. Machine Learning
(ML)-based threat detection technologies solve these challenges;
however crucial consumer electronics privacy concerns are often
bypassed. The growing connectivity of consumer devices raises
the possibility of adversarial cyberattacks. Quantum technology
may give stronger protection against threats, while FL-based
edge computing may help to ensure data privacy and security. This work proposes a Quantum-based Privacy-Preserving
Federated Learning (Q-P2FL) technique for detecting adversarial
attacks on consumer edge devices. First, as quantum computing
advances, standard validation approaches may become obsolete.
Quantum-based registration and authentication with Additive
Homomorphic Encryption (AHE) is employed to safeguard
privacy and secure model weights on edge devices. Second,
image-based features are extracted from network traffic bytes to
generate distinguished datasets. Third, adversarial examples are
generated to assess the robustness of datasets. This is achieved
by employing four distinct types of adversarial techniques that
incorporate perturbations into the input data. The pre-trained
Vision Transformer (ViT) extracts features to generate the local
model weights. Finally, the Q-P2FL approach detects and classifies adversarial attacks, ensuring data security and privacy. The
proposed method is evaluated on two standard datasets: EdgeIIoT and CICIoMT2024, with detection accuracies of 99.38%
and 99.41%, respectively. This approach presents a promising
solution for protecting consumer edge devices from adversarial
attacks and improving their privacy-preserving capabilities.
Index Terms—Quantum computing, consumer devices, edge
computing, federated learning, adversarial attacks, cybersecurity.

Received 5 January 2025; revised 3 March 2025 and 25 April 2025;
accepted 10 May 2025. Date of publication 19 May 2025; date of current version 14 August 2025. This work was supported by the National
Program for Research, Development, and Innovation in Cybersecurity,
National Cybersecurity Authority, Saudi Arabia, under Grant CRPG-25-3245.
(Corresponding author: Yue Zhao.)
Farhan Ullah and Nazeeruddin Mohammad are with the Cybersecurity
Center, Prince Mohammad Bin Fahd University, Al Khobar 31952, Saudi
Arabia (e-mail: fullah@pmu.edu.sa; nmohammad@pmu.edu.sa).
Leonardo Mostarda is with the Department of Mathematics and
Computer Science, University of Perugia, 06123 Perugia, Italy
(e-mail: leonardo.mostarda@unipg.it).
Diletta Cacciagrano is with the Division of Computer Science, University
of Camerino, 62032 Camerino, Italy (e-mail: diletta.cacciagrano@unicam.it).
Yue Zhao is with the Department of Computer Science, College of Science,
Mathematics and Technology, Wenzhou-Kean University, Wenzhou 325060,
China (e-mail: yuezhao@kean.edu).
Digital Object Identifier 10.1109/TCE.2025.3571352

I. I NTRODUCTION
HE EXPANSION of consumer peripheral devices has
significantly influenced the evolution of contemporary
ecosystems, resulting in more personalized services and adaptive solutions. These devices, which range from smart home
systems to wearable technology, generate and analyze vast
quantities of private data, providing unique perspectives on
individual preferences and actions. However, the interconnectivity of this ecosystem has posed substantial challenges
to protecting data privacy and security. The integrity and
dependability of these systems are at risk due to adversarial attacks, including ransomware, Denial-of-Service (DoS),
and man-in-the-middle attacks. Consequently, robust defenses
are necessary to maintain functionality and confidence [1].
Figure 1 demonstrates that traditional malware detection algorithms and antivirus software based on signatures frequently
fail to address modern cyber threats. A potential alternative
is the integration of ML into threat detection systems. These
systems, however, are susceptible to privacy concerns because
they rely on centralized infrastructures for model training.
Sensitive data transported to centralized systems is vulnerable
to breaches and unwanted access, underlining the need for
more secure, decentralized decisions [2], [3].
Federated Learning (FL) has become an important step
forward in addressing privacy concerns. FL ensures that
data is maintained on local devices during the learning
process by transferring only model changes, not unprocessed
data. Furthermore, this methodology promotes privacy and
allows for collaborative learning in distributed environments.
However, FL is still vulnerable. Attackers can utilize techniques such as the Fast Gradient Sign Method (FGSM),
Iterative Gradient Sign Method (IGSM), Projected Gradient
Descent (PGD), or a hybrid approach to compromise the
security and resilience of FL systems. These methods are
referred to as evasion assaults and involve the use of adversarial samples to deceive the model into producing inaccurate
predictions [4]. In our research, we assess the robustness of
the classification task by employing these strategies to produce
adversarial images. Furthermore, the current FL implementations use Fully Homomorphic Encryption (FHE) and Secure
Multi-party Computation (SMC), which have large processing
costs, limiting their usefulness in resource-constrained edge
applications. Quantum technology improves the prevention of
cyber threats, while edge computing enables data processing,

T

c 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
1558-4127 
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

ULLAH et al.: Q-P2FL: QUANTUM-ENHANCED FEDERATED EDGE INTELLIGENCE

Fig. 1.

Impact of adversarial attacks on traditional model training methods.

thereby reducing the vulnerabilities associated with centralized
infrastructures [5], [6]. Quantum-based FL employs advanced
quantum authentication to secure edge device communication
while maintaining privacy. It employs quantum security techniques to defend against adversarial attacks. In contrast to
conventional methods, it utilizes the Quantum Conference Key
Agreement (QCKA) to establish high-security key exchange
protocols. This provides quantum states impermeable in digital
encryption, as any interception or duplication is immediately
detectable, even under adverse conditions. Reliable interaction
is ensured by this innovative technique, which safeguards
critical data within decentralized FL systems [7], [8].
To address these difficulties, this study presents Q-P2FL, an
FL framework for detecting adversarial attacks on consumer
edge devices. The method protects against data breaches and
model manipulation by utilizing quantum computing to overcome the limitations of conventional cryptography. Q-P2FL
incorporates Additive Homomorphic Encryption (AHE) to
balance data privacy with computational efficiency, making it
beneficial for edge intelligence applications [9]. This method
addresses consumer edge device heterogeneity and resource
constraints by incorporating quantum-driven registration and
authentication procedures to protect FL systems from adversarial threats [10], [11]. Q-P2FL enhances the security and
scalability of federated edge intelligence systems, making
consumer edge devices more resilient and privacy-preserving.
The main contributions are given below:
1) This study leverages image-based features to effectively
capture structured data categories, such as headers, procedures, and storage. The datasets used in this research
are generated by systematically processing large volumes of network traffic packets. These customized
datasets are then evaluated to develop a lightweight
intrusion detection approach.
2) To reduce overfitting and class imbalance, data augmentation techniques are used to increase dataset diversity.
Adversarial examples are produced utilizing FGSM,
IGSM, PGD, and a hybrid IGSM-PGD method to

4915

assess and strengthen resilience to evasion attacks. This
approach enhances model performance, data security,
and dataset resilience to adversarial threats.
3) We presented a novel Q-P2FL framework that combines
quantum technology and FL to improve the security and privacy of consumer edge devices [12]. By
employing quantum-based registration, authentication,
and AHE, the architecture effectively protects model
weights. This approach protects data privacy while
also providing effective resistance against malicious
attacks.
4) We conducted experiments using different numbers
of edge devices to assess the performance of the
proposed approach. Across all test scenarios, the method
consistently achieved superior classification results,
demonstrating its scalability and effectiveness.
The remaining sections of the paper are organized as follows:
Section II discusses related work, and Section III describes the
proposed methodology. In Section IV, the experimental results
and discussions are presented, and the study is concluded in
Section V.
II. R ELATED W ORK
Quantum-based FL approaches are gradually replacing conventional ML-based methods in the detection of adversarial
intrusions in consumer electronics [2], [8], [12], [13]. The
following section examines a variety of methods that utilize
ML and quantum-based FL to identify and categorize attacks
on consumer electronic devices.
A. ML/FL Methods
Qiu et al. [14] have created a novel adversarial attack
that targets network intrusion detection systems based on
the Internet of Things (IoT). This attack utilizes closed-box
access to the Deep Learning (DL) model. Model extraction
duplicates the closed-box model with minimum training data,
and saliency maps highlight the most important packet features
in detection results. These methods facilitate the efficient
generation of adversarial examples by utilizing conventional
models. Pawlicki et al. [15] used four previously proposed
approaches to generate adversarial attacks that could damage
a well-optimized intrusion detection algorithm during testing
and proposed a mechanism to detect them. The four techniques
for creating adversarial attacks and the appropriate context for
artificial neural networks are described. Yamany et al. [4] used
FL and network traffic adversarial contexts to improve medical
device security with edge intelligence. An image-based dataset
is generated by converting bytes of network traffic. The dataset
is skewed due to the sporadic nature of client interactions,
which may impair effectiveness. Four adversarial attack techniques are implemented to generate instances and evaluate
the dataset’s resilience. Ibitoye et al. [16] used the UNSW
Canberra Cyber BoT-IoT dataset to evaluate Self-normalizing
Neural Networks (SNNs) and Feed-forward Neural Networks
(FNNs) in identifying breach vulnerabilities in an IoT network.
The findings show that the FNN performs better than the
SNN in terms of accuracy, precision, recall, and Cohen’s

4916

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 2, MAY 2025

Kappa score for intrusion detection. However, the SNN performed better against adverse samples from the IoT dataset.
Chen et al. [17] introduced the privacy score and evasion
rate for FL-based intrusion detection, which quantifies traffic
attribute similarity and adversarial attack impact. Experiments
showed that hostile communications circumvented the stateof-the-art SOTA Kitsune technique, proving that existing
protections are insufficient. They presented an optimizationbased security strategy that reduces gradient distance while
increasing input distance to improve FL-based intrusion detection and privacy.
B. Quantum-Based FL Methods
Namakshenas et al. [2] used quantum-based FL to address
two significant challenges in consumer threat identification.
The first issue addressed is the importance of rigorous customer validation in FL. The advent of quantum computing
may render traditional validation methods useless. To address
this issue, a quantum-centric enrollment and authorization
approach is provided, which ensures thorough client evaluation inside an FL paradigm. The second challenge is to
protect the model weights in FL. The incorporation of AHE
ensures the privacy of FL users and efficient computation.
Houda et al. [8] developed a privacy-preserving and efficient
network intrusion detection paradigm based on quantum computing and FL. While safeguarding user privacy, decentralized
FL enabled a multitude of consumer devices to train a
global model. The efficiency of model training and inference is enhanced by quantum computation. Results showed
significant improvements in processing efficiency and detection accuracy when compared to conventional approaches.
Friha et al. [18] presented a differentially FL-based decentralized secure intrusion detection system for smart industrial
locations. Quantum computing components include a key
exchange protocol for peer-to-peer weight communication, a
differentially private gradient exchange mechanism for FL
privacy, and a decentralized FL framework. The decentralized
framework reduces the possibility of aggregation server failure
or attack in traditional FL systems. The approach identified
several types of Industrial IoT cyberattacks in a real-world
IIoT dataset. Yamany et al. [19] presented a quantum-based
FL system capable of autonomously changing FL hyperparameters in autonomous vehicle settings during adversarial
attacks. A quantum-behaved particle swarm optimization technique is employed to adjust the learning rate and local &
global epochs. The proposed technique is integrated into a
cyber-defense system to mitigate the impact of malicious
attacks.
The proposed Q-P2FL approach improves the security and
privacy of consumer devices in response to adversarial attacks.
It integrates quantum-based registration, authentication, and
AHE to enhance the privacy and protection of model weights.
Additionally, image-based features retrieved from network
traffic are used to generate novel datasets and tested for
robustness using adversarial methods. The Q-P2FL approach
efficiently identifies and classifies adversarial attacks, providing a reliable privacy-preserving solution for edge devices.

Fig. 2.
Quantum-enhanced federated edge intelligence framework for
detecting adversarial attacks on consumer edge devices.

III. P ROPOSED M ETHODOLOGY: Q UANTUM -BASED
P RIVACY-P RESERVING FL
Figure 2 illustrates the proposed Q-P2FL framework.
Quantum-based registration, which uses AHE, protects edge
device privacy and model weights. Network traffic data is
acquired using a customized crawling method and turned
into images to generate adversarial examples. These are then
classified using FL to ensure the system’s resilience.
A. Dataset Preparation
The proposed approach is assessed using two widely recognized datasets. The first, Edge-IIoTset1 [20], dataset is
generated using an IoT/IIoT testbed that includes a range
of devices, sensors, protocols, and edge configurations. It
includes data from over ten IoT devices, including low-cost
humidity and temperature sensors. It addresses 14 different
forms of attacks, including malware, injection, man-in-themiddle, and DoS/DDoS. The data, which originally had 1176
attributes, has been reduced to 61 key features. This dataset
provides a wide range of attack scenarios, making it useful
for testing industrial and IoT intrusion detection systems. The
second dataset primarily focuses on the security of healthcare
devices, CICIoMT20242 [21]. It explores attacks on 40 devices
(25 physical and 15 simulated) using protocols such as
Bluetooth, MQTT, and Wi-Fi. The most prominent attacks are
spoofing, reconnaissance, DDoS, and MQTT-based exploits.
The security dataset is generated by replaying network traffic
between switches and IoMT devices in real time using a
network probe.
1 https://www.kaggle.com/datasets/mohamedamineferrag/edgeiiotset-cybersecurity-dataset-of-iot-iiot/code
2 https://www.unb.ca/cic/datasets/iomt-dataset-2024.html

ULLAH et al.: Q-P2FL: QUANTUM-ENHANCED FEDERATED EDGE INTELLIGENCE

4917

network traffic images, especially when identifying malicious
behavior. By producing synthetic data, the model can gain
knowledge from a greater variety of network patterns, improving its ability to identify anomalies [25], [26].
To simulate different orientations of the image, a synthetic
rotation by an angle θ can be described in equation (1):
Isynthetic = Rθ (I)

(1)

where Rθ denotes the operation that rotates image I by
angle θ .
Scaling the image to new dimensions x × y is another
important transformation in synthetic data generation shown
in equation (2):
Iscaled = I · S(x, y)
Fig. 3.

Distribution of images in the CICIoMT2024 dataset.

B. Light-Weight Feature Extraction
Packet Capture (PCAP) files provide essential packet logs
that enhance network performance and security. They help
detect threats, identify unusual behavior, and track network
issues during incident investigations. PCAP files are also critical for protocol analysis, aiding in the detection of errors and
illegal activities [22], [23]. Packet data analysis can be used to
measure performance more accurately, revealing latency issues
and barriers. In addition to facilitating the identification of
threats by exposing aberrant behaviors and potential security
risks, PCAP files serve as an audit trail, ensuring adherence
to laws and security policies. They help troubleshoot network
faults by revealing individual data flows. Addressing static
and dynamic classification problems is becoming increasingly
important with the growth of network traffic. We explored
using visual signals to detect malicious communications as a
solution. This method employs image processing to convert
network traffic patterns into textural features, eliminating the
necessity for traffic signatures or reverse engineering. PCAP
file analysis uses byte sequences that show harmful changes
to transform 8-bit vectors into grayscale images. A structured
image representation of the network traffic is formed by mapping each byte in the sequence to a pixel intensity value. This
transformation allows for the visibility of patterns associated
with harmful activity, resulting in more efficient intrusion
detection. Subsequently, the dimensions of these images are
reduced to 128 × 128 pixels. Image-based characteristics are
faster and utilize fewer resources than previous approaches
due to their small size. They also uncover subtle patterns that
conventional approaches may overlook, making them useful
for identifying malicious attacks [24]. Figure 3 shows the
number of extracted images using the CICIoMT2024 train
dataset. The lightweight nature of these capabilities makes
it easier to detect possible vulnerabilities in real time and
respond quickly to security threats.
C. Synthetic Data Generation
Synthetic data generation is an effective strategy for increasing feature extraction and addressing class imbalances in

(2)

where S(x, y) is the scaling function that resizes the image I
to the dimensions x × y.
Incorporating noise into the image for enhanced robustness
can be modeled as shown in equation (3):
Inoisy = I + ,

 ∼ N (μ, σ )

(3)

where  is noise sampled from a Gaussian distribution with
mean μ and standard deviation σ .
For simulating variations in data composition as shown
in equation (4), synthetic cropping is applied to the image,
adjusting its size to x × y :


(4)
Icropped = I x × y
where x × y indicates the target dimensions of the cropped
image.
Synthetic color jittering, which modifies the image’s
brightness, contrast, saturation, and hue, is represented in
equation (5):


(5)
Ijittered = I  J δbrightness , δcontrast , δsaturation , δhue
where J (δbrightness , δcontrast , δsaturation , δhue ) applies random
changes to these properties.
Horizontal and vertical flipping, key for generating different
image perspectives, can be formalized in equation (6):

Fh (I) with probability phorizontal
Iflipped =
(6)
Fv (I) with probability pvertical
where Fh (I) and Fv (I) represent the horizontal and vertical
flip operations.
Lastly, applying an affine transformation to the image for
synthetic data generation can be written in equation (7):
Iaffine = A(I, M, b)

(7)

where A(I, M, b) applies the affine transformation using
matrix M and translation vector b.
These strategies are used to produce synthetic data, which
makes the training dataset more diverse and allows the model
to learn more robust and generalized features. This enables
the model to more effectively identify malicious traffic, even
in scenarios where the network conditions are dynamic or
the data is insufficient. Additionally, synthetic data production
ensures that the model is trained on a wide range of realworld traffic patterns and anomalies. For intrusion detection

4918

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 2, MAY 2025

Equations (9) and (10) specify the iterations, starting from the
initial input x:
x(0) = x,

(9)

(t+1)

(10)

x

Fig. 4.
flows.

Examining evasion attacks based on irregularities in network traffic

applications, this method enhances both generalization and
accuracy.
D. Synthesizing Adversarial Perturbations
Evasion attacks are a common adversarial strategy in which
attackers intentionally alter inputs to confuse ML models.
These attacks take advantage of weaknesses in the model by
making small changes to legitimate inputs, causing them to
be misclassified as shown in Figure 4. This study evaluates
four adversarial techniques: PGD, FGSM, IGSM, and a hybrid
approach that combines PGD and IGSM [27]. These strategies
are used to evaluate their efficacy in creating adversarial
examples that can fool the target model while also lowering
the degree of perturbation introduced. Understanding and protecting against evasion attacks requires the ability to synthesize
suspicious perturbations. The examination of the robustness of
intrusion detection against evasion attacks offers information
about their ability to effectively manage sophisticated cyber
intrusions [28].
By utilizing adversarial perturbation approaches, it is possible to predict evasion risks and improve the adaptability
of intrusion detection. In addition to revealing potential
vulnerabilities during model testing in these scenarios, countermeasures are also implemented to mitigate these attacks.
By predicting and resolving evasion strategies, it is possible
to detect Advanced Persistent Threats (APTs), malware, and
other cyberattacks that employ minor modifications to evade
detection [14], [29].
1) FGSM: FGSM uses a gradient-based, one-step technique for adversarial sample generation. It changes the input x
in the direction of the gradient of the loss function L(w, x, y),
where it w represents the model coefficients and y represents
the true label. Equation (8) calculates the adversarial input x ,
whereas λ determines the perturbation magnitude.
x = x + λ · sign(∇x L(w, x, y)).

(8)

This method is computationally efficient, making it appropriate for fast adversarial attacks. However, its simplicity limits
its effectiveness against strong defensive strategies.
2) IGSM: The FGSM concept is employed iteratively by
IGSM, which is an acronym for Basic Iterative Method
(BIM). This technique uses smaller perturbation steps δ
across multiple rounds to ensure that adversarial perturbations
accumulate gradually without exceeding a predetermined limit.




= clipx,λ x(t) + δ · sign ∇x L(w, x(t) , y) ,

where t is the iteration step, and clipx,λ (·) constrains the
adversarial input to the perturbation range described by λ.
This repeated technique improves the relevancy of adversarial
examples.
3) PGD: PGD improves IGSM by including a projection
operation that keeps perturbations under a Lp -norm limit. It
uses the initial input as a starting point for each iteration and
applies perturbations to return the adversarial example to a
suitable range. For example, the formulation is indicated in
equations (11) (12).
x(0) = x,

(11)

(t+1)

(12)

x




= B(x,λ) x(t) + δ · sign ∇x L(w, x(t) , y) ,

The projection operator on the Lp -norm ball of radius λ
around the original input x is represented by B(x,λ) (·). This
ensures that the generated adversarial examples adhere to the
specified perturbation limitations.
4) Hybrid Method (PGD and IGSM): The hybrid technique
combines the optimal features of both IGSM and PGD, combining their iterative nature with resilient optimization. It initiates
the process by generating adversarial samples using IGSM,
which are subsequently refined using PGD. This two-step technique improves attack efficiency while preserving imperceptible
disruptions, as illustrated in equations (13) (14) (15).
IGSM Phase:
x(0) = x,

(13)

(t+1)

(14)

x




= clipx,λ x(t) + δ · sign ∇x L(w, x(t) , y) .

PGD Refinement Phase:



x(t+1) = B(x,λ) x(t) + δ · sign ∇x L(w, x(t) , y) .

(15)

This hybrid approach emphasizes the benefits of both methods, with IGSM enabling precise initialization. In contrast,
PGD ensures that adversarial instances adhere to perturbation
requirements, resulting in more effective and resilient samples.
These developments increase the detection and analysis of
sophisticated cyberattacks, including evasion attacks, allowing
for proactive countermeasures in the real world. The pretrained ViT, which is renowned for its exceptional performance
in image processing and feature extraction, is utilized to
extract features for local model training [30], [31], [32]. The
ViT architecture efficiently captures complex patterns and
dependencies inside network traffic data by using self-attention
methods. In this work, ViT is applied on the client side to
process adversarial instances produced from network traffic,
therefore improving its capacity to identify abnormalities,
including DDoS attacks. The feature map extracted by the
ViT model during training is illustrated in Figure 5, which
demonstrates its ability to learn unique representations. The
ViT model updates model weights depending on processed
adversarial examples by local training on the client device.

ULLAH et al.: Q-P2FL: QUANTUM-ENHANCED FEDERATED EDGE INTELLIGENCE

4919

Algorithm 1: Quantum-Based Secured FL for Adversarial
Attack Detection
Input: Client datasets: Di for i = 1, 2, . . . , N
Output: Global model for adversarial attack detection
Mg

Fig. 5.

Cyberattack features map utilizing pre-trained vision transformer.

Function QuantumSecuredFL(D1 , D2 , . . . , DN ):
Initialize client datasets Di for i = 1, 2, . . . , N;
Initialize QKD keys for secure communication: ki for
each client i;
Initialize quantum classical key agreement for
client-server mutual authentication:
kshared = QCKA(ki , kj );
for each client i do
Train local model: wi ← Train(Di ) // Train local
model on client data Di ;
E(θi ) ← Encrypt(wi ) // Encrypt model weights
for privacy preservation using AHE;

Fig. 6.

Training times distributed across edge devices.

Figure 6 shows the distributed training time among separate
nodes. After local training, the model weights are sent to the
server for global aggregation, enabling collaborative learning
and enhancing detection performance.
E. Quantum-Based Secured FL
The proposed Q-P2FL design effectively protects user
privacy and detects adversarial attacks on edge devices by
utilizing quantum-based cryptography and AHE.
F. Quantum-Based Cryptography for Privacy Preservation
Quantum Key Distribution (QKD) is used extensively to
ensure a secure connection between the aggregation server
and clients, as shown in Algorithm 1. During QKD, quantum channels are utilized for exchanging cryptographic keys.
An alarm would be triggered regarding potential security
vulnerabilities in the system if an attempt to eavesdrop on
the key exchange disrupts the quantum state [6], [19]. To
encrypt and authenticate communications, both the client and
the aggregation server use shared keys (ki ).
Client-aggregation server mutual authentication is secured
via the Quantum Classical Key Agreement (QCKA) protocol
as shown in equation (16):


(16)
kshared = QCKA ki , kj
The term kj refers to one of the keys involved in
the Quantum Classical Key Agreement (QCKA) protocol.
Specifically, kj represents the key associated with the second
party (typically the server or another client) in the key
exchange process. In the QCKA protocol, two parties (such
as a client and a server) exchange keys, ki (the client’s key)
and kj (the server’s key or another client’s key). These keys
are subsequently employed to generate a shared secret key,

for each client i do
Send encrypted model update to server: Send
E(θi ) to aggregation server for global model
aggregation;


N
Aggregation step: E(Mg ) = AHE
E(θ
)
i ;
i=1
encrypted

wglobal ← Aggregate(E(Mg )) // Aggregate
encrypted model updates;
Decryption step:
encrypted
wglobal ← Decrypt(wglobal , kshared ) // Decrypt
aggregated model;
for each input x in test dataset do
ŷi ← f (Mg , x) // Use global model to predict and
detect adversarial attack;
Compare ŷi with intrusion patterns to detect
malicious activities;
Final Output: Return the global model Mg for
adversarial attack detection;

kshared . This shared key secures client-server communication,
preventing attackers from impersonating valid clients or inserting malicious data into FL.
G. Additive Homomorphic Encryption for Privacy-Preserving
Aggregation
AHE is used to ensure the privacy of model updates
during the FL aggregation phase. HE allows computations
on encrypted data to be performed without the need for
decryption. As a result, the aggregation server can generate
the global model weights Mg from encrypted updates without
accessing the sensitive data underlying.
Let E(θi ) represent the encrypted model weights for each
client i as given in equation (17):


E Mg = AHE

N

E(θi )
i=1

(17)

4920

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 2, MAY 2025

This guarantees that the server may aggregate model
updates from multiple clients without disclosing any sensitive
information regarding the data or local models of any of the
clients. HE encryption ensures that sensitive data remains confidential during the FL process, providing further protection
against malicious attempts and data leaks.

H. Federated Learning for Adversarial Detection
The proposed approach uses federated averaging (FedAvg)
to aggregate the global server model. This method guarantees
the reliable and effective integration of locally trained models
by computing the weighted average of model updates from
client devices. Consequently, it ensures the privacy of data
throughout the aggregation process. Clients in this system train
local models to detect adversarial behaviors by minimizing a
local loss function Li as given in equation (18):


L ŷi , y

Li =

Individual vs global accuracy epoch curves for 3 edge nodes.

IV. R ESULTS AND D ISCUSSIONS
A. Performance Indicators

(18)

x∈Di

Afterward, QKD is used for secure communication, and
encrypted model updates are merged into a global model
Mg safely and privately. The global approach benefits from
the diverse and secure contributions made by several clients,
which improves the detection of malicious attacks.

I. Adversarial Attack Detection
The global model Mg is used to identify adversarial attacks
by comparing its predictions to existing intrusion patterns. The
detection function ŷi is determined for a given input x using
the following computation in equation (19):
ŷi = f (Mi , x)

Fig. 7.

(19)

The prediction results for the i-th input, denoted as ŷi , are
obtained by applying the model function f to the model Mi
and the input data x, where ŷi stores the complete output
of this prediction. By incorporating the knowledge of all
participating clients, the global model enhances its ability to
identify adversarial activities on edge devices and increases its
resilience to a variety of attack strategies.
The use of quantum-based cryptography provides an extra
layer of protection, making the system resilient to eavesdropping and adversarial attacks. The proposed method improves
adversarial attack detection by combining QKD, QCKA,
and AHE, ensuring secure communication and privacy as
shown in Algorithm 1. Clients use their datasets to train local
models and then send encrypted updates to the server after
encrypting the model weights with AHE. The server uses the
common QCKA key to decrypt and aggregate the local models
received from various clients. After comparing predictions
to observed intrusion patterns, the final model is used to
detect adversarial attacks. This approach ensures secure data
transmission, privacy-preserving FL, and effective adversarial
threat detection.

We selected various network traffic-based images and
several edge nodes to evaluate the proposed method comprehensively. The proposed method is evaluated using
two publicly available standard datasets, Edge-IIoT, and
CICIoMT2024. We measured performance using precision,
recall, FL-score, and accuracy. These metrics are calculated
from True Positives (TP), False Positives (FP), True Negatives
(TN), and False Negatives (FN) counts. The performance
measures are provided by Equations (20)-(23).
TP
.
(TP + FP)
FP
Recall =
.
(FP + TN)
(2 ∗ TP)
FL − score =
.
(2TP + FP + FN)
(TP + TN)
Accuracy =
.
(TP + TN + FP + FN)
Precision =

(20)
(21)
(22)
(23)

B. Performance Analysis and Comparisons
The proposed approach is tested across a variety of edge
node variants to demonstrate its effectiveness. Figure 7 shows
the dynamic epoch curves for each node and the global server
with three edge nodes. Nodes 2 and 3 start at 82%, the node
1 at 91%, and the global server at 86%. The curves have
an increasing trend and 99% accuracy up to the fifth epoch,
after which they decrease to 95% and then grow again. The
global curve exhibits the same continuous and normal behavior
as the epoch curves of the other nodes. Figure 8 shows
the dynamic loss values for three edge nodes. These values
are behaving oppositely, as illustrated in Figure 7, which
illustrates the consistent efficacy of the proposed approach.
Figure 9 shows the dynamic accuracy curves for five edge
nodes. The model may have initially struggled to identify the
optimal parameters when it examined various parts of the loss,
which could explain the large decline in accuracy between
epochs 10 and 20. However, as training progresses and the
model stabilizes, it begins to generalize more well, resulting
in the observed increase in accuracy, which eventually reaches

ULLAH et al.: Q-P2FL: QUANTUM-ENHANCED FEDERATED EDGE INTELLIGENCE

4921

TABLE I
P ERFORMANCE C OMPARISON FOR A DVERSARIAL ATTACK D ETECTION
U SING E DGE II OT DATASET

TABLE II
P ERFORMANCE C OMPARISON FOR A DVERSARIAL ATTACK D ETECTION
U SING CICI O MT2024 DATASET
Fig. 8.

Individual vs global loss epoch curves for 3 edge nodes.

Fig. 9.

Individual vs global accuracy epoch curves for 5 edge nodes.

Fig. 10.

Individual vs global loss epoch curves for 5 edge nodes.

99.60%. Similarly, Figure 10 depicts the loss values for 5 edge
nodes that behave inversely to the values shown in Figure 9.
Table I compares the performance of adversarial attack
detection using the EdgeIIoT dataset. Four adversarial
approaches are used: FGSM, IGSM, PGD, and a hybrid
of IGSM and PGD. The precision, recall, FL-score, and
accuracy performance indicators are utilized to assess the
effectiveness of the proposed approach. The FGSM has the
lowest performance because of its straightforward properties.
The hybrid method provides its highest performance, with
precision, recall, FL-score, and accuracy of 99.82%, 99.64%,
and 99.15% for the benign class, and 99.06%, 99.46%,
and 99.28% for the attack class, respectively. Overall, the
accuracy is 99.38%. Table II compares the performance of
the same indicators using the CICIoMT2024 dataset. It can

be seen that the hybrid approach is stronger and has higher
performance metrics than individual methods such as FGSM,
IGSM, and PGD.
Table III demonstrates the results of comparing the PGD
and Hybrid techniques to classify adversarial attacks on the
EdgeIIoT dataset. We have shown only these two techniques
as they deliver the highest classification results. The PGD
technique performs somewhat worse for MITM and SQL
Injection attacks, but it achieves good precision and recall for
DDoS UDP Flood (98.89% and 98.77%) and Vulnerability
Scanner (99.12% and 99.34%). In comparison, the Hybrid
approach regularly beats PGD, with an accuracy of more than
96% for the majority of attack types. The results include a
100% recall for DDoS UDP Flood and a strong FL-score for
Ransomware (98.88%) and XSS (99.32%). The hybrid model
effectively detects adversarial attacks, despite significantly
weaker performance on MITM and Password attacks. Table IV
compares FGSM, IGSM, PGD, and Hybrid approaches for
DDoS, DoS, MQTT, Recon, and Spoofing adversarial attack
classification using the CICIoMT2024 dataset. FGSM is quite
effective for spoofing (98.87% precision, 99.24% FL-score)
and recon (96.09% FL-score), but less effective for DDoS
and MQTT. IGSM maintains good performance for recon
and spoofing while improving on MQTT (94.1% FL-score),
however, it performs moderately for DDoS. PGD exhibits
exceptional performance, particularly in the areas of DoS
(96.96% FL-score) and Spoofing (99.77% precision). The
Hybrid approach outperforms all others, receiving the highest
scores across most attack types, including notable findings
for Spoofing (99.52% FL-score) and MQTT (97.89% FLscore), demonstrating greater reliability in adversarial attack
detection.
Table V displays the classification accuracy of Edge-IIoTset
and CICIoMT 2024 datasets with varying edge nodes. The
findings suggest that adding edge nodes consistently increases
accuracy. In the Edge-IIoTset, accuracy rises from 92.46%

4922

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 2, MAY 2025

TABLE III
P ERFORMANCE C OMPARISON FOR A DVERSARIAL ATTACK C LASSIFICATION U SING E DGE II OT DATASET

TABLE IV
P ERFORMANCE C OMPARISON FOR A DVERSARIAL ATTACK
C LASSIFICATION U SING CICI O MT2024 DATASET

TABLE V
C OMPARISON OF C LASSIFICATION ACCURACY U SING VARIOUS
N UMBERS OF E DGE N ODES

with two nodes to 99.38% with twelve nodes. Similarly,
CICIoMT 2024 increases from 90.81% with 2 nodes to
99.41% with 12 nodes. FL performs better with more
clients because it provides a more diverse and representative dataset, improving generalization. It also improves the
model’s robustness by reducing overfitting to individual client
data. Furthermore, parallel client training speeds up learning,
improving the model. Figure 11 shows the confusion matrix
for intrusion detection using an EdgeIIoT dataset. The attack
class has 99.2% detection accuracy, while benign has 99.6%.
Figure 12 shows the confusion matrix for intrusion detection
using the CICIoMT2024 dataset. The attack is classified as
99.3%, while the benign is classified as 99.9%.

Table VI shows the performance comparison of
the proposed work with the related published works.
Ullah et al. [24] used CNN-based FL for intrusion detection
on edge devices. Further, it addressed the issue of intermittent
client behavior and class imbalance. The proposed approach
is tested on two datasets and provides 99.28% classification
accuracy. Idrissi et al. [33] introduced Fed-ANIDS, a network
intrusion detection system that uses anomaly detection and FL
to overcome privacy problems in centralized architectures. The
Fed-ANIDS model achieved 94.48% classification accuracy
across prominent datasets such as USTC-TFC2016, CICIDS2017, and CSE-CIC-IDS2018. Thein et al. [34] introduced
Personalized Federated Learning for Intrusion Detection
Systems (pFL-IDS), a resilient method that integrates a
poisoned client detector to reduce poisoning attacks while
tackling the diversity of IoT data. The proposed approach
provides 99.04% accuracy. Chen et al. [35] created VAN-IDS,
a hybrid model that uses Bi-LSTM for packet analysis and
LGBM for vehicle attributes to detect DoS and Sybil attacks
with 98.5% accuracy. FL-based VAN-FED-IDS aggregates
collaborative detection models using cloud services and

ULLAH et al.: Q-P2FL: QUANTUM-ENHANCED FEDERATED EDGE INTELLIGENCE

Fig. 11.

Confusion Matrix using EdgeIIoT dataset.

4923

edge devices while ensuring adequate security and privacy. Combining AHE with quantum-based registration and
authentication protects user privacy and model weights. Four
perturbation techniques are employed to generate adversarial instances to test the resilience of the dataset, and the
image-based properties of network traffic bytes are utilized
for developing unique datasets. We used a pre-trained ViT
to extract features and generate local model weights to
detect adversarial attacks. The proposed method achieved
99.38% and 99.41% detection accuracies on the Edge-IIoT
and CICIoMT2024 datasets, demonstrating its potential as
a privacy-preserving solution for protecting consumer edge
devices in smart environments. Despite its excellent detection
accuracy, the proposed method may need optimization for
large-scale, heterogeneous edge scenarios. The computational
costs of quantum authentication and homomorphic encryption
may affect real-time performance. Adaptive defenses and
hybrid approaches such as blockchain-quantum technologies
may improve its robustness and functionality in intelligent
environments. Future research can improve the scalability,
efficacy, and feasibility of Q-P2FL in smart environments.
Furthermore, future work may focus on novel adversarial
strategies, testing on a wide range of datasets and real-world
settings, and optimizing computational efficiency.
R EFERENCES

Fig. 12.

Confusion Matrix using CICIoMT2024 dataset.

TABLE VI
P ERFORMANCE C OMPARISON W ITH R ELATED P UBLISHED W ORKS

manages local training through roadside units to improve
privacy and training speed.
V. C ONCLUSION
This study presents a Q-P2FL technique to mitigate
the increasing threat of adversarial attacks on consumer

[1] X. Chen, P. Wang, Y. Yang, and M. Liu, “Resource-constraint deep
forest-based intrusion detection method in Internet of Things for
consumer electronic,” IEEE Trans. Consum. Electron., vol. 70, no. 2,
pp. 4976–4987, May 2024.
[2] D. Namakshenas, A. Yazdinejad, A. Dehghantanha, and G. Srivastava,
“Federated quantum-based privacy-preserving threat detection model for
consumer Internet of Things,” IEEE Trans. Consum. Electron., vol. 70,
no. 3, pp. 5829–5838, Aug. 2024.
[3] A. Libri, A. Bartolini, and L. Benini, “pAElla: Edge AI-based realtime malware detection in data centers,” IEEE Internet Things J., vol. 7,
no. 10, pp. 9589–9599, Oct. 2020.
[4] W. Yamany, M. Keshk, N. Moustafa, and B. Turnbull, “Swarm
optimization-based federated learning for the cyber resilience of Internet
of Things systems against adversarial attacks,” IEEE Trans. Consum.
Electron., vol. 70, no. 1, pp. 1359–1369, Feb. 2024.
[5] L. Malina et al., “Post-quantum era privacy protection for intelligent
infrastructures,” IEEE Access, vol. 9, pp. 36038–36077, 2021.
[6] M. Al-Hawawreh and M. S. Hossain, “A privacy-aware framework for
detecting cyber attacks on Internet of Medical Things systems using
data fusion and quantum deep learning,” Inf. Fusion, vol. 99, Nov. 2023,
Art. no. 101889.
[7] H. Kadry, A. Farouk, E. A. Zanaty, and O. Reyad, “Intrusion detection model using optimized quantum neural network and elliptical
curve cryptography for data security,” Alexandria Eng. J., vol. 71,
pp. 491–500, May 2023.
[8] Z. A. E. Houda, H. Moudoud, B. Brik, and M. Adil, “A privacypreserving framework for efficient network intrusion detection in
consumer network using quantum federated learning,” IEEE Trans.
Consum. Electron., vol. 70, no. 4, pp. 7121–7128, Nov. 2024.
[9] O. A. Alzubi, J. A. Alzubi, T. M. Alzubi, and A. Singh, “Quantum
mayfly optimization with encoder-decoder driven LSTM networks for
malware detection and classification model,” Mobile Netw. Appl., vol. 28,
no. 2, pp. 795–807, 2023.
[10] M. Al-Hawawreh, O. Shindi, Z. Baig, M. Alazab, A. Anwar, and
R. Doss, “Quantum-powered extended visibility for zero trust-based
ransomware detection in smart grids,” IEEE Internet Things J., vol. 12,
no. 6, pp. 6721–6733, Mar. 2025.
[11] C. Qiao, M. Li, Y. Liu, and Z. Tian, “Transitioning from federated
learning to quantum federated learning in Internet of Things: A comprehensive survey,” IEEE Commun. Surveys Tuts., vol. 27, no. 1, pp.
509–545, Feb. 2025.

4924

[12] A. Khraisat, A. Alazab, S. Singh, T. Jan, and A. Jr. Gomez, “Survey on
federated learning for intrusion detection system: Concept, architectures,
aggregation strategies, challenges, and future directions,” ACM Comput.
Surveys, vol. 57, no. 1, pp. 1–38, 2024.
[13] K. He, D. D. Kim, and M. R. Asghar, “Adversarial machine learning for
network intrusion detection systems: A comprehensive survey,” IEEE
Commun. Surveys Tuts., vol. 25, no. 1, pp. 538–566, 1st Quart., 2023.
[14] H. Qiu, T. Dong, T. Zhang, J. Lu, G. Memmi, and M. Qiu, “Adversarial
attacks against network intrusion detection in IoT systems,” IEEE
Internet Things J., vol. 8, no. 13, pp. 10327–10335, Jul. 2021.
[15] M. Pawlicki, M. Choraś, and R. Kozik, “Defending network intrusion
detection systems against adversarial evasion attacks,” Future Gener.
Comput. Syst., vol. 110, pp. 148–154, Sep. 2020.
[16] O. Ibitoye, O. Shafiq, and A. Matrawy, “Analyzing adversarial attacks
against deep learning for intrusion detection in IoT networks,” in Proc.
IEEE Global Commun. Conf. (GLOBECOM), 2019, pp. 1–6.
[17] J. Chen, Y. Zhao, Q. Li, X. Feng, and K. Xu, “FedDef: Defense against
gradient leakage in federated learning-based network intrusion detection
systems,” IEEE Trans. Inf. Forensics Security, vol. 18, pp. 4561–4576,
2023.
[18] O. Friha, M. A. Ferrag, M. Benbouzid, T. Berghout, B. Kantarci,
and K.-K. R. Choo, “2DF-IDS: Decentralized and differentially private
federated learning-based intrusion detection system for Industrial IoT,”
Comput. Security, vol. 127, Apr. 2023, Art. no. 103097.
[19] W. Yamany, N. Moustafa, and B. Turnbull, “OQFL: An optimized
quantum-based federated learning framework for defending against
adversarial attacks in intelligent transportation systems,” IEEE Trans.
Intell. Transp. Syst., vol. 24, no. 1, pp. 893–903, Jan. 2023.
[20] M. A. Ferrag, O. Friha, D. Hamouda, L. Maglaras, and H. Janicke,
“Edge-IIoTset: A new comprehensive realistic cyber security dataset of
IoT and IIoT applications for centralized and federated learning,” IEEE
Access, vol. 10, pp. 40281–40306, 2022.
[21] S. Dadkhah, E. C. P. Neto, R. Ferreira, R. C. Molokwu, S. Sadeghi,
and A. Ghorbani, “CiCioMT2024: Attack vectors in healthcare devicesa multi-protocol dataset for assessing IoMT device security,” Internet
Things, vol. 28, Dec. 2024, Art. no. 101351.
[22] J. Ghadermazi, A. Shah, and N. D. Bastian, “Towards real-time network
intrusion detection with image-based sequential packets representation,”
IEEE Trans. Big Data, vol. 11, no. 1, pp. 157–173, Feb. 2025.

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 2, MAY 2025

[23] S. Hore, J. Ghadermazi, A. Shah, and N. D. Bastian, “A sequential deep
learning framework for a robust and resilient network intrusion detection
system,” Comput. Security, vol. 144, Sep. 2024, Art. no. 103928.
[24] F. Ullah, G. Srivastava, S. Ullah, and L. Mostarda, “Privacy-preserving
federated learning approach for distributed malware attacks with
intermittent clients and image representation,” IEEE Trans. Consum.
Electron., vol. 70, no. 1, pp. 4585–4596, Feb. 2024.
[25] C. Dewi, R.-C. Chen, Y.-T. Liu, and S.-K. Tai, “Synthetic data generation
using DCGAN for improved traffic sign recognition,” Neural Comput.
Appl., vol. 34, no. 24, pp. 21465–21480, 2022.
[26] A. Srivastava, D. Sinha, and V. Kumar, “WCGAN-GP based synthetic
attack data generation with GA based feature selection for IDS,”
Comput. Security, vol. 134, Nov. 2023, Art. no. 103432.
[27] L. Sun et al., “Adversarial attack and defense on graph data: A
survey,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 8, pp. 7693–7711,
Aug. 2023.
[28] I. Rosenberg, A. Shabtai, Y. Elovici, and L. Rokach, “Adversarial
machine learning attacks and defense methods in the cyber security
domain,” ACM Comput. Surveys, vol. 54, no. 5, pp. 1–36, 2021.
[29] K. He, D. D. Kim, and M. R. Asghar, “NIDS-vis: Improving the generalized adversarial robustness of network intrusion detection system,”
Comput. Security, vol. 145, Oct. 2024, Art. no. 104028.
[30] X. Zhai, A. Kolesnikov, N. Houlsby, and L. Beyer, “Scaling vision
transformers,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.,
2022, pp. 12104–12113.
[31] J. Gu, V. Tresp, and Y. Qin, “Are vision transformers robust to patch
perturbations?” in Proc. Eur. Conf. Comput. Vis., 2022, pp. 404–421.
[32] K. Mahmood, R. Mahmood, and M. Van Dijk, “On the robustness of
vision transformers to adversarial examples,” in Proc. IEEE/CVF Int.
Conf. Comput. Vis., 2021, pp. 7838–7847.
[33] M. J. Idrissi et al., “Fed-Anids: Federated learning for anomaly-based
network intrusion detection systems,” Exp. Syst. Appl., vol. 234, Jun.
2023, Art. no. 121000.
[34] T. T. Thein, Y. Shiraishi, and M. Morii, “Personalized federated learningbased intrusion detection system: Poisoning attack and defense,” Future
Gener. Comput. Syst., vol. 153, pp. 182–192, Apr. 2024.
[35] X. Chen, W. Qiu, L. Chen, Y. Ma, and J. Ma, “Fast and practical
intrusion detection system based on federated learning for VANET,”
Comput. Security, vol. 142, Jul. 2024, Art. no. 103881.
PAPER_TEXT
