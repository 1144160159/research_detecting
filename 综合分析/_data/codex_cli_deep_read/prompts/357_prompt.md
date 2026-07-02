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
# [357] Advancing Intrusion Detection in V2X Networks: A Comprehensive Survey on Machine Learning, Federated Learning, and Edge AI for V2X Security
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
编号：357
题名：Advancing Intrusion Detection in V2X Networks: A Comprehensive Survey on Machine Learning, Federated Learning, and Edge AI for V2X Security
年份：2025
DOI：10.1109/tits.2025.3558849
来源：IEEE Transactions on Intelligent Transportation Systems
PDF：paper/10.1109_TITS.2025.3558849.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：数据集、基准、综述与开源工具、IoT、车联网、工业互联网与边缘安全
相关性：强相关，分数 13
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\357.txt
- 原始字符数：314922
- 本次发送字符数：140043
- 是否截断：True

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 8, AUGUST 2025

11137

Advancing Intrusion Detection in V2X Networks:
A Comprehensive Survey on Machine Learning,
Federated Learning, and Edge AI
for V2X Security
Shimaa A. Abdel Hakeem , Member, IEEE, and HyungWon Kim , Member, IEEE

Abstract— The security of Vehicle-to-Everything (V2X) networks is fundamental to the realization of next-generation
intelligent transportation systems. However, the dynamic nature
of V2X environments introduces critical challenges in ensuring
robust Intrusion Detection Systems (IDS), particularly concerning false alarm rates, adversarial attacks, computational
complexity, and real-world deployment constraints. Traditional
centralized machine learning-based IDS suffer from high computation costs, privacy risks, bandwidth constraints, and scalability
limitations, making them impractical for real-time, distributed
vehicular networks. To address these gaps, this paper provides
a comprehensive and structured survey of IDS methodologies
in V2X security, focusing on Federated Learning (FL) and
Edge AI for privacy-preserving and scalable IDS solutions.
Unlike prior works, we systematically analyze and benchmark
intrusion detection datasets, highlighting limitations in detecting
zero-day attacks and exploring the need for hybrid datasets
that integrate real-world vehicular data with adversarial attack
scenarios. Furthermore, we investigate the adversarial robustness of ML-based IDS, analyzing AI-based evasion techniques,
data poisoning threats, and misbehavior detection challenges.
A key novelty of this work lies in the detailed examination of
computational complexities in IDS deployment, including sensor
fusion methods, noise reduction techniques, and false alarm
mitigation strategies, which are often overlooked in previous
surveys. We also explore deep learning-based IDS, providing
a comparative evaluation of simulated versus real-world performance. Additionally, we present an in-depth discussion on
post-quantum cryptographic techniques and blockchain integraReceived 30 November 2024; revised 26 February 2025; accepted 2 April
2025. Date of publication 23 May 2025; date of current version 6 August
2025. This work was supported in part by the National Research Foundation
of Korea (NRF) Grant funded by Korea Government (MSIT) under Grant
2022R1A5A8026986; in part by the Innovative Human Resource Development
for Local Intellectualization Program through the Institute of Information and
Communications Technology Planning and Evaluation (IITP) Grant funded by
Korea Government (MSIT) under Grant IITP-2025-II201462 (33%); in part
by Korea Technology and Information Promotion Agency for SMEs (TIPA),
funded by the Korean Government (Ministry of SMEs and Startups) under the
Smart Manufacturing Innovation Research and Development Program under
Grant RS-2024-00434259; and in part by Chungbuk National University Brain
Korea 21 Program in 2023. The Associate Editor for this article was S. Garg.
(Corresponding author: HyungWon Kim.)
Shimaa A. Abdel Hakeem is with the Department of Electronics Engineering, College of Electrical and Computer Engineering, Chungbuk National
University, Cheongju 28644, South Korea, and also with the Computers and
Systems Department, Electronics Research Institute, Giza 12622, Egypt.
HyungWon Kim is with the School of Electronics Engineering, Chungbuk National University, Cheongju 28644, South Korea (e-mail: hwkim@
chungbuk.ac.kr).
Digital Object Identifier 10.1109/TITS.2025.3558849

tion for enhancing security in Federated Learning-based IDS.
This survey bridges the gap between theoretical IDS models
and real-world V2X deployment, addressing key constraints such
as energy efficiency, communication overhead, and scalability in
resource-constrained vehicular networks. By studying the stateof-the-art methodologies, identifying critical research gaps, and
proposing practical advancements, this paper serves as a definitive resource for researchers,and industry professionals, guiding
the development of robust, adaptive, and privacy-preserving IDS
solutions for next-generation autonomous and connected vehicles
(CAVs).
Index Terms— V2X security, intrusion detection systems
(IDS), machine learning, federated learning (FL), edge AI,
false alarm reduction, adversarial threats, distributed sensor
fusion, blockchain, post-quantum cryptography, hybrid IDS,
autonomous vehicles, 5G/6G security.

I. I NTRODUCTION
EHICLE-TO-EVERYTHING (V2X) networks facilitate
seamless communication among vehicles, infrastructure,
and pedestrians, forming the backbone of intelligent transportation systems and the autonomous vehicle industry. These
networks are essential for enhancing road safety, optimizing
traffic management, and improving overall driving efficiency.
However, securing V2X networks remains a formidable challenge due to their highly dynamic nature, decentralized
architecture, and stringent real-time requirements. Effective
security mechanisms are critical to ensuring message integrity,
identity authentication, network availability, and protection
against unauthorized access, all while preserving user privacy
[1], [2], [3].
Intrusion Detection Systems (IDS) play a pivotal role in
safeguarding V2X communication by continuously monitoring
network traffic to identify and mitigate security threats [4],
[5], [6]. Traditional IDS approaches, while effective in conventional network environments, face significant limitations
when applied to V2X networks due to the high mobility of
vehicles, low-latency communication demands, and the complexity of distributed attack surfaces. Therefore, the adoption
of advanced AI and Machine Learning (ML)-based IDS has
become increasingly crucial in V2X security research [7], [8].
Recent advancements in ML and Artificial Intelligence
(AI) have significantly improved the ability to detect and
respond to security threats in V2X networks. ML-based IDS

V

1558-0016 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

11138

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 8, AUGUST 2025

enhance intrusion detection through anomaly detection, predictive analytics, automated response mechanisms, real-time
traffic monitoring, and behavioral analysis. By learning normal
communication patterns, ML models can identify deviations
indicative of cyber threats, enabling proactive detection and
mitigation. ML techniques such as Support Vector Machines
(SVM), Artificial Neural Networks (ANN), Deep Learning
models, and Federated Learning (FL) have demonstrated
promising results in enhancing the robustness of V2X IDS [9].
The increasing complexity and scale of V2X networks
necessitate AI/ML-based IDS due to several reasons:
• Scalability and Adaptability: ML models can handle
vast amounts of real-time vehicular data and adapt to
dynamic network conditions more efficiently than traditional rule-based detection mechanisms [10].
• Early Threat Detection: ML-based IDS enables proactive identification of security threats by learning from
historical attack patterns and detecting anomalies in
vehicular communication.
• Automated Threat Mitigation: AI/ML models can automatically classify and respond to cyber threats, reducing
response time and minimizing network disruptions.
• Handling Encrypted Traffic: Unlike signature-based
IDS, ML-based approaches can detect malicious activities
in encrypted network traffic without requiring payload
inspection.
• Federated Learning and Privacy Preservation: Federated Learning (FL) allows decentralized training of IDS
models across multiple vehicles while preserving data
privacy, making it an essential technique for V2X security
[11], [12], [13].
A. Research Methodology and Objectives of This Survey
In this survey, we present a comprehensive and systematic study on intrusion and misbehavior detection in V2X
networks, focusing on AI/ML-based security solutions. Our
methodology ensures a structured, objective-based approach to
gathering and analyzing state-of-the-art research in this field.
This section elaborates on our research objectives, methodology, dataset analysis, and comparative evaluation to ensure
clarity and reproducibility.
1) Research Objectives: This study aims to analyze, evaluate, and compare machine learning (ML)-based Intrusion
Detection Systems (IDS) and Misbehavior Detection Systems
(MDS) in V2X networks. The key objectives of this survey
include:
• Comprehensive Investigation of V2X Security Threats
– Examine traditional and adversarial attacks in V2X
networks.
– Identify unique cybersecurity challenges in connected and autonomous vehicles (CAVs).
– Explore emerging attack vectors in 5G-V2X and
Beyond (6G-V2X).
• Survey and Categorization of AI/ML-Based Intrusion
Detection Approaches
– Analyze conventional machine learning models (e.g.,
SVM, RF, MLP, CNN, and LSTM) used in V2X
IDS/MDS.

– Investigate the effectiveness of deep learning models
for anomaly detection in vehicular networks.
– Identify the role of generative models such as GANs,
BiGANs, and Variational Autoencoders (VAEs) in
detecting zero-day attacks.
• Study the Impact of Federated Learning (FL) and
Edge AI in V2X Security
– Discuss how privacy-preserving techniques such as
federated learning enhance IDS deployment.
– Evaluate the trade-offs between centralized, distributed, and edge-based IDS architectures.
– Explore real-world feasibility of FL-based security
models for autonomous vehicles and IoV (Internet
of Vehicles).
• Dataset Evaluation and Comparative Analysis
– Identify and compare benchmark datasets used for
V2X security research.
– Analyze attack diversity, real-world applicability, and
dataset attributes.
– Study how synthetic vs. real-world datasets impact
model generalizability.
• Identify Challenges in Real-World Deployment of AIBased IDS
– Investigate the computational complexity of ML
models for large-scale V2X IDS deployment.
– Address challenges in sensor fusion, redundant
observer-based IDS, and edge-device resource constraints.
– Evaluate how network latency, communication overhead, and adversarial perturbations affect model
performance.
• Propose Future Directions for Secure V2X Communications
– Provide recommendations for hybrid approaches
(e.g., AI + blockchain for enhanced security).
– Suggest standardized datasets and evaluation benchmarks for future research.
– Explore the role of quantum cryptography, homomorphic encryption, and explainable AI (XAI) in V2X
cybersecurity.
2) Research Methodology: To achieve the above objectives,
we conducted a structured multi-phase research methodology
consisting of:
3) Systematic Literature Review (SLR) Approach: We followed a structured literature review methodology, ensuring
thorough and unbiased coverage of existing research.
Data Sources:
• We retrieved research papers from Google Scholar,
Scopus, IEEE Xplore, SpringerLink, and ACM Digital
Library.
• Our search focused on high-impact journals, conferences,
and preprint servers (e.g., arXiv, Springer, Elsevier, Wiley,
MDPI).
Keyword-Based Search Strategy:
• We used a combination of keywords and Boolean operators to ensure a broad yet focused search:
– (“Machine Learning” OR “Deep Learning”) AND
(“Intrusion Detection” OR “Misbehavior Detection”)
AND (“V2X Security” OR “Connected Vehicles”).

HAKEEM AND KIM: ADVANCING INTRUSION DETECTION IN V2X NETWORKS: A COMPREHENSIVE SURVEY

Paper Selection Process:
1) Initial Screening → Collected 300+ research papers
related to V2X security & AI-based IDS/MDS.
2) Relevance Filtering → Focused on papers specifically
addressing AI/ML techniques for V2X IDS.
3) Full-Text Analysis → Analyzed methodologies,
datasets, and findings of top 150 relevant studies.
4) Categorization & Comparison → Organized papers
into attack detection techniques, dataset studies, and IDS
deployment challenges.
Benchmark Surveys Considered:
• We compared our survey against existing benchmark
studies and identified research gaps.
• Our survey differentiates itself by including federated
learning, adversarial attack studies, dataset comparisons,
and real-world deployment challenges.
4) Comparative Analysis of V2X Datasets: A major component of our methodology was the detailed evaluation of
existing V2X security datasets.
Dataset Selection Criteria:
• We selected benchmark datasets based on the following
criteria:
– Attack coverage (e.g., DDoS, DoS, Man-in-theMiddle, Spoofing, Replay, Adversarial Attacks).
– Real-world applicability (i.e., collected from real
vehicles vs. simulated environments).
– Feature representation (i.e., CAN traffic, GPS, timestamps, sensor fusion).
– Suitability for ML training (i.e., balanced vs. imbalanced classes, labeled vs. unlabeled data).
Key Datasets Evaluated:
• CICIDS 2017, TON_IoT, Car-Hacking Datasets, VeReMi,
SYNDoS, NSL-KDD, KDD’99, UNSW-NB15, and custom V2X datasets.
• We compared datasets in terms of attack diversity, real
vs. synthetic traffic, and feature granularity.
Findings and Limitations:
• Many datasets lack real-world vehicular attack data,
limiting their applicability to V2X-specific security challenges.
• Zero-day attacks are poorly represented, necessitating
generative approaches (GANs) for synthetic attack generation.
• High imbalance in intrusion datasets leads to bias in ML
model predictions, requiring SMOTE-based oversampling
techniques.
5) Experimental Considerations for AI-Based IDS: To
ensure real-world applicability, we evaluated:
• Computational Complexity of AI models for real-time
V2X IDS deployment.
• Trade-offs between centralized vs. federated IDS architectures for connected vehicles.
Performance Metrics for IDS Evaluation:
• Detection Rate, False Alarm Rate (FAR), Accuracy,
F1-score, Precision, Recall, AUC-ROC, Latency, and
Communication Overhead.
Comparison of AI Models in Terms of:
• Lightweight models for resource-constrained vehicles.

•
•

11139

Scalability of IDS models in large V2X environments.
Integration of IDS with SDN, blockchain, and cloud
computing.

B. Identification of Research Gaps
Despite significant progress in AI/ML-based IDS for V2X
security, existing survey studies exhibit several limitations that
hinder their applicability in real-world deployment. Through
an in-depth review of prior surveys, the following critical
research gaps have been identified:
• Real-World Deployment Challenges: Existing surveys
focus on theoretical ML models, overlooking constraints
like computing resources, energy efficiency, and network
latency in V2X environments.
• Insufficient IDS Dataset Benchmarking: Many studies
fail to compare generalized IDS datasets with V2Xspecific ones in terms of attack coverage and real-world
applicability.
• Limited Discussion on Adversarial Attacks: The increasing sophistication of cyber threats, particularly AI-based
evasion techniques, remains underexplored in IDS
research.
• Federated Learning & Edge AI in V2X: Despite FL’s
potential for privacy-preserving IDS, existing studies lack
information on scalability, security risks, and feasibility
of deployment.
• IDS Deployment on Resource-Constrained Devices: Key
challenges like energy consumption, communication
overhead, and computational costs remain largely unaddressed.
• 5G/6G-V2X Security Analysis: There is a lack of dedicated surveys evaluating how next-generation networks
impact IDS performance and emerging security threats.
• Sensor Fusion & Computational Complexities:Prior work
overlooks issues like sensor noise, false alarms, and
computational overhead. We explore noise mitigation and
optimization strategies for real-world IDS deployment.
C. Enhancements and Novel Contributions
To strengthen the novelty and impact of this work,
we have significantly expanded the scope of our survey to
address the key research challenges identified above. The
following contributions distinguish this study from previous
surveys:
1) Evaluation of Real-World Deployment Challenges: We
analyze the practical challenges of deploying ML-based IDS
in resource-constrained V2X environments, considering:
• Computational limitations and energy consumption constraints that impact IDS feasibility in vehicular networks.
• Communication overhead and real-time performance
requirements, which are critical for deploying IDS
solutions in dynamic and bandwidth-sensitive V2X environments.
2) Comprehensive Dataset Benchmarking and Zero-Day
Attack Detection: Our survey systematically compares and
categorizes existing IDS datasets, distinguishing between generalized IDS datasets and V2X-specific datasets by:

11140

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 8, AUGUST 2025

Evaluating dataset attributes, attack coverage, and suitability for real-world deployment.
• Proposing hybrid dataset recommendations that integrate
real-world and synthetic adversarial attacks to improve
zero-day attack detection.
3) Modern Threats and Adversarial Attacks in V2X Security: our study significantly expands the discussion on
adversarial ML attacks that exploit vulnerabilities in AI-based
intrusion detection models. We examine:
• AI-powered evasion techniques, data poisoning, and
adaptive adversarial attacks targeting IDS.
• Defensive mechanisms such as adversarial training, robust
ML architectures, and differential privacy-based protection techniques to mitigate adversarial threats.
4) Federated Learning for Privacy-Preserving IDS:
• We study the impact of FL-based IDS on privacy,
decentralization, scalability, and real-world V2X implementation.
• We explore the Security risks in FL-based IDS, including
model inversion attacks, and gradient leakage, along with
defensive strategies.
5) Computational Complexity and Feasibility of IDS in
V2X:
• We provide a detailed analysis of the computational
overhead of ML-based IDS, focusing on: Real-time
processing constraints, energy efficiency, and network
latency issues.
6) Noise Reduction and False Alarm Rate Mitigation:
• We introduce Distributed Sensor Fusion Techniques for
improving signal quality and reducing IDS false alarms.
• We introduce a comparative analysis of feature engineering methods, denoising algorithms, and techniques for
enhancing detection accuracy.
7) Comparative Study of IDS Performance in Simulated Vs.
Real-World Environments:
• Evaluate the performance of CNNs for anomaly detection, LSTMs for sequential pattern recognition, GANs
for attack scenario generation, and Transformer-based
architectures for scalable intrusion detection.
• Conduct a comparative analysis of IDS performance in
simulation-based vs. real-world environments, identifying performance gaps, and proposing realistic validation
strategies.
8) Blockchain and Post-Quantum Security for Federated
Learning-Based IDS: To strengthen the security of FL-based
IDS, we introduce discussions on:
• We analyze blockchain-enhanced IDS frameworks to
ensure secure model aggregation and data integrity in FLbased V2X security architectures.
• We discuss quantum-safe encryption techniques such as
lattice-based cryptography, hash-based signatures, and
quantum-resistant key exchange protocols, bridging cryptographic advancements with vehicular cybersecurity.
By addressing these key challenges and expanding discussions on emerging security paradigms, we believe that our
work provides a comprehensive, high-impact contribution to
the intelligent transportation and vehicular security research
community.
•

