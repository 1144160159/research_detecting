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
# [536] Securing Intelligent Transportation Systems: A Dual-Framework Approach for Privacy Protection and Cybersecurity Using Generative AI
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
编号：536
题名：Securing Intelligent Transportation Systems: A Dual-Framework Approach for Privacy Protection and Cybersecurity Using Generative AI
年份：2025
DOI：10.1109/tits.2025.3591007
来源：IEEE Transactions on Intelligent Transportation Systems
PDF：paper/10.1109_TITS.2025.3591007.pdf
已有粗分类：基础理论、密码协议与安全机制
二级关联：无
相关性：弱相关，分数 
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\536.txt
- 原始字符数：56485
- 本次发送字符数：56485
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

1

Securing Intelligent Transportation Systems: A
Dual-Framework Approach for Privacy Protection
and Cybersecurity Using Generative AI
Muhammad Attique Khan , Member, IEEE, Areej Alasiry , Mehrez Marzougui , Isa Bayhan ,
Siva Sarana Kuna, G. Siva Nageswara Rao, Shabbab Ali Algamdi , and Haya Aldossary , Member, IEEE

Abstract— Integrating Generative AI (GenAI) into Intelligent
Transportation Systems (ITS) raises both enormous opportunities
and major worries, especially in the areas of privacy and
cybersecurity, which are already at the forefront of these developments. Developing and implementing robust security measures
to secure sensitive data and address new cyber threats is of
utmost importance, especially with the growing dependence on
AI technology in transportation networks. This article looks at
GenAI and how it may improve ITS intelligence and efficiency
while addressing the risks of using it a lot. It delves into the
difficulties of protecting AI-driven systems against hostile assaults
(AI-MA), particularly emphasizing transportation infrastructure
security, intrusion detection, and data privacy. The research
stresses the significance of modern encryption methods, realtime monitoring threats, and adaptive security frameworks to
ensure ITS are secure and resilient. In addition, it delves into
how transportation systems are affected by ever-changing cyber
threats, offering proactive security solutions to combat these
dangers and strengthen ITS. This paper’s overarching goal is
to lay out a course of action for integrating GenAI into ITS in
a way that strikes a good balance between fostering innovation
and ensuring privacy and security via thorough analysis. The
proposed AI-MA model achieves a high threat detection accuracy
of 96.2%, a privacy protection score of 91.8%, a computational efficiency of 92.9%, a resilience score of 97.8%, and a
network reliability ratio of 92.6% compared to other existing
models.
Received 22 March 2025; revised 1 May 2025 and 2 June 2025;
accepted 16 July 2025. This work was supported by the Deanship of Research
and Graduate Studies at King Khalid University through Large Research
Project under Grant RGP2/471/46. The Associate Editor for this article was
S. Rani. (Corresponding author: Muhammad Attique Khan.)
Muhammad Attique Khan is with the Department of Artificial Intelligence,
Prince Mohammad Bin Fahd University, Dhahran 34754, Saudi Arabia
(e-mail: mkhan3@pmu.edu.sa).
Areej Alasiry and Mehrez Marzougui are with the College of Computer Science, King Khalid University, Abha 61413, Saudi Arabia (e-mail:
areej.alasiry@kku.edu.sa; mhrez@kku.edu.sa).
Isa Bayhan is with the Tourist Guiding Department, Bolu Abant Izzet Baysal
University at Golkoy, 14030 Bolu, Türkiye (e-mail: isa.bayhan@gmail.com).
Siva Sarana Kuna resides in Holly Springs, NC 27540 USA (e-mail:
ssk0315515865@gmail.com).
G. Siva Nageswara Rao is with the Department of Computer Science
and Engineering, Koneru Lakshmaiah Education Foundation, Vaddeswaram,
Andhra Pradesh 522302, India (e-mail: sivanags@kluniversity.in).
Shabbab Ali Algamdi is with the Department of Software Engineering,
College of Computer Science and Engineering, Prince Sattam Bin Abdulaziz
University, Al-Kharj 16278, Saudi Arabia (e-mail: s.algamdi@psau.edu.sa).
Haya Aldossary is with the Department of Computer Science, College of
Science and Humanities, Imam Abdulrahman Bin Faisal University, Jubail
31961, Saudi Arabia (e-mail: Healdossary@iau.edu.sa).
Digital Object Identifier 10.1109/TITS.2025.3591007

Index Terms— GenAI, privacy protection, security protocols,
cyber threats, intelligent transportation system.

I. I NTRODUCTION

S

EVERAL advantages and disadvantages, especially concerning privacy and cybersecurity, come with the growing
use of GenAI in ITS [1]. The security risks posed by
GenAI are substantial, including data breaches, adversarial
assaults, and unlawful system manipulation [2], even though
it offers several advantages, such as better traffic optimization,
predictive analytics, and timely decision-making. Cyberattacks such as deepfake attacks on traffic monitoring, illegal
data access, and AI-driven malware are a major concern
for AI-driven ITS [3]. Intelligent and adaptive cybersecurity
solutions are necessary because traditional security solutions
cannot handle these new threats [4]. Strong encryption and
privacy-preserving methods are top priorities since ITS is
based on vast quantities of sensitive data, such as data passed
between vehicles and everything else, users’ locations, and
automatic decision-making output [5]. Real-time detection
of cyber-attacks is another challenge, with current solutions
unable to differentiate between usual system behavior and
advanced attacks with artificial intelligence (AI) [6]. The
non-traditional and decentralized security mechanisms result
from the decentralized environment of modern transport systems [7]. The development of GenAI in ITS without a robust
cybersecurity system poses the threat of catastrophic failures,
undermined user protection, and deep-rooted system disruptions [4]. To alleviate these issues, this study conceptualizes a
two-framework framework for protecting privacy and systems
within ITS environments against evolving cyber threats [5].
The solution includes adaptive security mechanisms, timebased threat monitoring, and advanced encryption techniques.
Various techniques have been employed to enhance privacy
and cybersecurity in ITS; however, these techniques are not
sufficient to handle emerging threats fueled by AI [6]. Security
of data transmission within ITS is based on conventional
encryption techniques such as Public Key Infrastructure (PKI)
and Advanced Encryption Standard (AES) [8]. Real-time
processing and quantum computing threats are needed more
than they can manage [9]. Most organizations install intrusion
detection systems (IDS) to track suspicious network traffic,

1558-0016 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
2

