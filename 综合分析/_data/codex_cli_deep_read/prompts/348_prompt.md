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
# [348] A survey on encrypted network traffic: A comprehensive survey of identification/classification techniques, challenges, and future directions
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
编号：348
题名：A survey on encrypted network traffic: A comprehensive survey of identification/classification techniques, challenges, and future directions
年份：2024
DOI：10.1016/j.comnet.2024.110984
来源：Computer Networks
PDF：paper/10.1016_j.comnet.2024.110984.pdf
已有粗分类：数据集、基准、综述与开源工具
二级关联：其他AI安全与跨域异常检测
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\348.txt
- 原始字符数：166885
- 本次发送字符数：140043
- 是否截断：True

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Computer Networks 257 (2025) 110984

Contents lists available at ScienceDirect

Computer Networks
journal homepage: www.elsevier.com/locate/comnet

Survey paper

A survey on encrypted network traffic: A comprehensive survey of
identification/classification techniques, challenges, and future directions
Adit Sharma

∗

, Arash Habibi Lashkari

Behaviour-Centric Cybersecurity Center (BCCC), School of Information Technology, York University, Toronto, Ontario, Canada

ARTICLE

INFO

Keywords:
Network traffic analysis
Encrypted traffic analysis
Encrypted traffic datasets
Network traffic analyzers
Encrypted traffic detection
Network traffic classification
Mobile traffic classification
ETC

ABSTRACT
Encrypted traffic detection and classification is a critical domain in network security, increasingly essential in
an era of pervasive encryption. This survey paper delves into integrating advanced Machine Learning (ML) and
Deep Learning (DL) techniques to address the challenges of robust encryption methods and dynamic network
behaviors. Despite notable advancements, there remains a substantial gap in the operational application
of these technologies, often constrained by scalability, efficiency, and adaptability to varied encryption
standards. We critically review existing methodologies from 7 surveys and 82 related technical papers,
highlight the shortcomings, and propose future research directions. Our analysis underscores the need to
develop innovative, resource-efficient models that seamlessly adapt to new threats and encryption techniques
without compromising performance. Additionally, we advocate for creating comprehensive datasets that merge
encrypted and non-encrypted traffic to enhance model training and testing. This survey maps out the trajectory
of recent developments and charts a course for future research that could significantly enhance encrypted traffic
management and security capabilities.

1. Introduction
Encryption has become a cornerstone of data privacy in the digital age, with its adoption driven by escalating security concerns and
stringent regulatory frameworks [1]. The rapid escalation of encrypted
internet traffic has profoundly impacted network security dynamics,
with recent data indicating that as of 2023, approximately 95% of web
traffic is encrypted using HTTPS protocols [2]. This significant increase
from previous years underscores a global shift towards prioritizing
data privacy and security. However, this surge in encryption has introduced new challenges for network management, security monitoring,
and quality of service, prompting the development of sophisticated
Encrypted Traffic Analysis (ETA) techniques [3].
Cybercriminals increasingly leverage encrypted channels to conceal
malicious activities, complicating traditional security measures. A 2023
report by Zscaler ThreatLabz revealed that 85.9% of cyberattacks now
utilize encrypted channels, marking a 20% increase from the previous
year [4]. This trend poses a challenge, as encrypted traffic can obscure
threats from standard detection tools. Additionally, the adoption of
TLS 1.3 has accelerated, with a notable rise in its implementation
over the past two years. While TLS 1.3 enhances security and performance, it also limits visibility into network traffic, posing challenges
for monitoring and threat detection [5].

In response to these developments, organizations increasingly invest
in advanced security solutions that inspect encrypted traffic without
compromising privacy. Techniques such as machine learning and artificial intelligence are employed to analyze traffic patterns and detect
anomalies indicative of malicious behavior [6]. In summary, the exponential growth of encrypted traffic over the past few years has
necessitated reevaluating network security strategies. Balancing the
benefits of encryption with the imperative of effective threat detection
remains a critical focus for researchers and practitioners.
This survey paper delves into the advancements in Machine Learning (ML) and Deep Learning (DL) models that are at the forefront of detecting and analyzing encrypted traffic [7]. These models offer promising solutions by enabling effective network monitoring and anomaly
detection without decrypting the data, thus preserving user privacy [8].
We explore various ML approaches, including supervised and unsupervised techniques [9], and DL strategies such as Convolutional Neural
Networks (CNNs) and Recurrent Neural Networks (RNNs), which have
shown considerable success in pattern recognition within encrypted
flows [10].
In encrypted traffic detection and classification, network security
can be broadly divided into two critical aspects: security and privacy.
While security focuses on protecting the network infrastructure from

∗ Corresponding author.

E-mail address: adit27@yorku.ca (A. Sharma).
https://doi.org/10.1016/j.comnet.2024.110984
Received 3 September 2024; Received in revised form 13 November 2024; Accepted 5 December 2024
Available online 15 December 2024
1389-1286/© 2024 Elsevier B.V. All rights are reserved, including those for text and data mining, AI training, and similar technologies.

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari

unauthorized access, attacks, and vulnerabilities [11], privacy emphasizes safeguarding the confidentiality of the data being transmitted
within that network [12]. Both aspects are vital for ensuring the overall integrity of network communications, especially in today’s digital
landscape where large volumes of sensitive information are constantly
in transit [13].
Encryption techniques have recently been enhanced by integrating
blockchain technology, which offers a decentralized and transparent
platform that significantly strengthens the security of IoT devices—
integral components in managing encrypted traffic [14]. Blockchain’s
ability to maintain immutable records and provide enhanced privacy
through advanced encryption techniques has become crucial in ensuring security and privacy within network communications [15]. Additionally, the convergence of blockchain with IoT fortifies the security
landscape while introducing innovative privacy-preserving strategies
that protect data across distributed networks [16]. These advancements
are instrumental in developing encrypted traffic detection and analysis,
offering robust solutions against potential cyber threats [17,18].
Focusing on privacy within industrial IoT applications, secure inference solutions such as Secure Multiparty Computation (SMC) have
emerged as effective tools to mitigate privacy risks. These solutions
allow multiple parties to securely conduct AI reasoning without exposing sensitive data, making them particularly valuable in environments
like smart manufacturing [11]. Privacy-enhancing techniques, such
as Geo-Indistinguishability—demonstrated through Group-Based Noise
Addition (CANOE)—protect individual privacy in spatial crowdsourcing, ensuring efficient task allocation without compromising the utility
of spatial data [12]. Moreover, tensor-based Recurrent Neural Networks
(RNNs) integrated with differential privacy address privacy concerns
in IoT environments by securely processing heterogeneous sequential
data, maintaining confidentiality across various IoT platforms [13].
These methodologies contribute to advancing privacy-preserving technologies and play a pivotal role in enhancing encrypted traffic analysis
in complex network environments.
Further enhancing the dialogue on encrypted network traffic, recent studies delve into the dynamics of Tor networks, emphasizing
the dual challenge of ensuring user anonymity and system integrity.
Notably, Shahbar and Zincir-Heywood [19] investigates traffic flow
analysis within Tor’s pluggable transports, revealing vulnerabilities that
could potentially be exploited to compromise user privacy. Concurrently, Shahbar and Zincir-Heywood [20] benchmarks methods for
classifying Tor traffic at both flow and circuit levels, illustrating the
complexities of discerning user activities without decrypting traffic,
thereby underscoring the intricate balance between operational transparency and user confidentiality. Additionally, Montieri et al. [21]
and Montieri et al. [22] explore the efficacy of traffic classification
techniques across various anonymity tools, including Tor, I2P, and
JonDonym, highlighting the significant challenges in identifying the
type of traffic and the applications it encapsulates due to the robust
encryption and routing mechanisms employed. These insights illuminate the ongoing tensions between enhancing security measures and
preserving the stringent privacy requirements demanded in modern
networked environments.
This survey paper seeks to paint a broad picture of ETA’s current
landscape and emerging trends by providing a comprehensive overview
of the methods, challenges, and datasets integral to this domain.
The structure of the survey paper is as follows. The second section,
the Search Methodology, outlines the systematic approach used to
select and analyze the technical articles and datasets that form the
foundation for this survey.
The third section, Previous Survey Papers & Motivation, reviews the
existing literature, contextualizing this survey within the broader research landscape. It also discusses the compelling reasons for undertaking this survey, including the rapid evolution of encryption techniques
and their implications on network security.

The fourth and fifth sections, Encryption Traffic Techniques/
Services and Related Work - Technical Articles, explore the encryption
landscape. The fourth section details the prevalent encryption protocols
and services, laying the groundwork for understanding their detection
and analysis. Subsequently, the fifth section delves into the core of
recent research, categorizing efforts into machine learning (ML), deep
learning (DL) models, and hybrid approaches utilized in encrypted
traffic detection.
The sixth and seventh sections, titled Encrypted Traffic Datasets
and Information Extractors (IE) or Traffic Analyzers, offer an in-depth
exploration of the resources and tools pivotal to encrypted traffic
analysis. The sixth section critically examines the available datasets for
training and testing encrypted traffic detection systems. The seventh
section then analyzes the tools and techniques developed to extract
actionable insights from encrypted data, ensuring privacy concerns are
respected.
The eighth and ninth sections, titled Challenges & Future Work
and Conclusion, respectively, conclude the survey by addressing the
landscape of encrypted traffic analysis. The eighth section highlights
the unresolved issues and potential research directions that could address the limitations of current methods. Finally, the ninth section
synthesizes the findings from each section, emphasizing the integration
of machine learning techniques with encrypted traffic analysis and
outlining the implications for both research and practical applications.
The Fig. 1 succinctly outlines the logical progression and structure
of our survey paper. It starts with an introductory overview, followed
by a detailed search methodology, leading to discussions on previous
surveys and the motivation for a new analysis. This flowchart then
delineates the path through various sections of the paper, including
encryption techniques, relevant technical articles, and a synthesis of
machine learning, deep learning, and hybrid approaches. It continues
through the evaluation of encrypted traffic datasets and analyzers,
culminating in a discussion on current challenges and future directions before concluding. This structural diagram enhances the reader’s
comprehension of the paper’s framework, providing a clear visual
guide through the intricate landscape of encrypted traffic classification
research.
The acronyms and abbreviations used throughout this paper are
comprehensively detailed in Table 12, located in Appendix. This table
provides a clear reference for understanding all technical terms utilized
in the study.
This survey paper has endeavoured to provide a comprehensive
overview and a structured analysis of encrypted traffic detection and
classification. The significant contributions of this work can be summarized as follows:
• Taxonomy of Encrypted Traffic Detection and Classification
Models: We have developed a detailed taxonomy that categorizes
the existing models based on their methodological approaches
and operational capabilities, offering a clear framework for understanding the landscape of current technologies.
• Survey of Techniques for Encrypted Traffic Detection and
Classification: This paper reviews various techniques and
methodologies employed in encrypted traffic detection, providing
insights into their effectiveness and application scenarios.
• Comprehensive Analysis of Datasets: We compile and present
a table summarizing all available datasets pertinent to encrypted
traffic studies, listing their features and characteristics. This compilation is a valuable resource for researchers to evaluate and
select appropriate study datasets.
• Overview of Technical Analyzers/Information Extractors: A
comprehensive table is introduced, summarizing all existing analyzers and information extractors, highlighting their features and
utility. This overview facilitates a better understanding of the
tools for integrating into encrypted traffic detection systems.
2

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari
Table 1
List of digital libraries utilized in ETC research.
Site

URL

Springer
Elsevier
Wiley
IEEE explorer
ACM Digital Library
Cornell University Archive
SSRN
MDPI
SSRN
Spied Digital

link.springer.com
sciencedirect.com
onlinelibrary.wiley.com
ieeexplore.ieee.org
dl.acm.org
arxiv.org
papers.ssrn.com
mdpi.com
papers.ssrn.com
spieddigitallibrary.org

Fig. 2 presents the five steps of the proposed search methodology, beginning with selecting keywords and search items for various scientific
publishers.
In the first step, the following search queries and keywords were
employed across various scientific publishers (Listed in Table 1) to
identify existing survey papers :
• Encrypted Traffic Survey
• Encrypted Traffic Review
• Encrypted Traffic Classification Overview
• Encrypted Traffic Classification Survey
• Encrypted Traffic Classification Review
• Encrypted Traffic Classification using ML Approaches Survey
• Encrypted Traffic Classification using ML Approaches Review
• Encrypted Traffic Classification using DL Approaches Review
• Encrypted Traffic Classification using DL Approaches Survey
For the technical articles, the following keywords were used:
• Encrypted, Network, Traffic, Classification, Detection, Characterization, ML, DL, Feature Extraction, Supervised Learning, Unsupervised Learning, Neural Networks, Artificial Intelligence, Internet
Security, Cybersecurity etc.
In the second step, we collect all relevant literature comprehensively, spanning review articles and technical papers published within
the last five years. This aggregation is sourced from databases and
journals, as delineated in Table 1. This step ensures the inclusion of
recent advancements and contemporary research findings, thus laying
a foundation for a robust literature analysis.
The selected articles are checked for the third step to eliminate
duplicates and repeated studies. This process utilizes manual review
to ensure that each included article presents unique insights and contributes substantively to the breadth of knowledge being surveyed.
This refinement paves the way for a focused and concise synthesis of
literature.
Step four entails creating a unique list of articles by excluding those
irrelevant to the core topics of interest. This step includes a feedback
loop to step three, allowing for refinement and reevaluation of article
relevance, ensuring that only the most pertinent and significant articles
are considered for in-depth review.
The final step of our methodology involves generating a definitive list of technical and survey articles. This culmination involves a
thorough review, which includes a validation check to confirm the
relevance and credibility of the sources. The resulting compilation
is poised for in-depth analysis and synthesis, providing an extensive
summary of the present status of research as it pertains to our survey
topic.

Fig. 1. Comprehensive flowchart of methodological approach in encrypted traffic
detection and classification.

• Proposed Future Research Directions: Based on the gaps identified through our survey, we outline potential future research
directions that could address existing challenges and advance the
encrypted traffic detection and classification field.
As encrypted traffic becomes increasingly prevalent, the necessity
for robust ETA methods that respect privacy while ensuring network
security is more critical than ever [23]. This survey paper serves as a
primer on the state-of-the-art ML and DL techniques shaping the future
of encrypted network traffic analysis. Through a detailed review of the
technological advancements and their applications, we aim to foster a
deeper understanding of the field and spur further innovation in the
ongoing battle between data privacy and network security.
2. Search methodology

3. Previous survey papers & Motivation for a new survey paper
This section presents an investigation methodology for conducting
a comprehensive encrypted traffic detection and classification search.
This field includes domains such as ML, DL, and Hybrid approaches.

Cybersecurity has seen a marked increase in the significance of
detecting and classifying encrypted traffic, driven by the dual needs
3

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari

Fig. 2. Structured overview of methodological steps in encrypted traffic detection and Classification Survey.

of privacy and security [7]. Encrypted traffic, which includes protocols
like TLS, SSL, and QUIC, now forms a substantial segment of global
internet communications [24]. While encryption protects data from
unauthorized access, it also complicates network management and
anomaly detection [3]. As detailed in the previous section of this survey
paper, a meticulously crafted search methodology was employed to
address these challenges. This approach enabled the systematic review
and selection of survey papers that span the full spectrum of encrypted
traffic analysis techniques from the past decade in a chronological
manner.
The survey papers reviewed here build upon one another, tracing
the evolution from initial methods such as Deep Packet Inspection (DPI)
to sophisticated, privacy-preserving ML algorithms [8]. They reflect
a broader shift towards techniques that maintain user privacy while
providing security professionals with the necessary tools to monitor
and respond to threats effectively [10]. This section explores these key
contributions to the field and presents a thorough overview of existing
survey papers on the classification and detection of encrypted traffic.
The study by Velan, P. et al. provides an in-depth review of methods
for classifying and analyzing encrypted network traffic, examining
prevalent encryption protocols and their impact on network security.
The paper delineates a range of classification techniques, from payloadbased to feature-based methods, and organizes them into a structured
taxonomy. It presents an overview of how the initiation phase of
encrypted connections can offer valuable information for enforcing
security policies, highlighting how certain unencrypted elements, such
as protocol versions and cipher suites, can be exploited for network
anomaly detection and client identification. The survey emphasizes the
intricacy of classifying encrypted traffic due to varied protocol behaviors and the importance of selecting appropriate classification methods
that do not compromise user privacy. This work is especially relevant
given the increasing use of encryption, which complicates traditional
traffic analysis. The authors underscore the evolution of classification
strategies to effectively address the challenges posed by encrypted communications, emphasizing the need for advanced techniques that can
adapt to the enhanced security measures of modern network traffic. The
survey is a vital reference for the ongoing adaptation and innovation in
encrypted traffic analysis, signaling the significant impact of encryption
on network neutrality and end-user privacy [25].
Aminuddin, M. A. I. M. et al. propose a survey on ML methods for monitoring encrypted Tor traffic. The paper reviews various
ML strategies, including supervised, semi-supervised, and unsupervised
learning, each contributing distinct advantages to analyzing encrypted
network traffic. The authors discuss the efficacy of conventional algorithms, including Decision Trees, Support Vector Machines, and Naive
Bayes, successfully applied to classify patterns in encrypted Tor traffic.
Additionally, the survey highlights the use of advanced algorithms
for identifying specific traffic types within Tor, such as pluggable