Fig. 1.

Structure and organization of the paper.

D. Paper Structure and Organization
This paper provides a comprehensive survey on Intrusion
Detection Systems (IDS) in V2X networks, covering traditional and emerging security approaches, dataset limitations,
adversarial threats, and future research directions. The paper
is organized as follows:
Section I introduces the research problem, highlights gaps
in existing surveys, and presents the contributions of this
study. Section II reviews traditional misbehavior detection
techniques in V2X networks and their limitations, emphasizing
the need for machine learning-based IDS. Section III critically
examines existing machine learning-based IDS surveys for
V2X, discussing their limitations and identifying research
gaps. Section IV provides an overview of V2X communication
fundamentals, including its modes, components, and standard
protocols. Section V categorizes traditional attack models
in V2X networks and reviews existing mitigation strategies.
Section VI explores AI-based and adversarial attacks targeting V2X security, including simulation techniques and
countermeasures. Section VII presents a taxonomy of IDS
methods in V2X networks, classifying them based on detection
approaches, deployment strategies, and network architectures.
Section VIII provides an in-depth discussion of machine
learning-based IDS, categorizing various ML approaches such
as supervised, unsupervised, reinforcement, and deep learning
techniques. Section IX reviews publicly available datasets for
IDS in V2X, evaluating their limitations, and proposing recommendations for hybrid and more realistic datasets. Section X

HAKEEM AND KIM: ADVANCING INTRUSION DETECTION IN V2X NETWORKS: A COMPREHENSIVE SURVEY

11141

TABLE I
L IST OF ABBREVIATIONS

discusses the role of Federated Learning (FL) and Edge
AI in developing privacy-preserving and decentralized IDS
solutions for V2X networks. Section XI explores advanced
deep learning architectures, including LSTM and GAN-based
intrusion detection methods. Section XII addresses challenges in real-world deployment of ML-based IDS, focusing
on simulation-based validation and practical implementation
issues. Section XIII outlines future research directions, including blockchain-enhanced security, post-quantum cryptography,
and the integration of FL with 6G-V2X networks. Section XIV
concludes the paper by summarizing key findings and emphasizing the importance of privacy-preserving, scalable, and
adaptive IDS frameworks for V2X security.
Figure 1 illustrates the structure and organization of the
paper, providing a visual representation of the hierarchical flow
of sections and subsections. As shown in Table I, commonly
used abbreviations in V2X security research have been compiled based on previous studies.
II. T RADITIONAL M ISBEHAVIOR D ETECTION
A PPROACHES IN V2X N ETWORKS AND L IMITATIONS
Ensuring the reliability and security of data transmission
in Vehicle-to-Everything (V2X) communication systems is
paramount. Misbehavior detection plays a crucial role in
maintaining data accuracy, particularly in Basic Safety Messages (BSMs). Several studies have explored conventional

misbehavior detection techniques that do not rely on machine
learning algorithms.
A. Prior Detection Approaches
Various traditional approaches have been proposed to identify misbehavior in V2X networks without leveraging machine
learning techniques. These methods primarily rely on physical
layer plausibility checks, statistical analysis, and rule-based
anomaly detection.
So et al. [14] proposed a misbehavior detection technique utilizing the Received Signal Strength Indicator (RSSI)
for essential safety messages (BSMs). Their study introduced three plausibility tests at the physical layer: FirstBSM (FBSM), Majority-BSM (MBSM), and Weighted-BSM
(WBSM), achieving a precision of 95.91% and a detection
rate of 83.73% when tested on the upgraded VeReMi dataset.
This work demonstrated that physical layer approaches outperform application layer plausibility checks in identifying V2X
misbehavior.
Bißmeyer et al. [15] suggested a scalable centralized misbehavior detection system that enables any node to report
an event while a central authority makes the final decision. However, a critical limitation of this approach is its
reliance on the assumption that most network nodes behave
honestly.

11142

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 8, AUGUST 2025

Sun et al. [16] introduced a technique that employs Doppler
speed and the angle of arrival to Explain trustworthiness.
This method utilizes chi-squared tests and Kalman filtering to
evaluate the reliability of other vehicles by comparing them
with a highly trustworthy node within a defined perimeter.
However, its effectiveness is reduced in scenarios involving
slow-moving traffic, where distinguishing between misbehavior and legitimate variations becomes challenging.
Yao et al. [17] proposed a technique to detect Sybil attacks
based on the statistical properties of RSSI measurements.
Vehicles with similar RSSI readings are grouped as potential
Sybil attackers, suggesting that they originate from the same
source. However, this method struggles against adversaries
generating ghost vehicles at different locations.
Chen et al. [18] demonstrated the vulnerability of Intelligent Signalized Intersection (I-SIG) systems by showing how
attackers can create traffic congestion using spoofed BSM
payloads to manipulate traffic control signals. Their study
highlights the weaknesses of application-layer plausibility
checks.
Several studies have explored authentication and intrusion
detection mechanisms for vehicular networks. Zhang and
Zhu [19] proposed a distributed privacy-preserving intrusion
detection system for Vehicular Ad-hoc Networks (VANETs).
Mahmood et al. [20] addressed security concerns in VANET
systems, while Irshad et al. [21] introduced a security key
authentication framework to enhance vehicular access control.
Faisal andZaidi [22] designed a detection system for
Sybil attacks based on geographical coordinate verification. Similarly, Mahmood et al. [23] developed an anonymous
identity-based key agreement protocol aimed at improving
security in smart grid-integrated vehicular systems.
Mirsky et al. [24] introduced an autoencoder-based anomaly
detection framework utilizing an ensemble structural algorithm
to identify unauthorized users. Sharma et al. [25] proposed a
certificateless authentication mechanism for V2X communication, reinforcing data integrity and confidentiality.
Additional approaches include Nayyar et al.’s [26]
hybrid data model for intrusion detection in VANETs and
Naqvi et al.’s [27] intrusion detection system (IDS) designed
to counteract malicious vehicle behavior. Yao et al. [28] presented a geographic-based Sybil attack detection method,
while Firl et al. [29] introduced MARV-X, a framework for
validating vehicle maneuvers. However, its efficacy depends
on the assumption that surrounding vehicles cooperate, making
it vulnerable to adversarial scenarios.
Other studies, such as Guo et al. [30] and [31], proposed
sensor-based anomaly detection approaches. However, these
methods heavily rely on sensor data consistency, making
them susceptible to data manipulation and Sybil attacks [32].
Several cooperative misbehavior detection models assume
an honest majority [33], rendering them ineffective against
collusion attacks. Abdelaziz et al. [34] introduced a signal
arrival angle-based authentication mechanism, but this technique remains vulnerable to position-offset attacks.
Nguyen et al. [35] devised a signal-based relative positioning approach to verify the authenticity of V2V shared

data. Naserian and Lewis [36] suggested a frequency-based
mechanism that detects misbehavior by analyzing changes
in message transmission frequencies, leveraging the Doppler
effect.
B. Why We Need Machine Learning-Based Intrusion
Detection Systems in V2X
Despite their foundational contributions, traditional misbehavior detection approaches face significant limitations in
real-world V2X deployments:
• Dependence on Ideal Cooperation: Methods such as
MARV-X [29] assume that surrounding vehicles will
cooperate, making them vulnerable to adversarial behaviors.
• Susceptibility to Data Manipulation: Techniques relying on sensor consistency [30], [31] are prone to
attacks that manipulate sensor inputs, particularly Sybil
attacks [32].
• Honest Majority Assumption: Several cooperative misbehavior detection approaches [33] assume that most
vehicles are honest, making them ineffective against
collusion attacks.
• Practical Vulnerabilities: Signal arrival angle-based
authentication mechanisms [34] can be compromised by
adversarial position manipulation.
• Limited Scope of Verification: Some techniques, such as
the signal-based positioning approach, focus on specific
attacks, limiting their ability to detect a wide range of
misbehaviors.
• Dependence on External Inputs: Frequency-based misbehavior detection methods require accurate environmental data, reducing their effectiveness in non-line-of-sight
(NLOS) scenarios.
• High False Positive Rates: Many traditional methods
generate excessive false positives, leading to unnecessary
alerts and decreased trust in the system.
• Scalability Challenges: As V2X networks grow, conventional detection methods struggle to scale efficiently due
to high computational and communication overhead.
• Inability to Adapt to Evolving Threats: Rule-based
approaches lack the flexibility to detect emerging cyber
threats, as attackers continuously refine their techniques.
The heterogeneous nature of V2X communication introduces additional security challenges, as different wireless
communication technologies, such as Dedicated Short-Range
Communications (DSRC) and 5G-V2X, operate under distinct protocols, requiring adaptable intrusion detection systems
(IDS) to ensure cross-technology security. These challenges
are illustrated in Figure 2. Furthermore, inconsistencies in
traditional misbehavior detection systems create gaps in scalability, accuracy, and real-time threat response, as shown in
Figure 3. This survey addresses these gaps by systematically
analyzing ML methodologies, evaluating benchmark datasets,
and exploring real-world applicability, ensuring a structured
and up-to-date reference for securing next-generation V2X
networks.

HAKEEM AND KIM: ADVANCING INTRUSION DETECTION IN V2X NETWORKS: A COMPREHENSIVE SURVEY

Fig. 2.

11143

Inconsistent security in V2X communication due to different wireless communications.

contributions and limitations, while distinguishing our work
from prior efforts.
A. Existing Machine Learning Based IDS Surveys

Fig. 3. Limitations of traditional misbehavior detection systems in V2X
networks.

III. C RITICAL R EVIEW OF E XISTING M ACHINE
L EARNING -BASED IDS S URVEYS FOR V2X: L IMITATIONS
AND R ESEARCH G APS
ML has emerged as a powerful tool for addressing complex challenges across various domains, including vehicular
networks. The wireless communication between vehicles and
infrastructure exposes these networks to potential security
threats, making ML an increasingly vital resource for identifying and mitigating risks in vehicle-to-everything (V2X)
communication systems. This section provides an overview
of existing surveys in the literature, highlighting their

We conducted a thorough review of relevant survey studies, focusing on their exploration of security issues and the
application of ML techniques in vehicular networks. Below,
we summarize key findings from these studies and outline how
our work diverges from theirs. Talpur et al. [37] conducted a
comprehensive survey on the intersection of ML and vehicular networks, emphasizing security challenges and advanced
ML-based solutions. While their work provides a detailed
classification of security attacks and reviews ML techniques,
it acknowledges limitations in privacy, trust, and scalability
when implementing ML in vehicular networks. Our survey
builds on this foundation by addressing these limitations
and offering a more focused analysis of ML methodologies
for V2X security. Sun et al. [38] explored cybersecurity in
Connected and Autonomous Vehicles (CAVs), categorizing
attacks into in-vehicle controller attacks, V2X attacks, and
miscellaneous threats. Although their survey examines defense
strategies and cybersecurity standards, it does not discuss the
use of ML for security solutions. Our work fills this gap
by providing a detailed analysis of ML-based approaches for
securing V2X networks.
Dibaei et al. [39] investigated attacks and defenses in intelligent connected vehicles, classifying threats into in-vehicle
and V2X communication attacks. While they discuss cryptographic techniques and network security measures, their study
lacks a thorough evaluation of relevant datasets and real-time
performance metrics. Our survey addresses these shortcomings
by incorporating diverse benchmark datasets and discussing
practical implementation challenges.
Ying et al. [40] provided a comprehensive overview of V2X
communication security, focusing on historical developments
and prevalent risks. However, their survey does not thoroughly

11144

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 8, AUGUST 2025

explore AI/ML-powered intrusion detection mechanisms or
evaluate datasets for developing effective security solutions.
Our work emphasizes recent advancements in ML techniques
and their application in V2X networks.Gularte et al. [41]
focused on the market significance of V2X security, including
investments, research, and patents. While their survey offers
valuable insights, it lacks detailed discussions on specific
attacks, mitigation methods, and AI approaches. Our study
complements their work by providing an in-depth analysis of
ML methodologies and dataset benchmarks. Solaas et al. [42]
systematically reviewed anomaly detection in CAVs, analyzing
AI algorithms such as LSTM, CNN, and autoencoders. However, their review primarily focuses on the CAN protocol and
lacks specifics on AI methodologies and dataset benchmarks.
Our survey expands on this by covering a broader range of
V2X communication protocols and evaluating diverse datasets.
Boualouache et al. [43] investigated ML-based Misbehavior Detection Systems (MDS) for 5G and beyond vehicular
networks. While their survey categorizes ML methodologies,
it lacks a comprehensive analysis of practical implementation challenges. Our work addresses this gap by discussing
real-time application scenarios and performance evaluation.
Sakiz et al. [44] examined security risks and detection
methods in VANETs and IoV, focusing on conventional
intrusion detection techniques. However, their survey does
not cover recent advancements in ML-based solutions. Our
study highlights the latest ML approaches for enhancing V2X
security. Nagarajan et al. [45] explored ML-based Intrusion
Detection Systems (IDS) for connected autonomous vehicles,
focusing on intra-vehicle communication via the CAN-BUS.
Their study does not consider alternative V2X communication
protocols or provide a thorough analysis of datasets. Our
survey addresses these limitations by including a broader range
of protocols and datasets. Sedar et al. [46] conducted a comprehensive examination of V2X cybersecurity mechanisms,
categorizing attacks and defense mechanisms. While they
explore the potential of AI/ML, their survey lacks a detailed
analysis of specific ML methods for intrusion detection. Our
work provides a more focused discussion on ML techniques
and their practical applications.
Sharma et al. [47] investigated IDS and proactive security
mechanisms in VANETs, highlighting unresolved issues and
future research areas. However, their paper does not offer an
in-depth analysis of ML methods or examine datasets for
practical applications. Our survey addresses these gaps by
providing a detailed evaluation of ML methodologies and
benchmark datasets.Tang et al. [48] examined ML methods
in vehicular networks, focusing on the 6G era. While their
survey offers valuable insights, it lacks specifics on ML
algorithms, validation methods, and dataset benchmarks. Our
work complements their study by addressing these aspects
in detail. Rajbahadur et al. [49] surveyed anomaly detection techniques for connected vehicle cybersecurity, providing
statistical overviews without detailed explanations of methodologies. Our survey offers a more in-depth analysis of ML
techniques and their practical applications. Alrehan et al. [50]
reviewed ML methods for DDoS attacks in VANETs, focusing
primarily on DDoS threats. Their survey lacks comprehensive

coverage of other VANET-specific attacks and ML techniques.
Our work addresses this by providing a broader analysis of
security threats and ML methodologies.
Gonçalves et al. [51] reviewed intelligent IDS for vehicular communication, emphasizing the significance of IDS
solutions. However, their study lacks an in-depth analysis
of practical implementation specifics. Our survey addresses
this gap by discussing real-world performance validation.
Asuquo et al. [52] examined privacy and security concerns
in vehicular networks, focusing on cryptographic mechanisms
and privacy-enhancing schemes. Their study does not address
ML-based solutions, which our survey comprehensively covers.
Liang et al. [53] reviewed ML frameworks for high-mobility
vehicular networks, focusing on network optimization. While
they discuss unauthorized access detection, their paper does
not study security threats or ML methodologies in depth. Our
work provides a more focused analysis of ML techniques for
V2X security.
Kuutti et al. [54] investigated deep learning in vehicle
control systems, showcasing its potential for improving control
systems. However, their survey does not address security
issues related to deep learning in vehicular networks. Our
study fills this gap by exploring the role of ML in enhancing
V2X security. Hossain et al. [55] reviewed ML methods
in cognitive radio-based vehicular networks (CR-VANETs),
focusing on security threats within the CR environment. Our
survey expands on this by addressing a broader range of
security challenges in V2X networks.
Lu et al. [56]provided an overview of advancements in
VANET security, privacy, and trust management. However,
their survey does not consider the importance of ML algorithms or their practical implementation. Our work addresses
this by emphasizing the role of ML in enhancing VANET
security.
Sheikh et al. [57] analyzed security concerns in VANETs,
focusing on the structure and challenges of VANETs without
discussing the use of ML for security issues. Our survey
complements their work by providing a detailed analysis of
ML-based solutions.
Tong et al. [58] surveyed ML in vehicular communication
networks, briefly touching upon ML-based methodologies for
identifying and preventing malicious activities. Our study
builds on their work by comprehensively analyzing ML techniques and their applications in V2X networks.
Farsimadan et al. [59] review security challenges in
V2X communications, highlighting vulnerabilities in Vehicular Ad-hoc Networks (VANETs) and classifying threats
based on architecture, models, and attack types. They discuss
countermeasures such as cryptographic authentication, trust
management, and intrusion detection. However, the study lacks
a detailed examination of machine learning-based intrusion
detection systems (IDS), adversarial AI threats, and dataset
benchmarking. While IDS approaches are mentioned, their
effectiveness in anomaly detection and resilience to adversarial
attacks remain unaddressed.
Zhang et al. [60] provide a survey on V2X
communication in Intelligent Connected Vehicles (ICVs),

HAKEEM AND KIM: ADVANCING INTRUSION DETECTION IN V2X NETWORKS: A COMPREHENSIVE SURVEY