and they can employ either a signature-based or anomalybased method [10]. However, these systems are not always
effective in detecting malicious AI-driven software; thus,
reactions are slow [5]. Research on blockchain technology
has been aimed at improving the security of vehicle-toeverything (V2X) communications through more secure data
transmission [6]. While blockchain enhances transparency
and trust, it suffers from scalability issues and high computational overhead and is not appropriate for application
in ITS systems based on real-time data [11]. Decentralized
AI-based security protocols are now achievable with the advent
of federated learning, reducing the centralized data storage
requirement [10]. However, its effectiveness is hampered by
challenges such as model poisoning attacks and resource
constraints in edge devices [12].
In addition, privacy-preserving techniques try to protect
user data, e.g., homomorphic encryption and differential
privacy. Still, these techniques often introduce trade-offs
between computation efficiency and security. A problem
with such approaches is that they cannot switch to address
the continuously evolving cyber threats impacting ITS. For
resilience, this paper presents a responsive, dual-architecture
solution with better encryption, real-time threat monitoring, and self-adjusting cybersecurity protocols. This method
attempts to solve this study’s drawbacks.
A. Motivation
The proliferation of ITS has transformed modern-day
mobility. ITS allows autonomous decision-making, real-time
traffic management, and forecasting analytics. Improved ITS
performance and capability are potential gains in applying
Generative AI (GenAI). However, a serious security and
privacy risk lies with this advance. ITS reliability and security
are heavily under threat by cyber threats such as AI-based
malware, deepfake assaults against monitoring infrastructure,
and data leakages by unauthorized access. Centralized security architectures, signature-based intrusion detection, and
conventional encryption cannot keep up with the speed of
these sophisticated assaults. Consequently, an advanced and
adaptable cybersecurity infrastructure capable of detecting and
countering attacks driven by artificial intelligence is necessary
for ITS privacy protection. An important risk for AI-driven
ITS is cyberattacks including malware, illicit data access, and
deepfake attacks on traffic monitoring. Because traditional
cybersecurity solutions are unable to manage these emerging
threats, intelligent and adaptive cybersecurity solutions are
required. The approach employs AI-driven intrusion detection
systems (IDS) to monitor unusual or malicious behavior and
self-adjust security protocols to change encryption and firewall
settings in reaction to real-time threats. Improve the resilience
of ITS against cyber threats with real-time threat monitoring
and fast incident response capabilities. These features help
identify assaults early, isolate affected systems, and reduce
their effects.
B. Problem Statement
ITS ’ current security systems have limitations despite AI
and cyber security advancements. Despite their effectiveness,

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

encryption mechanisms like AES and PKI are computationally
intensive and non-real-time flexible. False alarms and deteriorated responses are caused by intrusion detection systems not
being able to distinguish between malicious and benign AIgenerated abnormalities. Blockchain-based security systems
guarantee data integrity but are expensive to process and have
poor scalability. Provide system reliability, privacy protection,
and data integrity to improve the framework. This strategy
provides a great way to foster overall transportation security
by fusing necessary protection with innovation. Organizations
can improve their security posture, manage and lower cybersecurity risks, and stay in compliance with applicable legislation
by using security frameworks, which are defined rules and
best practices. The decentralized and dynamic nature of ITS
is a threat to the ever-evolving cyber world. Public trust
is lost, users are compromised, and transportation systems
are impaired by cyberattacks when it has no dynamic and
intelligent security system.
C. Contribution
To solve the privacy and cybersecurity challenges of ITS,
this research proposes a double-framework approach that
utilizes Generative AI. Some of the proposed frameworks
include:
• Generative AI is utilized to identify anomalies and
counter adversarial attacks on ITS networks in real-time.
• Advanced encryption techniques are applied to ensure
data integrity while allowing computing efficiency.
• A security model based on AI-MA should be created to
learn how to counter new threats as they emerge.
• Secure data sharing with minimal risk of exposure
through federated learning and differentiated privacy.
The research paper’s structure is laid out in this section,
including the following: Section II focuses on integrating
security measures into ITS. The Section III of this dissertation
delves into the topic of AI-driven systems and how they protect
against malicious attacks (AI-MA). Section IV provides an
in-depth examination, a review of related approaches, and an
interpretation of the results and their significance. This study’s
findings are discussed in detail in Section V.
II. L ITERATURE S URVEY
The quick advances in ITS have raised critical cybersecurity
issues, and powerful defense systems are needed to cope with
emerging threats. Various cybersecurity approaches have been
developed to enhance ITS security, each with advantages and
limitations.
A. Cybersecurity Measures in ITS: Strengths and Limitations
of Existing Approaches
The suggested Multicriteria Decision-Making (MCDM)Based Cybersecurity Metrics Evaluation approach by
Bhol et al. [13] employs five critical metrics to quantify
cybersecurity strength. Permits the methodical evaluation of
security efficacy—Trickiness in determining the best weights
for criteria. Improving decision-making using MCDM
necessitates careful metric selection for reliable cybersecurity
evaluation.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
KHAN et al.: SECURING INTELLIGENT TRANSPORTATION SYSTEMS: A DUAL-FRAMEWORK APPROACH

The Cybersecurity-Integrated Machine Learning (CIML)
Framework, developed by Wazid et al. [14], improves security and can identify zero-day attacks. its benefits lower
the need for human involvement. Negative aspects adversely
affected by hostile assaults. Inference Strong protections
against ever-changing threats are necessary for CIML to boost
cybersecurity efficiency.

3

TABLE I
C OMPARISON OF C YBERSECURITY M EASURES

B. AI-Driven Threats in ITS: Challenges in Securing
Intelligent Systems
Chaudhary suggested Cybersecurity Awareness Evaluation
Metrics (CSA-EM) [1] to assess cybersecurity awareness
programs fully. Ensures complete, reproducible measurement.
No standards for measurement exist. While CSA-EM enhances
program performance, it must be developed further before it
can be applied more extensively.
Machine learning-based cybersecurity risk detection (MLCRD) is a method that analyzes cyber threats, as suggested by
Shaukat et al. [2]. ML-CRD improves cybersecurity, though it
requires optimization to function optimally.
C. Advancing ITS Security: The Role of Generative AI in
Privacy Protection and Cybersecurity
Pollini proposed a Human Factors-Based Cybersecurity
Framework (HF-CF) [3], incorporating user behavior into CIS.
HF-CF enhances cybersecurity by finding a middle ground
between technological and people-focused strategies.
Cyber hazards can be measured using the DecisionAnalysis-Based Cybersecurity Framework (DAB-CF) proposed by Ganin et al. [4]. Decisions are made subjectively.
DAB-CF improves the management of cybersecurity risks in
an organized and transparent manner.
A comparison of cybersecurity measures with existing studies is made in Table I.
Although existing methodologies adequately illuminate the
means of protecting ITS, they possess limitations such as
high computational intensity, conflicts in compliance, and
dependence on personal judgment. The AI-driven systems
Against Malicious Attacks (AI-MA) approach outshines other
approaches using advanced generative AI technologies for
adaptive threat recognition and reaction. AI-MA enhances
cybersecurity effectiveness by stopping threats in real-time
with reduced human intervention. In addition, it enables
methods that protect privacy, such as synthetic data production, which lessens the need for raw personal data. Negative
aspects include, but are not limited to, the following: increased
complexity of systems, which increases the attack surface;
the possibility of adversarial attacks generated by GenAI that
could fool perception and decision-making systems; and an
amplified risk to privacy if synthetic outputs unintentionally
reconstruct sensitive information. Using GenAI, bad actors can
create believable phishing, spoofing, or data poisoning attacks
against ITS systems.
III. P ROPOSED M ETHOD
Though Generative AI (GenAI) in ITS has advantages, data
privacy and cybersecurity are at risk. Transportation systems