transports or distinguishing between different network applications.
Building on these insights, the paper also addresses the broader challenges and considerations in classifying encrypted traffic using ML
approaches, noting the importance of dataset and feature selection,
the challenges posed by the encryption’s complexity, and the need
for real-time classification capabilities. It emphasizes that no single
algorithm can perform optimally under all conditions, highlighting the
relevance of selecting appropriate ML models based on accuracy, training time, computational resources, and feature selection to enhance
privacy protection within the Tor network. The comprehensive nature
of this survey underscores the significant progress in applying ML to
bolster the security and analysis of encrypted network traffic within
anonymity networks like Tor [26].
Rezaei et al. and Iliyasu et al. provide comprehensive analyses of
DL techniques in ETC. Rezaei et al. focus on the utility of CNNs for
their hierarchical processing capabilities and delve into the application
of Long Short-Term Memory (LSTM) networks and Recurrent Neural Networks(RNNs) for handling sequential data integral to network
traffic flows. They highlight the growth of hybrid models that blend
these neural architectures to improve the accuracy of classification in
the face of encryption protocols like QUIC and TLS 1.3, as well as
complex challenges such as multi-label classification in multiplexed
streams [27].
Iliyasu et al. echo this narrative by underscoring the importance
of LSTM and CNN networks, especially in capturing long-term dependencies in encrypted traffic data. Their review extends into the realm
of hybrid DL models, which they present as advanced, versatile tools
capable of addressing the limitations presented by increasingly sophisticated encryption methods. Both surveys note significant hurdles,
such as gathering and labeling comprehensive datasets and managing
multiplexed traffic streams that combine multiple traffic classes within
single flows. Collectively, these works illustrate a landscape where DL
enhances traffic analysis capabilities and faces a continuous challenge
from the evolving scope of network encryption [28].
Li, Y. et al. propose a comprehensive survey that underscores the
critical role of DL and ML in detecting encrypted malicious traffic.
The authors meticulously examine the application of CNNs for robust feature extraction from encrypted data, which is foundational
in identifying potential security threats. The paper further explores
the significance of sequence data processing capabilities of RNNs and
LSTMs, which are instrumental for maintaining contextual awareness
in traffic flow analysis. The authors also shed light on hybrid DL architectures, which amalgamate the strengths of individual models to yield
a more sophisticated and accurate detection mechanism. The survey
concludes that these advanced methodologies signify a paradigm shift
in network security strategies, moving away from traditional heuristicbased systems towards more dynamic, data-driven models that can
keep pace with the complexities introduced by modern encryption
4

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari

standards. Moreover, the paper discusses ongoing issues and challenges,
such as the scarcity of public datasets, the necessity for more robust
feature extraction techniques, and the difficulty of implementing these
technologies in real networks with considerable variability. It emphasizes that while the identification of encrypted malicious traffic has
progressed, transitioning from passive to active defense mechanisms
remains a pivotal area for future research, suggesting an imminent need
to improve the applicability and real-world efficacy of current detection
technologies [29].
In [30], Papadogiannaki, E., & Ioannidis, S. conduct a thorough
investigation into the domain of encrypted network traffic analysis in
their paper ’A Survey on Encrypted Network Traffic Analysis: Applications, Techniques, and Countermeasures,’ published in ACM Computing
Surveys (CSUR). This survey navigates through the increasing necessity
for sophisticated methods to analyze and classify encrypted traffic,
driven by the widespread adoption of encryption protocols aimed at
enhancing security and protecting user privacy. The authors meticulously categorize the spectrum of research efforts into applications
for network analytics, security enhancements, and privacy protections.
They highlight the significant challenges around dataset construction,
traffic representation, and analysis model building, as outlined in their
review. The survey emphasizes the instrumental role of ML and DL in
deciphering encrypted traffic nuances without undermining the core
advantages of encryption, spotlighting the need for innovative solutions
that reduce false positives and improve real-time processing performance in encrypted networks. By setting a foundation for advancing
this critical area of network analysis and security, Papadogiannaki
and Ioannidis call for directions of future research that address these
ongoing challenges, enriching the field with new methodologies and
tools.
In [31], Shen, M. et al. present a comprehensive survey titled ’Machine Learning-Powered Encrypted Network Traffic Analysis’ in IEEE
Communications Surveys & Tutorials. This extensive study encapsulates
the evolution of encrypted traffic analysis from traditional methodologies, which struggle with the advent of encryption, to modern ML
techniques that proficiently unravel encrypted data’s complexities. The
survey highlights the significant challenges in dataset construction,
traffic representation, analysis model building, and developing countermeasures against encryption while also offering a detailed taxonomy
of analysis objectives such as anomaly detection and privacy leakage.
It reviews the diverse machine-learning tools at the forefront of this
field. It emphasizes the necessity for high-quality datasets, robust traffic
representations, and adaptive analysis models to enhance accuracy
and efficiency. By underlining the importance of addressing these
challenges, the survey guides future research towards developing more
robust and flexible security frameworks, thereby adapting measures for
network security to the evolving landscape of widespread encryption.

Moreover, the fragmented approach observed in existing studies
concerning the impact of advanced encryption on the classification of
traffic methods hampers the accurate classification and detection of
encrypted traffic [29]. There is a clear need for a survey consolidating
existing knowledge and addressing areas poorly covered or omitted in
prior surveys.
By pinpointing these gaps, Table 2 serves as a critical resource
for guiding future research towards more comprehensive and inclusive
studies that address the evolving complexities of encrypted traffic
detection.
In light of these observations, this survey seeks to bridge identified
gaps by integrating upcoming ML/DL models and privacy-enhancing
technologies. This approach is vital for developing solutions that meet
the increasingly complex demands of modern cybersecurity. This survey aims to analyze encrypted network traffic thoroughly, employing
advanced ML and DL techniques alongside an in-depth examination of
the evolving landscape of encryption protocols. Such an analysis will
equip researchers and practitioners with a robust toolkit for navigating
the complexities of encrypted traffic analysis, addressing theoretical
advancements and practical deployment challenges.
The primary objective of this survey is to address the following questions regarding the different detection and classification approaches
proposed for encrypted traffic:
Fundamental Research Questions:
• Question 1: ‘‘Has there been a comprehensive taxonomy of the
various data collection approaches utilized in the domain of
encrypted traffic analysis? - Covered in Section 5 - Related Work
- Technical Articles ’’
• Question 2: ‘‘Are the encryption protocols used for secure data
transmission adequately classified and analyzed within existing
literature? - Covered in Section 4 - Encryption Traffic Techniques/Services’’
Technical Questions:
• Question 3: ‘‘What information extraction methods are employed
throughout the analysis, and are these thoroughly surveyed? Covered in Section 7 - Information Extractors (IE) or Traffic
Analyzers’’
• Question 4: ‘‘How extensively have traffic classification techniques been explored? - Covered in Section 5 - Related Work Technical Articles’’
• Question 5: ‘‘What ML models are applied and reviewed? - Covered in Section 5 - Related Work - Technical Articles’’
• Question 6: ‘‘To what extent have DL techniques been utilized,
and is there a detailed survey of their effectiveness? - Covered in
Section 5 - Related Work - Technical Articles’’
• Question 7: ‘‘Are the features of encrypted traffic and their classification methods systematically cataloged in the surveyed papers?
- Covered in Section 5 - Related Work - Technical Articles’’
• Question 8: ‘‘Is there an assessment of the performance metrics &
datasets utilized in the surveyed studies? - Covered in Sections 5 &
6 - Related Work - Technical Articles & Encrypted Traffic Datasets
respectively’’
• Question 9: ‘‘How have model selection techniques been incorporated, and are they evaluated comprehensively? - Covered in
Section 5 - Related Work - Technical Articles’’

3.1. Motivation
The comprehensive review, systematically summarized in Table 2,
uncovers notable limitations in the methodologies and the scope of
existing surveys on encrypted traffic classification. Our analysis reveals
that many of these surveys tend to focus narrowly on specific segments
of the field, often emphasizing machine learning (ML) and deep learning (DL) applications [25,26]. This table highlights the areas where
these studies lack breadth or fail to capture emerging technologies and
approaches beyond the conventional ML and DL paradigms. It also
sheds light on the underrepresentation of hybrid and advanced analytical models that combine multiple techniques for enhanced accuracy
and efficiency. However, they often overlook the integration of these
technologies into real-world scenarios, resulting in gaps such as inadequate protocol-specific analyses, insufficient adaptability of feature
sets across varied encryption standards, and a general disregard for
operational challenges like scalability and efficiency in deployment [28,
31].

Research Gaps & Future Work Questions:
• Question 10: ‘‘How is encrypted traffic detection technology covered in existing research, and what gaps remain? - Covered in
Sections 5 & 8 - Related Work - Technical Articles & Challenges
& Future Work respectively’’
5

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari

Table 2
Comparative survey of techniques employed for encrypted traffic classification and analysis where covered ✓✓; partially covered ✓; not covered ✗.
Title

Year

Area covered

Taxonomy

Data
collection
techniques

Encryption
protocols

Information/Feature
extraction

Traffic
classification
techniques

ML
techniques

DL
techniques

Performance
evaluation
metrics

Model
selection
techniques

A survey of methods for
ETC and analysis [25]

2015

Encrypted traffic
identification

✓✓

✗

✓✓

✓✓

✓✓

✓✓

✗

✗

✗

A Survey on Tor
Encrypted Traffic
Monitoring [26]

2018

Tor/non-tor
encrypted traffic
classification

✓✓

✗

✓✓

✗

✓✓

✓✓

✗

✗

✗

Deep Learning for
Encrypted Traffic
Classification: An
Overview [27]

2019

DL for encrypted
traffic classification

✓✓

✓✓

✗

✗

✗

✓

✓✓

✗

✓✓

A Review of Deep
Learning Techniques for
Encrypted Traffic
Classification [28]

2020

Deep Learning
Techniques for
Encrypted Traffic
Classification

✓✓

✗

✗

✗

✗

✗

✓✓

✗

✗

A Survey of Encrypted
Malicious Traffic
Detection [29]

2021

Encrypted traffic
identification

✗

✓✓

✓✓

✓✓

✗

✓✓

✓

✓✓

✓

A Survey on Encrypted
Network Traffic Analysis
Applications, Techniques,
and Countermeasures
[30]

2021

Encrypted traffic in
network analysis

✓✓

✗

✗

✗

✓✓

✓✓

✓✓

✓✓

✓✓

Machine
Learning-Powered
Encrypted Network
Traffic Analysis [31]

2022

Encrypted traffic in
network analysis

✓✓

✓✓

✓✓

✓✓

✓✓

✓✓

✓

✓✓

✓✓

This paper

2024

ETC Techniques,
Challenges, and
Future Directions

✓✓

✓✓

✓✓

✓✓

✓✓

✓✓

✓✓

✓✓

✓✓

including Tor, VPNs, and other emerging technologies. These tables
detail the integration of these services with different analytical models, highlighting their effectiveness in enhancing privacy and security.
Specifically, they examine the diverse approaches and algorithms used
across different studies, providing insights into the strengths and weaknesses of each encryption technique. This collective analysis aids in
understanding the broader implications of encryption technologies on
the accuracy and reliability of traffic classification systems, thereby
illuminating the specific challenges and benefits associated with each
service.
Fig. 3 depicts the count of encryption protocols/services employed
in the various technical articles reviewed. It shows the widespread use
of protocols/services cited in various studies, highlighting the predominant use of VPNs, noted in 30 instances, underscoring their widespread
acceptance for securing online communications. Tor usage, observed
in 9 cases, and use of VPN and Tor combined in 6 instances reflect
specialized approaches for enhancing user anonymity. The ‘Others’
category, comprising 27 instances, includes diverse technologies like
I2P, Zeronet, and cryptographic protocols such as HTTPS and SSL,
illustrating various encryption strategies catering to different security
needs. This distribution invites further investigation into why certain
protocols are preferred in specific scenarios and how combinations of
these technologies might offer enhanced security. Such insights are
necessary for developing advanced, user-friendly encryption solutions.
By examining these detailed comparisons, future researchers can
discern patterns and effectiveness of different encryption models, assess
the synergy between encryption methods and ML algorithms, and
identify trends that may influence the direction of future innovations.
Such insights are invaluable for scholars aiming to enhance existing
encryption frameworks or to pioneer novel approaches that align with
the evolving landscape of digital security technologies.

The subsequent sections of this survey paper focus on covering
the questions mentioned above in detail and elaborating on these
methodologies, providing a more informed and effective approach to
encrypted traffic detection and classification techniques. This comprehensive analysis is essential in an era characterized by rapidly
evolving encryption standards and protocols, underscoring the evolving
nature of the cybersecurity field and its critical role in maintaining the
integrity of online communications.
4. Encryption traffic techniques/services
Encryption techniques and services have evolved significantly over
the decades, responding to the growing demand for secure communication across various domains, including military, commercial, and personal interactions [32]. At its core, encryption converts plaintext into
ciphertext using an algorithm and a key, rendering the data unreadable
to unauthorized parties [33]. Historically, encryption began with simple ciphers, such as the Caesar cipher, which employed a basic substitution method [32]. However, as computational power increased, encryption methods became more sophisticated, creating complex algorithms
that could withstand advanced cryptanalysis techniques [34].
The trajectory of cryptography, from these simple methods to advanced systems, mirrors the continuous development of robust encryption standards like the Data Encryption Standard (DES) and the
Advanced Encryption Standard (AES), designed to resist computational
attacks. Modern techniques such as differential privacy and homomorphic encryption represent the cutting edge of this evolution. Differential
privacy, for example, adds controlled random noise to data, providing
strong privacy guarantees without significantly compromising data
utility, which is particularly critical in areas like cloud computing and
big data analytics [35]. Meanwhile, homomorphic encryption allows
computations on encrypted data without decryption, ensuring secure
data processing and maintaining privacy in scenarios such as cloud
environments [36].
These advancements reflect cryptography’s progression towards securing complex and large-scale digital communications, highlighting
historical techniques and modern innovations that address today’s security challenges.
This section meticulously examines and highlights the characteristics of various encryption techniques and services prevalent in the field.
Tables 3, 4, 5, 6, and 7 collectively offer a comprehensive comparative
analysis of various encryption services used in traffic management,

• VPN (Virtual Private Network) (1996, Gurdeep Singh-Pall) VPNs create a private network from a public internet connection,
encapsulating and encrypting data packets to provide secure and
anonymous access to the internet. This technology is fundamental
in bypassing geo-restrictions and safeguarding sensitive data from
unauthorized access, especially beneficial in environments that
require confidentiality like corporate networks [37].
• TOR (The Onion Router) (2002, Paul Syverson, Michael G.
Reed, David Goldschlag - U.S. Naval Research Laboratory)
— TOR is a network of servers that enables anonymous communication by directing internet traffic through a free, worldwide,
6

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari

Fig. 3. Quantitative overview of encryption protocols and services in encrypted traffic studies.