analyzing pre-communication, during-communication, and
post-communication challenges. They examine wireless
technologies, security threats, datasets, and experimental
platforms, emphasizing their impact on traffic efficiency
and autonomous driving. However, the study has notable
gaps: it does not deeply evaluate intrusion detection methods
or compare their performance against different attacks.
The dataset review is limited to cooperative perception,
overlooking real-world challenges such as sensor fusion
and
privacy-preserving
communication.
Additionally,
while experimental platforms are discussed, the lack of
benchmarking and performance comparisons weakens
practical applicability. The study also overlooks key emerging
areas, including quantum security, 6G-enabled V2X, and
federated learning, which are essential for future secure
V2X systems. While previous surveys provide valuable
insights into ML-based security for V2X communication,
they often lack comprehensive evaluations of specific ML
architectures, dataset benchmarking, real-world deployment
challenges, and federated learning scalability. Many studies
focus on theoretical models without addressing computational
constraints, adversarial threats, and emerging AI-driven
attacks. Additionally, limited coverage of key performance
metrics such as accuracy, precision, recall, and false alarm
rates makes it difficult to assess IDS effectiveness.
Our survey addresses these gaps by systematically analyzing
ML techniques for intrusion and misbehavior detection in
V2X networks. By integrating the latest advancements up
to 2025, we provide a comprehensive, up-to-date perspective
on emerging security threats and technological developments.
Tables II and III summarize the key limitations in recent V2X
security surveys.
IV. V2X C OMMUNICATION F UNDAMENTAL AND
C OMPONENTS
The architecture of V2X networks is structured hierarchically, enabling communication between vehicles, network
entities, and infrastructure components. This section provides
an analysis of V2X communication modes, protocols, fundamental components, message structures, and security concerns.
A. V2X Communication Modes, Layers and Standards
Protocols
V2X communication include multiple modes, facilitating
interactions between different entities within the network [61]:
• Vehicle-to-Vehicle (V2V): Direct wireless communication among vehicles within the same communication
range, ensuring real-time data exchange for collision
avoidance and cooperative driving [62].
• Vehicle-to-Infrastructure (V2I): Interaction between
vehicles and roadside units (RSUs), traffic signals, and
urban infrastructure to enhance road safety and traffic
management [63].
• Vehicle-to-Network (V2N): Establishing a connection
between vehicles and cellular networks, enabling access
to cloud-based services, remote updates, and enhanced
connectivity [64].

11145

Vehicle-to-Pedestrian (V2P): Sharing real-time situational awareness between vehicles and pedestrians,
improving safety in urban environments [65].
Figure 4 illustrates the different communication modes within
the V2X network architecture.
V2X communication relies on various protocols designed
to support high-reliability, low-latency interactions [35]:
• IEEE 802.11p (WAVE Standards): An extension of the
IEEE 802.11 standard, operating at 5.9 GHz, providing
dedicated short-range communication (DSRC) with low
latency for safety applications [66].
• LTE-V2X (Long-Term Evolution for V2X): A
cellular-based technology that offers improved coverage
and scalability, supporting advanced V2X applications
and enabling future integration with 5G networks [67].
• 5G-V2X: Extends LTE-V2X by leveraging Ultra-Reliable
Low-Latency Communication (URLLC) to support realtime mapping, autonomous driving, and cooperative
maneuvering [68].
• 6G-V2X: Future communication standard expected to
enhance ubiquitous connectivity, real-time decisionmaking, AI integration, and edge computing for intelligent transportation systems [69].
• IEEE 1609.x Standards: A family of standards defining
security mechanisms and communication architecture to
ensure confidentiality, integrity, and authenticity of transmitted messages [70].
Figure 5 summarizes different V2X communication standards,
while Figure 6 represents the V2X protocol stack.
The V2X communication stack is layered to ensure efficient
message transmission [71]:
• Application Layer: Handles V2X safety applications,
such as Basic Safety Messages (BSM), Signal Phase and
Timing (SPaT), and Emergency Vehicle Alerts (EVA)
[72].
• Transport Layer: Utilizes Transmission Control Protocol
(TCP) for reliable communication and User Datagram
Protocol (UDP) for low-latency data exchange [73].
• Network Layer: Supports IPv6-based routing and Named
Data Networking (NDN), which focuses on content-based
data retrieval [74].
• Data Link Layer: Includes IEEE 802.11p for short-range
wireless communication and LTE-V2X for cellular-based
connectivity [75].
• Physical Layer: Encompasses DSRC and 5G-V2X
technologies, providing high-speed and low-latency communication [76].
•

B. V2X Fundamental Components and Basic Messages
The efficient functioning of V2X networks depends on key
components [77]:
• On-Board Units (OBUs): Vehicle-mounted devices
responsible for transmitting and receiving V2X messages [78].
• Roadside Units (RSUs): Fixed infrastructure components that facilitate communication between vehicles and
network entities [79].

11146

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 8, AUGUST 2025

TABLE II
R ECENT S URVEY PAPERS AND T HEIR L IMITATIONS (PART 1)

HAKEEM AND KIM: ADVANCING INTRUSION DETECTION IN V2X NETWORKS: A COMPREHENSIVE SURVEY

11147

TABLE III
R ECENT S URVEY PAPERS AND T HEIR L IMITATIONS (PART 2)

Fig. 4.

V2X communication architecture.

Certificate Authorities (CAs): Entities that issue digital certificates to authenticate communication participants [80].
• Security Credential Management System (SCMS):
Manages the distribution, renewal, and revocation of
•

security certificates to maintain trust within the network [81].
V2X networks support various message types to enable
seamless communication [82]:

11148

Fig. 5.

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 8, AUGUST 2025

V2X communication standards.

Basic Safety Messages (BSMs): Provide critical
information on vehicle position, speed, and acceleration [83].
• Signal Phase and Timing (SPaT): Transmit traffic signal
status for improved intersection management [84].
• Map Data Messages: Offer detailed road topology, lane
configurations, and speed limit data [85].
• Emergency Vehicle Alerts (EVAs): Notify nearby
vehicles of emergency vehicle presence and intended
routes [86].
•

Ensuring security in V2X networks is paramount to prevent
unauthorized access and data breaches. The main security
measures include:
1) Message Authentication: Cryptographic digital signatures verify message authenticity and prevent spoofing [87].
2) Encryption: Symmetric and asymmetric encryption
techniques secure message confidentiality from eavesdropping threats [4].
3) Certificate Management: Certificate Authorities (CAs)
issue and revoke digital certificates for network entities [88].
4) Secure Key Management: Proper key generation, distribution, and renewal protect cryptographic
integrity [89].
5) Privacy Preservation: Pseudonymization techniques
prevent vehicle tracking and unauthorized profiling.
6) Intrusion Detection and Prevention: IDS solutions
detect and mitigate network anomalies to enhance cybersecurity.
Figure 7 illustrates the key security threats and mitigation
strategies in V2X communication.

Fig. 6.

V2X communication protocol stack.

V. T RADITIONAL ATTACKS IN V2X N ETWORKS : ATTACK
M ODELS AND M ITIGATION S TRATEGIES
This section provides an overview of key vulnerabilities
within V2X components, classifies potential traditional attack
models, and discusses mitigation strategies.
A. Targets of Attacks
The interconnected nature of V2X communication systems
relies on a range of sensors, controllers, and communication mechanisms. Any compromise to these components can
lead to system malfunctions, unauthorized access, or data
manipulation, ultimately affecting road safety. This subsection
outlines the primary V2X components susceptible to cyber
threats, supported by both theoretical and empirical attack
models [63] [66] [86] [90].
1) On-Board Diagnostic Port (OBD): The On-Board Diagnostic (OBD) port serves as a critical interface for monitoring
vehicle parameters such as emissions, speed, and engine status.
Initially introduced in 1987 with OBD-I and later standardized
as OBD-II in 1996, it provides real-time access to Electronic
Control Unit (ECU) data and supports firmware updates.
However, its accessibility poses a security risk, allowing adversaries to manipulate ECU data or inject malicious firmware.
Effective mitigation strategies include enforcing strict access
control policies and implementing secure firmware update
mechanisms.
2) Electronic Control Units (ECUs): ECUs govern multiple
vehicular subsystems, including engine management, braking
systems, tire pressure monitoring, and inertial measurement
units (IMUs). These units are responsible for critical functions

HAKEEM AND KIM: ADVANCING INTRUSION DETECTION IN V2X NETWORKS: A COMPREHENSIVE SURVEY

Fig. 7.

11149

Security consideration in V2X communication.
TABLE IV
V EHICLE C OMPONENTS , V ULNERABILITIES , AND M ITIGATION T ECHNIQUES

such as regulating air-fuel mixture, monitoring wheel-speed
sensors, and ensuring real-time adjustments to braking pressure. Cyberattacks targeting ECUs often involve firmware
manipulation or data injection, potentially leading to vehicle
malfunctions. To safeguard ECUs, strong encryption mechanisms and advanced anomaly detection techniques should be
implemented [91].
3) Controller Area Network (CAN): The Controller Area
Network (CAN) facilitates communication between ECUs
within a vehicle through a two-wire, half-duplex configuration.
Despite its efficiency, CAN lacks authentication mechanisms,
making it vulnerable to data interception and injection attacks.
Malicious actors can exploit this weakness to alter control messages or introduce fake commands. Countermeasures
include network segmentation and the adoption of secure
communication protocols to fortify the CAN bus against
unauthorized intrusions.
4) Sensors: Modern vehicles incorporate a variety of sensors to support autonomous functionalities, including:

LiDAR: Utilizes laser-based technology for distance
measurement and object detection.
• Radar: Employs electromagnetic waves to identify
objects and estimate their velocity.
• GPS: Relies on satellite signals to determine location and
provide navigation assistance.
• Cameras: Capture 360-degree environmental data to
enhance lane detection, obstacle avoidance, and traffic
sign recognition.
•

These sensors are susceptible to jamming, spoofing, and
data manipulation attacks. Effective countermeasures involve
multi-sensor data fusion, redundancy techniques, and signal
integrity verification. V2X communication relies on two primary communication mechanisms, each presenting unique
security challenges. Both V2V and V2I communications are
susceptible to data interception, signal jamming, and spoofing attacks. Implementing robust encryption standards and
secure authentication protocols is essential to maintaining the
integrity of these communication channels. Table IV outlines
the associated attack vectors for different vehicle components.

11150

Fig. 8.

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 8, AUGUST 2025

Attacks categories in V2X communication.

B. Categories of Attack Models

C. Traditional Attacks and Mitigation Strategies

V2X attacks can be classified based on the attacker’s access
level and primary objectives:
• Remote-Access Attacks: Conducted without physical
access to the vehicle, these attacks typically involve signal
interception, spoofing, or unauthorized data extraction.
Examples include injecting false sensor data or manipulating wireless signals to deceive navigation systems.
• Physical-Access Attacks: Require direct access to the
vehicle, often involving hardware manipulation, malicious firmware updates, or ECU reprogramming.
Cyberattacks on V2X communication networks are typically
motivated by one of the following objectives:
• Disrupt Operations: Includes Denial-of-Service (DoS)
attacks aimed at overwhelming vehicular networks,
disabling essential functions, or disrupting navigation
systems.
• Gain Control: Attackers attempt to take over vehicle
control systems, allowing unauthorized manipulation of
steering, acceleration, or braking.
• Steal Information: Exploits vulnerabilities to extract
sensitive user data, which can be used for identity theft,
industrial espionage, or illicit tracking.
Effective cybersecurity measures must be employed to protect
V2X networks from evolving threats:
• OBD Attacks: Prevent unauthorized access to ECU data
and vehicle operations by enforcing stringent access control mechanisms and secure firmware update protocols.
• ECU Attacks: Mitigate firmware tampering and data
manipulation risks by deploying strong encryption techniques and real-time anomaly detection.
• CAN Bus Attacks: Address authentication weaknesses to
prevent malicious data injection through secure network
segmentation and communication filtering.
• Sensor Attacks: Counter spoofing and jamming attempts
by integrating redundancy mechanisms, signal integrity
verification, and multi-sensor data fusion techniques.

This subsection classifies the major types of traditional
attacks targeting V2X systems, highlighting their characteristics, potential impact, and mitigation strategies. A summary
of these attacks is depicted in Figure 8.
1) Denial-of-Service (DoS) Attacks: DoS attacks aim to
overwhelm network nodes, such as roadside units (RSUs) or
onboard units (OBUs), with excessive data requests, rendering
them incapable of processing legitimate information. These
attacks can disrupt vehicle authentication, traffic updates, and
security protocols. A more severe variation, distributed denialof-service (DDoS) attacks, involves multiple compromised
vehicles or bots sending coordinated malicious requests, making detection and mitigation more challenging [85]. Traditional
mitigation strategies, such as blocking attacker IP addresses,
are ineffective against DDoS due to the use of multiple source
addresses. Advanced anomaly detection and traffic filtering
mechanisms can enhance resilience against these attacks.
2) Black-Hole Attacks: In a black-hole attack, a compromised vehicle intercepts and drops all network packets instead
of forwarding them to their intended destination, creating
a “black hole” that disrupts communication. A variant of
this attack, known as the grey-hole attack, selectively drops
packets to avoid detection [4]. These attacks degrade network performance and obstruct vital data flow. Implementing
sequence numbers in packet transmissions allows legitimate
nodes to detect anomalies in message forwarding. Additionally, machine learning-based solutions, such as the Black
Hole Attack Detection Algorithm (BADA), can help identify
malicious nodes based on historical routing behaviors.
3) Replay Attacks: Replay attacks involve intercepting and
retransmitting previously recorded legitimate messages to
deceive network participants. Attackers can use this technique
to bypass authentication mechanisms and gain unauthorized
access to the network [84]. Such attacks are particularly concerning in vehicle authentication and secure communication
protocols. Mitigation measures include implementing strong
encryption, incorporating time stamps or nonces in message

HAKEEM AND KIM: ADVANCING INTRUSION DETECTION IN V2X NETWORKS: A COMPREHENSIVE SURVEY

authentication protocols, and employing Virtual Private Networks (VPNs) to secure data exchanges.
4) Sybil Attacks: Sybil attacks involve an adversary generating multiple false identities or impersonating multiple
legitimate nodes to manipulate V2X network behavior.
Attackers may create congestion by simulating high traffic
density or misleading vehicles into rerouting unnecessarily. GPS spoofing is often used in conjunction with Sybil
attacks to manipulate navigation data. Machine learning-based
detection methods that analyze node behaviors, such as spatial inconsistencies and abnormal movement patterns, can
help mitigate Sybil attacks. Cryptographic authentication
techniques and certificate-based verification further enhance
network integrity [71].
5) Impersonation Attacks: Impersonation attacks occur
when an adversary masquerades as a legitimate RSU or vehicle, thereby gaining unauthorized access to network resources
or sensitive information. Such attacks may grant the attacker
privileged access to traffic updates, navigation data, or vehicle
control functions [90]. Countermeasures include employing
strong encryption for authentication, integrating location-based
verification mechanisms, and utilizing clustering techniques to
validate network entities.
6) Malware Attacks: Due to the dynamic nature of vehicle
networks, software updates and data exchanges occur frequently. If these updates originate from untrusted sources,
malware can infiltrate the vehicle’s system, leading to data corruption, system failures, or unauthorized control over vehicle
functionalities. Firewalls and intrusion detection systems (IDS)
serve as the primary defense mechanisms against malware by
filtering suspicious messages. Additionally, reputation-based
verification systems can help ensure that only trusted updates
are accepted [89].
7) False Information Attacks: Attackers can disseminate
misleading data regarding road conditions, accidents, or congestion to manipulate traffic flow or cause safety hazards.
For example, an adversary might transmit false congestion reports, diverting vehicles away from an optimal route.
Conversely, attackers could suppress warnings about actual
hazards, increasing the risk of collisions [84]. Reputationbased trust models that reward accurate reporting and penalize
misleading information help mitigate this threat. Anomaly
detection techniques and cross-validation with multiple data
sources further enhance the reliability of shared information.
8) Timing Attacks: Timing attacks involve delaying or
manipulating the transmission of time-sensitive messages,
disrupting real-time applications such as collision avoidance
and emergency braking. Delays in V2X communication can
be catastrophic, particularly in autonomous driving scenarios, where decision-making depends on instantaneous data
exchange [68]. Mitigation strategies include enforcing strict
timing constraints, using synchronized clocks, and implementing delay monitoring techniques to detect intentional message
delays.
9) Privacy Attacks: Privacy breaches in V2X networks
occur when attackers track vehicle locations, identities, and
behavioral patterns by intercepting communication signals.

11151

Adversaries may exploit side-channel information to infer
private user data, such as frequently visited locations or
personal driving habits [87]. Privacy-preserving techniques,
such as encryption, pseudonymization, and data obfuscation,
play a crucial role in preventing unauthorized tracking.
10) Jamming Attacks: Jamming attacks interfere with wireless signals, preventing vehicles from transmitting or receiving
critical safety messages. This type of attack can disrupt V2V
and V2I communication, leading to loss of situational awareness and potential traffic incidents [4]. Machine learning-based
IDS can help identify abnormal signal interference patterns
and distinguish legitimate transmissions from malicious jamming attempts.
11) Spoofing Attacks: Spoofing attacks involve an adversary pretending to be a legitimate V2X node to manipulate
traffic conditions, reroute vehicles, or introduce false safety
alerts. These attacks undermine trust in V2X communication
networks and can cause severe disruptions. IDS leveraging
machine learning algorithms can detect spoofed nodes by
analyzing behavioral inconsistencies and comparing them with
trusted network entities.
12) Eavesdropping Attacks: Eavesdropping attacks involve
unauthorized interception of V2X messages, allowing adversaries to access confidential vehicle information, such as user
credentials or navigation data. Attackers may exploit intercepted data for identity theft, industrial espionage, or targeted
attacks [69]. Implementing end-to-end encryption, secure key
management, and anomaly-based IDS helps prevent eavesdropping threats.
Table V provides a summary of the traditional attack models
in V2X communication.
VI. AI-BASED ATTACKS AND A DVERSARIAL T HREATS IN
V2X N ETWORKS
The integration of AI in V2X communication introduces
new vulnerabilities. AI-based attacks, particularly adversarial
attacks, target the ML models used for network optimization,
resource allocation, intrusion detection, and traffic prediction,
compromising safety-critical applications such as collision
avoidance, remote driving, and platooning. This section
examines adversarial attack types, their impact on V2X communication systems, a review of state-of-the-art research, and
mitigation strategies to secure vehicular networks.
A. Definition of AI-Based and Adversarial Attacks in V2X
Networks
The primary objective of adversarial attacks in V2X networks is to reduce the reliability of AI models, disrupt
resource allocation, and compromise safety-critical vehicular communications. This subsection provides a detailed
exploration of adversarial attack simulations in V2X ML models and deep reinforcement learning (DRL)-based mitigation
strategies, incorporating insights from Sharma et al. [92],
Sedar et al. [93], and others. Adversarial attacks in V2X
security exploit ML vulnerabilities to manipulate vehicular
data and mislead misbehavior detection models. These attacks