depend on AI-based solutions to control growing cyber risks,
and it is crucial to apply thorough security policies. Generative
AI (GenAI) can potentially improve traffic estimates on both
large and small scales via its capacity to analyze and forecast
massive volumes of real-time data. To improve dynamic traffic
management and eliminate bottlenecks, GenAI can examine
citywide traffic patterns, weather, and events on a macro scale,
allowing it to forecast congestion and optimize traffic flow over
vast regions.
Fig. 1 shows the dual framework security concept to
enhance protection against ITS cyberattacks. Privacy protection and cybersecurity are the two main components of the
framework, which rests under one security layer. Privacy is
protected through federated learning, encryption, and data
anonymization. These three methods protect sensitive transportation information from being released to the public [16].
An approach ensures that GenAI, which is utilized in ITS,
eliminates information abuse while keeping data privacy and
cybersecurity integrity in transportation systems [17].
h
i
h
i


′′
′′
∂ p f = C x a + nr ∗ V x a − m j + yr s − ki ′
(1)
Including adaptive security
parameters
including real-time
h
i
′′
threat mitigation (V x a − m j ), safeguarding measures
h
i
′′
(∂ p f ), and detection of intrusion signals (C x a + nr ),
Equation (1) illustrates the dynamic interaction between

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
4

Fig. 1.

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

Dual framework security model for ITS.

Fig. 2 illustrates how GenAI can assist in estimating traffic
with macro and micro-scale studies. Macroscale forecasting highlights region road segment-oriented traffic conditions
favoring prominent transportation planning and congestion
alleviation. GenAI offers detailed micro-scale analysis concerning human- and vehicle-oriented behavior. Vehicle-related
prediction enhances traffic flow management and road safety
by analyzing vehicle trajectory and accident risk. Human
forecasting is the backbone of pedestrian safety and adaptive traffic management and emphasizes individual mobility
and behavior patterns. By employing actual-time, fact-based
insights based on aggregating these predictive factors, the
method proposed improves ITS [18]. It diminishes traffic
congestion and enhances overall transportation efficiency by
enabling proactive decision-making. A comprehensive framework for maximizing urban mobility and safeguarding ITS
against emerging threats is offered by macro and micro-scale
traffic forecasting. The demands of the populace must be met
by a comprehensive mobility plan that prioritizes public and
non-motorized transportation above private automobiles as a
means of successfully combining land use and transportation
planning.
h
i
h
i


′′
′′
τ f t = Ev a + mk ∗ cs a + kd + y e − wq ′
(4)
h
i
′′
Incorporating safeguarding validation (Ev a + mk ), cyber

security
power
(y e − wq ′ ), and flexible threat mitigation
h
i
′′
(cs a + kd ) Equation (4) establishes the security factor of

Fig. 2.

Generative AI-Based Traffic Prediction Model.



confidentiality (yr ) and security issues ( s − ki ′ ) in ITS.
h
i




′′
R f g = tr a + nr + ew q + mz ′ ∗ v a − hr ′
(2)
Equation (2) describes the resilience measure (R f g) of ITS to
assess system
by combining real-time threat recogh robustness
i


′′
nition (tr a + nr ), data encryption weight (v a − hr ′ ),


and adaptive protection response (ew q + mz ′ ).
h
i
h
i


′′
′′
∂a r = b f r + xk − V a − m ju ∗ h e − tu ′
(3)
h
i
′′
By balancing threat effect (b f r + xk ), privacy-preserving
h
i
′′
data encryption (V a − m ju ), and changing safety


responses (h e − tu ′ ), Equation (3) describes the adaptive
risk component (∂a r ) in ITS. The ITS coordinator of communication flows is the nerve center that controls the flow of
information between cars and traffic control systems, allowing
for a precise and rapid reaction to any dangers that can be
recognized. Vehicle and roadside sensors instantly notify a
centralized traffic management system of any danger, such as
an accident or blockage.

confidence (τ f t) in ITS. This suggested a dual-framework
strategy by measuring the contribution to improving real-time
threat mitigating and secure communications.
h
i
h
i


′′
′′
τ p x = C x a + nr ∗ ew a + br + t r − bw ′
(5)
Integrating safeguarding
weight
(τ p x), network assessh
i
′′
ment of risk (C x a + nr ), and threat impact mitigating
h
i
′′
(ew a + br ), Equation (5) reflects the privacy endurance


factor (t r − bw′ ) in ITS. This quantifies how generative AI
improves data privacy while mitigating real-time cyber risks.
h
i
h
i


′′
′′
τa qm = vx a + slo ∗ vd s + ny + cx s − ui ′
(6)
Integrating the loads of system
optimization
(τa qm), vulh
i
′′
nerability identification (vx a + slo ), and illegal access
h
i
′′
countermeasures (vd s + ny ), Equation (6) describes the


adaptive privacy factor (cx s − ui ′ ) in ITS. The Equation
provides dynamic threat response and system resilience, guaranteeing safety and confidentiality protection in ITS. ITS has
integrated cutting-edge technology to improve transportation
safety, efficiency, and sustainability, and their broad adoption
has transformed contemporary transportation. ITS optimizes
traffic flow, reduces congestion, and minimizes delays by
using real-time data collected from sensors, cameras, and GPS
systems to manage dynamic traffic. There has been a marked
improvement in traffic safety thanks to adaptive traffic signal
systems that react in real-time to traffic circumstances.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
KHAN et al.: SECURING INTELLIGENT TRANSPORTATION SYSTEMS: A DUAL-FRAMEWORK APPROACH

5