• IPSec (Internet Protocol Security) (1995, IETF) — IPSec is
used to secure Internet communications across an IP network by
encrypting and authenticating each IP packet of a communication session. It is widely used for creating secure VPNs, particularly important for protecting data flowing between corporate
networks [45].
• SSH (Secure Shell) (1995, Tatu Ylönen) — SSH is a protocol for
operating network services securely over an unsecured network.
Best known for its more secure approach to remote login than
older protocols like Telnet, SSH encrypts all traffic (including
passwords) to eliminate eavesdropping, connection hijacking, and
other network-level attacks [46].
• PGP (Pretty Good Privacy) (1991, Phil Zimmermann) — Pretty
Good Privacy, or PGP, is a data encryption and decryption program that provides cryptographic privacy and authentication for
data communication. Developed by Phil Zimmermann in 1991,
PGP is most commonly used for securing emails but is also
employed to encrypt and decrypt texts, files, and even disk partitions. The system relies on symmetric-key cryptography for speed
and public-key cryptography for secure key exchange, typically
using the RSA algorithm. One of the key features of PGP is its
use of a web of trust, where users can sign each other’s keys to
endorse the authenticity of the key owner’s identity instead of
relying on a centralized authority [47].
• S/MIME (Secure/Multipurpose Internet Mail Extensions)
(1995, RSA Data Security, Inc.) — Secure/Multipurpose Internet Mail Extensions, or S/MIME, is a standard for public key
encryption and signing of MIME data, widely used in email systems. S/MIME allows for encryption (to maintain confidentiality)
and digital signatures (for authenticity and integrity). It employs
a hierarchical Public Key Infrastructure (PKI) system where certificate authorities (CAs) authenticate the identity of users and
devices, making it suitable for use in enterprise settings where
certificates can be managed and distributed through central IT
departments. S/MIME is supported by most modern email clients,
making it accessible for users needing secure and verifiable email
communication [48].
• OpenPGP (1997, IETF) — OpenPGP is an open standard for
data encryption and signing, encompassing a suite of encryption,
decryption, and signing algorithms. It was originally derived from
the PGP software, designed to be an open standard for PGP
encryption by the IETF through RFC 4880. OpenPGP is used
to encrypt not only emails but also files and directories when
privacy and security are required. It is unique because it allows

volunteer overlay network consisting of more than seven thousand relays. The design ensures that the user’s location and usage
from anyone conducting network surveillance or traffic analysis
is hidden, making it a crucial tool for preserving privacy and
freedom online [38].
• I2P (Invisible Internet Project) (2003, I2P Team and Community) — I2P specializes in allowing anonymous communication
over the internet. It uses a peer-to-peer-like routing structure to
create a private network layer that enables secure and anonymous
communication. Unique to I2P is its use of garlic routing, which
encapsulates multiple messages together to enhance security and
privacy beyond traditional onion routing [39].
• Zeronet (2015, Tamas Kocsis) — Zeronet uses Bitcoin cryptography and BitTorrent technology to build a decentralized web.
It enables open, free, and uncensorable websites, using peer-topeer networking to ensure that sites are hosted by multiple nodes,
making it difficult to shut down [40].
• Freenet (2000, Ian Clarke) — Freenet is a peer-to-peer platform
for censorship-resistant communication. It uses a decentralized
distributed data store to keep and deliver information, supporting websites, forums, and file-sharing, emphasizing privacy and
anonymity by routing data through multiple nodes [41].
• HTTPS (Hypertext Transfer Protocol Secure) (1995, Netscape)
— HTTPS ensures secure communication over a computer network, with widespread use on the Internet. Encryption via HTTPS
protects the integrity and confidentiality of data between the
user’s computer and the site, which is crucial for secure online
transactions and data privacy [42].
• TLS (Transport Layer Security) (1999, IETF) —TLS is a cryptographic protocol designed to provide secure communication
over a computer network. While SSL is the predecessor to TLS,
both are widely used to secure segments of the internet’s traffic,
safeguarding data from eavesdroppers and tamperers [43].
• SSL (Secure Sockets Layer) (1995, Netscape) — SSL operates
by establishing an encrypted link between a web server and a
browser, ensuring that all data passed between them remains
private and secure. This process involves using digital certificates,
which authenticate the identity of the parties and enable a secure
connection. The protocol uses a combination of public key and
symmetric key encryption to secure connections, which helps
protect against eavesdropping, tampering, and message forgery.
SSL protects sensitive communications, such as online banking
and shopping transactions [44].
7

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari

non-proprietary implementations, which means various software
providers can implement systems that are compatible with each
other. OpenPGP uses a combination of strong public-key and
symmetric cryptography to ensure that communications and data,
regardless of medium, remain confidential and secure. Like PGP,
OpenPGP also supports the concept of a web of trust instead of
relying solely on a hierarchical trust model used in S/MIME [49].
• WPA2/3 (Wi-Fi Protected Access 2/3) - WPA2 (2004, WiFi Alliance) and WPA3 (2018, Wi-Fi Alliance) — WPA2 and
WPA3 are security protocols and security certification programs
developed by the Wi-Fi Alliance to secure wireless computer
networks. WPA3, which replaced WPA2, provides enhanced security features, such as improved encryption and protection against
brute-force attacks [50].

Approaches, Deep Learning Approaches, and Hybrid Approaches. The
Machine Learning tier includes foundational algorithms such as J48,
Random Forest (RF), and Instance-Based Learning (IBk), which have
proven essential for baseline classifications. Expanding to Deep Learning Approaches, our taxonomy captures advanced techniques ranging
from basic neural networks to sophisticated configurations like Convolutional Neural Networks (CNNs) with multi-head attention and Spiking
Neural Networks (SNNs), highlighting their utility in intricate feature
extraction scenarios. Additionally, this group includes innovative models such as Generative Adversarial Networks (GANs) and Transformers
for dynamic learning capabilities. The Hybrid Approaches layer integrates diverse methodologies, blending Machine Learning with Deep
Learning (e.g., LSTM + RF + SVM + KNN) and advanced ensembles like
Decision Trees (DT), RF, Multi-Layer Perceptrons (MLP) with Recursive
Feature Elimination for enhanced predictive performance. This robust
framework not only delineates the structured evolution of encrypted
traffic analysis tools but also assesses their effectiveness across varied
real-world applications, providing a detailed guide for future research
directions in this rapidly evolving field.
The Tables 3,4,5,6, and 7 present an organized overview of the
datasets, encryption service, algorithms, and performance metrics utilized in ML, DL, and hybrid approaches for ETC. This structured layout
facilitates easy comparison across different studies and highlights the
variances in methodology and results within the field.
Table 3 offers a comprehensive overview of the datasets, algorithms, and performance metrics employed in machine learning (ML)
approaches for encrypted traffic classification (ETC). This table delineates the variety of datasets used, detailing their characteristics such
as size, type, and the challenges they present. Additionally, it catalogs
the ML algorithms applied, discussing their operational complexities
and the rationale behind their selection. Performance metrics such as
accuracy, precision, recall, and F1-score are systematically presented
to evaluate and compare the effectiveness of each ML approach in
handling encrypted traffic.
Tables 4,5,6 provides an exhaustive summary of the datasets, algorithms, and performance metrics utilized in deep learning (DL) approaches for ETC. It highlights the advanced neural network architectures and learning paradigms adopted to enhance detection capabilities.
This table also examines the intricacies of dataset compatibility with DL
models, emphasizing the impact of data volume and feature richness
on model performance. Essential performance metrics are analyzed
to gauge the efficiency and accuracy of DL techniques in various
encrypted traffic scenarios.
Table 7 examines the intersection of machine learning and deep
learning through hybrid approaches in encrypted traffic classification.
It details the integration of ML and DL techniques to create robust models that leverage the strengths of both paradigms. This table reviews
the algorithms in the context of their combined utility, showcasing
how hybrid models outperform single-approach models in accuracy
and reliability. Performance metrics detailed in this table highlight the
synergy effects and the enhanced capability of hybrid approaches to
adapt to the evolving landscape of network encryption.
These tables serve as a valuable resource for researchers, offering
a clear snapshot of how different strategies perform under varied
conditions and guiding future studies in selecting appropriate datasets
and algorithms to advance the accuracy and efficiency of encrypted
traffic detection systems.
The following subsections will delve into the diverse models detailed in our taxonomy, offering a critical analysis of each approach’s
efficacy. By emphasizing literature that aligns with our robust search
methodology, we ensure that our survey is exhaustive and tailored to
the field’s most impactful and innovative studies. We further synthesize
these findings into a cohesive conclusion, highlighting the present
landscape and future directions in analyzing encrypted traffic detection
and classification.

The Tables 3, 4, 5, 6, and 7 examine encryption techniques and
highlight a substantial reliance on advanced protocols such as TOR,
VPN, and others across varied computational frameworks. The deployment of such protocols has been extensively analyzed using diverse ML
and DL algorithms, including Deep Neural Networks, Graph Neural Networks, and transformer-based models. These models reflect a concerted
effort to tackle the complexities of detecting and classifying encrypted
traffic within secure communication channels.
Despite the robust theoretical foundations of TOR and VPN technologies, practical challenges persist, particularly in their integration
with ML models for real-time and accurate threat detection. The data
shows a recurring theme of employing ML techniques to improve the
effectiveness of these encryption services. However, the performance
inconsistency across different datasets suggests a crucial challenge in
generalizing these models in real-world scenarios, where encrypted
traffic patterns are continuously evolving [51].
Furthermore, as digital communication becomes increasingly encrypted, maintaining privacy while ensuring security poses a dual
challenge. Protocols like TOR, designed for anonymity, often complicate legitimate monitoring and threat detection tasks, leading to
conflicts between privacy preservation and security enforcement [52].
Future research should, therefore, prioritize the development of
adaptive encryption techniques that can operate effectively across different network architectures and conditions. Emphasizing the refinement of ML models to interpret better the nuances of encrypted traffic
within TOR and VPN usages will be crucial. This includes exploring
hybrid models that integrate the strengths of existing approaches to
create more resilient and flexible encryption systems [53].
As the digital landscape continues evolving, so does the need for robust encryption techniques/services to safeguard sensitive information
against increasingly sophisticated cyber threats. The next section transitions into a detailed literature review of technical articles, categorizing
the models employed into three distinct categories: ML, DL, and Hybrid
models. It examines the methodologies within each category, offering
a deeper understanding of their respective strengths and limitations.
5. Related work - Technical articles
This section offers a structured overview of the methodologies
employed in detecting and classifying encrypted traffic. Grounded in
a comprehensive literature review, we leveraged a robust search across
multiple databases, as detailed in Table 1. This search identified 60
pertinent papers published within the last five years, significantly shaping the current landscape of encrypted traffic analysis. These studies
are categorized into three primary methodological approaches: ML, DL,
and Hybrid Techniques. The selection and classification of these articles aligned with our search criteria to ensure comprehensive domain
coverage.
In our survey, we present an expansive taxonomy of encrypted traffic classification models designed to encompass a wide spectrum of current methodologies in the domain as illustrated in Fig. 4. Our taxonomy
categorizes approaches into three primary groups: Machine Learning
8

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari

Fig. 4. Taxonomy of encrypted traffic detection models derived from previous technical literature.

Furthermore, Choorod et al. utilized ML to effectively differentiate encrypted Tor and NonTor traffic. Focusing on unique patterns
within encrypted payloads, their approach employs DPI and statistical analysis to offer robust tools for real-time encrypted traffic monitoring and analysis, significantly contributing to network security
advancements [59].
These studies collectively underscore the potential of ML in transforming ETC, offering robust solutions to safeguard digital infrastructures.

5.1. ML models
In the evolving landscape of cybersecurity, ML techniques have
become instrumental in decrypting the complexities of encrypted traffic [54]. This innovative research category aims to devise algorithms
that can accurately classify, identify, and characterize potential cyber
threats hidden within encrypted data flows [8]. The essence of these
approaches lies in their ability to learn from data patterns, offering a
dynamic shield against evolving network vulnerabilities [55]. We delve
into the significant contributions that have pushed the boundaries of
this field, each presenting a unique angle on encrypted traffic analysis.
Recent advancements in ETC leverage various innovative ML techniques to enhance the granularity and accuracy of analysis. Zaki, F.
et al. developed ‘‘Granular multi-label encrypted traffic classification
using classifier chain(GRAIN) [56]’’, which employs classifier chains to
dissect network traffic into detailed classes. Their method significantly
improves classification through novel statistical features derived from
packet payload lengths, thereby preserving user privacy. In a similar
vein, Dong, S. et al. tackled the challenge of data imbalance common
in network traffic classification by introducing a cost-sensitive SVM
enhanced by active learning, which dynamically adjusts weights to enhance accuracy across varied traffic types [57]. Yao, Z. et al. combined
Gaussian Mixture Models with Hidden Markov Models to provide a
nuanced classification of encrypted traffic, leveraging statistical and
temporal patterns for improved network security analytics [58].

5.2. DL models
DL approaches have significantly advanced encrypted traffic analysis in network security, offering profound insights and enhanced
detection capabilities for concealed cyber threats [60]. These methodologies excel in interpreting complex data patterns, thereby fortifying
digital defenses against sophisticated attacks [61]. We highlight key
contributions in this area and explore the pivotal studies that have
notably enriched our understanding and classification of encrypted
network traffic [62].
5.2.1. Auto encoders
In encrypted traffic analysis, innovative applications of autoencoders are paving the way for enhanced precision and efficiency. Lv,
9

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari

S. et al. [63] introduce Adversarial AutoEncoders with Deep Support Vector Data Description(AAE-DSVDD), a model to elevate VPN
traffic analysis. This method significantly improves the analysis of
VPN traffic, providing a deeper understanding of encrypted network
traffic flows, thus enhancing network security measures. Additionally,
Aceto, G. et al. [64] present DISTILLER, a multifaceted classifier that
capitalizes on multimodal and multitask DL techniques. By harnessing
diverse input data, DISTILLER effectively navigates the complexities
of ETC, overcoming the constraints of traditional single-mode learning
approaches. This model’s versatility allows it to handle various classification tasks concurrently, showcasing a significant step forward in
adapting to the dynamic nature of network security.

balancing computational efficiency with accuracy. Wang, M. et al. [77]
and Lotfollahi, M. et al. [62] further advanced CNN utility by pairing
them with Stacked Auto Encoders (SAEs), with notable success in
differentiating VPN and non-VPN traffic and reducing information loss.
Soleymanpour [78] et al. addressed unbalanced data challenges in
traffic classification through CSCNN, a cost-sensitive CNN model that
enhances accuracy for minority classes. Concurrently, Xu, L. et al. [79]
demonstrated the adaptability of Siamese convolutional networks in
ETC, which can handle dataset limitations effectively.
In a novel approach, Lin, C. Y. et al. combined CNNs with Bidirectional GRUs, enhancing spatial and temporal feature extraction to analyze encrypted data streams [80] comprehensively. Izadi, S. et al. [81]
proposed combining CNNs with evolutionary algorithms, such as AntLion Optimizer and Self-Organizing Maps with fuzzy logic, to improve
classification accuracy in cybersecurity.
Other notable contributions include Habibi Lashkari, A. et al. [82]
and Lan, J. et al. [83], who enhanced darknet traffic detection using deep image learning and advanced neural mechanisms like selfattention and Bi-LSTM, respectively. Moreover, innovative frameworks
like BFSN [84], AEFETA [85], and tCLD-Net [86] have utilized combinations of CNNs with LSTMs and attention mechanisms to tackle the
complexities of ETC, showcasing significant enhancements in handling
encrypted communications.
Further enriching the field, new architectures such as SPPNet [87],
CENTIME [88], and EETC [89] leverage DL to surpass traditional classification tools inefficiencies, with focus on real-time processing and incremental learning. Also, innovative methods like the CBD model [90]
and BCFNet [91] have explored the combination of CNNs with emerging technologies like BERT and multi-scale feature fusion to capture
detailed traffic characteristics, thus setting new benchmarks in ETC.