11152

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 8, AUGUST 2025

TABLE V
T YPES OF T RADITIONAL ATTACKS IN V2X N ETWORKS AND M ITIGATION S TRATEGIES

can lead to traffic congestion, safety hazards, and compromised
emergency response systems. With the increasing deployment
of AI-based decision-making in V2X communication, attackers exploit vulnerabilities in deep learning models through
various attack vectors [94], [95]:
• Data Poisoning Attacks: Injecting malicious data into
training datasets, leading to incorrect traffic flow predictions or sensor fusion errors.
• Evasion Attacks: Modifying input signals (e.g., spoofed
sensor data, altered CSI values) to mislead AI models
into making incorrect decisions.
• Model Extraction Attacks: Reconstructing AI models
through repeated queries to steal decision-making algorithms.
Adversarial attacks involve intentionally inputs that mislead
AI-based V2X systems, affecting network security and efficiency. These attacks are categorized into:
• Open-Box (Transparent) Attacks: The attacker has full
access to the AI model, allowing precise manipulation of
network decisions.
• Closed-Box (Opaque) Attacks: The attacker has limited
knowledge of the model but alters the AI’s responses
through repeated inputs.
B. Simulating Adversarial Attacks in V2X ML Models
in this section, we introduce some simulated adversarial
attacks on V2X systems.
1) Adversarial Attacks Targeting ML-Based Misbehavior
Detection Models for CAVs: Sharma et al. [92] present an
experiment that follows a structured adversarial attack simulation to evaluate the effectiveness of current ML models.
Step 1: Generating Adversarial Data

Dataset Selection: The study uses the VeReMi dataset,
a benchmark dataset for VANET misbehavior detection, containing Basic Safety Messages (BSMs) with
vehicle parameters such as speed, acceleration, and
position.
• Generating Adversarial Examples: The study employs
a traditional attack engine to create attack samples
simulating:
– Location Spoofing Attacks (GPS manipulation)
– Sybil Attacks (Fake identities)
– Denial-of-Service (DoS) Attacks (Message flooding)
Step 2: Training the ML Model to Generate Hard-toDetect Attacks
• Supervised ML Training: ML models, including
K-Nearest Neighbor (KNN), Random Forest (RF),
Logistic Regression (LR), and Long Short-Term Memory
(LSTM), are trained using time-series data extracted from
normal BSMs.
• Adversarial Model Training: A second ML model is
trained to generate attack samples that mimic normal
behavior, bypassing conventional misbehavior detection
mechanisms.
Step 3: Evaluating Attack Effectiveness
• The generated adversarial attacks are tested against standard ML-based misbehavior detection systems.
• Findings: LSTM models demonstrate better resistance
but still exhibit reduced detection performance against
adversarial attacks.
2) Adversarial Attacks on V2X Resource Allocation: Fast
Gradient Sign Method (FGSM): FGSM is a one-step adversarial attack that perturbs resource allocation parameters (e.g.,
channel state, transmission power) to force incorrect AI-based
scheduling decisions, reducing [96], [97]:
•

HAKEEM AND KIM: ADVANCING INTRUSION DETECTION IN V2X NETWORKS: A COMPREHENSIVE SURVEY

11153

TABLE VI
DRL P ERFORMANCE AGAINST A DVERSARIAL ATTACKS

Data transmission efficiency.
Packet delivery rates.
• QoS performance for V2X applications.
Projected Gradient Descent (PGD): PGD [98] improves
FGSM by applying iterative perturbations to mislead DRLbased V2X resource allocation models. It:
• Creates cumulative misallocations over multiple iterations.
• Significantly increases network congestion.
• Reduces V2X connectivity reliability.
Policy Infiltration Attack (PIA): PIA is a gradient-based
adversarial attack that tricks DRL algorithms into misallocating network resources [99]. It:
• Reduces packet delivery rates by 77.74%.
• Increases latency by 150%.
• Disrupts
ultra-reliable low-latency communication
(uRLLC).
3) Adversarial Attacks on Signal Processing & Physical
Layer: Signal Manipulation Attacks: Adversaries inject fake
wireless signals that trick AI-based spectrum classifiers. These
attacks:
• Mislead deep learning models in modulation classification.
• Trigger false alarms in intrusion detection systems (IDS).
• Compromise AI-powered interference mitigation.
Bearer Migration Poisoning (BMP): BMP exploits weaknesses in bearer migration procedures [100], causing:
• Traffic misrouting in V2X networks.
• Denial-of-Service (DoS) attacks on connected vehicles.
• Severe delays in collision avoidance systems.
Intelligent Reflecting Surface (IRS) Manipulation:
Attackers control IRS configurations to redirect signals incorrectly, causing:
• Beamforming errors.
• Network disconnection in vehicular systems.
• Increased power consumption in smart vehicle networks.
•

•

C. Mitigation Strategies for Adversarial Attacks in V2X
Networks
To counter adversarial threats, the following mitigation
strategies can be implemented:
• Adversarial Training: ML models are trained with
adversarial examples to improve robustness.
• Defensive Distillation: Distillation-based ML models
improve resistance to adversarial perturbations.
• Blockchain-Enabled Authentication: Blockchain technology ensures tamper-proof vehicle authentication and
prevents Sybil attacks.

Anomaly Detection with Deep Learning: Autoencoders
and anomaly detection models can identify subtle attack
patterns.
• Federated Learning for Secure Training: Decentralized
ML training prevents model poisoning attacks by ensuring no single entity controls all training data.
To counter adversarial ML threats, Sedar et al. [93]
propose a DRL-based defense mechanism for vehicular
communication systems. Their study focuses on defending
against:
• Label-Flipping Attacks: Adversaries flip training data
labels to mislead ML classifiers.
• Policy Induction Attacks: Adversaries inject perturbations into state observations, corrupting DRL models.
1) DRL-Based Defense Framework: The proposed DRL
defense system operates at RSUs, classifying vehicular data
and detecting misbehavior in V2X networks.
Step 1: Reinforcement Learning for Attack Detection
• Defining the Environment: The RSU receives real-time
BSMs and maintains a time-series repository.
• Training the DRL Agent: A Markov Decision Process (MDP) is used for sequential decision-making. The
Q-learning algorithm ensures adaptive attack detection.
Step 2: Evaluating DRL Performance Against Adversarial Attacks
Adversarial attacks pose a significant risk to V2X communication security, allowing attackers to manipulate vehicle
data, evade intrusion detection, and disrupt traffic systems.
Studies by Sharma et al. [92] and Sedar et al. [93] demonstrate
that conventional ML-based security mechanisms fail against
AI-adversarial attacks. The DRL-based detection framework
offers a promising defense mechanism, achieving 99% detection accuracy for label-flipping attacks and maintaining
moderate robustness under extreme adversarial conditions.
Future research should focus on real-world adversarial datasets
and adaptive security models to ensure resilient V2X networks.
As shown in Table VI, Deep Reinforcement Learning (DRL)
outperforms LSTM and MLP in handling adversarial attacks,
achieving higher accuracy in label-flipping and policy induction scenarios.
Adversarial Training: Training AI models with adversarial
examples improves defense against FGSM, PGD, and PIA
attacks.
Secure Reinforcement Learning (RL) Models:
• Regularizing policy updates in DRL models reduces
policy infiltration risks.
• Entropy-based reinforcement learning ensures secure
V2X decision-making.
•

11154

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 8, AUGUST 2025

TABLE VII
T YPES OF A DVERSARIAL AND M ODERN ATTACKS IN V2X N ETWORKS AND M ITIGATION S TRATEGIES

AI-based Intrusion Detection Systems (IDS): Deploying
adversarially trained IDS improves anomaly detection accuracy and prevents evasion attacks.
Secure Open Interfaces in V2X:
End-to-end encryption for V2X communication prevents
signal injection attacks.
• Zero-trust authentication for connected vehicles strengthens security [101].

•

Radio Positioning & Trusted Location Validation: Using
multi-array antennas for UE positioning validation prevents
fake CSI-based adversarial attacks.
Multi-Agent AI for Distributed Security:
Distributed multi-agent learning enhances attack detection capabilities.
• Cross-validation among V2X nodes prevents DRL policy
exploitation.
•

As summarized in Table VII, adversarial and modern attacks
pose significant security challenges in V2X networks. Various countermeasures, including adversarial training, secure
federated learning, and anomaly-based detection, have been
proposed to mitigate these threats.

VII. I NTRUSION D ETECTION IN V2X N ETWORKS :
D ETECTION M ETHODS , D EPLOYMENT S TRATEGIES , AND
S COPE OF P ROTECTION
This section discusses IDS classification based on detection
methodology, deployment location, network architecture, and
scope of detection, as depicted in Figure 9.
A. IDS Categorization Based on Detection Approach
Various IDS models have been proposed to detect cyber
threats in V2X communication. These systems can be broadly
classified into the following categories:
• Signature-Based IDS: This type of IDS detects known
threats by comparing incoming network traffic against a
database of predefined attack signatures. These signatures
are derived from previous attack patterns and known
vulnerabilities. When a match is identified, the IDS
generates an alert or initiates mitigation measures. While
signature-based IDSs are highly efficient in recognizing
previously documented threats, their major limitation is
the inability to detect novel or zero-day attacks, as they
rely solely on predefined signatures [102].
• Anomaly-Based IDS: Unlike signature-based detection,
anomaly-based IDSs identify intrusions by analyzing

HAKEEM AND KIM: ADVANCING INTRUSION DETECTION IN V2X NETWORKS: A COMPREHENSIVE SURVEY

Fig. 9.

Fig. 10.

Host-based IDS (HIDS) in V2X Networks.

Fig. 11.

Network-based IDS (NIDS) in V2X Networks.

11155

IDS types in v2x.

deviations from normal network behavior. These systems establish a baseline of legitimate activity and flag
any anomalies as potential threats. Statistical models
and machine learning techniques are often employed
to enhance detection accuracy. Although anomaly-based
IDSs are more effective in detecting unknown attacks
compared to signature-based IDSs, they tend to produce
higher false positive rates due to their dependency on
baseline deviations [103], [104].
• Machine Learning-Based IDS: This approach employs
supervised or unsupervised machine learning algorithms
to detect abnormal traffic patterns. By training models
on historical network data, these IDSs can identify complex attack patterns and detect emerging threats. While
machine learning-based IDSs offer significant advantages
in detecting zero-day attacks, their performance depends
on the availability of high-quality training datasets and
continuous model updates to maintain accuracy.
B. IDS Categorization Based on Deployment Location
IDS deployment in V2X networks can be categorized based
on whether they operate at the host level (individual vehicles)
or across the network infrastructure.
• Host-Based IDS (HIDS): HIDS operates at the individual vehicle or infrastructure level, monitoring internal
system activities such as system logs, file integrity, and
process execution. By analyzing system behavior, HIDS
can detect unauthorized access or malicious activities
occurring within a specific node. However, one limitation
is that HIDS may not be able to detect network-wide
attacks occurring beyond the monitored device [105].

Figure 10 illustrates the role of HIDS in V2X networks,
where each vehicle autonomously monitors and analyzes
network traffic to enhance security.
• Network-Based IDS (NIDS): Deployed at strategic network locations such as Roadside Units (RSUs), NIDS
monitors real-time network traffic for malicious activity.
These systems analyze communication patterns, packet
payloads, and network anomalies to detect potential security threats. Since NIDS operates at network ingress and
egress points, it is particularly effective in identifying
large-scale attacks. Figure 11 demonstrates how NIDS
functions in a V2X environment, with RSUs overseeing
traffic flows and identifying network vulnerabilities.
• Hybrid IDS: Combining the capabilities of both HIDS
and NIDS, hybrid IDSs provide a more holistic approach

11156

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 8, AUGUST 2025

false data injection, denial-of-service (DoS) attacks, and
other security threats targeting critical infrastructure.
• V2X IDS: Providing a comprehensive security framework, V2X IDSs cover all communication modes within
the V2X ecosystem. These systems detect multi-layered
attacks, including malware propagation, coordinated
cyberattacks, and large-scale data breaches affecting both
vehicles and infrastructure [109].Table VIII provides a
comprehensive classification of IDSs based on their
deployment location, detection techniques, network architecture, and scope of detection.
VIII. C OMPREHENSIVE TAXONOMY OF M ACHINE
L EARNING -BASED I NTRUSION D ETECTION S YSTEMS FOR
V2X S ECURITY

Fig. 12.

Hybrid IDS in V2X Networks.

to intrusion detection. By integrating host-level monitoring with network-wide traffic analysis, hybrid IDSs
can detect a broader range of security threats, including
sophisticated multi-vector attacks. Figure 12 illustrates a
hybrid IDS framework in V2X networks, demonstrating
the synergy between decentralized (HIDS) and centralized (NIDS) detection mechanisms.
C. IDS Categorization Based on Network Architecture
Intrusion detection mechanisms in V2X networks can also
be classified based on their architectural implementation:
• Centralized IDS: These systems operate from a central
control point, such as a cloud-based security server or
a core RSU, offering a unified view of network-wide
threats. Centralized IDSs facilitate efficient monitoring
and management but may be vulnerable to single-point
failures and scalability limitations [93].
• Distributed IDS: Distributed IDSs are deployed across
multiple nodes within the V2X network, enabling collaborative detection and mitigation of security threats.
By distributing detection responsibilities, these systems
enhance resilience against localized attacks. However,
distributed IDSs may introduce increased complexity and
higher false positive rates due to inconsistencies in data
aggregation and correlation [106], [107], [108].
D. IDS Categorization Based on Scope of Detection
V2X networks encompass different communication
paradigms, each presenting distinct security challenges. IDSs
can be classified based on their scope of detection:
• V2V IDS: Designed to monitor and secure direct vehicleto-vehicle (V2V) communication, these IDSs detect
threats such as message spoofing, replay attacks, and
unauthorized data manipulation.
• V2I IDS: Focused on securing interactions between
vehicles and infrastructure components, V2I IDSs detect

ML-based IDS leverage data-based models to learn complex
patterns and detect anomalies that may otherwise be overlooked, Unlike traditional IDS methods that rely on predefined
rules and signatures.
A. Classification of Machine Learning Approaches
ML-based IDS enhance security by learning from network
traffic patterns, continuously updating detection models, and
autonomously responding to cyber threats. These models
operate under different learning paradigms, including supervised, unsupervised, and reinforcement learning, each offering
unique benefits for V2X security [110], [111] [112].
1) Supervised Learning: Supervised learning relies on
labeled datasets to classify network traffic as benign or malicious. Once trained, these models effectively detect predefined
attack patterns and generalize to unseen threats. Figure 13
illustrates the typical supervised learning framework in IDS.
Common Supervised Learning Algorithms:
• Logistic Regression
• Support Vector Machines (SVM)
• Random Forest
• k-Nearest Neighbors (KNN)
• Neural Networks
• Gradient Boosting Algorithms (XGBoost, AdaBoost,
LightGBM)
• Ensemble Learning (Voting, Stacking)
Supervised learning is well-suited for detecting known attack
types but requires high-quality labeled datasets, which may
not always be available in dynamic V2X environments [113].
Supervised learning methods are illustrated in Figure 14.
2) Unsupervised Learning: Unsupervised learning detects
anomalies without labeled data, making it ideal for identifying
unknown or evolving threats. These models analyze deviations
from normal network behavior to flag potential intrusions
[114]. Figure 15 presents key unsupervised learning techniques
for IDS.
Common Unsupervised Learning Algorithms:
• Gaussian Mixture Models (GMM)
• Hierarchical Clustering
• K-Means Clustering
• One-Class SVM
• Isolation Forest

HAKEEM AND KIM: ADVANCING INTRUSION DETECTION IN V2X NETWORKS: A COMPREHENSIVE SURVEY

11157

TABLE VIII
IDS C ATEGORIZATION BASED ON D EPLOYMENT L OCATION , D ETECTION M ETHODS , S COPE OF D ETECTION , AND N ETWORK A RCHITECTURE

TABLE IX
M ACHINE L EARNING T ECHNIQUES C ATEGORIZATION

Local Outlier Factor (LOF)
Autoencoders
While effective for zero-day attack detection, unsupervised
models often require fine-tuning to minimize false positives.
3) Reinforcement Learning: Reinforcement Learning (RL)
enhances IDS by dynamically optimizing security policies
through trial-and-error learning. Unlike supervised models,
RL continuously improves its attack response strategies based
on reward-based feedback. This approach is particularly beneficial in adaptive threat detection and mitigation for V2X
networks.
Applications of RL in IDS:
• Autonomous anomaly detection and adaptive response
• Optimized resource allocation for security mechanisms
•

•

Adversarial learning to improve robustness against AI
attacks
A diverse range of ML techniques can be employed
to enhance IDS performance in V2X networks. Table IX
categorizes key methods based on their learning paradigm.
4) Deep Learning for IDS: Deep Learning (DL), a subset of ML, utilizes multi-layer neural networks to analyze
complex attack patterns in large-scale V2X datasets. DLbased IDS can identify intricate cyber threats by leveraging
high-dimensional feature extraction and sequential analysis.A
detailed comparison of deep learning-based IDS techniques
is provided in Table X, highlighting their performance and
associated challenges.
•

11158

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 8, AUGUST 2025

TABLE X
D IFFERENT D EEP L EARNING M ETHODS AND R ELATED DATASETS W ITHIN VARIOUS A PPLICATION S CENARIOS

Common Deep Learning Architectures:
•

Convolutional Neural Networks (CNNs): Effective for
spatial pattern detection in network traffic.

•

Recurrent Neural Networks (RNNs): Suitable for
sequential data processing, including time-series intrusion
detection.

HAKEEM AND KIM: ADVANCING INTRUSION DETECTION IN V2X NETWORKS: A COMPREHENSIVE SURVEY