Algorithm 1 AI-Powered Intrusion Detection System
(AI-IDS) for ITS
def ai_intrusion_detection(anomaly_score, threshold):
if anomaly_score > threshold:
print(“ALERT: Potential intrusion detected! Initiating
countermeasures. . . ”)
block_suspicious_ip()
alert_security_team()
else:
print(“System secure. No intrusion detected.”)
def block_suspicious_ip():
print(“Blocking the suspicious IP address. . . ”)
def alert_security_team():
print(“Notifying security team for further investigation. . . ”)
anomaly_score = 0.85
threshold = 0.75
ai_intrusion_detection(anomaly_score, threshold)

This Algorithm 1 monitors network traffic using an
AI-derived anomaly score. If the score exceeds a set threshold,
it triggers alerts, blocks suspicious IP addresses, and notifies
the security team. Otherwise, it indicates a secure system. This
proactive approach effectively enhances real-time threat detection and rapid response in intelligent transportation networks.
By lowering system availability, tampering with traffic control
algorithms, and exposing crucial infrastructure to manipulation
or disruption, evolving cyber threats like APTs, coordinated
botnet attacks, data spoofing, and AI-generated adversarial
examples directly affect the reliability and security of transportation networks. System performance metrics, encrypted
communication logs, and intrusion attempts are used to evaluate the efficacy of security. GenAI for threat detection, privacy
protection, and resilience assessment is trained and validated
using this dataset. Real-time traffic data, cyber threat logs, and
ITS anomaly detection records are all included in the analytical
dataset. The ever-changing nature of these dangers makes it
more likely that linked ITS components fail one after the
other, damages trust models, and makes sensor data less reliable. These measures include using blockchain-based identity
management for decentralized authentication, monitoring distributed edge nodes without centralized vulnerabilities through
federated learning models for real-time anomaly detection,
applying moving target defense (MTD) techniques to randomize system configurations and limit attack surface exposure
continuously, and enforcing dynamic encryption key rotation
synchronized with network state changes to minimize the
window of exploitation.
Fig. 3 identifies the safety issues created by GenAI entering
ITS and the recommended actions to mitigate these risks [19].
GenAI is primarily accountable for traffic forecasting and
autonomous vehicle driving, with increased efficiency and
decision-making. Proactive decision-making is made possible,
which reduces traffic congestion and improves overall transportation efficiency. Traffic forecasting at both the macro and
micro scales offer a comprehensive framework for maximizing
urban mobility and safeguarding ITS against emerging threats.
Its usage does have its downfalls, as autonomous vehicle
systems and predictive models can be leveraged in adversarial
attacks under the control of AI. These attacks can compromise

Fig. 3.

Security challenges and solutions in GenAI-Driven ITS.

the reliability of ITS using traffic management methods,
illegal control, or data leakage. By utilizing advanced security
protocols employed by the system, such hazards are minimized
through strong encryption techniques, machine learning-based
anomaly detection, and real-time attack detection [20].
h
i
h
i


′′
′′
τv x = kt d + nx − j a − xk ′ ∗ vx a + sp
(7)
Incorporating the network of things
threat

 detection (τv x)
policy on security enforcement ( j a − xk ′ ), and the method
h
i
′′
protection measures (kt d + nx ), Equation (7) establishes
h
i
′′
the vulnerability mitigating factor (vx a + sp ) in ITS.
This suggested dual-framework strategy as it quantifies how
generative AI helps to lower data privacy violations.
h
i
h
i
′′
′′
′′
∂v s = vx a + sx ∗ r e w + n ji + vd
(8)
h
i
′′
Equation (8) integrates system resilience (vx a + sx ),
′′

instantaneous data
h encryption
i (vd ), along with vulnerability
′′
assessment (r e w + n ji ), thereby modeling the security
versatility factor (∂v s) in ITS. This is consistent with the
suggested dual-framework strategy: generative AI improves
adaptive security mechanisms to fight developing cyber
threats.
h
i
h
i


′′
′′
∀z q = tr k − s j y + r e w + naw ∗ n o − p ′
(9)
Equation (9) integrates
h
ithreat reduction (∀z q), immediate
′′
encryption (tr k − s j y ), and network anomaly identifih
i
′′
cation (r e w + naw ), thereby representing the universal


security positive reinforcement take n o − p ′ ) in ITS.
This suggested dual-framework approach by generative AI
improves proactive security systems to reduce cyber threats
and defend privacy.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
6

Fig. 4.

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

Cooperative Collision Avoidance in ITS.

Fig. 4 shows a cooperative collision avoidance strategy to improve traffic safety with ITS technologies. The
approach combines economy, management, technology, and
constituents, making it possible to make real-time decisions
with minimal mistakes [21]. Using ITS technologies, an avoidance strategy can increase traffic safety. The strategy integrates
constituents, technology, management, and economy to enable
real-time decision-making with few errors. To detect and
reduce potential problems, the coordinated strategy makes use
of data from several sources. Sensors and the required degree
of communication are provided by infrastructure components.
However, the optimal and efficient management of computational and network resources assures perfect data processing.
Data processing perfection is ensured by the effective and
efficient use of network and computational resources. The
communication flow coordinator makes it possible for cars
and traffic control systems to react precisely to hazards that
are identified. Furthermore, raising awareness means alerting
autonomous cars to potential dangers and obstructions on the
road. In addition, increasing awareness indicates notifying
self-driving vehicles of possible risks and road obstacles. The
combined use of GenAI and cooperative collision avoidance
systems creates powerful and safe ITS that reduces road accidents and enhances transportation efficiency through predictive
analytics and adaptive response technologies.
h
i
h
i


′′
′′
∂l cx = a + jv ∗ yt s + nmk + r s − az ′
(10)
By
h including
i adaptive threat response (∂l cx), system
h resilience
i
′′
′′
( a + jv ), and anomaly mitigating (yt s + nmk ),
Equation

(10) describes the latent cyber-risk factor
(r s − az ′ ) in ITS. This generative AI improves
cybersecurity protections while preserving privacy protection.
h
i
h
i
′′
′′
′′
nz! = F nS + σ ϵ − πβ τ σ + yr w ∗ µϑc
(11)
Incorporating method
sensitivity
(nz!), security data
h
i
′′
encryption (F nS + σ ϵ ), and response to threats
h
i
′′
(πβ τ σ + yr w ), Equation (11) predicts the advanced
′′

cybersecurity risk factor (µϑc ). Integrating these factors

Fig. 5. Block diagram secure communication in intelligent transportation
systems.

helps the Equation enable a proactive, powered by AI security
policy to guarantee robust data protection.
h
i
h
i