5.2.2. Neural networks
The exploration of neural networks in network security represents a
critical evolution in identifying and classifying encrypted traffic [65].
Neural network models, with their profound learning capabilities, offer
nuanced approaches to understanding complex data patterns, thereby
enhancing the identification of cyber threats within encrypted data
flows [66]. This section outlines significant advancements across various neural network architectures, each contributing uniquely to ETC. It
includes a dedicated subsection on models integrating CNNs to enhance
feature extraction and classification accuracy.
The use of neural networks in the domain of ETC has witnessed
several innovative contributions that enhance network security systems’ functionality and accuracy. Jorgensen, S. et al. [67] explore VPN
application labeling through a Probabilistic Neural Network (PNN) that
incorporates uncertainty quantification, markedly improving reliability
by addressing inherent uncertainties in encrypted environments. Furthermore, Song, Z. et al. [68] introduce I2 RNN, an Incremental and
Interpretable Recurrent Neural Network that not only focuses on interpretability but also adapts incrementally to new traffic types through
a fingerprint learning process significantly enhancing the dynamics of
network security measures.
Zhou, K. et al. [69] employ a combination of neural networks and
entropy estimation to refine traffic classification, differentiating between encrypted and plaintext traffic while offering precise applicationspecific insights. Additionally, Pathmaperuma, M. H. et al. utilize Deep
Neural Networks (DNNs) to achieve fine-grained detection of in-app
activities, demonstrating high accuracy in identifying both known and
unknown data patterns [70].
Rasteh, A. et al. explore the potential of Spiking Neural Networks
(SNNs) for classifying encrypted internet traffic, capitalizing on their
ability to recognize time-related data features, offering a promising
alternative to conventional neural models [71]. Lastly, Xu, Y. et al.
present ‘FastTraffic’, a lightweight Multilayer Perceptron (MLP) framework designed for real-time ETC on less capable devices, striking a
balance between efficiency and efficacy [72].

5.2.2.2. Graph-based neural networks. Using Graph-Based Models in
network security offers a nuanced and powerful approach to analyzing encrypted traffic. These models provide an advanced framework
for detecting and classifying cyber threats by harnessing the intricate
structures and relationships within network data [92,93]. This section
delves into recent innovations that leverage graph-based techniques to
enhance the precision and robustness of ETC [93].
Several groundbreaking approaches have been introduced in the
innovative realm of graph-based models for ETC, each contributing
unique insights into network traffic analysis. Diao, Z. et al. [94] have
developed EC-GCN, a sophisticated framework employing multi-scale
graph convolution networks to capture spatial–temporal traffic features. This dynamic, graph-based analysis adapts well to noise and
changes in network conditions, marking a significant leap forward in
the field.
Expanding upon this foundation, Hong, Y. et al. [95] presented
’MalDiscovery,’ a graph-based method for detecting malicious traffic within encrypted communications. By integrating the GraphSAGE
model with multi-view features, ‘MalDiscovery’ improves the detection
accuracy and enhances the efficiency of analyzing malicious activities,
leveraging a comprehensive graph-based approach to explore traffic
correlations more deeply.
Wang, L. et al. [96] introduced TGPrint, which uses Graph Convolutional Networks (GCNs) combined with attention mechanisms to transform network traffic into attack graphs. This innovative method significantly improves the accuracy of classifying different types of attacks
in encrypted traffic, including those previously unseen, showcasing the
robust potential of graph-based analytical techniques.
Further advancing the field, Han et al. [97] unveiled the Dual Embedding with Graph Neural Network (DE-GNN) model, which conducts
a fine-grained ETC by separating packet headers and payloads during
the initial encoding phase. This method uses PacketCNN to extract
packet-level features. It constructs a Traffic Interaction Graph (TIG) for
analyzing flow-level features through Graph Neural Networks (GNNs),
thus enhancing classification accuracy by effectively integrating these
disparate data aspects.

5.2.2.1. Convolutional Neural Networks (CNNs). CNNs have become
a cornerstone in network security, especially for the ETC [60]. By
exploiting spatial hierarchies in data, CNNs offer an unparalleled ability
to extract features and identify patterns within complex, encrypted data
streams [73]. This segment showcases various innovative approaches
leveraging CNNs, each addressing specific challenges in analyzing encrypted traffic [62].
The utilization of CNNs in the analysis of encrypted traffic has
evolved with several innovative contributions enhancing the accuracy
and efficiency of classification. He, Y. et al. [74] pioneered an imagebased approach, transforming network session payload sizes into gray
images for classification via CNNs, simplifying feature extraction, and
enhancing traffic classification accuracy. Further expanding CNN applications, Moreira, R. et al. combined CNNs with Reinforcement Learning
to optimize TOR traffic classification. SqueezeNet demonstrates rapid
prediction capabilities vital for real-time applications [75].
Cheng, J. et al. [76] introduced MATEC, integrating multi-head
attention with CNNs to excel in real-time encrypted traffic analysis,
10

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari

Zhang et al. [98] proposed the Contrastive Learning Enhanced
Temporal Fusion Encoder (CLE-TFE), combining supervised contrastive
learning with cross-level multi-task learning for ETC. This model utilizes contrastive learning to improve semantic invariance across packetand flow-level representations, thereby significantly boosting classification performance.
Lastly, Yang et al. [99] introduced MTSecurity, a model that uses
Graph Neural Networks (GNNs) and Transformer technologies to classify encrypted malicious traffic. By combining byte features with graphbased traffic interaction features through the innovative Malicious
Traffic Interaction Graph (MTIG), this model sets a new benchmark
in network security analytics with its robust detection capabilities,
significantly improving the classification accuracy outcomes across
diverse datasets. Together, these advancements underscore the significant impact of graph-based models on the evolving landscape of ETC,
highlighting their potential to transform cybersecurity practices.

Together, these studies showcase the significant strides in employing
advanced ML techniques, particularly semi-supervised and transformer
models, to tackle the complexities of ETC in the modern cybersecurity
landscape.

5.3. Hybrid models
The Hybrid Model Approaches in ETC demonstrate the synergy
between ML and DL and their integration with traditional methodologies. They offer robust, versatile, and innovative solutions to network security challenges [110]. This category underscores the strength
of combining different analytical techniques to enhance classification
accuracy, adaptability, and computational efficiency [111].
Marim, M.C. et al. [112] highlight the enduring utility of classical
ML models like Decision Trees and Multilayer Perceptrons in classifying
darknet traffic using the CIC-Darknet2020 dataset, emphasizing their
role in offering interpretability and efficiency. Xu, B. et al. [113] introduce ME-Box, a system that integrates ML with evidence verification to
balance security and privacy in encrypted traffic detection, signaling a
shift towards adaptive security strategies.

5.2.3. Generative Adversarial Networks (GANs) and transformers
The category of Generative Adversarial Networks (GANs) and Transformers presents an avant-garde approach to ETC, leveraging the generative capabilities of GANs and the sophisticated processing power of
transformer models [100]. These methodologies offer innovative solutions to longstanding challenges in network security, such as class imbalance, data augmentation, and feature extraction. This section showcases the notable advancements in employing GANs and transformers
to analyze encrypted network traffic [100,101].
Several pioneering approaches have emerged in the domain of
Generative Adversarial Networks (GANs) for the analysis of encrypted
traffic. Tang, Z. et al. [102] have introduced Markov-GAN, which
transforms encrypted traffic into Markov images to enhance classification, creatively merging GANs with Markov image transformation to
improve dataset quality and address limitations of traditional methods.
Meanwhile, Wang, P. et al. [103] tackled the issue of class imbalance
through PacketCGAN, using Conditional GANs to generate samples for
underrepresented classes, thereby balancing datasets and enhancing DL
classifier performance in the analysis of encrypted traffic.
Continuing this innovative trend, Sanjalawe, Y. et al. [104] combined GANs with Vision Transformers (ViTs) for the detection of obfuscated internet traffic, a method that surpasses the capabilities of
conventional CNNs and RNNs by leveraging GANs for data augmentation and ViTs for effective feature extraction. In a similar vein, Wang, P.
et al. [105] explored ETC using the semi-supervised GAN model ByteSGAN, focusing on SDN Edge Gateways to demonstrate the adaptability
of semi-supervised learning in the evolving landscape of network security. Additionally, Zhao, R. et al. [106] introduced MT-FlowFormer.
This semi-supervised transformer-based framework adeptly manages
the complexities of encrypted network traffic by leveraging the benefits
of transformers and semi-supervised learning to address the scarcity of
labeled data. Together, these studies illustrate significant advancements
in applying GANs to encrypted traffic detection and classification,
heralding a new era of possibilities in cybersecurity methodologies.
Further extending the use of transformers, Lin, X. et al. [107]
introduced ET-BERT, employing transformers for pre-training on largescale unlabeled encrypted traffic, which enhances traffic classification
by capturing contextualized datagram representations. In a similar
vein, Huang et al. [108] unveiled the BSTFNet model, which uniquely
combines global semantic features extracted by transformers alongside
local spatiotemporal features analyzed using BiGRU and TextCNN,
effectively classifying encrypted traffic with notable accuracy on the
USTC-TFC2016 dataset.
Adding to these advancements, Park et al. [109] presented a method
that uses the multi-task learning model, DistilBERT, for encrypted network traffic classification. This innovative approach facilitates simultaneous training across multiple classification tasks—encapsulation, category, and application—within a single model framework, significantly
enhancing efficiency and accuracy in network security management.

Further, Hu, Y. et al. [114] detail a hierarchical hybrid classifier
merging ML and DL for analyzing user behavior in darknet environments, providing deep insights into anonymous online activities.
Rust-Nguyen, N. et al. [115] evaluate the resilience of ML and DL
models against adversarial attacks, underscoring the necessity of robust
models in cybersecurity. Malekghaini, N. et al. [116] explore AutoML
and Neural Architecture Search in ‘‘AutoML4ETC’’, demonstrating their
potential in optimizing neural networks for encrypted traffic analysis.
Elmaghraby, R. T. et al. [117] examine advanced ML and DL techniques, focusing on distinctive feature extraction such as packet length
and timestamps to improve network management. Luo, P. et al. [118]
propose an ML-based system incorporating ‘BITization’ and an optimal
sliding window technique, marking significant progress in encrypted
traffic pattern recognition.
Yan et al. [119] introduce a high-speed classification method using
payload features and a Random Forest model, efficiently distinguishing
between encrypted and unencrypted traffic. Zhao et al. [120] present
METAROCKETC, a framework combining time series analysis and metalearning for rapid adaptation to ETC tasks. This adaptive framework
exemplifies integrating innovative techniques to tackle the dynamic
challenges of encrypted traffic analysis.
Li et al. [121] present the MISS framework, an incremental learning
system for ETC that adapts efficiently to new network applications
without complete retraining. This method conserves resources and enhances model scalability by exploiting multi-view sequences to obtain
a comprehensive feature set.
Wang et al. [122] propose a classification method with contrastive
learning, incorporating spatial and temporal feature fusion for a consistent representation of traffic samples. Finally, Wang and Gu [123]
introduce a multi-task scenario approach with a Parameter-Efficient
Fine-Tuning method, enhancing computational efficiency and interpretability in ETC, potentially transforming network security practices.
Together, these studies demonstrate the profound impact of hybrid
models in advancing the analysis of encrypted traffic, setting new
standards in network efficiency and security.
In summary, the hybrid model approaches in ETC exemplify how
the convergence of ML, DL, and traditional methods can create powerful tools for addressing the complexities of network security. These
integrative strategies improve the accuracy and efficiency of classification systems and pave the way for more adaptive and forward-thinking
solutions in the ever-evolving field of cybersecurity.
11

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari

• MOORE_SET and NOC_SET(2013, Moore, A. W., & Shi Dong)
— Analyzes network behavior and security through data from internet communications at a research site and Southeast University
using protocols like HTTP, FTP, and SMTP. Although valuable for
network protocol analysis, the dataset falls short in representing
a diverse range of global internet traffic conditions, potentially
limiting its applicability in varied geographical contexts [130].
• ISCX Tor/Non-Tor 2016 (2016, Canadian Institute for Cybersecurity) — Includes Tor and non-Tor traffic for ETC. Mixes Tor
and non-Tor traffic using protocols like HTTP, HTTPS, SMTP/S,
and FTP over SSH. While the dataset effectively detects encrypted
Tor traffic, its specific focus on Tor limits its broader applicability
to other types of encrypted communications [131].
• ISCX VPN/Non-VPN 2016 (2016, Canadian Institute for Cybersecurity) — Includes traffic from VoIP, P2P, and streaming
over VPN and non-VPN channels. Analyzed using ISCXFlowMeter.
The dataset primarily focuses on VPN traffic, which may not
adequately represent the full spectrum of network threats, thereby
narrowing its utility in broader security contexts [55].
• USTC-TFC2016 (2016, University of Science and Technology
of China) — Features traffic from applications like BitTorrent
and Skype and malware communications. Aimed at distinguishing
between user data and security threats. This dataset does not extensively cover all types of encrypted traffic, which may limit its
effectiveness in comprehensive encrypted traffic analysis [132].
• BetterNet HTTPS (2016, Wazen Shbair) — Captures full HTTPS
raw PCAP files from popular websites, aiding in HTTPS traffic
analysis. The dataset focuses exclusively on web traffic, omitting other crucial network interactions, which might restrict its
relevance in more comprehensive network studies [133].
• Anon-17 (2017, Network Information Management and Security Lab) — Focuses on the operational dynamics within
anonymity networks such as Tor, I2P, and JonDonym. It provides an extensive collection of benign, encrypted, and nonencrypted traffic to facilitate research on the effectiveness of
these anonymity services. The dataset includes detailed protocol
usage across various scenarios to examine how these networks
manage privacy protection. A notable limitation of Anon-17 is its
exclusion of malicious traffic and modern attack vectors, which
may affect the applicability of the findings to real-world threat
scenarios [134,135].
• CIC IDS2017 (2017, Canadian Institute for Cybersecurity)
— Captures benign and malicious traffic using protocols like
HTTP and FTP, including DDoS and Heartbleed attacks. While
the dataset is tailored towards intrusion detection, this focus
might overlook the nuances of deeper encrypted traffic analysis,
potentially limiting the dataset’s broader applicability [136,137]
.
• Google Home(2018/20, C Wang, S Kennedy) — Focuses on
device-specific interactions through 100 voice commands, collecting 1500 traffic traces per command over nine weeks. A
significant dataset for studying responses within a controlled
environment. The dataset is specific to Google Home, which
limits its generalizability to other encrypted voice-activated devices and may reduce its applicability in broader IoT security
analyses [138].
• Mirage (2019, ARCLAB, University of Napoli ‘Federico II’) —
Focuses on mobile app traffic analysis by capturing encrypted
traffic from Android devices. This dataset includes traffic from
various applications across multiple protocols to differentiate between app-specific traffic patterns. The dataset is noted for lacking traffic diversity related to direct attacks, which may impact its
applicability in network security research. However, its comprehensive data on mobile application behavior makes it invaluable
for studying encrypted mobile traffic characteristics [139].