Fig. 15.
Fig. 13.

11159

Unsupervised learning common algorithms used in IDS-V2X.

Typical supervised learning framework in IDS.

layer applies nonlinear activation functions to extract
hierarchical features. Th

[...正文过长，此处由批处理脚本仅做上下文截断；请在结论中说明该限制...]

implementing decentralized IDS while preserving data privacy. Experimental results indicate that FL-based IDS reduce
communication overhead by 5–10% compared to traditional
centralized IDS architectures. Although slight accuracy degradation of approximately 1–2% is observed in FL models,
fine-tuning and optimized model aggregation mitigate this
issue, making FL a viable security solution for large-scale
V2X deployments. However, challenges remain in optimizing communication efficiency, addressing aggregation security
risks, and ensuring seamless coordination among participating
nodes.
The study also highlights the increasing threat posed by
adversarial attacks, which exploit vulnerabilities in AI-based
IDS models. The incorporation of adversarial training significantly improves detection robustness, with an observed
enhancement of up to 30% against evasion attacks. The
potential integration of blockchain with FL-based IDS offers
an additional layer of security, particularly in securing data
exchange and model updates among connected vehicles. However, existing datasets used for IDS research still present
limitations, particularly in representing real-world adversarial
attack scenarios, emphasizing the need for more diverse and
standardized security datasets.
Despite the advancements in AI-based IDS, real-world
deployment poses several challenges. Scalability and computational complexity remain significant concerns, especially when
deploying deep learning-based IDS in resource-constrained
vehicular environments. Communication latency and bandwidth limitations also impact IDS efficiency, necessitating the
adoption of edge computing and optimized model aggregation
techniques. Furthermore, the lack of high-quality V2X-specific
datasets limits the generalizability of IDS solutions, underscoring the need for more representative real-world datasets that
capture diverse attack scenarios.
To address these challenges, future research should explore
the integration of post-quantum cryptographic techniques to
enhance the resilience of IDS frameworks against emerging cyber threats. The adoption of Explainable AI (XAI)
will further improve the interpretability and trustworthiness
of AI-based IDS, facilitating their real-world deployment.
Additionally, hybrid security frameworks combining AI,
blockchain, and FL offer a promising direction toward achieving a scalable, privacy-preserving IDS for V2X networks.
The development of 6G-enabled IDS architectures leveraging
ultra-low latency and distributed intelligence will also play a
vital role in securing the next generation of autonomous and
connected vehicles.
By bridging the gap between theoretical IDS frameworks and practical V2X security implementations, this study
provides valuable insights for researchers and industry practitioners. The comparative evaluations, dataset analyses, and
experimental findings contribute to a deeper understanding
of IDS methodologies and their real-world applicability. The

HAKEEM AND KIM: ADVANCING INTRUSION DETECTION IN V2X NETWORKS: A COMPREHENSIVE SURVEY

results emphasize the necessity of developing adaptive, scalable, and privacy-preserving IDS solutions capable of securing
connected vehicles against increasingly sophisticated cyber
threats.
R EFERENCES
[1] M. Hasan, S. Mohan, T. Shimizu, and H. Lu, “Securing vehicleto-everything (V2X) communication platforms,” IEEE Trans. Intell.
Vehicles, vol. 5, no. 4, pp. 693–713, Dec. 2020.
[2] A. Alnasser, H. Sun, and J. Jiang, “Cyber security challenges and
solutions for V2X communications: A survey,” Comput. Netw., vol. 151,
pp. 52–67, Mar. 2019.
[3] J. Huang, D. Fang, Y. Qian, and R. Q. Hu, “Recent advances and
challenges in security and privacy for V2X communications,” IEEE
Open J. Veh. Technol., vol. 1, pp. 244–266, 2020.
[4] S. A. A. Hakeem, A. A. Hady, and H. Kim, “Current and future developments to improve 5G-NewRadio performance in vehicle-to-everything
communications,” Telecommun. Syst., vol. 75, no. 3, pp. 331–353,
Nov. 2020.
[5] H. M. Furqan, M. Sohaib J. Solaija, J. M. Hamamreh, and H. Arslan,
“Intelligent physical layer security approach for V2X communication,”
2019, arXiv:1905.05075.
[6] A. Ghosal and M. Conti, “Security issues and challenges in V2X: A
survey,” Comput. Netw., vol. 169, Mar. 2020, Art. no. 107093.
[7] D. Ulybyshev, A. O. Alsalem, B. Bhargava, S. Savvides, G. Mani,
and L. B. Othmane, “Secure data communication in autonomous V2X
systems,” in Proc. IEEE Int. Congr. Internet Things (ICIOT), Jul. 2018,
pp. 156–163.
[8] P. K. Mvula, P. Branco, G. V. Jourdan, and H. L. Viktor, “A survey
on the applications of semi-supervised learning to cyber-security,” ACM
Comput. Surv., vol. 56, no. 10, pp. 1–41, 2024.
[9] A. Selamnia, B. Brik, S. M. Senouci, A. Boualouache, and S. Hossain,
“Edge computing-enabled intrusion detection for C-V2X networks
using federated learning,” in Proc. IEEE Global Commun. Conf.
(GLOBECOM), Dec. 2022, pp. 2080–2085, doi: 10.1109/GLOBECOM48099.2022.10001675.
[10] H. Navidan et al., “Generative adversarial networks (GANs) in networking: A comprehensive survey & evaluation,” Comput. Netw., vol. 194,
Jul. 2021, Art. no. 108149.
[11] F. W. Alsaade and M. H. Al-Adhaileh, “Cyber attack detection for selfdriving vehicle networks using deep autoencoder algorithms,” Sensors,
vol. 23, no. 8, p. 4086, Apr. 2023.
[12] A. Boualouache, T. E. T. Djaidja, S. Senouci, and T. Engel,
“Deep learning-based intra-slice attack detection for 5G-V2X sliced
networks,” in Proc. IEEE 95th Vehicular Technol. Conf. (VTC2022Spring), Helsinki, Finland, 2022, pp. 1–5, doi: 10.1109/VTC2022Spring54318.2022.9860373.
[13] T. Sowmya and E. A. Mary Anita, “A comprehensive review of AI
based intrusion detection system,” Meas., Sensors, vol. 28, Aug. 2023,
Art. no. 100827.
[14] S. So, J. Petit, and D. Starobinski, “Physical layer plausibility checks
for misbehavior detection in V2X networks,” in Proc. 12th Conf. Secur.
Privacy Wireless Mobile Netw., Miami, FL, USA, May 2019, pp. 84–93.
[15] N. Bißmeyer, J. Njeukam, J. Petit, and K. M. Bayarou, “Central
misbehavior evaluation for VANETs based on mobility data plausibility,”
in Proc. 9th ACM Int. workshop Veh. Inter-Netw., Syst., Appl., Jun. 2012,
pp. 73–82.
[16] M. Sun, M. Li, and R. Gerdes, “A data trust framework for VANETs
enabling false data detection and secure vehicle tracking,” in Proc. IEEE
Conf. Commun. Netw. Secur. (CNS), Oct. 2017, pp. 1–9.
[17] Y. Yao et al., “Voiceprint: A novel Sybil attack detection method based
on RSSI for VANETs,” in Proc. 47th Annu. IEEE/IFIP Int. Conf.
Dependable Syst. Netw. (DSN), Jun. 2017, pp. 591–602.
[18] Q. A. Chen, Y. Yin, Y. Feng, Z. M. Mao, and H. X. Liu, “Exposing
congestion attack on emerging connected vehicle based traffic signal
control,” in Proc. Netw. Distrib. Syst. Secur. Symp., 2018, pp. 1–5.
[19] T. Zhang and Q. Zhu, “Distributed privacy-preserving collaborative
intrusion detection systems for VANETs,” IEEE Trans. Signal Inf.
Process. Netw., vol. 4, no. 1, pp. 148–161, Mar. 2018.
[20] J. Mahmood, Z. Duan, Y. Yang, Q. Wang, J. Nebhen, and
M. N. M. Bhutta, “Security in vehicular ad hoc networks: Challenges
and countermeasures,” Secur. Commun. Netw., vol. 2021, Jun. 2021,
Art. no. 9997771.

11199

[21] A. Irshad, M. Usman, S. A. Chaudhry, H. Naqvi, and M. Shafiq,
“A provably secure and efficient authenticated key agreement scheme
for energy internet-based vehicle-to-grid technology framework,” IEEE
Trans. Ind. Appl., vol. 56, no. 4, pp. 4425–4435, Jul. 2020.
[22] S. M. Faisal and T. Zaidi, “Timestamp-based detection of Sybil attack
in VANET,” Int. J. Netw. Secur., vol. 22, no. 3, pp. 399–410, 2020.
[23] K. Mahmood, J. Arshad, S. A. Chaudhry, and S. Kumari, “An
enhanced anonymous identity-based key agreement protocol for smart
grid advanced metering infrastructure,” Int. J. Commun. Syst., vol. 32,
no. 16, Nov. 2019, Art. no. e4137.
[24] Y. Mirsky, T. Doitshman, Y. Elovici, and A. Shabtai, “Kitsune: An
ensemble of autoencoders for online network intrusion detection,” 2018,
arXiv:1802.09089.
[25] S. Sharma, H. Sharma, and J. B. Sharma, “An adaptive color image
watermarking using RDWT-SVD and artificial bee colony based quality metric strength factor optimization,” Appl. Soft Comput., vol. 84,
Nov. 2019, Art. no. 105696.
[26] A. Nayyar, “Flying adhoc network (FANETs): Simulation based performance comparison of routing protocols: AODV, DSDV, DSR, OLSR,
AOMDV and HWMP,” in Proc. Int. Conf. Adv. Big Data, Comput. Data
Commun. Syst. (icABCD), Durban, South Africa, Aug. 2018, pp. 1–9.
[27] I. Naqvi, A. Chaudhary, and A. Rana, “Intrusion detection in VANETs,”
in Proc. 9th Int. Conf. Rel., INFOCOM Technol. Optim. (Trends Future
Directions) (ICRITO), Noida, India, Sep. 2021, pp. 1–5.
[28] M. Yao, X. Wang, Q. Gan, Y. Lin, and C. Huang, “An improved
and privacy-preserving mutual authentication scheme with forward
secrecy in VANETs,” Secur. Commun. Netw., vol. 2021, Apr. 2021,
Art. no. 6698099.
[29] J. Firl, H. Stübing, S. A. Huss, and C. Stiller, “MARV-X: Applying maneuver assessment for reliable verification of car-to-X mobility
data,” IEEE Trans. Intell. Transp. Syst., vol. 14, no. 3, pp. 1301–1312,
Sep. 2013.
[30] F. Guo et al., “Detecting vehicle anomaly in the edge via sensor
consistency and frequency characteristic,” IEEE Trans. Veh. Technol.,
vol. 68, no. 6, pp. 5618–5628, Jun. 2019.
[31] R. W. van der Heijden, S. Dietzel, T. Leinmüller, and F. Kargl, “Survey on misbehavior detection in cooperative intelligent transportation
systems,” IEEE Commun. Surveys Tuts., vol. 21, no. 1, pp. 779–811,
1st Quart., 2019.
[32] H. Zhu, K.-V. Yuen, L. Mihaylova, and H. Leung, “Overview of
environment perception for intelligent vehicles,” IEEE Trans. Intell.
Transp. Syst., vol. 18, no. 10, pp. 2584–2601, Oct. 2017.
[33] T. Zhou, R. R. Choudhury, P. Ning, and K. Chakrabarty, “P2DAP—
Sybil attacks detection in vehicular ad hoc networks,” IEEE J. Sel. Areas
Commun., vol. 29, no. 3, pp. 582–594, Mar. 2011.
[34] A. Abdelaziz, R. Burton, F. Barickman, J. Martin, J. Weston, and
C. E. Koksal, “Enhanced authentication based on angle of signal
arrivals,” IEEE Trans. Veh. Technol., vol. 68, no. 5, pp. 4602–4614,
May 2019.
[35] V.-L. Nguyen, P.-C. Lin, and R.-H. Hwang, “Multi-array relative positioning for verifying the truthfulness of V2X messages,” IEEE Commun.
Lett., vol. 23, no. 10, pp. 1704–1707, Oct. 2019.
[36] M. Naserian and A. Lewis, “Detecting misbehavior in vehicle-to-vehicle
communications,” U.S. Patent 9 865 168, Jan. 9, 2018.
[37] A. Talpur and M. Gurusamy, “Machine learning for security in vehicular
networks: A comprehensive survey,” IEEE Commun. Surveys Tuts.,
vol. 24, no. 1, pp. 346–379, 1st Quart., 2022.
[38] X. Sun, F. R. Yu, and P. Zhang, “A survey on cyber-security of connected
and autonomous vehicles (CAVs),” IEEE Trans. Intell. Transp. Syst.,
vol. 23, no. 7, pp. 6240–6259, Jul. 2022.
[39] M. Dibaei et al., “Attacks and defences on intelligent connected vehicles:
A survey,” Digit. Commun. Netw., vol. 6, no. 4, pp. 399–421, 2020.
[40] Z. Ying, K. Wang, J. Xiong, and M. Ma, “A literature review on V2X
communications security: Foundation, solutions, status, and future,” IET
Commun., vol. 18, no. 20, pp. 1683–1715, Dec. 2024.
[41] K. H. M. Gularte et al., “Safeguarding the V2X pathways: Exploring
the cybersecurity landscape through systematic review,” IEEE Access,
vol. 12, pp. 72871–72895, 2024.
[42] J. R. V. Solaas, N. Tuptuk, and E. Mariconti, “Systematic review:
Anomaly detection in connected and autonomous vehicles,” 2024,
arXiv:2405.02731.
[43] A. Boualouache and T. Engel, “A survey on machine learning-based
misbehavior detection systems for 5G and beyond vehicular networks,”
IEEE Commun. Surveys Tuts., vol. 25, no. 2, pp. 1128–1172, 2nd Quart.,
2023.

11200

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 8, AUGUST 2025

[44] F. Sakiz and S. Sen, “A survey of attacks and detection mechanisms
on intelligent transportation systems: VANETs and IoV,” Ad Hoc Netw.,
vol. 61, pp. 33–50, Jun. 2017.
[45] J. Nagarajan et al., “Machine learning based intrusion detection systems
for connected autonomous vehicles: A survey,” Peer-Peer Netw. Appl.,
vol. 16, no. 5, pp. 2153–2185, Sep. 2023.
[46] R. Sedar, C. Kalalas, F. Vázquez-Gallego, L. Alonso, and J. AlonsoZarate, “A comprehensive survey of V2X cybersecurity mechanisms and
future research paths,” IEEE Open J. Commun. Soc., vol. 4, pp. 325–391,
2023.
[47] S. Sharma and A. Kaul, “A survey on intrusion detection systems and
honeypot based proactive security mechanisms in VANETs and VANET
cloud,” Veh. Commun., vol. 12, pp. 138–164, Apr. 2018.
[48] F. Tang, Y. Kawamoto, N. Kato, and J. Liu, “Future intelligent and
secure vehicular network toward 6G: Machine-learning approaches,”
Proc. IEEE, vol. 108, no. 2, pp. 292–307, Feb. 2020.
[49] G. K. Rajbahadur, A. J. Malton, A. Walenstein, and A. E. Hassan,
“A survey of anomaly detection for connected vehicle cybersecurity
and safety,” in Proc. IEEE Intell. Vehicles Symp. (IV), Jun. 2018,
pp. 421–426.
[50] A. M. Alrehan and F. A. Alhaidari, “Machine learning techniques to
detect DDoS attacks on VANET system: A survey,” in Proc. 2nd Int.
Conf. Comput. Appl. Inf. Secur. (ICCAIS), May 2019, pp. 1–6.
[51] F. Gonçalves et al., “A systematic review on intelligent intrusion
detection systems for VANETs,” in Proc. 11th Int. Congr. Ultra Modern
Telecommun. Control Syst. Workshops (ICUMT), Oct. 2019, pp. 1–10.
[52] P. Asuquo et al., “Security and privacy in location-based services for
vehicular and mobile communications: An overview, challenges, and
countermeasures,” IEEE Internet Things J., vol. 5, no. 6, pp. 4778–4802,
Dec. 2018.
[53] L. Liang, H. Ye, and G. Y. Li, “Toward intelligent vehicular networks:
A machine learning framework,” IEEE Internet Things J., vol. 6, no. 1,
pp. 124–135, Feb. 2019.
[54] S. Kuutti, R. Bowden, Y. Jin, P. Barber, and S. Fallah, “A survey of
deep learning applications to autonomous vehicle control,” IEEE Trans.
Intell. Transp. Syst., vol. 22, no. 2, pp. 712–733, Feb. 2021.
[55] M. A. Hossain, R. M. Noor, K. A. Yau, S. R. Azzuhri, M. R. Z’aba, and
I. Ahmedy, “Comprehensive survey of machine learning approaches in
cognitive radio-based vehicular ad hoc networks,” IEEE Access, vol. 8,
pp. 78054–78108, 2020.
[56] Z. Lu, G. Qu, and Z. Liu, “A survey on recent advances in vehicular
network security, trust, and privacy,” IEEE Trans. Intell. Transp. Syst.,
vol. 20, no. 2, pp. 760–776, Feb. 2019.
[57] M. S. Sheikh and J. Liang, “A comprehensive survey on VANET
security services in traffic management system,” Wireless Commun.
Mobile Comput., vol. 2019, Sep. 2019, Art. no. 2423915.
[58] W. Tong, A. Hussain, W. X. Bo, and S. Maharjan, “Artificial intelligence for Vehicle-to-everything: A survey,” IEEE Access, vol. 7,
pp. 10823–10843, 2019.
[59] E. Farsimadan, L. Moradi, and F. Palmieri, “A review on security challenges in V2X communications technology for VANETs,” IEEE Access,
vol. 13, pp. 31069–31094, 2025, doi: 10.1109/ACCESS.2025.3541035.
[60] X. Zhang et al., “Vehicle-to-everything communication in intelligent
connected vehicles: A survey and taxonomy,” Automot. Innov., vol. 8,
no. 1, pp. 13–45, Feb. 2025.
[61] A. Maria, M. Biagi, and R. Cusani, “Smart vehicles, technologies
and main applications in vehicular ad hoc networks,” Veh. Technol.Deployment Appl., vol. 2013, pp. 3–20, Feb. 2013.
[62] S. Chen et al., “Vehicle-to-Everything (V2X) services supported by LTEbased systems and 5G,” IEEE Commun. Standards Mag., vol. 1, no. 2,
pp. 70–76, Feb. 2017.
[63] N. Xia and C.-S. Yang, “Vehicular communications: Standards and
challenges,” in Proc. 4th Int. Conf. Internet Vehicles. Technol. Services
Smart Cities (IOV), Kanazawa, Japan. Cham, Switzerland: Springer,
Jan. 2017, pp. 1–12.
[64] J. Kolleda et al., “National security credential management system
(SCMS) deployment support: SCMS baseline summary report,” U.S.
Dept. Transp. (USDOT), Intell. Transp. Syst. Joint Program Office (ITS
JPO), Washington, DC, USA, Tech. Rep. FHWA-JPO-18-686, 2018.
[65] R. D. Mushrall, M. D. Furtado, and H. Liu, “EmuLab of security
credential management system (SCMS) for vehicular communications,”
in Proc. IEEE 88th Veh. Technol. Conf. (VTC-Fall), Aug. 2018, pp. 1–5.
[66] S. A. Abdel Hakeem and H. Kim, “Centralized threshold key generation
protocol based on Shamir secret sharing and HMAC authentication,”
Sensors, vol. 22, no. 1, p. 331, Jan. 2022, doi: 10.3390/s22010331.