′′
′′
τl c = tr s + nc ∗ x z a + br + r e s − ja ′
(12)
Integrating
fragility
h
i risk mitigation (τ
h l c), ′′system
i
′′
(tr s + nc ), and encryption (x z a + br ), Equation (12)


establishes the cyber endurance factor (r e s − ja ′ ) in ITS.
This is consistent with the suggested dual-framework strategy:
AI preserves privacy while enhancing security mechanisms
against new risks.
Fig. 5 focuses on protecting ITS, thus filling gaps in the
communication networks. Cyberattacks that include spoofing,
eavesdropping, jamming, compromising Vehicle-to- Vehicle
(V2V), Vehicle-to-Infrastructure (V2I), Vehicle-to- Pedestrian
(V2P), and Vehicle-to- Network (V2N). The figure illustrates
probable attack sites, such as a spoofer altering V2V communication, an eavesdropper assembling V2I information, and
a jammer disrupting railway signals [22]. A scalable security
architecture and robust encryption ensure secure data transport
and defense against new threats. To increase our systems’
resistance to attacks, we use AI-based anomaly detection and
secure authentication methods. These security methods provide data integrity, privacy protection, and system reliability
in GenAI-based ITS, strengthening the architecture.
Secure authentication techniques and AI-based anomaly
detection are employed to boost the robustness of our systems to attacks [23]. In GenAI-based ITS, these security
techniques deliver data integrity, privacy safeguarding, and
system dependability, thus enhancing the framework. Such
an approach offers an excellent way of combining required
security with creativity to promote overall transport security.
h
i
h
i
′′
′′
′′
τ µx a = jr vπ + ba − σ ϑ ′ εγ + baw + π σ τ (13)

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
KHAN et al.: SECURING INTELLIGENT TRANSPORTATION SYSTEMS: A DUAL-FRAMEWORK APPROACH

Algorithm 2 Secure AI-Driven Communication in ITS

7

TABLE II

def secure_data_transmission(is_encrypted, sender_verified):
if is_encrypted:
if sender_verified:
print(“Data transmission secure. Proceeding with
communication.”)
else:
print(“WARNING:
Unverified
sender!
Blocking
communication.”)
block_unverified_sender()
else:
print(“ERROR: Data not encrypted! Enforcing encryption
protocols. . . ”)
enforce_encryption()
def block_unverified_sender():
print(“Blocking data packets from unverified sender. . . ”)
def enforce_encryption():
print(“Applying end-to
-end encryption to secure transmission. . . ”)
is_encrypted = True
sender_verified = False
secure_data_transmission(is_encrypted, sender_verified)

h
i
′′
integrating real-time threat identification (σ ϑ ′ εγ + baw ),
h
i
′′
system encryption ( jr vπ + ba ), and adaptive risk mitigation (τ µx a), Equation (13) describes the advanced protection
′′
adaptability take (πσ τ ) in ITS. This is consistent with
the suggested dual-framework strategy as it underlines how
generative AI improves confidentiality adaptive actions.
h
i
h
i
′′
′′
′′
∀c q = tr ∂ + baw ∗ tr θ δ + bnr + µρ
(14)
h
i
′′
By combining dynamic threat identification (tr θ δ + bnr ),
h
i
′′
adaptive risk management (tr ∂ + baw ), and anomaly
detection (∀c q), Equation (14) describes the whole security
′′
factor (µρ ) in ITS. This suggested a dual-framework strategy
by measuring how generative AI improves ITS proactive
protection systems monitoring.
h
i
h
i
′′
′′
′′
Rz x = kp ℵs + yr ∗ C a − nr + δγ t ∗ vx ′′
(15)
Integrating the
of threats (Rz x), system
safeh identification
i
h
i
′′
′′
guarding (kp ℵs + yr ), and risk-mitigating (C a − nr ),
′′

Equation (15) describes the security endurance factor (δγ t ∗
vx ′′ ) in ITS. The Equation provides adaptive defenses,
strengthening AI-driven transit systems’ cybersecurity and
resilience [24].
Algorithm 2 secures AI-driven communication in ITS by
verifying encryption and sender authenticity. This function
verifies the sender’s identity and determines if the data
is encrypted. To safeguard AI-driven ITS, this article suggests a security architecture that includes adaptive security
mechanisms, better encryption, and real-time threat monitoring [25]. By utilizing the system’s sophisticated security
procedures, such risks are reduced by real-time attack detection, machine learning-based anomaly detection, and robust
encryption approaches. By protecting transport systems against
cybercrime, these protocols secure data transfer and ITS
operations.

S IMULATION AND E NVIRONMENT TABLE

By incorporating advanced encryption techniques, real-time
threat monitoring, and adaptive security frameworks, ITS is
strengthened in terms of safety and resilience. Lightweight
elliptic curve cryptography and post-quantum algorithms are
two examples of advanced encryption methods that safeguard
vehicle-to-infrastructure (V2I) and vehicle-to-vehicle (V2V)
communications against manipulation and eavesdropping
while preserving low latency. AI-based intrusion detection
systems can detect and isolate real-time abnormalities by
analyzing sensor data, network traffic, and behavioral patterns,
preventing cascading failures. Adaptive security frameworks
adapt defensive mechanisms depending on changing threat
landscapes by incorporating continuous learning, behavior
analytics, and context-aware risk assessment.
IV. R ESULTS AND D ISCUSSION
Security and performance in ITS require cyber threat mitigation, computational efficiency, resilience, reliability, and
privacy protection. GenAI enhances real-time threat detection,
anomaly detection, and secure data sharing.
The analytical dataset [15] includes real-time traffic data,
cyber threat logs, and ITS anomaly detection records. Security effectiveness is assessed using encrypted communication
records, intrusion attempts, and system performance indicators. The dataset trains and validates GenAI for threat
detection, privacy protection, and resilience evaluation.
In the above table II, the simulation environment uses
NS-3, Python (TensorFlow, PyTorch), and MATLAB on a
GPU-accelerated HPC cluster. It tests the safety of ITS against
a variety of cyber threats utilizing methods such as AES-256
encryption, blockchain authentication, and intrusion detection
systems based on GenAI. To achieve the necessary level
of connectivity and sensor integration in ITS, infrastructure
components like Roadside Units (RSUs), On-Board Units
(OBUs), centralized Traffic Management Centers (TMCs),
edge computing nodes, and Vehicle-to-Everything (V2X) communication modules are utilized. OBUs handle vehicle-specific

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
8

Fig. 6.

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

Fig. 7.

(a) Cyber threat incidents in its over time.

Fig. 8.