5.4. Synthesis
Classifying encrypted traffic is a crucial yet complex challenge in the
dynamic field of network security. As we delve into the multifaceted
issues of computational efficiency and resource demands, this section
explores the inherent limitations and potential drawbacks of current
models/techniques utilized in this domain.
We focus on high computational complexity and the resourceintensive nature of preprocessing and model architecture. These factors
significantly determine the practicality of deploying these models in
real-time or resource-constrained environments. The limitations include but are not limited to the dependency on diverse and quality data,
the scalability and complexity of models, the necessity for continuous
adaptation and learning, and the feasibility of real-time processing.
Every element is essential in understanding the broader implications
of ETC systems and their viability in contemporary networked environments. The following bullet points outline these limitations, each
supported by specific references that, to some extent, illuminate the
discussed shortcomings.
• High Computational Complexity [62,63,72,75,86,96,98,99,103,
108,124]
• Resource-Intensive Preprocessing and Model Architecture [69,90,
109]
• Impact of Data Quality and Diversity on Model Effectiveness [64,
69,76,84,95,104,112,116,119,123]
• Challenges in Data Collection and Representation [56,74,78,107]
• Complex Model Integration and Scalability Issues [67,70,79,80,
96,117,125,126]
• Scalability Concerns Due to Advanced Features [106,127]
• Need for Ongoing Model Updates [57,67,71,77,102,121,128]
• Adaptation Challenges in Evolving Network Conditions [115,120]
• Real-Time Application Feasibility [63,81,82,87–89,95,105,114]
• Practical Deployment Issues in Dynamic Networks [68,94,102]
This study of the drawbacks and limitations in the models of ETC
highlights critical challenges that impact the practical deployment of
sophisticated models. High computational complexity and resourceintensive processes hinder real-time applications and limit the scalability necessary for broader network implementations. By analyzing these
limitations, this survey paper sets the stage for further discussion on
the need for model innovation and optimization. The insights gathered
here underscore the urgency for developing more efficient techniques
that do not compromise performance while ensuring adaptability and
minimal resource utilization. As we progress, these considerations will
guide the development of more robust and practical solutions in the
ever-evolving network security landscape.
6. Encrypted traffic datasets
The rapid expansion of encrypted traffic across the internet necessitates the creation of advanced techniques for its overall analysis
and classification. Encrypted traffic data collection is critical in this
process, providing the raw material necessary for training ML, DL,
and hybrid models. The efficacy of these models heavily depends on
the diversity and quality of the datasets utilized. In this section, we
discuss the various encrypted traffic datasets available chronologically
to underscore the characteristics and features of a high-quality dataset.
We will also score the used datasets presented in recent literature and
categorize them based on the encryption technique used, labels, attack
diversity, etc.
• CTU-13 (2011, CTU University, Czech Republic) — Focuses
on botnet behavior analysis in network traffic. Analyzes botnet
traffic across 13 scenarios with various protocols to differentiate
between malicious and benign traffic. The dataset exhibits a
notable limitation in its lack of direct focus on modern encrypted
traffic technologies, which may impact the generalizability of the
findings [129].
12

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari
Table 3
Overview of datasets, algorithms, and performance metrics in ML approaches for ETC.

Ref.

Dataset used

Algorithm/
Model used

Type of
encryption
service

Precision

Recall

Accuracy

F1-Score

Others

Additional
comments

Zaki et al. [56]

ISCX-VPN2016

Chained RF

VPN

100%,
100%

100%,
93%

–

100%,
94%

–

Application
Name level,
Application
Service
level

Dong [57]

MOORE_SET
and NOC_SET

SVM with
Active
Learning

Others

–

–

–

–

G-mean:
0.718,
0.768;
MAUC:
0.709,
0.774

–

Yao et al. [58]

CIC-IDS2017
and private
traffic dataset
collected from
a self-built
LAN

GMM, HMM

Others

100%

99.43%

99.98%

99.72%

–

–

Choorod et al. [59]

UNB-CIC and
ISCXTor2016

J48, RF, IBk

TOR

0.93%

0.93%

95.65%

0.93%

–

Avg, J48

• Orange (2020, Orange Labs, France) — Focuses on encrypted
web traffic classification using deep learning to enhance service
detection across multiple web protocols such as HTTP/2 and
QUIC. The dataset captures a comprehensive mix of encrypte

[...正文过长，此处由批处理脚本仅做上下文截断；请在结论中说明该限制...]

21(Tor, I2P,
Jon Donym)-2021

Zhao et al. [147]

17

21

CSTNET TLS 1.3-2021

Lin et al. [107]

11

22

Self Generated Public
– Dataset7cz -2021

Pathmaperuma et al. [70]

10

23
24

CESNET-QUIC22
AppClassNet-2022

Luxemburk et al. [150]
Wang et al. [151]

17
16

25

Self Generated Private
– Pure TLS-2022

Li et al. [121]

9

26
27

5GAD dataset-2022
CIC IoT -2023

Coldwell et al. [152]
Neto et al. [153]

11
20

28

VPN/NonVPN Network
Application Traffic Dataset
(VNAT)-2023

Jorgensen et al. [154]

13

29

Self Generated Private
- OBW 30 HW19-2023

Diao et al. [155]

11

30

Self Generated Private
– TCP/UDP- 2024

Elmaghraby et al. [117]

12

31

BCCC-cpacket-cloud
-DDoS-2024

Shafi et al. [156]

15

a broad range of features from network traffic. Its development
aimed to support the needs of researchers by providing detailed
flow-level information, facilitating the study of network behavior
and security incidents [55].
• CICFlowMeter (2017, Canadian Institute for Cybersecurity):
CICFlowMeter, developed by the same institute as ISCX, offers
enhanced capabilities for traffic analysis. It can generate bidirectional flows with nearly 80 statistical features, crucial for
analyzing encrypted and unencrypted traffic [162].
• NFStream (2019, Free Software Foundation, Inc.): NFStream
is a multiplatform Python framework providing fast, flexible, and
expressive data structures designed to make working with online
or offline network data easy and intuitive. It aims to be Python’s

fundamental high-level building block for practical, real-world
network flow data analysis. Additionally, it has the broader goal
of becoming a unifying network data analytics framework for researchers providing data reproducibility across experiments. NFStream is a recent addition to the field, offering high-performance
flow-based network traffic analysis. Its design prioritizes efficiency and scalability, making it suitable for modern high-speed
networks [163].
• NTLFlowLyzer (2024, MM Shafi, AH Lashkari): NTLFlowLyzer
produces bidirectional flows from the Network and Transport
Layers of network traffic, with the initial packet defining the forward (source to destination) and backward (destination to source)
directions. This allows for the separate calculation of statistical
20

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari

time-related features in both directions. Additional capabilities
include selecting from existing features, introducing new features,
and managing flow timeout duration. Moreover, TCP flows are
terminated upon connection teardown (by FIN or RST packet),
reaching the flow’s maximum duration, or being inactive for a
certain amount of time (timeout) [156].
• ALFlowLyzer (2024, MM Shafi, AH Lashkari, H Mohanty):
ALFlowLyzer generates bidirectional flows from the Application
Layer of network traffic, with the initial packet defining the forward (source to destination) and backward (destination to source)
directions. This enables the separate calculation of statistical
time-related features for each direction. It also offers functionalities such as selecting from existing features, adding new ones,
and managing the flow timeout duration. The current version
supports DNS protocol; in the next versions, other protocols will
be supported [164].

on creating more advanced, efficient, and adaptable analyzers to meet
the evolving challenges in encrypted traffic analysis.
8. Challenges & Future work
In this survey paper, we explore the various methodologies and
technologies employed in detecting and classifying encrypted traffic,
identifying critical gaps and highlighting the limitations of current approaches. Despite significant advances, recurring shortcomings inhibit
the practical application of these technologies in real-world scenarios. The following paragraphs delineate the remaining challenges and
outline future directions for research, as discussed in the subsequent
sections of this paper.
In Section 3, ‘‘Previous Survey Papers’’, we assess the foundational
insights provided by existing literature and pinpoint substantial limitations in the scope and methodologies of surveyed studies. Many focus
narrowly on specific technologies, predominantly leveraging ML and
DL, often overlooking their integration into real-world scenarios. This
results in gaps such as inadequate protocol-specific analyses and a general disregard for operational challenges like scalability and efficiency
in deployment. Future work should bridge these gaps by integrating
upcoming ML/DL models with practical deployment scenarios.
Section 4, ‘‘Encryption Techniques/Services’’, highlights various encryption techniques’ characteristics and usage patterns. Despite the
wide application of encryption techniques such as VPNs and Tor,
there is a lack of in-depth comparative analysis to understand why
certain protocols are preferred over others. Future research should
delve deeper into these choices and their implications for security
solutions, aiming to improve the synergy between encryption methods
and analytical models.
In Section 5, ‘‘Related Work—Technical Articles’’, we review the
limitations and drawbacks of ETC models. Their high computational
complexity and resource-intensive nature hinder their scalability and
real-time application. The need for innovation in model design is clear,
with future research focusing on developing more efficient methods
that maintain performance while ensuring adaptability and minimal
resource utilization.
Section 6, ‘‘Encrypted Traffic Datasets’’, examines the datasets used
in encrypted traffic detection and classification. A significant challenge
is the lack of datasets combining encrypted and non-encrypted traffic
with comprehensive metadata. Future efforts should aim to create more
inclusive datasets that cover a broader spectrum of encryption services
and attack types, thus providing a richer foundation for model testing
and development.
In Section 7, ‘‘Information Extractors (IE) or Traffic Analyzers’’, we
evaluate the capabilities and limitations of various analyzers used in
network traffic analysis. The current tools often fall short in scalability,
real-time processing, and adaptability to new encryption protocols. Future research should focus on creating advanced analyzers that are efficient, adaptable, and capable of handling the complexities of modern
encrypted traffic.
In synthesizing the findings from the various sections of this survey,
the following key challenges and directions for future research are
proposed, each based on specific observations and gaps identified in
encrypted traffic detection and classification as denoted in Fig. 5:

The Table 11 presented in this section provides a detailed examination of several prominent analyzers, including ALFlowLyzer, NTLFlowLyzer, NFStream, CICFlowMeter, ISCX Flowmeter, Tranalyzer, NetFlow,
Zeek, and Argus in a chronological manner. This chronological range
allows us to observe significant advancements in the number of features
these tools can extract, and the programming languages used, showcasing a trend towards more robust and flexible systems. Each entry
encompasses critical details such as the Analyzer’s Name and Number
of Extracted Features, Source code availability, Programming language,
Supported protocols, and Key features they present.
The table shows a trend in the increasing complexity of supported
protocols and the shift in programming languages from predominantly
C in the earlier tools to Python in the more recent analyzers. For
instance, ‘ALFlowLyzer’ (2024) and ‘NFStream’ (2019) utilize Python,
indicating a preference for this language in contemporary network
traffic analysis owing to its extensive libraries and community support. This shift also correlates with the broader implementation of ML
techniques, as Python is well-suited for such applications.
The table also reveals a progression in the number of extracted
features, from 30+ in ‘Argus’ (1986) to 348 and 130 in ‘NTLFlowLyzer’
(2024) and ‘ALFlowLyzer’ (2024) respectively. This increase is pivotal
as it reflects the growing complexity of network environments and the
corresponding need for more granular data to perform sophisticated
analysis. For example, ‘ALFlowLyzer’ supports DNS protocol analysis
and integrates application-layer protocol visibility, which is vital for
modern cybersecurity applications.
Researchers can leverage this data to identify gaps in current
methodologies or extend existing analyzers with newer protocols and
ML techniques. Enhancing C-based analyzers like ‘NetFlow’ (1996)
with modern capabilities or developing new tools that integrate crossprotocol analysis and real-time processing to address emerging security
threats are viable paths forward. Additionally, open-source tools are
advantageous for academic research, allowing for customization and
further enhancement. This synthesis provides a comprehensive understanding of the current landscape. It underscores the continuous
progression and innovation in the field, charting a path forward for
the next generation of network traffic analyzers.
The broad spectrum of Traffic Analyzers or IEs available for detecting and classifying encrypted traffic demonstrates the ongoing efforts to
tackle the complexities of modern network environments [165]. However, despite the advancements, there remains a notable gap in developing analyzers that can seamlessly integrate with emerging technologies
and handle increasingly sophisticated encryption methods [27]. The
need for new, innovative analyzers is evident, as current tools often
fall short in scalability, real-time processing, and adaptability to new
encryption protocols. Future research and development should focus

•

21

Development of Comprehensive Models: A critical finding
across multiple studies reviewed in this survey is the need for
models that can handle encrypted traffic’s dynamic and evolving
nature. Current machine learning (ML) and deep learning (DL)
models often struggle with high-dimensional data and real-time
requirements due to the computational intensity of encryption
and decryption processes. Integrating advanced ML and DL techniques, such as reinforcement learning and transfer learning,
has shown promise in other cybersecurity areas but remains

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari

Table 11
Overview of analyzers/IEs employed in encrypted traffic studies.

Name of
analyzer

No. of
features

Source code
availability

Programming
language

Supported
Protocols

Key features

ALFlowLyzer
2024

130

Yes

Python

DNS

Application layer protocol scalability
& analysis.

NTLFlowLyzer
2024

348

Yes

Python

TCP Based

Comprehensive feature set, Impressive
performance metrics, Capability to handle
and analyzecloud traffic effectively

NFStream
2019

88+

Yes

Python

TCP, UDP, IP

High-performance tool for encrypted
application identification and statistical
feature extraction, offering extensibility via
NFPlugins and a standardized framework for
reproducible machine learning in network
traffic management.

CICFlowMeter
2017

80

Yes

Java

TCP, UDP

Generates and analyzes bidirectional
network traffic flows, calculating statistical
features in both directions and offering
customizable settings for feature selection and
flow timeouts.

ISCX
Flowmeter
2016

28

Yes

Java

TCP, UDP

Creates bidirectional flows, allowing
for the separate calculation of statistical
time-related features in each direction. It
provides options for feature customization
and flow timeout control, with flows
outputting based on connection teardown for
TCP and user-defined timeouts for UDP.

Tranalyzer
2008

14+

Yes

C

ARP, CDP, DNS,
FTP, HTTP, ICMP,
LLDP, MODBUS,
MQTT, NTP,
RADIUS,
SSH, STP, TCP, VRRP

Lightweight,
Extensible plugins/modules.

NetFlow
1996

19+

Yes

C

IP, TCP, UDP

Key features include the aggregation of
packets into flows, the export of flow records
to collectors, and the use of data for network
monitoring and intrusion detection.

Zeek(BRO)
1995

25+

Yes

C++

Multiple protocols
including HTTP,
DNS, FTP

In-depth protocol analysis with
application-layer insights, supported by a
domain-specific scripting language for
adaptable monitoring. It is designed for
high-performance networks, maintaining
extensive stateful data and providing a
comprehensive archive of network activity.

Argus
1986

30+

Yes

C

IP, TCP, UDP,
ICMP & Others

High-performance data capture, extensive
protocol support, Provides a comprehensive
audit engine for all network traffic, designed
to support diverse network management
functions including security.

Name of Analyzer: The name of the analyzer or information extractor. No. of Features: Tells the no. of features the analyzer extracts. Source Code Availability:
Whether the source code for the analyzer is publicly available (Yes/No). Supported Protocols: The analyzer can process network protocols (e.g., TCP, UDP, ICMP).
Key Features: Notable features or characteristics of the analyzer. ‘‘+’’ - Means protocol wise more features added(PLUGINS BASED FEATURES).

• Creation of Rich Datasets: The survey identified a prominent
gap in the availability and diversity of datasets covering encrypted traffic. Current datasets are limited in scope, often focusing on narrow encryption services or attack types (e.g., VPN or
Tor traffic). This restricts the ability of models to generalize across
different real-world scenarios. Richer datasets encompassing a
wider range of encrypted services, attack vectors, and protocols
are required. For example, while VPN and Tor datasets are common, there is a lack of datasets reflecting the rapidly increasing
use of newer encryption methods like DNS over HTTPS (DoH) and
TLS 1.3 combined with various services. Furthermore, existing
datasets often lack comprehensive metadata, making it challenging to simulate real-world network conditions. As highlighted

underutilized in encrypted traffic. For instance, our analysis of recent detection frameworks indicates that models trained on static
datasets quickly become outdated, lacking adaptability to emerging encryption standards and novel attack patterns. Future models
should simulate actual encryption scenarios, such as continuously
adapting to updated encryption protocols (e.g., TLS 1.3) and
evolving attack techniques, to enhance robustness and resilience.
An example of this need is the integration of federated learning in
privacy-sensitive environments, where centralized training can be
challenging. A federated approach could enable continuous model
refinement across distributed data sources without compromising
user privacy.
22

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari

Fig. 5. Proposed future research directions.