[67] M. Houmer, M. Ouaissa, and M. Ouaissa, “Secure authentication scheme
for 5G-based V2X communications,” Proc. Comput. Sci., vol. 198,
pp. 276–281, Sep. 2022.
[68] S. A. Abdel Hakeem and H. Kim, “Authentication and encryption
protocol with revocation and reputation management for enhancing 5GV2X security,” J. King Saud Univ.-Comput. Inf. Sci., vol. 35, no. 7,
Jul. 2023, Art. no. 101638, doi: 10.1016/j.jksuci.2023.101638.
[69] Y. Yang, Z. Wei, Y. Zhang, H. Lu, K.-K.-R. Choo, and H. Cai, “V2X
security: A case study of anonymous authentication,” Pervas. Mobile
Comput., vol. 41, pp. 259–269, Oct. 2017.
[70] J. Camenisch, M. Drijvers, A. Lehmann, G. Neven, and P. Towa, “Zone
encryption with anonymous authentication for V2V communication,”
in Proc. IEEE Eur. Symp. Secur. Privacy (EuroS&P), Sep. 2020,
pp. 405–424.
[71] M. Wu et al., “Research on certificate management and key management
of C-V2X security authentication technology in intelligent network
vehicle,” Proc. SPIE, vol. 12641, pp. 115–123, May 2023.
[72] G. Rigazzi, A. Tassi, R. J. Piechocki, T. Tryfonas, and A. Nix,
“Optimized certificate revocation list distribution for secure V2X communications,” in Proc. IEEE 86th Veh. Technol. Conf. (VTC-Fall),
Sep. 2017, pp. 1–7.
[73] W. Whyte, A. Weimerskirch, V. Kumar, and T. Hehn, “A security
credential management system for V2V communications,” in Proc. IEEE
Veh. Netw. Conf., Dec. 2013, pp. 1–8.
[74] T. Yoshizawa and B. Preneel, “A new approach to pseudonym certificate
management in V2X communication,” in Proc. IEEE Veh. Netw. Conf.
(VNC), Apr. 2023, pp. 25–32.
[75] T. Yoshizawa and B. Preneel, “On handling of certificate digest in V2X
communication,” in Proc. 18th Int. Conf. Wireless Mobile Comput.,
Netw. Commun. (WiMob), Oct. 2022, pp. 160–165.
[76] H. Aliev, H. Kim, and S. Choi, “A scalable and secure group key
management method for secure V2V communication,” Sensors, vol. 20,
no. 21, p. 6137, Oct. 2020.
[77] V. Sharma, I. You, and N. Guizani, “Security of 5G-V2X: Technologies,
standardization, and research directions,” IEEE Netw., vol. 34, no. 5,
pp. 306–314, Sep. 2020.
[78] S. A. Abdel Hakeem, M. A. Abd El-Gawad, and H. Kim, “A decentralized lightweight authentication and privacy protocol for vehicular
networks,” IEEE Access, vol. 7, pp. 119689–119705, 2019.
[79] S. Anbalagan, G. Raja, S. Gurumoorthy, R. D. Suresh, and K. Dev,
“IIDS: Intelligent intrusion detection system for sustainable development
in autonomous vehicles,” IEEE Trans. Intell. Transp. Syst., vol. 24,
no. 12, pp. 15866–15875, Dec. 2023.
[80] E. S. Ali et al., “Machine learning technologies for secure vehicular
communication in Internet of Vehicles: Recent advances and applications,” Secur. Commun. Netw., vol. 2021, Mar. 2021, Art. no. 8868355.
[81] N. Trkulja, D. Starobinski, and R. A. Berry, “Denial-of-Service attacks
on C-V2X networks,” 2020, arXiv:2010.13725.
[82] SolarMainframe. IDS Intrusion CSV. Accessed: Apr. 25, 2025. [Online].
Available:
https://www.kaggle.com/datasets/solarmainframe/idsintrusion-csv
[83] M. N. Saulaiman, M. Kozlovszky, and Á. Csilling, “A survey on
vulnerabilities and classification of cyber-attacks on 5G-V2X,” in Proc.
IEEE 21st Int. Symp. Comput. Intell. Informat. (CINTI), Nov. 2021,
pp. 000235–000240.
[84] N. Mazher, M. Alhadaad, and O. Shagdar, “A brief summary of
cybersecurity attacks in V2X communicationm,” Nat. Renew. Energy
Lab. (NREL), Golden, CO, USA, Tech. Rep., 2022.
[85] S. A. Abdel Hakeem, A. A. Hady, and H. Kim, “5G-V2X: Standardization, architecture, use cases, network-slicing, and edge-computing,”
Wireless Netw., vol. 26, no. 8, pp. 6015–6041, Nov. 2020.
[86] M. A. Mohiuddin, K. Nirosha, D. Anusha, M. Nazeer, G. R. Nv, and
S. Lakhanpal, “AI to V2X privacy and security issues in autonomous
vehicles: Survey,” MATEC Web Erences, vol. 392, Jan. 2024,
Art. no. 01097.
[87] S. Ullah et al., “TNN-IDS: Transformer neural network-based intrusion
detection system for MQTT-enabled IoT networks,” Comput. Netw.,
vol. 237, Dec. 2023, Art. no. 110072.
[88] M. Muhammad and G. A. Safdar, “Survey on existing authentication
issues for cellular-assisted V2X communication,” Veh. Commun., vol. 12,
pp. 50–65, Apr. 2018.
[89] S. A. A. Hakeem, S. M. A. El-Kader, and H. Kim, “A key management protocol based on the hash chain key generation for securing
LoRaWAN networks,” Sensors, vol. 21, no. 17, p. 5838, Aug. 2021,
doi: 10.3390/s21175838.

HAKEEM AND KIM: ADVANCING INTRUSION DETECTION IN V2X NETWORKS: A COMPREHENSIVE SURVEY

[90] S. A. A. Hakeem, H. H. Hussein, and H. Kim, “Security requirements
and challenges of 6G technologies and applications,” Sensors, vol. 22,
no. 5, p. 1969, Mar. 2022, doi: 10.3390/s22051969.
[91] S. Taha and X. Shen, “Lightweight group authentication with dynamic
vehicle-clustering for 5G-based V2X communications,” in Proc. IEEE
Global Commun. Conf. (GLOBECOM), Dec. 2018, pp. 1–6.
[92] P. Sharma, D. Austin, and H. Liu, “Attacks on machine learning:
Adversarial examples in connected and autonomous vehicles,” in Proc.
IEEE Int. Symp. Technol. Homeland Secur. (HST), Woburn, MA, USA,
Nov. 2019, pp. 1–7, doi: 10.1109/HST47167.2019.9032989.
[93] R. Sedar, C. Kalalas, F. Vázquez-Gallego, and J. Alonso-Zárate, “Deep
reinforcement learning-based adversarial defense in vehicular communication systems,” in Proc. IEEE Int. Conf. Commun. (ICC), Jun. 2024,
pp. 5250–5256, doi: 10.1109/icc51166.2024.10622762.
[94] Z. H. Khattak, B. L. Smith, and M. D. Fontaine, “Cyberattack monitoring architectures for resilient operation of connected and automated
vehicles,” IEEE Open J. Intell. Transp. Syst., vol. 5, pp. 322–341, 2024,
doi: 10.1109/OJITS.2024.3391830.
[95] A. Kurakin, I. J. Goodfellow, and S. Bengio, “Adversarial examples in
the physical world,” in Proc. 5th Int. Conf. Learn. Represent., Toulon,
France, 2017, pp. 1–14.
[96] A. Lad, R. Bhale, and S. Belgamwar, “Fast gradient sign method
(FGSM) variants in white box settings: A comparative study,” in
Proc. Int. Conf. Inventive Comput. Technol. (ICICT), Lalitpur, Nepal,
Apr. 2024, pp. 382–386, doi: 10.1109/icict60155.2024.10544606.
[97] J. Zhang, W. Qian, R. Nie, J. Cao, and D. Xu, “Generate adversarial
examples by adaptive moment iterative fast gradient sign method,” Int.
J. Speech Technol., vol. 53, no. 1, pp. 1101–1114, Jan. 2023, doi:
10.1007/s10489-022-03437-z.
[98] L. He, Z. Wang, S. Yang, T. Liu, and Y. Huang, “Generalizing projected
gradient descent for deep-learning-aided massive MIMO detection,”
IEEE Trans. Wireless Commun., vol. 23, no. 3, pp. 1827–1839,
Mar. 2024.
[99] Y. A. Ergu et al., “Efficient adversarial attacks against DRL-based
resource allocation in intelligent O-RAN for V2X,” IEEE Trans. Veh.
Technol., vol. 74, no. 1, pp. 1674–1686, Jan. 2025.
[100] S. Soltani, M. Shojafar, A. Brighente, M. Conti, and R. Tafazolli,
“Poisoning bearer context migration in O-RAN 5G network,” IEEE
Wireless Commun. Lett., vol. 12, no. 3, pp. 401–405, Mar. 2023.
[101] S. A. A. Hakeem, H. H. Hussein, and H. Kim, “Vision and research
directions of 6G technologies and applications,” J. King Saud Univ.Comput. Inf. Sci., vol. 34, no. 6, pp. 2419–2442, Jun. 2022, doi:
10.1016/j.jksuci.2022.03.019.
[102] A. Alshammari, M. A. Zohdy, D. Debnath, and G. Corser, “Classification approach for intrusion detection in vehicle systems,” Wireless Eng.
Technol., vol. 9, no. 4, pp. 79–94, 2018.
[103] G.
Karopoulos,
G.
Kambourakis,
E.
Chatzoglou,
J. L. Hernández-Ramos, and V. Kouliaridis, “Demystifying in-vehicle
intrusion detection systems: A survey of surveys and a meta-taxonomy,”
Electronics, vol. 11, no. 7, p. 1072, Mar. 2022.
[104] F. Gonçalves, J. Macedo, and A. Santos, “Intelligent hierarchical
intrusion detection system for VANETs,” in Proc. 13th Int. Congr. Ultra
Modern Telecommun. Control Syst. Workshops (ICUMT), Oct. 2021,
pp. 50–59.
[105] B. Lampe and W. Meng, “Intrusion detection in the automotive domain:
A comprehensive review,” IEEE Commun. Surveys Tuts., vol. 25, no. 4,
pp. 2356–2426, 4th Quart., 2023.
[106] G. Raja et al., “AI-empowered trajectory anomaly detection and classification in 6G-V2X,” IEEE Trans. Intell. Transp. Syst., vol. 24, no. 4,
pp. 4599–4607, Apr. 2023.
[107] D. Man, F. Zeng, J. Lv, S. Xuan, W. Yang, and M. Guizani, “AI-based
intrusion detection for intelligence Internet of Vehicles,” IEEE Consum.
Electron. Mag., vol. 12, no. 1, pp. 109–116, Jan. 2023.
[108] S. Rajapaksha, H. Kalutarage, M. O. Al-Kadri, A. Petrovski,
G. Madzudzo, and M. Cheah, “AI-based intrusion detection systems for
in-vehicle networks: A survey,” ACM Comput. Surv., vol. 55, no. 11,
pp. 1–40, Nov. 2023.
[109] W. Gou, H. Zhang, and R. Zhang, “Multi-classification and tree-based
ensemble network for the intrusion detection system in the Internet of
Vehicles,” Sensors, vol. 23, no. 21, p. 8788, Oct. 2023.
[110] T. Schlegl, P. Seeböck, S. M. Waldstein, U. Schmidt-Erfurth, and
G. Langs, Unsupervised Anomaly Detection With Generative Adversarial
Networks To Guide Marker Discovery. Cham, Switzerland: Springer,
Jan. 2017, pp. 146–157.

11201

[111] W. Xu, J. Jang-Jaccard, A. Singh, Y. Wei, and F. Sabrina, “Improving
performance of autoencoder-based network anomaly detection on NSLKDD dataset,” IEEE Access, vol. 9, pp. 140136–140146, 2021.
[112] M. S. Amir et al., “Efficient & sustainable intrusion detection system
using machine learning & deep learning for IoT,” in Proc. 4th Int. Conf.
Comput., Math. Eng. Technol., May 2023, pp. 1–6.
[113] F. A. Khan, A. Gumaei, A. Derhab, and A. Hussain, “A novel twostage deep learning model for efficient network intrusion detection,”
IEEE Access, vol. 7, pp. 30373–30385, 2019.
[114] K. Kim, M. E. Aminanto, and H. C. Tanuwidjaja, Network Intrusion
Detection Using Deep Learning: A Feature Learning Approach. Cham,
Switzerland: Springer, 2018.
[115] C. Zhang, D. Jia, L. Wang, W. Wang, F. Liu, and A. Yang, “Comparative research on network intrusion detection methods based on machine
learning,” Comput. Secur., vol. 121, Oct. 2022, Art. no. 102861.
[116] J. Grover, N. K. Prajapati, V. Laxmi, and M. S. Gaur, “Machine
learning approach for multiple misbehavior detection in VANET,”
in Advanced Computational and Communication Paradigms. Berlin,
Germany: Springer, 2011, pp. 644–653.
[117] S. Y. Wang and C. L. Chou, “NCTUns 5.0 network simulator for
advanced wireless vehicular network researches,” in Proc. 10th Int.
Conf. Mobile Data Manage., Syst., Services Middleware, May 2009,
pp. 375–376.
[118] W. Li, A. Joshi, and T. Finin, “SVM-CASE: An SVM-based context
aware security framework for vehicular ad-hoc networks,” in Proc. IEEE
82nd Veh. Technol. Conf. (VTC-Fall), Sep. 2015, pp. 1–5.
[119] M. Sarhan, S. Layeghy, N. Moustafa, M. Gallagher, and M. Portmann,
“Feature extraction for machine learning-based intrusion detection in
IoT networks,” 2021, arXiv:2108.12722.
[120] L. Yang, A. Moubayed, and A. Shami, “MTH-IDS: A multitiered
hybrid intrusion detection system for Internet of Vehicles,” IEEE Internet
Things J., vol. 9, no. 1, pp. 616–632, Jan. 2022.
[121] H. Sedjelmaci and S. M. Senouci, “An accurate and efficient collaborative intrusion detection framework to secure vehicular networks,”
Comput. Elect. Eng., vol. 43, pp. 33–47, Apr. 2015.
[122] Y. Li, F. Li, and J. Song, “The research of random forest intrusion
detection model based on optimization in Internet of Vehicles,” J. Phys.,
Conf. Ser., vol. 1757, no. 1, Jan. 2021, Art. no. 012149.
[123] E. A. Shams, A. Rizaner, and A. H. Ulusoy, “Trust aware support
vector machine intrusion detection and prevention system in vehicular
ad hoc networks,” Comput. Secur., vol. 78, pp. 245–254, Sep. 2018.
[124] A. Shenfield, D. Day, and A. Ayesh, “Intelligent intrusion detection
systems using artificial neural networks,” ICT Exp., vol. 4, no. 2,
pp. 95–99, 2018.
[125] S. Mane and D. Rao, “Explaining network intrusion detection system
using explainable AI framework,” 2021, arXiv:2103.07110.
[126] G. Zhao, C. Zhang, and L. Zheng, “Intrusion detection using deep
belief network and probabilistic neural network,” in Proc. IEEE Int.
Conf. Comput. Sci. Eng. (CSE) IEEE Int. Conf. Embedded Ubiquitous
Comput. (EUC), vol. 1, Jul. 2017, pp. 639–642.
[127] A. Alsaedi, N. Moustafa, Z. Tari, A. Mahmood, and A. Anwar,
“TON_IoT telemetry dataset: A new generation dataset of IoT and
IIoT for data-driven intrusion detection systems,” IEEE Access, vol. 8,
pp. 165130–165150, 2020.
[128] A. R. Gad, A. A. Nashat, and T. M. Barkat, “Intrusion detection system
using machine learning for vehicular ad hoc networks based on ToN-IoT
dataset,” IEEE Access, vol. 9, pp. 142206–142217, 2021.
[129] J. Grover, V. Laxmi, and M. S. Gaur, “Misbehavior detection based on
ensemble learning in VANET,” in Proc. Adv. Comput. Commun. Secur.,
Jan. 2012, pp. 602–611.
[130] P. K. Singh, S. Gupta, R. Vashistha, S. K. Nandi, and S. Nandi,
“Machine learning-based approach to detect position falsification
attack in VANETs,” in Security Privacy. Singapore: Springer, 2019,
pp. 166–178.
[131] R. W. van der Heijden, T. Lukaseder, and F. Kargl, “VeReMi: A
dataset for comparable evaluation of misbehavior detection in VANETs,”
in Security Privacy Communication Networks. Cham, Switzerland:
Springer, 2018, pp. 318–337.
[132] S. So, P. Sharma, and J. Petit, “Integrating plausibility checks and
machine learning for misbehavior detection in VANET,” in Proc. 17th
IEEE Int. Conf. Mach. Learn. Appl. (ICMLA), Dec. 2018, pp. 564–571.
[133] O. A. Wahab, A. Mourad, H. Otrok, and J. Bentahar, “CEAP:
SVM-based intelligent detection model for clustered vehicular ad hoc
networks,” Exp. Syst. Appl., vol. 50, pp. 40–54, May 2016.