Cyber threat detection and mitigation analysis.

Privacy protection effectiveness analysis.
TABLE III
C YBER T HREATS IN ITS (2018–2025)

sensing and local decision-making, while RSUs provide
vehicle-to-infrastructure connectivity and collect environmental data. Edge nodes reduce latency for real-time answers by
processing data closer to the source.
From the above fig. 6, ITS with GenAI enhances efficiency
at the expense of privacy. Real-time threat monitoring, strong
encryption, and adaptive security models maintain privacy.
AI-MA offers real-time anomaly detection and response and
works well in identifying emerging cyber threats. Model
updates are necessary because of adversarial attacks. IDS
and GenAI identify unwanted attempts at access to enhance
cybersecurity resiliency.
h
i h
i
h ′′ i
′′
′′
∂ f r = ∂∀ a + br ∗ ∝ +vr e + ∀Xa πρ
(16)
h
i
′′
Integrating adaptive precautions (∂∀ a + br ), threat mith
i
′′
igation ( ∝ +vr e ), and safeguarding privacy encryption (∂ f r ), Equation
describes the dynamic risk
h (16)
i
′′
component (+∀Xa πρ ) in ITS. Data privacy and
cybersecurity are actively controlled, strengthening the security regarding AI-driven analysis of privacy protection
effectiveness.

ransomware cases have increased significantly, emphasizing
the growing risks of evolving cyber threats. The data highlights the urgent need for improved cybersecurity measures
in ITS.
AI-powered security systems are essential for defending
against changing cyberattacks in ITS. GenAI-based IDS
enhance anomaly detection through real-time identification
of malicious patterns. From the above fig. 7, predictive
threat analysis is enhanced by AI-MA algorithms, while
blockchain-based authentication secures data. MFA and endto-end encryption minimize illegal access.
h
i
h
i
′′
′′
′′
ℵz e = π θ ω + ut ∗ V x µ + baq + σ ωl
(17)
Integrating encryption
h
i measures (ℵz e), resilient system
′′
resilience (πθ ω + ut ), along with real-time detection of
h
i
′′
threats (V x µ + baq ), Equation (17) describes the security
′′

improving factor (σ ωl ) in ITS. This dual-framework strategy
uses generative AI to improve adaptive analysis of cyber threat
detection and mitigation.
B. Efficiency of Intrusion Detection Systems (IDS) in ITS

A. Cyber Threat Incidents in ITS Over Time
Objective: Illustrates the increasing frequency of cyber
threats targeting ITS from 2018 to 2025 (projected).
Fig. 6(a) and Table III show the rise in cyber threats
targeting ITS from 2018 to 2025. AI-powered attacks and

Objective: Compares detection rates of different security
approaches, including Traditional IDS, AI-powered IDS, and
GenAI-Enhanced IDS.
Fig. 7(a) and Table IV compares Traditional IDS, AIPowered IDS, and GenAI-Enhanced IDS. GenAI-based IDS

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
KHAN et al.: SECURING INTELLIGENT TRANSPORTATION SYSTEMS: A DUAL-FRAMEWORK APPROACH

9

TABLE IV
IDS E FFICIENCY C OMPARISON (%)

Fig. 10.

Computational efficiency.

complexity and parallel processing enhance performance,
making ITS security frameworks efficient and scalable without
compromising system responsiveness.
h
i
h
i


′′
′′
a4 τ = π + vr ∗ ew ϵ + naw + ut π − nc′
(18)
Fig. 9.

(a) Efficiency of intrusion detection systems (IDS) in ITS.

outperforms others, achieving the highest detection accuracy
(95%) with the lowest false positive rate (3%) and the
fastest response time (100ms). The results emphasize integrating AI-driven security solutions to protect ITS from cyber
threats.
One way to make ITS more resilient is to use the responsive dual-architecture method, which combines two important
levels of security. Secure data transmission among cars, infrastructure, and control centers is the primary goal of the first
layer, which employs sophisticated cryptographic algorithms
like elliptic curve or quantum-resistant encryption. Because
of this, it can be certain that your critical data will stay
private and untouchable. As a second layer, self-adjusting
Sensitive data must be protected using a multi-layered security
strategy that includes technological, procedural, and physical
safeguards. A defined cybersecurity policy, frequent backups,
strong access controls, data encryption, and security awareness
training are all part of this. Security procedures apply safety
operations instructions in conjunction with security policies,
regulations, and recommendations. cybersecurity protocols
dynamically alter security measures in response to changing
threat environments. These procedures enhance the system’s
responsiveness to novel, unanticipated dangers using machine
learning models that study assault trends and make real-time
adjustments to security systems.
From the above Fig. 8, ITS security demands computational power for real-time threat detection and mitigation.
GenAI streamlines pattern recognition and anomaly detection to minimize false positives and accelerate calculation.
Edge computing minimizes latency by processing near data
sources, increasing reaction times. Lightweight encryption
methods balance security and processing power, ensuring
seamless ITS operations. AI-MA models need effective
resource management and hardware acceleration because
they have high computational requirements. Algorithmic