in our dataset analysis, comprehensive datasets with labeled encrypted and non-encrypted traffic would support the development
of more nuanced models capable of differentiating between legitimate and malicious traffic. Therefore, future datasets should
capture more granular information, including the type of encryption and traffic context (e.g., benign vs. malicious traffic in
IoT and edge devices), enabling more robust model training and
validation.
• Enhanced Analytical Tools: Emerging encryption standards and
the increasing volume of encrypted traffic have revealed limitations in existing analytical tools, particularly in real-time processing and protocol adaptability. For instance, the survey found
that traditional traffic analysis tools often struggle with newer
encryption technologies, which obscure payload data and thereby
impede effective traffic inspection. This challenge has increased
as organizations adopt stronger encryption standards like TLS 1.3,
which minimizes visibility by limiting middlebox compatibility.
Analytical tools need to be adaptable, efficient, and capable of
functioning in real-time, with a focus on non-intrusive techniques
that respect user privacy. For example, tools leveraging sidechannel analysis or encrypted traffic flow characteristics could
provide insights into traffic patterns without decrypting data.
Enhanced tools could also use AI-driven anomaly detection to
identify suspicious patterns in encrypted flows, enabling rapid
responses to potential threats. To accommodate these needs, future tools should prioritize modularity, allowing them to integrate
seamlessly with a variety of encryption protocols and to scale with
evolving encryption methods.

transparent and trustworthy [169,170]. However, the adoption of these
technologies in encrypted traffic classification remains limited, presenting a crucial area for future research and development. Exploring
these methodologies could lead to more robust, privacy-preserving, and
transparent solutions, essential for next-generation network security
frameworks.
9. Conclusion
This survey has critically examined the domain of ETC, an everevolving field pivotal to maintaining network security in an era of
ubiquitous encryption. Encryption, while essential for privacy, poses
substantial hurdles to traditional network monitoring and threat detection methods, necessitating a balanced approach that respects user
privacy without exposing network vulnerabilities.
Throughout this survey paper, we have traced the trajectory of
advancements in the field of ETC, emphasizing the amalgamation of
cutting-edge ML and DL technologies. These technologies have shown
promise in parsing encrypted traffic, yet they grapple with the robustness of modern encryption and the mutable characteristics of network
flow. As highlighted in the ‘‘Challenges and Future Work’’ section, there
remains a pressing need for research strategies that refine these technologies and address operational challenges like scalability, efficiency,
and adaptability to diverse encryption standards.
The analysis has revealed a significant gap in the comprehensive
evaluation of encrypted traffic tools and methodologies. Many existing surveys focus too narrowly on DL and ML applications, often
overlooking the practical deployment challenges critical for real-world
applicability. Our findings suggest that future research should pivot
towards creating more adaptive and lightweight models that maintain
high performance while being feasible for everyday use. Moreover,
the lack of expansive datasets that blend encrypted and non-encrypted
traffic continues to be a bottleneck in developing more sophisticated
analysis models.
In conclusion, while the detection and classification of encrypted
traffic have advanced significantly, it faces formidable challenges that
hinder its progress. This survey paper serves as a foundational resource,
offering a comprehensive overview of the current state and paving the
way for future research that could potentially revolutionize our ability
to analyze and manage encrypted traffic effectively.

This survey has highlighted various critical challenges in encrypted
traffic detection and classification. Addressing these challenges through
innovative research and development is necessary for advancing our
capabilities in managing and safeguarding encrypted communications
in a rapidly digitizing world. The emerging fields of federated learning and explainable artificial intelligence (XAI) offer promising pathways. Federated learning, particularly privacy-preserving approaches
in distributed environments, demonstrates significant potential to enhance encrypted traffic classification without compromising user privacy [166–168]. Furthermore, integrating XAI can improve traffic classification models’ reliability and interpretability, making them more
23

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari
Table 12
List of acronyms/abbreviations used in the paper.

Abbreviations

Full form/Definition

Abbreviations

Full form/Definition

ETC
ML
DL
ETA
CNN
RNN
IE
IEEE
ACM
SSRN
MDPI
TLS
SSL
QUIC
DPI
LSTM
VPN
HTTPS
TOR
HTTP
IP
SSH
PGP
MIME
WPA
SVM
AAE
DSVDD
PNN
DNN
SNN
MLP
SAE
CSCNN
GRU
BFSN
EETC
BERT
GAN
CGAN
SGAN
SDN
BSTFN
USTC
GCN
PEFT
DE-GNN
GNN
TIG
CLE
TFE
MTIG
CIC
ME
STP
SMTP

Encrypted Traffic Classification
Machine Learning
Deep Learning
Encrypted Traffic Analysis
Convolutional Neural Network
Recurrent Neural Network
Information Extractor
Institute of Electrical and Electronics Engineers
Association for Computing Machinery
Social Science Research Network
Multidisciplinary Digital Publishing Institute
Transport Layer Security
Secure Sockets Layer
Quick UDP Internet Connections
Deep Packet Inspection
Long Short-Term Memory
Virtual Private Network
Hypertext Transfer Protocol Secure
The Onion Router
Hypertext Transfer Protocol
Internet Protocol
Secure Shell
Pretty Good Privacy
Multipurpose Internet Mail Extensions
Wi-Fi Protected Access
Support Vector Machine
Adversarial Autoencoder
Deep Support Vector Data Description
Probabilistic Neural Network
Deep Neural Network
Spiking Neural Network
Multilayer Perceptron
Stacked Autoencoder
Cost Sensitive Convolutional Neural Network
Gated Recurrent Unit
Binary Forward Stochastic Neurons
Extended Encrypted Traffic Classification
Bidirectional Encoder Representations from Transformers
Generative Adversarial Network
Conditional GAN
Semi-Supervised GAN
Software-Defined Networking
Bidirectional Stacked Temporal Fusion Networks
University of Science and Technology of China
Graph Convolutional Network
Parameter-Efficient Fine-Tuning
Dynamic Edge Graph Neural Network
Graph Neural Network
Traffic Interaction Graph
Contrastive Learning Enhanced
Temporal Fusion Encoder
Malicious Traffic Interaction Graph
Canadian Institute for Cybersecurity
Machine learning and Evidence verification
Spanning Tree Protocol
Simple Mail Transfer Protocol

ISCX
RADIUS
PCAP
IDS
DDoS
DNS
CMS
SJTU
AN
CSTNET
MIT
TCP
UDP
BCCC
CSV
ANN
RL
BIGAN
RF
ALO
SOM
GMM
HMM
OS
MCFP
KNN
DT
LR
GBDT
XGB
GBM
NAS
MAUC
LAN
IOS
SOFTMAX
AUC
RC
FAR
FPR
CLETFE
ACGAN
MAML
FIN
RST
ALF
ICMP
VRRP
ARP
CDP
LLDP
MQTT
NTP
CTU
FTP

Information Security Center of Excellence
Remote Authentication Dial-In User Service
Packet Capture
Intrusion Detection System
Distributed Denial of Service
Domain Name System
Content Management System
Shanghai Jiao Tong University
Autonomous Networks
China Science and Technology Network
Massachusetts Institute of Technology
Transmission Control Protocol
User Datagram Protocol
Behaviour-Centric Cybersecurity Center
Comma-Separated Values
Artificial Neural Network
Reinforcement Learning
Bidirectional Generative Adversarial Network
Random Forest
Ant Lion Optimizer
Self-Organizing Maps
Gaussian Mixture Model
Hidden Markov Model
Operating System
Multi-Class Flow Prediction
K-Nearest Neighbors
Decision Tree
Logistic Regression
Gradient Boosting Decision Trees
Extreme Gradient Boosting
Gradient Boosting Machine
Neural Architecture Search
Mean Area Under Curve
Local Area Network
Internet Operating System
Softmax Function
Area Under Curve
Recall
False Alarm Rate
False Positive Rate
Cross Layer Encrypted Traffic Feature Extraction
Auxiliary Classifier GAN
Model-Agnostic Meta-Learning
Finish Flag
Reset Flag
Application Layer Filtering
Internet Control Message Protocol
Virtual Router Redundancy Protocol
Address Resolution Protocol
Cisco Discovery Protocol
Link Layer Discovery Protocol
Message Queuing Telemetry Transport
Network Time Protocol
Czech Technical University
File Transfer Protocol

CRediT authorship contribution statement

The authors report financial support was provided by Natural Sciences
and Engineering Research Council of Canada (NSERC).

Adit Sharma: Writing – original draft, Visualization, Methodology,
Formal analysis. Arash Habibi Lashkari: Writing – review & editing,
Supervision, Funding acquisition, Conceptualization.