11202

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 8, AUGUST 2025

[134] S. Gyawali, Y. Qian, and R. Q. Hu, “Machine learning and reputation
based misbehavior detection in vehicular communication networks,”
IEEE Trans. Veh. Technol., vol. 69, no. 8, pp. 8871–8885, Aug. 2020.
[135] F. Hawlader, A. Boualouache, S. Faye, and T. Engel, “Intelligent
misbehavior detection system for detecting false position attacks in
vehicular networks,” in Proc. IEEE Int. Conf. Commun. Workshops
(ICC), Aug. 2021, pp. 1–6.
[136] A. Sharma and A. Jaekel, “Machine learning based misbehaviour
detection in VANET using consecutive BSM approach,” IEEE Open
J. Veh. Technol., vol. 3, pp. 1–14, 2022.
[137] S. Ercan, M. Ayaida, and N. Messai, “Misbehavior detection for
position falsification attacks in VANETs using machine learning,” IEEE
Access, vol. 10, pp. 1893–1904, 2022.
[138] Z. Yang, K. Zhang, L. Lei, and K. Zheng, “A novel classifier exploiting
mobility behaviors for Sybil detection in connected vehicle systems,”
IEEE Internet Things J., vol. 6, no. 2, pp. 2626–2636, Apr. 2019.
[139] S. Tariq, S. Lee, and S. S. Woo, “CANTransfer: Transfer learning based
intrusion detection on a controller area network using convolutional
LSTM network,” in Proc. 35th Annu. ACM Symp. Appl. Comput.,
Mar. 2020, pp. 1048–1055.
[140] K. A. Tait et al., “Intrusion detection using machine learning techniques: An experimental comparison,” 2021, arXiv:2105.13435.
[141] A. Rosay, E. Cheval, F. Carlier, and P. Leroux, “CIC-IDS2017 dataset
report,” Canadian Inst. Cybersecurity (CIC), Univ. New Brunswick,
Fredericton, NB, Canada, Tech. Rep., 2022.
[142] M. Almi’ani, A. A. Ghazleh, A. Al-Rahayfeh, and A. Razaque,
“Intelligent intrusion detection system using clustered self organized
map,” in Proc. 5th Int. Conf. Softw. Defined Syst. (SDS), Barcelona,
Spain, Apr. 2018, pp. 138–144.
[143] L. A. Maglaras, “A novel distributed intrusion detection system for
vehicular ad hoc networks,” Int. J. Adv. Comput. Sci. Appl., vol. 6, no. 4,
pp. 101–106, 2015.
[144] M. E. Verma et al., “A comprehensive guide to CAN IDS data and
introduction of the ROAD dataset,” 2020, arXiv:2012.14600.
[145] F. A. Alhaidari and A. M. Alrehan, “A simulation work for generating a novel dataset to detect distributed denial of service attacks
on vehicular ad hoc NETwork systems,” Int. J. Distrib. Sensor
Netw., vol. 17, no. 3, Mar. 2021, Art. no. 155014772110002, doi:
10.1177/15501477211000287.
[146] Veremi Dataset. Accessed: Apr. 25, 2025. [Online]. Available:
https://veremi-dataset.github.io/
[147] R. Rahal, A. A. Korba, and N. Ghoualmi-Zine, “Towards the development of realistic DoS dataset for intelligent transportation systems,”
Wireless Pers. Commun., vol. 115, no. 2, pp. 1415–1444, Nov. 2020,
doi: 10.1007/s11277-020-07635-1.
[148] S. Kumar, Sunanda, and S. Arora, “A statistical analysis on KDD
cup’99 dataset for the network intrusion detection system,” in Applied
Soft Computing and Communication Networks, vol. 125, S. M. Thampi,
Ed., Singapore: Springer, 2020, pp. 83–92.
[149] H. P. Vinutha and B. Poornima, “Analysis of NSL-KDD dataset using
K-means and canopy clustering algorithms based on distance metrics,” in
Integrated Intelligent Computing, Communication and Security, vol. 771.
Singapore: Springer, 2019, pp. 239–248.
[150] N. Moustafa, “ToN_IoT datasets,” IEEE Dataport, Piscataway, NJ,
USA, Tech. Rep., Oct. 2019, doi: 10.21227/fesz-dm97.
[151] Can.
Inst.
Cybersecurity.
(2028).
Intrusion
Detection
Evaluation Dataset (CSE-CIC-IDS2018). [Online]. Available:
https://www.unb.ca/cic/datasets/ids-2018.html
[152] The UNSW-NB15 Dataset. Accessed: Jul. 10, 2024. [Online]. Available:
https://research.unsw.edu.au/projects/unsw-nb15-dataset
[153] N. Moustafa and J. Slay, “The evaluation of network anomaly detection
systems: Statistical analysis of the UNSW-NB15 data set and the comparison with the KDD99 data set,” Inf. Secur. J., A Global Perspective,
vol. 25, nos. 1–3, pp. 18–31, Apr. 2016.
[154] M. Al-Hawawreh, E. Sitnikova, and N. Aboutorab, “X-IIoTID: A
connectivity- and device-agnostic intrusion dataset for industrial Internet
of Things,” IEEE Dataport, Piscataway, NJ, USA„ Tech. Rep., Jul. 2021,
doi: 10.21227/mpb6-py55.
[155] S. T. Banafshehvaragh and A. M. Rahmani, “Intrusion, anomaly, and
attack detection in smart vehicles,” Microprocessors Microsyst., vol. 96,
Feb. 2023, Art. no. 104726.
[156] CAN Dataset for intrusion detection (OTIDS). Accessed: Jan. 18, 2024.
[Online]. Available: https://ocslab.hksecurity.net/Dataset/CAN-intrusiondataset

[157] Car-Hacking Dataset. Accessed: Oct. 18, 2024. [Online]. Available:
https://ocslab.hksecurity.net/Datasets/car-hacking-dataset
[158] S. Burschka and B. Dupasquier, “Tranalyzer: Versatile high performance network traffic analyser,” in Proc. IEEE Symp. Ser. Comput.
Intell. (SSCI), Dec. 2016, pp. 1–8.
[159] A. Azab, M. Khasawneh, S. Alrabaee, K.-K.-R. Choo, and M.
Sarsour, “Network traffic classification: Techniques, datasets, and
challenges,” Digit. Commun. Netw., vol. 10, no. 3, pp. 676–692,
Jun. 2024.
[160] E. Moradi-Pari, D. Tian, M. Bahramgiri, S. Rajab, and S. Bai, “DSRC
versus LTE-V2X: Empirical performance analysis of direct vehicular
communication technologies,” IEEE Trans. Intell. Transp. Syst., vol. 24,
no. 5, pp. 4889–4903, May 2023.
[161] N. T. Tangirala, A. Abraham, A. Choudhury, P. Vyas, R. Zhang,
and J. Dauwels, “Analysis of packet drops and channel crowding in
vehicle platooning using V2X communication,” in Proc. IEEE Symp.
Ser. Comput. Intell. (SSCI), Nov. 2018, pp. 281–286.
[162] H. B. McMahan, E. Moore, D. Ramage, S. Hampson, and
B. A. Y. Arcas, “Communication-efficient learning of deep networks
from decentralized data,” in Proc. 20th AISTATS, Fort Lauderdale, FL,
USA, Jan. 2016, pp. 1–8.
[163] T. Li et al., “Federated optimization in heterogeneous networks,” in
Proc. 3rd MLSys Conf., Austin, TX, USA, 2020, pp. 1–13.
[164] R. Song, L. Zhou, V. Lakshminarasimhan, A. Festag, and A. Knoll,
“Federated learning framework coping with hierarchical heterogeneity
in cooperative ITS,” in Proc. IEEE 25th Int. Conf. Intell. Transp. Syst.
(ITSC), Macau, China, Oct. 2022, pp. 3502–3508.
[165] S. Narkedimilli et al., “FL-DECO-BC: A privacy-preserving, secure,
and provenance-preserving Fl framework with blockchain for VANETs,”
2024, arXiv:2407.21141.
[166] L. Alekszejenko et al., “A V2X-based privacy-preserving federated
learning system,” 2024, arXiv:2401.13848.
[167] H. Korba, “Federated learning-based intrusion detection in vehicular
networks,” IEEE Trans. Veh. Technol., vol. 73, no. 2, pp. 2456–2472,
Feb. 2024.
[168] Y. Zhou, “Privacy-preserving federated learning for autonomous vehicles,” IEEE Internet Things J., vol. 11, no. 5, pp. 6783–6797, May 2024.
[169] X. Li, “Federated intrusion detection for V2X networks: Challenges
and solutions,” Comput. Netw., vol. 225, Jul. 2024, Art. no. 109835.
[170] J. Huang, “An execution & evaluation dual-network FL framework for
edge security in IoT,” IEEE Trans. Dependable Secure Comput., vol. 21,
no. 1, pp. 89–102, Jan. 2024.
[171] M. Raza, “SDN-enabled federated learning for secure V2X communication,” IEEE Trans. Mobile Comput., vol. 23, no. 3, pp. 1347–1361,
Mar. 2024.
[172] X. Chen, W. Qiu, L. Chen, Y. Ma, and J. Ma, “Fast and practical intrusion detection system based on federated learning for
VANET,” Comput. Secur., vol. 142, Jul. 2024, Art. no. 103881, doi:
10.1016/j.cose.2024.103881.
[173] K. Huang, R. Xian, M. Xian, H. Wang, and L. Ni, “A comprehensive intrusion detection method for the Internet of Vehicles based on
federated learning architecture,” Comput. Secur., vol. 147, Dec. 2024,
Art. no. 104067, doi: 10.1016/j.cose.2024.104067.
[174] A. Renda et al., “Federated learning of explainable AI models in 6G
systems: Towards secure and automated vehicle networking,” Information, vol. 13, no. 8, p. 395, Aug. 2022, doi: 10.3390/info13080395.
[175] M. Doostmohammadian, H. Zarrabi, H. R. Rabiee, U. A. Khan,
and T. Charalambous, “Distributed detection and mitigation of biasing
attacks over multi-agent networks,” IEEE Trans. Netw. Sci. Eng., vol. 8,
no. 4, pp. 3465–3477, Oct. 2021, doi: 10.1109/TNSE.2021.3115032.
[176] P. H. Mirzaee, M. Shojafar, H. Bagheri, T. H. Chan, H. Cruickshank,
and R. Tafazolli, “A two-layer collaborative vehicle-edge intrusion
detection system for vehicular communications,” in Proc. IEEE 94th
Veh. Technol. Conf. (VTC-Fall), Norman, OK, USA, Sep. 2021, pp. 1–6,
doi: 10.1109/VTC2021-Fall52928.2021.9625388.
[177] D. J. Yeong, K. Panduru, and J. Walsh, “Exploring the unseen: A
survey of multi-sensor fusion and the role of explainable AI (XAI) in
autonomous vehicles,” Sensors, vol. 25, no. 3, p. 856, Jan. 2025, doi:
10.3390/s25030856.
[178] M. Doostmohammadian and T. Charalambous, “Distributed anomaly
detection and estimation over sensor networks: Observationalequivalence and Q-redundant observer design,” in Proc. Eur. Control Conf. (ECC), London, U.K., Jul. 2022, pp. 460–465, doi:
10.23919/ECC55457.2022.9838396.

HAKEEM AND KIM: ADVANCING INTRUSION DETECTION IN V2X NETWORKS: A COMPREHENSIVE SURVEY

[179] M. Zabihi, R. V. Mehrizi, A. Kasaiezadeh, M. Pirani, and A. Khajepour,
“A hybrid model-data vehicle sensor and actuator fault detection and
diagnosis system,” IEEE Trans. Intell. Transp. Syst., vol. 25, no. 7,
pp. 8121–8133, Jul. 2024.
[180] X. He, X. Ren, H. Sandberg, and K. H. Johansson, “How
to secure distributed filters under sensor attacks,” IEEE Trans.
Autom. Control, vol. 67, no. 6, pp. 2843–2856, Jun. 2022, doi:
10.1109/TAC.2021.3092603.
[181] M. Doostmohammadian and H. R. Rabiee, “Distributed observer design
for tracking platoon of connected and autonomous vehicles,” 2025,
arXiv:2501.18890.
[182] K. Samy, “Edge AI-based real-time intrusion detection for smart vehicles,” IEEE Trans. Intell. Transp. Syst., vol. 25, no. 4, pp. 3401–3416,
May 2024.
[183] T. Alladi, “MEC-enabled intrusion detection systems for secure
V2X networks,” IEEE Trans. Netw. Service Manage., vol. 21, no. 2,
pp. 211–226, Feb. 2024.
[184] M. Hasan, “Lightweight federated learning for energy-efficient IoT
security,” IEEE Access, vol. 12, pp. 7456–7472, 2024.
[185] H. Bangui, “Hybrid AI-driven security mechanism for V2X networks,” ACM Trans. Cyber-Phys. Syst., vol. 8, no. 1, pp. 56–72,
2024.
[186] M. Rihan, M. Elwekeil, Y. Yang, L. Huang, C. Xu, and M. M. Selim,
“Deep-VFog: When artificial intelligence meets fog computing in V2X,”
IEEE Syst. J., vol. 15, no. 3, pp. 3492–3505, Sep. 2021.
[187] K. L. Williams, Y. D. Prasanth, and M. Jeyaselvi, “Hybrid AI architecture using edge-cloud computing for secure V2X communication,”
in Proc. 9th Int. Conf. Commun. Electron. Syst. (ICCES), Dec. 2024,
pp. 913–920, doi: 10.1109/icces63552.2024.10859430.
[188] C. Zhang, X. Liu, X. Zheng, R. Li, and H. Liu, “FengHuoLun:
A federated learning based edge computing platform for cyberphysical systems,” in Proc. Int. Conf. Pervasive Comput. Commun.
(PerCom) Workshops, 2020, pp. 1–4, doi: 10.1109/PerComWorkshops48775.2020.9156259.
[189] M. M. Moussa and L. Alazzawi, “A hybrid deep learning cyber-attacks
intrusion detection system for CAV path planning,” in Proc. IEEE Int.
Midwest Symp. Circuits Syst. (MWSCAS), Aug. 2021, pp. 607–610, doi:
10.1109/MWSCAS47672.2021.9531858.
[190] A. Patel, M. Bhavsar, and K. Roy, “Enchanced CAV security
using machine learning,” in Proc. Int. Conf. Artif. Intell., Big Data,
Comput. Data Commun. Syst. (icABCD), Aug. 2024, pp. 1–6, doi:
10.1109/icabcd62167.2024.10645287.
[191] M. Kim, I. Oh, K. Yim, M. Sahlabadi, and Z. Shukur, “Security
of 6G-enabled vehicle-to-everything communication in emerging federated learning and blockchain technologies,” IEEE Access, vol. 12,
pp. 33972–34001, 2024, doi: 10.1109/ACCESS.2023.3348409.
[192] M. Yoshida, K. Mori, T. Inoue, and H. Tanaka, “EdgeRE: An edge
computing-enhanced network redundancy elimination service for connected cars,” in Proc. 6th Int. Conf. Fog Mobile Edge Comput. (FMEC),
Dec. 2021, pp. 1–6, doi: 10.1109/FMEC54266.2021.9732548.
[193] M. A. Khan et al., “Robust, resilient and reliable architecture for
V2X communications,” IEEE Trans. Intell. Transp. Syst., vol. 22, no. 7,
pp. 4414–4430, Jul. 2021.
[194] V. Rishiwal, U. Agarwal, A. Alotaibi, S. Tanwar, P. Yadav, and
M. Yadav, “Exploring secure V2X communication networks for humancentric security and privacy in smart cities,” IEEE Access, vol. 12,
pp. 138763–138788, 2024, doi: 10.1109/ACCESS.2024.3467002.
[195] H. Ibn-Khedher, M. Laroui, H. Moungla, H. Afifi, and
E. Abd-Elrahman, “Next-generation edge computing assisted
autonomous driving based artificial intelligence algorithms,”
IEEE
Access,
vol.
10,
pp. 53987–54001,
2022,
doi:
10.1109/ACCESS.2022.3174548.
[196] N. Albogami, “Intelligent deep federated learning model for enhancing
security in Internet of Things enabled edge computing environment,”
Sci. Rep., vol. 15, no. 1, p. 4041, Feb. 2025, doi: 10.1038/s41598-02588163-5.
[197] R. Taslimasa, “ImageFed: Federated learning for cyberattack detection
in autonomous vehicles,” IEEE Trans. Artif. Intell., vol. 5, no. 3,
pp. 312–328, Mar. 2024.
[198] D. Bhavsar, “Blockchain-enhanced federated learning for secure
vehicular networks,” IEEE Trans. Inf. Forensics Security, vol. 19,
pp. 1458–1473, 2024.

11203