Integrating
h
i threat mitigation (a4 τ ), encryption weight
′′
( π + vr ),
and
adaptive
mitigating
measures
h
i
′′
(ew ϵ + naw , Equation (18) describes the general


security factor (ut π − nc′ ) in ITS. These components
of AI-enhanced security solutions are designed to provide
strong safeguards and resilience in analyzing computational
efficiency. Various measures have enhanced ITS cybersecurity
and privacy. Data confidentiality is ensured by using
encryption methods such as lightweight cryptography, which
allows for safe connection between infrastructure and cars.
Blockchain technology is used for transparent transaction
records and decentralized authentication to lessen the impact
of potential failure points. Because sensitive information
is never shared, federated learning allows dispersed data
processing for anomaly detection while maintaining privacy.
Intrusion detection systems (IDS) powered by AI constantly
watch for any signs of intrusion, while access control
techniques like role-based authentication ensure that only
authorized users can access the system. To further ensure the
security of personally identifiable information while data is
being analyzed, models are trained, data is anonymized, and
synthetic data is generated.
From the above fig. 9, the resilience of ITS against cyberattacks is assessed. GenAI improves resilience by learning
from changing attack patterns and mitigating threats. AI-MAdriven anomaly detection and blockchain data integrity layers
strengthen the system. Enhancing incident response tactics and
self-healing mechanisms can boost ITS resilience, ensuring
security and operational continuity in dynamic transportation
contexts.
h
i
h
i


′′
′′
T s = ∝ +bx + ∀z ∂ + yr e ∗ σ ϵγ a − s ′
(19)
Integrating
the iresponse to threats (T s), adaptive
mitigath
h
i
′′
′′
ing ( ∝ +bx ), and system resilience (+∀z ∂ + yr e ),
Equation
(19)
describes the security protection factor


(σ ϵγ a − s ′ ) in ITS. This suggested a dual-framework strategy using generative AI to improve resilience analysis.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
10

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

Fig. 13.

Reliability of transportation networks.
TABLE VI
C OMPARISON OF E XISTING W ITH P ROPOSED M ETHOD

Fig. 11.

Resilience analysis.
TABLE V
E NCRYPTION E FFECTIVENESS M ETRICS

Fig. 12.

(a) Encryption techniques on data privacy in ITS.

C. Impact of Encryption Techniques on Data Privacy in ITS
Objective: Evaluate the effectiveness of AES-256, Homomorphic Encryption (HE), and Blockchain-based Encryption
in securing ITS communications.
Fig. 9(a) and Table V evaluate AES-256, Homomorphic
Encryption, and Blockchain-Based Encryption in securing
ITS data. Blockchain-based encryption provides the highest
security (98/100) and data breach reduction (90%) with moderate processing overhead (15%). The results suggest that
advanced encryption methods enhance data privacy while
minimizing computational costs in ITS environments. Modern

transportation networks include unconventional and decentralized security mechanisms, such as blockchain-based identity
management, allowing for trustworthy peer-to-peer identification independent of any governing body.
From fig. 10, transportation networks must be reliable
against cyberattacks for uninterrupted operations. GenAIdriven security frameworks improve reliability by providing
predictive threat analysis, real-time anomaly detection, and
automated incident response. Secure data transfer and adaptive
encryption decrease risks and minimize system disturbances.
However, network congestion, latency, and computational
resource requirements are concerns. Network resilience is
improved via redundancy protocols, blockchain for secure
transactions, and self-healing techniques. Strong cybersecurity safeguards ITS from dangers and maintains trust and
efficiency.
h
i




′′
j x a − r ′ = 1m ∀′ + te ∗ vx µa + tw
(20)
Equation (20) integrates
of the system (vx),
 ′ the weaknesses

threat growth (= 1m
∀
+
te
),
and
adaptive
defensive mech
anisms ( j x a − r ′ ), thereby modeling the security answer
h
i
′′
factor ( µa + tw ). This strategy is based on cybersecurity
defensive flexibility in analyzing the reliability of transportation networks.
In Table VI, this comparison shows how the AI-MA security
framework is far better than the old techniques in terms of
security, efficiency, and resilience.
Findings indicate that AI-MA security frameworks based on
GenAI augment ITS security by detecting real-time anomalies, predicting threats, and responding automatically. Privacy,

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
KHAN et al.: SECURING INTELLIGENT TRANSPORTATION SYSTEMS: A DUAL-FRAMEWORK APPROACH

system adaptation, and computational demand continue to
be significant barriers. Edge computing and parallel processing enhance efficiency, whereas self-healing mechanisms and
redundancy techniques enhance robustness. Ensuring trust,
reliability, and uninterrupted ITS functionality in evolving
contexts calls for safe, scalable, and efficient cybersecurity
solutions.
Data privacy, effective intrusion detection, and secure
communication are the biggest challenges when protecting
AI-driven transportation infrastructure systems against malicious assaults (AI-MA). Data aggregation sites are appealing
targets for inference and extraction attacks, leading to privacy
concerns. These points gather and analyze sensitive real-time
information, including vehicle positions, user identities, and
behavioral patterns. As malicious actors use intricate evasion
strategies, adversarial instances, and zero-day attacks to exploit
weaknesses in AI models, intrusion detection systems are
becoming more difficult to detect.
Using Generative AI (GenAI) in ITS systems can lead to
problems like adversarial input generation, model drift from
using synthetic data for training, vulnerability to injection
attacks, and more opportunities for reverse engineering to
exploit the models. An adversary with malicious intent can
use GenAI-driven decision models to cause erroneous sensor
data interpretation, dangerous routing, or misclassify vehicle
actions. If synthetic data distributions differ from real-world
traffic patterns, model drift might negatively affect the operational effectiveness of continuous learning processes driven
by GenAI. Hackers can disrupt traffic flow optimization and
incident prediction by manipulating real-time GenAI results
via quick injection.
First, transportation systems must adhere to several national
and international regulations about data privacy, cybersecurity,
and traffic management to fulfill regulatory requirements.
Data processing, encryption, and accountability are heavily
regulated areas; as a result, system changes can be delayed,
or AI models can become less flexible. The swift implementation of cutting-edge security measures can be slowed down
by the time and effort needed to comply with these rules.
Secondly, there is yet another major obstacle in the form
of computational limitations. Threat detection and privacy
protection using AI-powered approaches have much potential,
but in contexts with limited resources, the computational
demands of these methods might be too much for the current infrastructure to handle. In some deployment situations,
the computer capacity needed to interpret massive volumes
of data in real-time from sensors, cars, and traffic control
systems could not be readily accessible. This might lead to
less efficient response times, especially in highly populated
areas with massive traffic data. Finally, thieves are always
looking for new ways to exploit weaknesses; thus, hostile
attacks are something to be worried about. Emerging attack
vectors, such as zero-day vulnerabilities or complex denialof-service assaults, can evade current protections, regardless
of how advanced AI security mechanisms are. Due to the
ever-changing nature of these attacks, ITS security solutions
must be flexible and regularly upgraded to tackle emerging
vulnerabilities.

11

V. C ONCLUSION
GenAI can revolutionize ITS; however, additional security
concerns must be addressed. Adaptive security models, realtime threat detection, and sophisticated encryption techniques
are necessary to combat AI-driven cyber threats. It has tackled
data privacy, intrusion detection, and secure communication, among other important issues. Addressing these issues
involves striking an equilibrium between protective measures
and technological advancement. Privacy-preserving techniques
that enable effective data analysis without disclosing personally identifying information include data anonymization,
differential privacy, and synthetic data creation. While AIpowered real-time intrusion detection systems assist in
identifying and removing such threats, ellipsocurl cryptography and other cutting-edge encryption technologies aid to
safeguard communication lines. The proposed AI-MA model
achieves a high threat detection accuracy of 96.2%, a privacy
protection score of 91.8%, a computational efficiency of
92.9%, a resilience score of 97.8%, and a network reliability
ratio of 92.6% compared to other existing models. Using
pre-trained AI models known to be biased and fragile is a
research limitation. Shifts in processing costs and policy issues
are two examples associated with real-life implementation that
need further investigation. The barriers mentioned above must
be removed for intelligent transport networks to be effective
in further deployments.
R EFERENCES
[1] S. Chaudhary, V. Gkioulos, and S. Katsikas, “Developing metrics to
assess the effectiveness of cybersecurity awareness program,” J. Cybersecurity, vol. 8, no. 1, Jan. 2022, Art. no. tyac006.
[2] K. Shaukat et al., “Performance comparison and current challenges of
using machine learning techniques in cybersecurity,” Energies, vol. 13,
no. 10, p. 2509, May 2020.
[3] A. Pollini et al., “Leveraging human factors in cybersecurity: An
integrated methodological approach,” Cognition, Technol. Work, vol. 24,
no. 2, pp. 371–390, May 2022.
[4] A. A. Ganin et al., “Multicriteria decision framework for cybersecurity risk assessment and management,” Risk Anal., vol. 40, no. 1,
pp. 183–199, Jan. 2020.
[5] M. Ahsan, K. E. Nygard, R. Gomes, M. M. Chowdhury, N. Rifat, and
J. F. Connolly, “Cybersecurity threats and their mitigation approaches
using machine learning—A review,” J. Cybersecurity Privacy, vol. 2,
no. 3, pp. 527–555, Jul. 2022.
[6] M. K. Hasan, A. A. Habib, Z. Shukur, F. Ibrahim, S. Islam,
and M. A. Razzaque, “Review on cyber-physical and cyber-security
system in smart grid: Standards, protocols, constraints, and recommendations,” J. Netw. Comput. Appl., vol. 209, Jan. 2023,
Art. no. 103540.
[7] A. Torok, Z. Szalay, and B. Saghi, “New aspects of integrity
levels in automotive industry-cybersecurity of automated vehicles,”
IEEE Trans. Intell. Transp. Syst., vol. 23, no. 1, pp. 383–391,
Jan. 2022.
[8] S. Safavat and D. B. Rawat, “On the elliptic curve cryptography for
privacy-aware secure ACO-AODV routing in intent-based Internet of
Vehicles for smart cities,” IEEE Trans. Intell. Transp. Syst., vol. 22,
no. 8, pp. 5050–5059, Aug. 2021.
[9] M. Alloghani, D. Al-Jumeily, A. Hussain, J. Mustafina, T. Baker, and
A. J. Aljaaf, “Implementation of machine learning and data mining
to improve cybersecurity and limit vulnerabilities to cyber attacks,” in
Nature-Inspired Computation in Data Mining and Machine Learning.
Cham, Switzerland: Springer, 2020, pp. 47–76.
[10] H. Kayan, M. Nunes, O. Rana, P. Burnap, and C. Perera, “Cybersecurity
of industrial cyber-physical systems: A review,” ACM Comput. Surv.,
vol. 54, no. 11s, pp. 1–35, Jan. 2022.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
12

[11] J. Petit and G. Le Lann, “Next generation vehicles, safety, and
cybersecurity—The CMX framework,” IEEE Trans. Intell. Transp. Syst.,
vol. 25, no. 2, pp. 1333–1345, Feb. 2024.
[12] A. Yaseen, “The role of machine learning in network anomaly detection
for cybersecurity,” Sage Sci. Rev. Appl. Mach. Learn., vol. 6, no. 8,
pp. 16–34, 2023.
[13] S. Gupta Bhol, J. Mohanty, and P. Kumar Pattnaik, “Taxonomy of cyber
security metrics to measure strength of cyber security,” Mater. Today,
Proc., vol. 80, pp. 2274–2279, Jan. 2023.
[14] M. Wazid, A. K. Das, V. Chamola, and Y. Park, “Uniting cyber security
and machine learning: Advantages, challenges and future research,” ICT
Exp., vol. 8, no. 3, pp. 313–321, Sep. 2022.
[15] Edge-IIoTset Cyber Security Dataset of IoT & IIoT. Accessed:
Feb. 7, 2025. [Online]. Available: https://www.kaggle.com/datasets/
mohamedamineferrag/edgeiiotset-cyber-security-dataset-of-iot-iiot
[16] Y. Zhang et al., “Privacy protection for open sharing of psychiatric and
behavioral research data: Ethical considerations and recommendations,”
Alpha Psychiatry, vol. 26, no. 1, p. 38759, 2025.
[17] S. Shirvani, Y. Baseri, and A. Ghorbani, “Evaluation framework for
electric vehicle security risk assessment,” IEEE Trans. Intell. Transp.
Syst., vol. 25, no. 1, pp. 33–56, Jan. 2024.
[18] H. Hufron, S. Fikri, S. Hadi, I. Shulga, and A. S. Wibowo, “Digital
platform power play: Indonesian and European union law perspective,”
Lex Scientia Law Rev., vol. 8, no. 2, pp. 707–742, Nov. 2024.

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

[19] H. Khalid, S. J. Hashim, F. Hashim, W. A. M. Al-Jawher,
M. A. Chaudhary, and H. H. M. Altarturi, “RAVEN: Robust anonymous
vehicular end-to-end encryption and efficient mutual authentication for
post-quantum intelligent transportation systems,” IEEE Trans. Intell.
Transp. Syst., vol. 25, no. 11, pp. 17574–17586, Nov. 2024.
[20] R. Ejjami, “The digital evolution strategies for overcoming cybersecurity
and adoption challenges in French SMEs,” Int. J. Multidisciplinary Res.,
vol. 6, no. 3, May 2024.
[21] A. Chhabra, R. Saha, and M. Conti, “PITCOR: Privacy-assured
time-controlled revocation in blockchain transactions,” in Proc.
6th Int. Conf. Blockchain Comput. Appl. (BCCA), Nov. 2024,
pp. 141–148.
[22] M. Khodayari, M. Akbari, and P. Foroudi, “The sharing economy: A
systematic literature review and research agenda,” Int. J. Consum. Stud.,
vol. 49, no. 1, Jan. 2025.
[23] L. Caldwell, Cybersecurity As a Human Right: A Reformulation of the
Theoretical Framework of Securitization Theory. Scottsdale, AZ, USA:
Northcentral University, 2022.
[24] C. Tran, F. Fioretto, and P. Van Hentenryck, “Differentially private and
fair deep learning: A Lagrangian dual approach,” in Proc. AAAI Conf.
Artif. Intell., May 2021, vol. 35, no. 11, pp. 9932–9939.
[25] E. Pacheco, “Older adults’ safety and security online: A post-pandemic
exploration of attitudes and behaviors,” 2024, arXiv:2403.
09208.
PAPER_TEXT