Acknowledgments
The authors acknowledge the grant from Canada Research Chair Tier II (#CRC-2021-00340) and the Natural Sciences and Engineering
Research Council of Canada — NSERC (#RGPIN-2020-04701) — to
Arash Habibi Lashkari.

Declaration of competing interest
The authors declare the following financial interests/personal relationships which may be considered as potential competing interests:
24

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari

Appendix

[23] T. Auld, A.W. Moore, S.F. Gull, Bayesian neural networks for internet traffic
classification, IEEE Trans. Neural Netw. 18 (1) (2007) 223–239.
[24] R.K. Knake, Untangling attribution: Moving to accountability in cyberspace, in:
Prepared Statement before the Subcommittee on Technology and Innovation,
Committee on Science and Technology, Hearing: Planning for the Future of
Cyber Attack, 2010.
[25] P. Velan, M. Čermák, P. Čeleda, M. Drašar, A survey of methods for encrypted
traffic classification and analysis, Int. J. Netw. Manage. 25 (5) (2015) 355–374.
[26] M.A.I.M. Aminuddin, Z.F. Zaaba, M.K.M. Singh, D.S.M. Singh, A survey on tor
encrypted traffic monitoring, Int. J. Adv. Comput. Sci. Appl. 9 (8) (2018).
[27] S. Rezaei, X. Liu, Deep learning for encrypted traffic classification: An overview,
IEEE Commun. Mag. 57 (5) (2019) 76–81.
[28] A.S. Iliyasu, I. Abba, B.S. Iliyasu, A.S. Muhammad, A review of deep learning
techniques for encrypted traffic classification, Unknown Journal The publication
details need to be filled in as they were not provided, Unknown Year.
[29] Y. Li, H. Guo, J. Hou, Z. Zhang, T. Jiang, Z. Liu, A survey of encrypted malicious traffic detection, in: 2021 International Conference on Communications,
Computing, Cybersecurity, and Informatics, CCCI, IEEE, 2021, pp. 1–7.
[30] E. Papadogiannaki, S. Ioannidis, A survey on encrypted network traffic analysis
applications, techniques, and countermeasures, ACM Comput. Surv. 54 (6)
(2021) 1–35.
[31] M. Shen, K. Ye, X. Liu, L. Zhu, J. Kang, S. Yu, Q. Li, K. Xu, Machine learningpowered encrypted network traffic analysis: a comprehensive survey, IEEE
Commun. Surv. Tutor. (2022).
[32] D. Kahn, The Codebreakers: The Comprehensive History of Secret Communication from Ancient Times to the Internet, Simon and Schuster,
1996.
[33] R.L. Rivest, A. Shamir, L. Adleman, A method for obtaining digital signatures
and public-key cryptosystems, Commun. ACM 21 (2) (1978) 120–126.
[34] W. Diffie, M.E. Hellman, New directions in cryptography, in: Democratizing
Cryptography: The Work of Whitfield Diffie and Martin Hellman, 2022, pp.
365–390.
[35] X. Yi, R. Paulet, E. Bertino, X. Yi, R. Paulet, E. Bertino, Homomorphic
Encryption, Springer, 2014.
[36] T. Lepistö, A. Salomaa, Automata, Languages and Programming: 15th International Colloquium, Tampere, Finland, July 11-15, 1988. Proceedings, vol. 317,
Springer Science & Business Media, 1988.
[37] G. Singh-Pall, Virtual private network, 1996, https://www.microsoft.com,
Developed by Microsoft Corporation.
[38] P. Syverson, M.G. Reed, D. Goldschlag, The onion router, 2002, https://www.
torproject.org, Developed at the U.S. Naval Research Laboratory.
[39] Invisible internet project, 2003, https://geti2p.net, A decentralized anonymizing
network.
[40] T. Kocsis, Zeronet, 2015, https://zeronet.io, Decentralized websites using
Bitcoin cryptography and BitTorrent network.
[41] I. Clarke, Freenet, 2000, https://freenetproject.org, A peer-to-peer platform for
censorship-resistant communication.
[42] Netscape, Hypertext transfer protocol secure, 1995, https://www.netscape.com,
An extension of HTTP for secure communication over a computer network.
[43] Transport layer security, 1999, https://tools.ietf.org/html/rfc5246, Protocol for
secure communications over a computer network.
[44] Netscape, Secure sockets layer, 1995, https://www.netscape.com, Protocol for
establishing encrypted links between networked computers.
[45] Internet protocol security, 1995, https://tools.ietf.org/html/rfc4301, A suite of
protocols for securing Internet Protocol communications.
[46] T. Ylönen, Secure shell, 1995, https://www.ssh.com/ssh/protocol/, Protocol for
secure network services over an unsecured network.
[47] P. Zimmermann, Pretty good privacy, 1991, https://www.pgpi.org, Program
used for encrypting and decrypting data.
[48] Secure/multipurpose internet mail extensions, 1995, https://tools.ietf.org/html/
rfc5751, Standard for public key encryption and signing of MIME data.
[49] OpenPGP, 1997, https://tools.ietf.org/html/rfc4880, An open standard for
encrypting and signing data.
[50] Wi-Fi protected access 2, 2004, https://www.wi-fi.org/discover-wi-fi/security,
A security protocol for Wi-Fi networks.
[51] A.J. Menezes, P.C. Van Oorschot, S.A. Vanstone, Handbook of Applied
Cryptography, CRC Press, 2018.
[52] M. Dworkin, Recommendation for block cipher modes of operation, NIST Spec.
Publ. 800 (2001) 38B.
[53] W. Stallings, Information Privacy Engineering and Privacy by Design: Understanding Privacy Threats, Technology, and Regulations Based on Standards and
Best Practices, Addison-Wesley Professional, 2019.
[54] R. Alshammari, A.N. Zincir-Heywood, Machine learning based encrypted traffic
classification: Identifying ssh and skype, in: 2009 IEEE Symposium on Computational Intelligence for Security and Defense Applications, IEEE, 2009, pp.
1–8.
[55] G. Draper-Gil, A.H. Lashkari, M.S.I. Mamun, A.A. Ghorbani, Characterization
of encrypted and vpn traffic using time-related, in: Proceedings of the 2nd
International Conference on Information Systems Security and Privacy, ICISSP,
2016, pp. 407–414.

See Table 12.

Data availability
No data was used for the research described in the article.

References
[1] A. Dainotti, C. Squarcella, E. Aben, K.C. Claffy, M. Chiesa, M. Russo, A. Pescapé,
Analysis of country-wide internet outages caused by censorship, in: Proceedings
of the 2011 ACM SIGCOMM Conference on Internet Measurement Conference,
2011, pp. 1–18.
[2] Google, Google Transparency Report — transparencyreport.google.com, 2024,
https://transparencyreport.google.com/https/overview?hl=en.
[3] C. Wright, F. Monrose, G.M. Masson, HMM profiles for network traffic classification, in: Proceedings of the 2004 ACM Workshop on Visualization and Data
Mining for Computer Security, 2004, pp. 9–15.
[4] Zscaler, Zscaler ThreatLabz 2023 state of encrypted attacks report — zscaler.com, 2023, https://www.zscaler.com/resources/2023-threatlabz-state-ofencrypted-attacks-report. (Accessed 11 November 2024).
[5] M. Handelman, USenix security ’23 - rosetta: Enabling robust TLS
encrypted traffic classification in diverse network environments with
TCP-aware
traffic
augmentation
—
securityboulevard.com,
2023,
https://securityboulevard.com/2024/01/usenix-security-23-rosetta-enablingrobust-tls-encrypted-traffic-classification-in-diverse-network-environmentswith-tcp-aware-traffic-augmentation/. (Accessed 11 November 2024).
[6] ENISA, Encrypted traffic analysis: Use cases & security challenges
—
enisa.europa.eu,
2020,
https://www.enisa.europa.eu/news/enisanews/encrypted-traffic-analysis-use-cases-security-challenges, (Accessed 11
November 2024).
[7] M. Abbasi, A. Shahraki, A. Taherkordi, Deep learning for network traffic
monitoring and analysis (NTMA): A survey, Comput. Commun. 170 (2021)
19–41.
[8] B. Anderson, S. Paul, D. McGrew, Deciphering malware’s use of TLS (without
decryption), J. Comput. Virol. Hack. Tech. 14 (2018) 195–211.
[9] A. Nadeem, M.Y. Javed, A performance comparison of data encryption algorithms, in: 2005 International Conference on Information and Communication
Technologies, IEEE, 2005, pp. 84–89.
[10] M. Lopez-Martin, B. Carro, A. Sanchez-Esguevillas, J. Lloret, Network traffic
classifier with convolutional and recurrent neural networks for Internet of
Things, IEEE Access 5 (2017) 18042–18050.
[11] J. Lin, Y. Miao, L. Wei, T. Leng, K.-K.R. Choo, Efficient secure inference scheme
in multiparty settings for industrial Internet of Things, IEEE Trans. Ind. Inform.
(2024).
[12] J. Feng, L.T. Yang, B. Ren, D. Zou, M. Dong, S. Zhang, Tensor recurrent neural
network with differential privacy, IEEE Trans. Comput. 73 (3) (2023) 683–693.
[13] P. Zhang, X. Cheng, S. Su, N. Wang, Task allocation under geoindistinguishability via group-based noise addition, IEEE Trans. Big Data 9 (3)
(2022) 860–877.
[14] L. Da Xu, Y. Lu, L. Li, Embedding blockchain technology into IoT for security:
A survey, IEEE Internet Things J. 8 (13) (2021) 10452–10473.
[15] A. Reyna, C. Martín, J. Chen, E. Soler, M. Díaz, On blockchain and its
integration with IoT. Challenges and opportunities, Future Gener. Comput. Syst.
88 (2018) 173–190.
[16] H.-N. Dai, Z. Zheng, Y. Zhang, Blockchain for Internet of Things: A survey,
IEEE Internet Things J. 6 (5) (2019) 8076–8094.
[17] S. Rathore, Y. Pan, J.H. Park, BlockDeepNet: A blockchain-based secure deep
learning for IoT network, Sustainability 11 (14) (2019) 3974.
[18] J. Feng, L.T. Yang, R. Zhang, B.S. Gavuna, Privacy-preserving tucker train
decomposition over blockchain-based encrypted industrial IoT data, IEEE Trans.
Ind. Inform. 17 (7) (2020) 4904–4913.
[19] K. Shahbar, A.N. Zincir-Heywood, Traffic flow analysis of tor pluggable
transports, in: 2015 11th International Conference on Network and Service
Management, CNSM, IEEE, 2015, pp. 178–181.
[20] K. Shahbar, A.N. Zincir-Heywood, Benchmarking two techniques for tor classification: Flow level and circuit level classification, in: 2014 IEEE Symposium
on Computational Intelligence in Cyber Security, CICS, IEEE, 2014, pp. 1–8.
[21] A. Montieri, D. Ciuonzo, G. Aceto, A. Pescape, Anonymity services tor, i2p,
jondonym: classifying in the dark (web), IEEE Trans. Dependable Secure
Comput. 17 (3) (2018) 662–675.
[22] A. Montieri, D. Ciuonzo, G. Bovenzi, V. Persico, A. Pescapé, A dive into the
dark web: Hierarchical traffic classification of anonymity tools, IEEE Trans.
Netw. Sci. Eng. 7 (3) (2019) 1043–1054.
25

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari
[56] F. Zaki, F. Afifi, S. Abd Razak, A. Gani, N.B. Anuar, GRAIN: Granular multi-label
encrypted traffic classification using classifier chain, Comput. Netw. 213 (24)
(2022) 109084.
[57] S. Dong, Multi class SVM algorithm with active learning for network traffic
classification, Expert Syst. Appl. 176 (2021) 114885.
[58] Z. Yao, J. Ge, Y. Wu, X. Lin, R. He, Y. Ma, Encrypted traffic classification based
on Gaussian mixture models and hidden Markov models, J. Netw. Comput.
Appl. 166 (2020) 102711.
[59] P. Choorod, G. Weir, A. Fernando, Classifying tor traffic encrypted payload
using machine learning, IEEE Access (2024).
[60] G. Aceto, D. Ciuonzo, A. Montieri, A. Pescapé, Mobile encrypted traffic
classification using deep learning: Experimental evaluation, lessons learned, and
challenges, IEEE Trans. Netw. Serv. Manage. 16 (2) (2019) 445–458.
[61] W. Wang, M. Zhu, J. Wang, X. Zeng, Z. Yang, End-to-end encrypted traffic
classification with one-dimensional convolution neural networks, in: 2017 IEEE
International Conference on Intelligence and Security Informatics, ISI, IEEE,
2017, pp. 43–48.
[62] M. Lotfollahi, M. Jafari Siavoshani, R. Shirali Hossein Zade, M. Saberian, Deep
packet: A novel approach for encrypted traffic classification using deep learning,
Soft Comput. 24 (3) (2020) 1999–2012.
[63] S. Lv, C. Wang, Z. Wang, S. Wang, B. Wang, Y. Zhang, AAE-DSVDD: A one-class
classification model for VPN traffic identification, Comput. Netw. 236 (2023)
109990.
[64] G. Aceto, D. Ciuonzo, A. Montieri, A. Pescapé, DISTILLER: Encrypted traffic
classification via multimodal multitask deep learning, J. Netw. Comput. Appl.
183 (31) (2021) 102985.
[65] Y. Zeng, H. Gu, W. Wei, Y. Guo, 𝐷𝑒𝑒𝑝 − 𝐹 𝑢𝑙𝑙 − 𝑅𝑎𝑛𝑔 𝑒: a deep learning based
network encrypted traffic classification and intrusion detection framework, IEEE
Access 7 (2019) 45182–45190.
[66] S. Rezaei, X. Liu, How to achieve high classification accuracy with just a few
labels: A semi-supervised approach using sampled packets, 2018, arXiv preprint
arXiv:1812.09761.
[67] S. Jorgensen, J. Holodnak, J. Dempsey, K. de Souza, A. Raghunath, V. Rivet, A.
Wollaber, Extensible machine learning for encrypted network traffic application
labeling via uncertainty quantification, IEEE Trans. Artif. Intell. (2023).
[68] Z. Song, Z. Zhao, F. Zhang, G. Xiong, G. Cheng, X. Zhao, B. Chen, I 2 RNN:
An incremental and interpretable recurrent neural network for encrypted traffic
classification, IEEE Trans. Dependable Secure Comput. (56) (2023).
[69] K. Zhou, W. Wang, C. Wu, T. Hu, Practical evaluation of encrypted traffic
classification based on a combined method of entropy estimation and neural
networks, ETRI J. 42 (3) (2020) 311–323.
[70] M.H. Pathmaperuma, Y. Rahulamathavan, S. Dogan, A.M. Kondoz, Deep learning for encrypted traffic classification and unknown data detection, Sensors 22
(19) (2022) 7643.
[71] A. Rasteh, F. Delpech, C. Aguilar-Melchor, R. Zimmer, S.B. Shouraki, T.
Masquelier, Encrypted internet traffic classification using a supervised spiking
neural network, Neurocomputing 503 (2022) 272–282.
[72] Y. Xu, J. Cao, K. Song, Q. Xiang, G. Cheng, FastTraffic: A lightweight method
for encrypted traffic fast classification, Comput. Netw. 235 (2023) 109965.
[73] T. O’shea, J. Hoydis, An introduction to deep learning for the physical layer,
IEEE Trans. Cogn. Commun. Netw. 3 (4) (2017) 563–575.
[74] Y. He, W. Li, Image-based encrypted traffic classification with convolution
neural networks, in: 2020 IEEE Fifth International Conference on Data Science
in Cyberspace, DSC, (29) IEEE, 2020, pp. 271–278.
[75] R. Moreira, L.F.R. Moreira, F. de Oliveira Silva, An intelligent network monitoring approach for online classification of darknet traffic, Comput. Electr. Eng.
110 (2023) 108852.
[76] J. Cheng, Y. Wu, E. Yuepeng, J. You, T. Li, H. Li, J. Ge, MATEC: A lightweight
neural network for online encrypted traffic classification, Comput. Netw. 199
(20) (2021) 108472.
[77] M. Wang, K. Zheng, D. Luo, Y. Yang, X. Wang, An encrypted traffic classification
framework based on convolutional neural networks and stacked autoencoders,
in: 2020 IEEE 6th International Conference on Computer and Communications,
ICCC, IEEE, 2020, pp. 634–641.
[78] S. Soleymanpour, H. Sadr, M. Nazari Soleimandarabi, CSCNN: cost-sensitive
convolutional neural network for encrypted traffic classification, Neural Process.
Lett. 53 (5) (2021) 3497–3523.
[79] L. Xu, D. Dou, H.J. Chao, ETCNet: encrypted traffic classification using
siamese convolutional networks, in: Proceedings of the Workshop on Network
Application Integration/CoDesign, 2020, pp. 51–53.
[80] C.Y. Lin, B. Chen, W. Lan, An efficient approach for encrypted traffic classification using CNN and bidirectional GRU, in: 2022 2nd International Conference
on Consumer Electronics and Computer Engineering, ICCECE, (43) IEEE, 2022,
pp. 368–373.
[81] S. Izadi, M. Ahmadi, R. Nikbazm, Network traffic classification using convolutional neural network and ant-lion optimization, Comput. Electr. Eng. 101
(2022) 108024.
[82] A. Habibi Lashkari, G. Kaur, A. Rahali, Didarknet: A contemporary approach to
detect and characterize the darknet traffic using deep image learning, in: 2020
the 10th International Conference on Communication and Network Security,
2020, pp. 1–13.

[83] J. Lan, X. Liu, B. Li, Y. Li, T. Geng, DarknetSec: A novel self-attentive deep
learning method for darknet traffic classification and application identification,
Comput. Secur. 116 (2022) 102663.
[84] X. Tong, X. Tan, L. Chen, J. Yang, Q. Zheng, BFSN: a novel method of encrypted
traffic classification based on bidirectional flow sequence network, in: 2020
3rd International Conference on Hot Information-Centric Networking (HotICN),
IEEE, 2020, pp. 160–165.
[85] J. Yang, Y. Guo, AEFETA: Encrypted traffic classification framework based on
self-learning of feature, in: 2021 6th International Conference on Intelligent
Computing and Signal Processing, ICSP, IEEE, 2021, pp. 876–880.
[86] X. Hu, C. Gu, Y. Chen, F. Wei, tCLD-Net: a transfer learning internet encrypted
traffic classification scheme based on convolution neural network and long
short-term memory network, in: 2021 International Conference on Communications, Computing, Cybersecurity, and Informatics, CCCI, IEEE, 2021, pp.
1–5.
[87] F. Meslet-Millet, E. Chaput, S. Mouysset, SPPNet: An approach for real-time
encrypted traffic classification using deep learning, in: 2021 IEEE Global
Communications Conference, GLOBECOM, (44) IEEE, 2021, pp. 1–6.
[88] W. Maonan, Z. Kangfeng, X. Ning, Y. Yanqing, W. Xiujuan, CENTIME: a direct
comprehensive traffic features extraction for encrypted traffic classification,
in: 2021 IEEE 6th International Conference on Computer and Communication
Systems, ICCCS, IEEE, 2021, pp. 490–498.
[89] X. Ma, W. Zhu, J. Wei, Y. Jin, D. Gu, R. Wang, EETC: An extended encrypted
traffic classification algorithm based on variant resnet network, Comput. Secur.
128 (49) (2023) 103175.
[90] X. Hu, C. Gu, Y. Chen, F. Wei, CBD: A deep-learning-based scheme for encrypted
traffic classification with a general pre-training method, Sensors 21 (24) (2021)
8231.
[91] P. Zhu, G. Wang, J. He, Y. Dong, Y. Chang, An encrypted traffic identification
method based on multi-scale feature fusion, Array (2024) 100338.
[92] M. Shen, J. Zhang, L. Zhu, K. Xu, X. Du, Accurate decentralized application
identification via encrypted traffic analysis using graph neural networks, IEEE
Trans. Inf. Forensics Secur. 16 (2021) 2367–2380.
[93] T.-L. Huoh, Y. Luo, P. Li, T. Zhang, Flow-based encrypted network traffic
classification with graph neural networks, IEEE Trans. Netw. Serv. Manag. 20
(2) (2022) 1224–1237.
[94] Z. Diao, G. Xie, X. Wang, R. Ren, X. Meng, G. Zhang, M. Qiao, EC-GCN: A encrypted traffic classification framework based on multi-scale graph convolution
networks, Comput. Netw. 224 (57) (2023) 109614.
[95] Y. Hong, Q. Li, Y. Yang, M. Shen, Graph based encrypted malicious traffic
detection with hybrid analysis of multi-view features, Inform. Sci. (2023)
119229.
[96] L. Wang, X. Ma, N. Li, Q. Lv, Y. Wang, W. Huang, H. Chen, TGPrint: Attack
fingerprint classification on encrypted network traffic based graph convolution
attention networks, Comput. Secur. 135 (2023) 103466.
[97] X. Han, G. Xu, M. Zhang, Z. Yang, Z. Yu, W. Huang, C. Meng, DE-GNN:
Dual embedding with graph neural network for fine-grained encrypted traffic
classification, Comput. Netw. 245 (2024) 110372.
[98] H. Zhang, X. Xiao, L. Yu, Q. Li, Z. Ling, Y. Zhang, One train for two tasks: An
encrypted traffic classification framework using supervised contrastive learning,
2024, arXiv preprint arXiv:2402.07501.
[99] J. Yang, X. Jiang, Y. Lei, W. Liang, Z. Ma, S. Li, MTSecurity: Privacy-preserving
malicious traffic classification using graph neural network and transformer, IEEE
Trans. Netw. Serv. Manag. (2024).
[100] D.A. Hudson, L. Zitnick, Generative adversarial transformers, in: International
Conference on Machine Learning, PMLR, 2021, pp. 4487–4499.
[101] J. Zhai, P. Lin, Y. Cui, L. Xu, M. Liu, GraphCWGAN-GP: A novel data
augmenting approach for imbalanced encrypted traffic classification., CMES
Comput. Model. Eng. Sci. 136 (2) (2023).
[102] Z. Tang, J. Wang, B. Yuan, H. Li, J. Zhang, H. Wang, Markov-GAN: Markov
image enhancement method for malicious encrypted traffic classification, IET
Inf. Secur. 16 (6) (2022) 442–458.
[103] P. Wang, S. Li, F. Ye, Z. Wang, M. Zhang, PacketCGAN: Exploratory study of
class imbalance for encrypted traffic classification using CGAN, in: ICC 20202020 IEEE International Conference on Communications, ICC, IEEE, 2020, pp.
1–7.
[104] Y. Sanjalawe, S. Fraihat, Detection of obfuscated tor traffic based on bidirectional generative adversarial networks and vision transform, Comput. Secur.
135 (2023) 103512.
[105] P. Wang, Z. Wang, F. Ye, X. Chen, Bytesgan: A semi-supervised generative
adversarial network for encrypted traffic classification in SDN edge gateway,
Comput. Netw. 200 (39) (2021) 108535.
[106] R. Zhao, X. Deng, Z. Yan, J. Ma, Z. Xue, Y. Wang, MT-FlowFormer: A semisupervised flow transformer for encrypted traffic classification, in: Proceedings
of the 28th ACM SIGKDD Conference on Knowledge Discovery and Data Mining,
2022, pp. 2576–2584.
[107] X. Lin, G. Xiong, G. Gou, Z. Li, J. Shi, J. Yu, Et-bert: A contextualized datagram
representation with pre-training transformers for encrypted traffic classification,
in: Proceedings of the ACM Web Conference 2022, 2022, pp. 633–642.
26

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari
[108] H. Huang, X. Zhang, Y. Lu, Z. Li, S. Zhou, BSTFNet: An encrypted malicious
traffic classification method integrating global semantic and spatiotemporal
features., Comput. Mater. Contin. 78 (3) (2024).
[109] J.-T. Park, C.-Y. Shin, U.-J. Baek, M.-S. Kim, Fast and accurate multi-task
learning for encrypted network traffic classification, Appl. Sci. 14 (7) (2024)
3073.
[110] X. Yun, Y. Wang, Y. Zhang, C. Zhao, Z. Zhao, Encrypted TLS traffic classification
on cloud platforms, IEEE/ACM Trans. Netw. 31 (1) (2022) 164–177.
[111] S. Disabato, M. Roveri, C. Alippi, Distributed deep convolutional neural
networks for the internet-of-things, IEEE Trans. Comput. 70 (8) (2021)
1239–1252.
[112] M.C. Marim, P.V.B. Ramos, A.B. Vieira, A. Galletta, M. Villari, R.M. de Oliveira,
E.F. Silva, Darknet traffic detection and characterization with models based on
decision trees and neural networks, Intell. Syst. Appl. 18 (2023) 200199.
[113] B. Xu, G. He, H. Zhu, ME-Box: A reliable method to detect malicious encrypted
traffic, J. Inf. Secur. Appl. 59 (2021) 102823.
[114] Y. Hu, F. Zou, L. Li, P. Yi, Traffic classification of user behaviors in tor, i2p,
zeronet, freenet, in: 2020 IEEE 19th International Conference on Trust, Security
and Privacy in Computing and Communications (TrustCom), IEEE, 2020, pp.
418–424.
[115] N. Rust-Nguyen, S. Sharma, M. Stamp, Darknet traffic classification and
adversarial attacks using machine learning, Comput. Secur. 127 (2023) 103098.
[116] N. Malekghaini, E. Akbari, M.A. Salahuddin, N. Limam, R. Boutaba, B. Mathieu,
S. Tuffin, AutoML4ETC: Automated neural architecture search for real-world
encrypted traffic classification, IEEE Trans. Netw. Serv. Manag. (23) (2023).
[117] R.T. Elmaghraby, N.M.A. Aziem, M.A. Sobh, A.M. Bahaa-Eldin, Encrypted
network traffic classification based on machine learning, Ain Shams Eng. J.
15 (2) (2024) 102361.
[118] P. Luo, J. Chu, G. Yang, IP packet-level encrypted traffic classification using
machine learning with a light weight feature engineering method, J. Inf. Secur.
Appl. 75 (2023) 103519.
[119] X. Yan, L. He, Y. Xu, J. Cao, L. Wang, G. Xie, High-speed encrypted traffic
classification by using payload features, Digit. Commun. Netw. (2024).
[120] J. Zhao, Q. Li, Y. Hong, M. Shen, MetaRockETC: Adaptive encrypted traffic
classification in complex network environments via time series analysis and
meta-learning, IEEE Trans. Netw. Serv. Manag. (55) (2024).
[121] X. Li, J. Xie, Q. Song, Y. Sang, Y. Zhang, S. Li, T. Zang, Let model keep evolving:
Incremental learning for encrypted traffic classification, Comput. Secur. 137
(2024) 103624.
[122] R. Wang, Z. Wu, Y. Li, F. Li, S. Tian, J. Liu, Encrypted traffic classification based
on contrastive learning with spatial-temporal feature fusion, in: International
Conference on Computer Application and Information Security (ICCAIS 2023),
Vol. 13090, SPIE, 2024, pp. 531–538.
[123] G. Wang, Y. Gu, Multi-task scenario encrypted traffic classification and
parameter analysis, Sensors 24 (10) (2024) 3078.
[124] R. Xie, Y. Wang, J. Cao, E. Dong, M. Xu, K. Sun, M. Zhang, Rosetta: Enabling
robust tls encrypted traffic classification in diverse network environments with
tcp-aware traffic augmentation, in: Proceedings of the ACM Turing Award
Celebration Conference-China 2023, 2023, pp. 131–132.
[125] K. Lin, X. Xu, H. Gao, TSCRNN: A novel classification scheme of encrypted
traffic based on flow spatiotemporal features for efficient management of IIoT,
Comput. Netw. 190 (41) (2021) 107974.
[126] Z. Chen, G. Cheng, Z. Wei, D. Niu, Classify traffic rather than flow: Versatile
multi-flow encrypted traffic classification with flow clustering, IEEE Trans.
Netw. Serv. Manag. (38) (2023).
[127] M. Seydali, F. Khunjush, B. Akbari, J. Dogani, CBS: A deep learning approach
for encrypted traffic classification with mixed spatio-temporal and statistical
features, IEEE Access (36) (2023).
[128] S. Tian, Y. Gao, G. Yuan, R. Zhang, J. Zhao, S. Zhang, An encrypted traffic
classification method based on contrastive learning, in: Proceedings of the 8th
International Conference on Communication and Information Processing, 2022,
pp. 101–105.
[129] CTU University, CTU-13 dataset, 2011, URL https://www.stratosphereips.org/
datasets-ctu13.
[130] A.W. Moore, D. Zuev, The art of network traffic classification: 10 years after,
ACM SIGCOMM Comput. Commun. Rev. 35 (3) (2005) 133–146, URL https:
//dl.acm.org/doi/10.1145/1070873.1070877.
[131] A. Habibi Lashkari, G. Draper-Gil, M. Mamun, A. Ghorbani, Characterization of
tor traffic using time based features, in: International Conference on Information
Systems Security and Privacy, 2017.
[132] University of Science and Technology of China, USTC-TFC2016, 2016, URL
https://github.com/yungshenglu/USTC-TFC2016/tree/master/Benign.
[133] W. Shbair, BetterNet HTTPS, 2016, URL https://betternet.lhs.loria.fr/datasets/
https/.
[134] K. Shahbar, A.N. Zincir-Heywood, Anon17: Network Traffic Dataset of
Anonymity Services, Tech. Rep, Faculty of Computer Science Dalhousie
University, 2017.
[135] K. Shahbar, A.N. Zincir-Heywood, How far can we push flow analysis to identify
encrypted anonymity network traffic? in: NOMS 2018-2018 IEEE/IFIP Network
Operations and Management Symposium, IEEE, 2018, pp. 1–6.

[136] I. Sharafaldin, A.H. Lashkari, A.A. Ghorbani, et al., Toward generating a
new intrusion detection dataset and intrusion traffic characterization, ICISSp
1 (2018) 108–116.
[137] M. Shafi, A.H. Lashkari, A.H. Roudsari, NLFlowLyzer: Toward generating an
intrusion detection dataset and intruders behavior profiling through network
layer traffic analysis and pattern extraction, Comput. Secur. (2024) 104160.
[138] C. Wang, S. Kennedy, H. Li, K. Hudson, G. Atluri, X. Wei, W. Sun, B. Wang,
Fingerprinting encrypted voice traffic on smart speakers with deep learning, in:
Proceedings of the 13th ACM Conference on Security and Privacy in Wireless
and Mobile Networks, 2020, pp. 254–265.
[139] G. Aceto, D. Ciuonzo, A. Montieri, V. Persico, A. Pescapè, MIRAGE: Mobile-app
traffic capture and ground-truth creation, 2019, http://dx.doi.org/10.21227/
maj9-vh13.
[140] I. Akbari, M.A. Salahuddin, L. Ven, N. Limam, R. Boutaba, B. Mathieu, S.
Moteau, S. Tuffin, A look behind the curtain: traffic classification in an
increasingly encrypted web, in: Proceedings of the ACM on Measurement and
Analysis of Computing Systems, 5, 2021, pp. 1–26.
[141] L. Xu, D. Dou, Oregon & Ohio HTTP2, 2020, URL https://drive.google.com/
drive/folders/1CHKcWotJg_jjE2HH6g-Z1lfr1RBBy0LO.
[142] Y. Hu, F. Zou, L. Li, P. Yi, Traffic classification of user behaviors in Tor,
I2P, ZeroNet, Freenet, in: 2020 IEEE 19th International Conference on Trust,
Security and Privacy in Computing and Communications (TrustCom), 2020, pp.
418–424, http://dx.doi.org/10.1109/TrustCom50675.2020.00064.
[143] University of California, Davis, UCDavis – QUIC, 2020, URL https://www.
kaggle.com/datasets/guillaumefraysse/ucdavisquic.
[144] T. Van Ede, R. Bortolameotti, Browser 2020, 2020, URL https://drive.google.
com/file/d/1wOdrfazbrcMDrL0NfA4GLoWegtPqkPj3/view.
[145] M. MontazeriShatoori, L. Davidson, G. Kaur, A.H. Lashkari, Detection of
doh tunnels using time-series classification of encrypted traffic, in: 2020
IEEE Intl Conf on Dependable, Autonomic and Secure Computing, Intl
Conf on Pervasive Intelligence and Computing, Intl Conf on Cloud and
Big Data Computing, Intl Conf on Cyber Science and Technology Congress
(DASC/PiCom/CBDCom/CyberSciTech), IEEE, 2020, pp. 63–70.
[146] A. Ferriyan, A.H. Thamrin, K. Takeda, J. Murai, Generating network intrusion
detection dataset based on real and encrypted synthetic attack traffic, Appl. Sci.
11 (17) (2021) http://dx.doi.org/10.3390/app11177868, URL https://www.
mdpi.com/2076-3417/11/17/7868.
[147] R. Zhao, Y. Huang, X. Deng, Z. Xue, J. Li, Z. Huang, Y. Wang, Flow transformer:
A novel anonymity network traffic classifier with attention mechanism, in: 17th
International Conference on Mobility, Sensing and Networking, MSN, 2021, pp.
223–230, http://dx.doi.org/10.1109/MSN53354.2021.00045.
[148] R. Zhao, X. Deng, Y. Wang, L. Chen, M. Liu, Z. Xue, Y. Wang, Flow
sequence-based anonymity network traffic identification with residual graph
convolutional networks, in: IEEE/ACM International Symposium on Quality of
Service (IWQoS), 2022, pp. 1–10.
[149] Y. Heng, V. Chandrasekhar, J.G. Andrews, UTMobileNetTraffic2021: A labeled
public network traffic dataset, IEEE Netw. Lett. 3 (3) (2021) 156–160.
[150] J. Luxemburk, K. Hynek, T. Čejka, A. Lukačovič, P. Šiška, CESNET-QUIC22: A
large one-month QUIC network traffic dataset from backbone lines, Data Brief
46 (2023) 108888.
[151] C. Wang, A. Finamore, L. Yang, K. Fauvel, D. Rossi, AppClassNet: A commercialgrade dataset for application identification research, ACM SIGCOMM Comput.
Commun. Rev. 52 (3) (2022) 19–27.
[152] C. Coldwell, D. Conger, E. Goodell, B. Jacobson, B. Petersen, D. Spencer, M.
Anderson, M. Sgambati, Machine learning 5G attack detection in programmable
logic, in: 2022 IEEE Globecom Workshops (GC Wkshps), 2022, pp. 1365–1370,
http://dx.doi.org/10.1109/GCWkshps56602.2022.10008647.
[153] E.C.P. Neto, S. Dadkhah, R. Ferreira, A. Zohourian, R. Lu, A.A. Ghorbani,
CICIoT2023: A real-time dataset and benchmark for large-scale attacks in IoT
environment, Sensors 23 (13) (2023) 5941.
[154] S. Jorgensen, J. Holodnak, J. Dempsey, K. de Souza, A. Raghunath, V.
Rivet, N. DeMoes, A. Alejos, A. Wollaber, Extensible machine learning for
encrypted network traffic application labeling via uncertainty quantification,
IEEE Trans. Artif. Intell. 5 (1) (2024) 420–433, http://dx.doi.org/10.1109/TAI.
2023.3244168.
[155] Z. Diao, G. Xie, X. Wang, R. Ren, X. Meng, G. Zhang, K. Xie, M. Qiao, ECGCN: A encrypted traffic classification framework based on multi-scale graph
convolution networks, Comput. Netw. 224 (2023) 109614.
[156] M. Shafi, A.H. Lashkari, V. Rodriguez, R. Nevo, Toward generating a new cloudbased Distributed Denial of Service (DDoS) dataset and cloud intrusion traffic
characterization, Information 15 (4) (2024) 195.
[157] C.V. Wright, F. Monrose, G.M. Masson, On inferring application protocol
behaviors in encrypted network traffic, J. Mach. Learn. Res. 7 (12) (2006).
[158] C. Bullard, Openargus - Home — openargus.org, 1984, https://openargus.org/.
(Accessed 25 July 2024).
[159] V. Paxton, 1995. https://zeek.org/, (Accessed 25 July 2024).
[160] K. Delgadillo, C.I.P. Marketing, Netflow Services and Applications, Cisco
Whitepaper, 1996.
[161] T. Team, Lightweight flow generator and packet analyzer - Tranalyzer —
tranalyzer.com, 2012, https://tranalyzer.com/about#theanteater. (Accessed 25
July 2024).
27