[199] D. Swessi and H. Idoudi, “A comparative review of security threats
datasets for vehicular networks,” in Proc. Int. Conf. Innov. Intell.
Informat., Comput., Technol. (3ICT), Manama, Bahrain, Sep. 2021,
pp. 746–751, doi: 10.1109/3ICT53449.2021.9581683.
[200] K. Geeta and K. Gulshan, “Machine learning and deep learning methods for intrusion detection systems: Recent developments
and challenges,” Soft Comput., vol. 25, no. 15, pp. 9731–9763,
2021.
[201] P. Vijayakumar, M. Azees, A. Kannan, and L. J. Deborah, “Dual
authentication and key management techniques for secure data transmission in vehicular ad hoc networks,” IEEE Trans. Intell. Transp. Syst.,
vol. 17, no. 4, pp. 1015–1028, Apr. 2016.
[202] G. Loukas, T. Vuong, R. Heartfield, G. Sakellari, Y. Yoon, and D. Gan,
“Cloud-based cyber-physical intrusion detection for vehicles using deep
learning,” IEEE Access, vol. 6, pp. 3491–3508, 2018.
[203] A. Rosay, F. Carlier, and P. Leroux, “Feed-forward neural network for
network intrusion detection,” in Proc. IEEE 91st Veh. Technol. Conf.
(VTC-Spring), May 2020, pp. 1–6.
[204] O. Y. Al-Jarrah, C. Maple, M. Dianati, D. Oxtoby, and A. Mouzakitis,
“Intrusion detection systems for intra-vehicle networks: A review,” IEEE
Access, vol. 7, pp. 21266–21289, 2019.
[205] F. A. Ghaleb et al., “Misbehavior-aware on-demand collaborative intrusion detection system using distributed ensemble learning for VANET,”
Electronics, vol. 9, no. 9, p. 1411, 2020.
[206] A. Thakkar and R. Lohiya, “A review on machine learning and deep
learning perspectives of IDS for IoT: Recent updates, security issues, and
challenges,” Arch. Comput. Methods Eng., vol. 28, no. 4, pp. 3211–3243,
Jun. 2021.
[207] M. Aloqaily, S. Otoum, I. A. Ridhawi, and Y. Jararweh, “An intrusion
detection system for connected vehicles in smart cities,” Ad Hoc Netw.,
vol. 90, Jul. 2019, Art. no. 101842.
[208] Q. He, X. Meng, R. Qu, and R. Xi, “Machine learning-based detection for cybersecurity attacks on connected and autonomous vehicles,”
Mathematics, vol. 8, no. 8, p. 1311, 2020.
[209] N. Thapa, Z. Liu, D. B. Kc, B. Gokaraju, and K. Roy, “Comparison
of machine learning and deep learning models for network intrusion
detection systems,” Future Internet, vol. 12, no. 10, p. 167, Sep. 2020.
[210] L. Vu, Q. U. Nguyen, D. N. Nguyen, D. T. Hoang, and E. Dutkiewicz,
“Deep transfer learning for IoT attack detection,” IEEE Access, vol. 8,
pp. 107335–107344, 2020.
[211] A. Samy, H. Yu, and H. Zhang, “Fog-based attack detection framework
for Internet of Things using deep learning,” IEEE Access, vol. 8,
pp. 74571–74585, 2020.
[212] M. Roopak, G. Y. Tian, and J. Chambers, “Multi-objective-based
feature selection for DDoS attack detection in IoT networks,” IET Netw.,
vol. 9, no. 3, pp. 120–127, May 2020.
[213] H. Taslimasa et al., “ImageFed: Practical privacy preserving intrusion
detection system for in-vehicle CAN bus protocol,” in Proc. IEEE IEEE
9th Intl. Conf. Big Data Secur. Cloud (BigDataSecurity) Intl. Conf. High
Perform. Smart Comput., (HPSC) IEEE Intl. Conf. Intell. Data Secur.
(IDS), May 2023, pp. 122–129.
[214] G. Bovenzi, G. Aceto, D. Ciuonzo, V. Persico, and A. Pescapé, “A
hierarchical hybrid intrusion detection approach in IoT scenarios,” in
Proc. IEEE Global Commun. Conf. (GLOBECOM), Taipei, Taiwan,
Dec. 2020, pp. 1–7.
[215] H. Bangui, M. Ge, and B. Buhnova, “A hybrid data-driven model
for intrusion detection in VANET,” Proc. Comput. Sci., vol. 184,
pp. 516–523, Jun. 2021.
[216] H. Al-Khateeb, G. Epiphaniou, A. Reviczky, P. Karadimas, and
H. Heidari, “Proactive threat detection for connected cars using recursive
Bayesian estimation,” IEEE Sensors J., vol. 18, no. 12, pp. 4822–4831,
Jun. 2018.
[217] Y. Xu, J. Xia, H. Wu, and L. Fan, “Q-learning based physicallayer secure game against multiagent attacks,” IEEE Access, vol. 7,
pp. 49212–49222, 2019.
[218] M. Salehi and L. Rashidi, “A survey on anomaly detection in evolving
data: [With application to forest fire risk prediction],” ACM SIGKDD
Explorations Newslett., vol. 20, no. 1, pp. 13–23, May 2018.
[219] G. Pang, A. van den Hengel, C. Shen, and L. Cao, “Toward deep
supervised anomaly detection: Reinforcement learning from partially
labeled anomaly data,” in Proc. 27th ACM SIGKDD Conf. Knowl.
Discov. Data Min., 2021, pp. 1298–1308.

11204

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 26, NO. 8, AUGUST 2025

[220] C. Huang, Y. Wu, Y. Zuo, K. Pei, and G. Min, “Towards experienced
anomaly detector through reinforcement learning,” in Proc. 32nd AAAI
Conf. Artif. Intell. 13th Innovat. Appl. Artif. Intell. Conf. 8th AAAI
Symp. Educ. Adv. Artif. Intell., 2018, pp. 8087–8088.
[221] Z. Li, Y. Kong, C. Wang, and C. Jiang, “DDoS mitigation based on
space-time flow regularities in IoV: A feature adaption reinforcement
learning approach,” IEEE Trans. Intell. Transp. Syst., vol. 23, no. 3,
pp. 2262–2278, Mar. 2022.
[222] R. Sedar, C. Kalalas, F. Vázquez-Gallego, and J. Alonso-Zarate,
“Reinforcement learning based misbehavior detection in vehicular
networks,” in Proc. IEEE Int. Conf. Commun. (ICC), May 2022,
pp. 3550–3555.
[223] F. Jameel, M. A. Javed, S. Zeadally, and R. Jäntti, “Secure transmission in cellular V2X communications using deep Q-learning,”
IEEE Trans. Intell. Transp. Syst., vol. 23, no. 10, pp. 17167–17176,
Oct. 2022.
[224] T. Alladi, V. Kohli, V. Chamola, and F. R. Yu, “Securing the Internet of
Vehicles: A deep learning-based classification framework,” IEEE Netw.
Lett., vol. 3, no. 2, pp. 94–97, Jun. 2021.
[225] T. Alladi, V. Kohli, V. Chamola, F. R. Yu, and M. Guizani, “Artificial intelligence (AI)-empowered intrusion detection architecture for
the Internet of Vehicles,” IEEE Wireless Commun., vol. 28, no. 3,
pp. 144–149, Jun. 2021.
[226] X. Zhu, Y. Luo, A. Liu, M. Z. A. Bhuiyan, and S. Zhang, “Multiagent deep reinforcement learning for vehicular computation offloading
in IoT,” IEEE Internet Things J., vol. 8, no. 12, pp. 9763–9773,
Jun. 2021.
[227] T. D. Nguyen, S. Marchal, M. Miettinen, H. Fereidooni, N. Asokan,
and A.-R. Sadeghi, “DÏoT: A federated self-learning anomaly detection
system for IoT,” in Proc. IEEE 39th Int. Conf. Distrib. Comput. Syst.
(ICDCS), Jul. 2019, pp. 756–767.
[228] W. Y. B. Lim et al., “Federated learning in mobile edge networks: A
comprehensive survey,” IEEE Commun. Surveys Tuts., vol. 22, no. 3,
pp. 2031–2063, 3rd Quart., 2020.
[229] H. H. W. J. Bosman, G. Iacca, A. Tejada, H. J. Wörtche, and A. Liotta,
“Ensembles of incremental learners to detect anomalies in ad hoc sensor
networks,” Ad Hoc Netw., vol. 35, pp. 14–36, Dec. 2015.
[230] Y. Zhang, N. Meratnia, and P. Havinga, “Adaptive and online one-class
support vector machine-based outlier detection techniques for wireless
sensor networks,” in Proc. Int. Conf. Adv. Inf. Netw. Appl. Workshops,
May 2009, pp. 990–995.
[231] M. Almgren and E. Jonsson, “Using active learning in intrusion detection,” in Proc. 17th IEEE Comput. Secur. Found. Workshop, May 2004,
pp. 88–98.
[232] B. Karthiga, D. Durairaj, N. Nawaz, T. K. Venkatasamy, G.
Ramasamy, and A. Hariharasudan, “Intelligent intrusion detection
system for VANET using machine learning and deep learning
approaches,” Wireless Commun. Mobile Comput., vol. 2022, pp. 1–13,
Oct. 2022.
[233] D. Sinha, A. Sharma, and S. Sharma, “Automated detection of coronary
artery disease comparing arterial fat accumulation using CNN,” J.
Electron. Imag., vol. 31, no. 5, Jan. 2022, Art. no. 051405.
[234] M. Wazid et al., “Explainable deep learning-enabled malware
attack detection for IoT-enabled intelligent transportation systems,”
IEEE Trans. Intell. Transp. Syst., early access, Jan. 16, 2025, doi:
10.1109/TITS.2025.3525505.
[235] S. Iqbal, P. Ball, M. H. Kamarudin, and A. Bradley, “Simulating
malicious attacks on VANETs for connected and autonomous vehicle cybersecurity: A machine learning dataset,” in Proc. 13th Int.
Symp. Commun. Syst., Netw. Digit. Signal Process. (CSNDSP), Jul. 2022,
pp. 332–337.
[236] P. Rajak and P. K. Mishra, “An attack detection model for enhancing
the security of 5G-enabled vehicle-to-everything (V2X) communication for smart vehicles,” in Proc. FedCSIS (Commun. Papers), 2023,
pp. 229–236.
[237] C. Jiménez, “Deep learning-based cyber attack detection in autonomous
vehicle networks,” J. AI-Assist. Sci. Discovery, vol. 2, no. 2, pp. 1–25,
2022.

[238] B. Sousa, N. Magaia, and S. Silva, “An intelligent intrusion detection
system for 5G-enabled Internet of Vehicles,” Electronics, vol. 12, no. 8,
p. 1757, Apr. 2023, doi: 10.3390/electronics12081757.
[239] A. A. Korba, A. Boualouache, B. Brik, R. Rahal, Y. Ghamri-Doudane,
and S. M. Senouci, “Federated learning for zero-day attack detection
in 5G and beyond V2X networks,” in Proc. IEEE Int. Conf. Commun.
(ICC), May 2023, pp. 1137–1142.
[240] A. H. Magsi, A. Ghulam, S. Memon, K. Javeed, M. Alhussein, and
I. Rida, “A machine learning-based attack detection and prevention
system in vehicular named data networking,” Comput., Mater. Continua,
vol. 77, no. 2, pp. 1445–1465, 2023.
[241] G. Twardokus and H. Rahbari, “Towards protecting 5G sidelink
scheduling in C-V2X against intelligent DoS attacks,” IEEE
Trans. Wireless Commun., vol. 22, no. 11, pp. 7273–7286,
Nov. 2023.
[242] M. Begum, G. Raja, and M. Guizani, “AI-based sensor attack
detection and classification for autonomous vehicles in 6G-V2X environment,” IEEE Trans. Veh. Technol., vol. 73, no. 4, pp. 5054–5063,
Apr. 2024.
[243] S. B. Prathiba, G. Raja, S. Anbalagan, K. S. Arikumar, S. Gurumoorthy,
and K. Dev, “A hybrid deep sensor anomaly detection for autonomous
vehicles in 6G-V2X environment,” IEEE Trans. Netw. Sci. Eng., vol. 10,
no. 3, pp. 1246–1255, May 2023.
[244] B. Sousa, N. Magaia, S. Silva, N. T. Hieu, and Y. L. Guan,
“Vehicle-to-vehicle flooding datasets using MK5 on-board unit devices,”
Sci. Data, vol. 11, no. 1, p. 1363, Dec. 2024. [Online]. Available:
https://www.nature.com/articles/s41597-024-03663-5
[245] S. Zhang, M. Lagutkina, K. O. Akpinar, and M. Akpinar, “Improving
performance and data transmission security in VANETs,” Comput.
Commun., vol. 180, pp. 126–133, Dec. 2021.
[246] A. A. Andrade Salazar, P. D. McDaniel, R. Sheatsley, and J. Petit,
“Physics-based misbehavior detection system for V2X communications,”
SAE Int. J. Connected Automated Vehicles, vol. 5, no. 3, pp. 237–258,
Mar. 2022.
[247] O. Minawi, J. Whelan, A. Almehmadi, and K. El-Khatib, “Machine
learning-based intrusion detection system for controller area networks,”
in Proc. 10th ACM Symp. Design Anal. Intell. Veh. Netw. Appl.,
Nov. 2020, pp. 41–47.
[248] M. H. Bhavsar, Y. B. Bekele, K. Roy, J. C. Kelly, and
D. Limbrick, “FL-IDS: Federated learning-based intrusion detection
system using edge devices for transportation IoT,” IEEE Access, vol. 12,
pp. 52215–52226, 2024, doi: 10.1109/ACCESS.2024.3386631.
[249] J.-P. Monteuuis, J. Petit, J. Zhang, H. Labiod, S. Mafrica, and
A. Servel, “‘My autonomous car is an elephant’: A machine learningbased detector for implausible dimension,” in Proc. 3rd Int. Conf.
Secur. Smart Cities, Ind. Control Syst. Commun. (SSIC), Oct. 2018,
pp. 1–8.
[250] S. Kong, K. Wang, C. Feng, and J. Wang, “Smart cities and transportation based vehicle-to-vehicle communication and cyber security analysis
using machine learning model in 6G network,” Wireless Pers. Commun.,
vol. 2024, pp. 1–19, Jun. 2024.
[251] S. Boddupalli and S. Ray, “REDEM: Real-time detection and mitigation of communication attacks in connected autonomous vehicle
applications,” in Proc. IFIP Int. Internet Things Conf., Jan. 2020,
pp. 105–122.
[252] B. Kihei, H. Wilson, and M. Fall, “Experimental results of
detecting primitive jamming attacks using machine learning
in vehicle-to-everything communication networks,” in Proc.
IEEE 7th World Forum Internet Things (WF-IoT), Jun. 2021,
pp. 530–535.
[253] T. Karunathilake, M. Zongo, D. Amarawardana, and A. Förster,
“CN+: Vehicular dataset at traffic light regulated intersection
in bremen, Germany,” Sci. Data, vol. 11, no. 1, p. 1363,
Jun. 2024.
[254] S. Mishra, N. Sengar, and D. Har, “A secure, blockchain-enabled
vehicular sensor communication protocol with deep learning-assisted
anomaly detection,” IEEE Intell. Transp. Syst. Mag., early access,
Jan. 7, 2025, doi: 10.1109/MITS.2024.3519620.

HAKEEM AND KIM: ADVANCING INTRUSION DETECTION IN V2X NETWORKS: A COMPREHENSIVE SURVEY

Shimaa A. Abdel Hakeem (Member, IEEE)
received the B.Sc. and M.Sc. degrees from Fayoum
University, Egypt, in 2011 and 2015, respectively.
From 2017 to 2021, she was awarded the prestigious Brain Korea 21 (BK21) Ph.D. scholarship
and completed her Ph.D. focusing on “Lightweight
Authentication and Encryption Protocols for Secure
Vehicular Networks in 5G and Beyond.” She is
currently a Lecturer with the Faculty of Electronics and Computer Engineering, Chungbuk National
University (CBNU), South Korea. With more than
a decade of security experience, she specializes in autonomous vehicle
security protocols. She is a Pivotal Contributor with the Mixed Sensing and
Intelligence Systems (MSIS) Laboratory, CBNU. Her industry experience
includes roles as a Network Security Administrator and a Senior Network
Engineer with Fayoum Information Center, Egypt, and collaboration with
Valeo Company on autonomous vehicle security projects. She has published
over 23 SCI(E) papers, with 13 appearing in ranked journals, and presented
at numerous prestigious conferences. Her research interests include wireless
communication security, 5G/6G networks, autonomous vehicle protocols, and
the IoT device security. Her expertise encompasses commercial 5G-V2X
devices, implementing security protocols based on IEEE, 3GPP, and ETSI
standards, and advancing 6G network architectures. These contributions make
her a leading expert in secure wireless communication and autonomous vehicle
technologies. Her accolades include the BK21 Post-Doctoral Research Fellow
Scholarship from 2021 to 2024, the Excellent Researcher Award from CBNU’s
BK21 CBSTAR Program in 2024, and the Best Paper Award from the KICS
Conference in 2018.

11205

HyungWon Kim (Member, IEEE) received the B.S.
and M.S. degrees from KAIST and the Ph.D. degree
in electrical engineering from the University of
Michigan, Ann Arbor, MI, USA. He has extensive industry experience, including founding and
serving as the CEO of Xronet, South Korea, and
working at renowned companies, such as Broadcom,
Synopsys, and Intel. Since 2013, he has been a
Distinguished Professor with Chungbuk National
University (CBNU), where he is currently the Director of the Mixed Sensing and Intelligence Systems
(MSIS) Laboratory. With over 300 publications in high-ranking journals and
conferences, he has made significant contributions to vehicular communication
security, anomaly detection in smart factories and cities, and ship design.
He has secured funding for numerous prestigious projects and oversees over
60 students at the MSIS Laboratory, fostering research in diverse domains.
Known for his strong industry connections, he ensures that the laboratories
research is both practical and experimental. His research interests include
interconnected autonomous-driving vehicle security, artificial intelligence,
analog/digital integrated SoCs, and wireless sensor networks. In addition
to registering numerous patents, he has received notable awards for his
contributions to science and technology, further solidifying his reputation as
a leader in his field.
PAPER_TEXT