Computer Networks 257 (2025) 110984

A. Sharma and A.H. Lashkari

Adit Sharma is a Research Assistant at the BehaviourCentric Cybersecurity Center(BCCC)at York University,
where he is currently focused on encrypted traffic detection
and classification under the supervision of Prof. Arash
Habibi Lashkari. As a Graduate Student in Information Technology, Adit is actively engaged in cybersecurity research
while also working as a Teaching Assistant for computer
programming courses. Previously, he worked as a Senior
Research and Analytics Officer at Broadband India Forum
and gained experience as an intern at the European Business
and Technology Centre. Adit graduated with a Bachelor of
Technology in Computer Engineering from Manipal University Jaipur, where he achieved a CGPA of 9.07, and is now
pursuing his Master’s degree at York University.

[162] A.H. Lashkari, G.D. Gil, M.S.I. Mamun, A.A. Ghorbani, Characterization of tor
traffic using time based features, in: International Conference on Information
Systems Security and Privacy, Vol. 2, SciTePress, 2017, pp. 253–262.
[163] Z. Aouini, A. Pekar, NFStream: A flexible network data analysis framework, Comput. Netw. 204 (2022) 108719, http://dx.doi.org/10.1016/j.
comnet.2021.108719, URL https://www.sciencedirect.com/science/article/pii/
S1389128621005739.
[164] M. Shafi, A.H. Lashkari, H. Mohanty, Unveiling malicious DNS behavior
profiling and generating benchmark dataset through application layer traffic
analysis, Comput. Electr. Eng. 118 (2024) 109436.
[165] T.T. Nguyen, G. Armitage, A survey of techniques for internet traffic classification using machine learning, IEEE Commun. Surv. Tutor. 10 (4) (2008)
56–76.
[166] X. Yan, Y. Miao, X. Li, K.-K.R. Choo, X. Meng, R.H. Deng, Privacy-preserving
asynchronous federated learning framework in distributed iot, IEEE Internet
Things J. 10 (15) (2023) 13281–13291.
[167] Y. Lu, X. Huang, Y. Dai, S. Maharjan, Y. Zhang, Blockchain and federated
learning for privacy-preserved data sharing in industrial IoT, IEEE Trans. Ind.
Inform. 16 (6) (2019) 4177–4186.
[168] Z. Jin, K. Duan, C. Chen, M. He, S. Jiang, H. Xue, FedETC: Encrypted traffic
classification based on federated learning, Heliyon 10 (16) (2024).
[169] A. Nascita, A. Montieri, G. Aceto, D. Ciuonzo, V. Persico, A. Pescapé, XAI
meets mobile traffic classification: Understanding and improving multimodal
deep learning architectures, IEEE Trans. Netw. Serv. Manag. 18 (4) (2021)
4225–4246.
[170] A. Nascita, A. Montieri, G. Aceto, D. Ciuonzo, V. Persico, A. Pescapé,
Improving performance, reliability, and feasibility in multimodal multitask
traffic classification with XAI, IEEE Trans. Netw. Serv. Manag. 20 (2) (2023)
1267–1289.

Dr. Arash Habibi Lashkari, a Canada Research Chair
(CRC) in Cybersecurity, holds a prominent position as an
Associate Professor at the School of Information Technology
at York University. As the founder and director of the
Behaviour-Centric Cybersecurity Center (BCCC), with an extensive background spanning over 26 years in industry and
academia, he has taught and conducted research & development at various international universities and organizations,
contributing significantly to the field. Dr. Lashkari’s expertise has earned him numerous accolades, including 15
international cybersecurity competition awards and three
gold awards. He was also recognized among Canada’s Top
150 Researchers in 2017. With a remarkable publication
record, including 11 books and over 120 academic articles,
his work covers diverse cybersecurity topics. He focuses on
developing vulnerability detection technology to safeguard
network systems against cyberattacks. He also has extensive
industrial and development experience in network, software,
information, and computer security.

28
PAPER_TEXT
