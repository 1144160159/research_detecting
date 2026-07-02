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
# [644] Detecting and Mitigating Adversarial Machine Learning Attacks in Autonomous Vehicles Within the Internet of Vehicles
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
编号：644
题名：Detecting and Mitigating Adversarial Machine Learning Attacks in Autonomous Vehicles Within the Internet of Vehicles
年份：2026
DOI：10.1109/tits.2026.3652712
来源：IEEE Transactions on Intelligent Transportation Systems
PDF：paper/10.1109_TITS.2026.3652712.pdf
已有粗分类：IoT、车联网、工业互联网与边缘安全
二级关联：其他AI安全与跨域异常检测、恶意流量、暗网与攻击检测
相关性：强相关，分数 11
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\644.txt
- 原始字符数：68623
- 本次发送字符数：68623
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 27, NO. 5, MAY 2026

5385

Detecting and Mitigating Adversarial Machine
Learning Attacks in Autonomous Vehicles
Within the Internet of Vehicles
Mahmood Safaei , Ahmad Soleymani , Member, IEEE, Shahla Asadi , Mitra Safaei,
and Shidrokh Goudarzi , Member, IEEE
Abstract—Adversarial Machine Learning (AML), particularly
model poisoning, presents a critical threat to Autonomous Vehicles (AVs) in the Internet of Vehicles (IoV) environment. To
address this challenge, we propose a framework that integrates
Federated Learning (FL) with a Deep Learning-based Intrusion
Detection and Behavior Monitoring (DL-based IBM) system, a
vehicle scoring mechanism, Digital Twin (DT), and Generative AI
(Gen-AI) to enhance security in IoV environments. Each AV
employs a DL-based IBM as its local model, which is trained on
vehicle-local operational data and contributes to a global model
through FL aggregation. A vehicle scoring system is responsible for identifying and flagging compromised AVs (Zombies)
exhibiting suspicious behavior. When the DT detects that the
Zombie’s model has been manipulated through poisoning attacks,
the DT updates the compromised model with the correct global
model to restore normal operation. Furthermore, DT leverages
Gen-AI to simulate and learn from novel attack scenarios
that AVs have not previously encountered, ensuring that the
framework adapts to evolving threats. The simulation results
demonstrate significant improvements in resilience and detection
accuracy, with F1 scores reaching 99% for known attacks and
exceeding 87% for new unseen threats. This integrated approach
ensures robust and adaptive protection for AVs, maintaining
high trust and performance in the dynamic and adversarial IoV
network.
Index Terms—Autonomous vehicle, adversarial machine learning, digital twin, federated learning, Gen-AI, deep learning.

I. I NTRODUCTION

T

HE Internet of Vehicles (IoV) represents a rapidly evolving network in which vehicles, road infrastructure, and

Received 18 December 2024; revised 21 June 2025, 23 September 2025,
and 8 November 2025; accepted 30 December 2025. Date of publication
28 January 2026; date of current version 5 May 2026. The Associate Editor
for this article was A. Petrillo. (Corresponding author: Ahmad Soleymani.)
Mahmood Safaei is with the Computer Science Department, College of
Engineering and Polymer Science, The University of Akron, Akron, OH
44325 USA (e-mail: msafaei@uakron.edu).
Ahmad Soleymani is with the Department of Computing, Birmingham
City University (BCU), B4 7XG Birmingham, U.K. (e-mail: seyed.
soleymani@bcu.ac.uk).
Shahla Asadi is with the Department of Information Systems and Business Analytics, Kent State University, Kent, OH 44242 USA (e-mail:
sasadi1@kent.edu).
Mitra Safaei is with the Fakultät Electronic und Informatik, Gottfried
Wilhelm Leibniz Universität Hannover, 30060 Hanover, Germany (e-mail:
mitra.safaei2015@gmail.com).
Shidrokh Goudarzi is with the School of Computing and Engineering, University of West London, W5 5RF London, U.K. (e-mail:
shidrokh.goudarzi@uwl.ac.uk).
Digital Object Identifier 10.1109/TITS.2026.3652712

other systems communicate and collaborate to improve traffic
management, safety, and driving efficiency. IoV enables the
exchange of real-time data between Vehicles (V2V), Vehicles
and Infrastructure (V2I) and Vehicles and other devices (V2X).
This vast amount of data enables intelligent decisions about
vehicle behavior, route optimization, and accident prevention.
Autonomous Vehicles (AVs) rely on IoV for safe and efficient
navigation. By processing real-time information about road
conditions, other vehicles, and potential hazards, IoV provides
critical input to AV decision-making systems [1], [2], [3].
To manage this complex network of interactions, Machine
Learning (ML) and Deep Learning (DL) play a crucial role
in IoV. ML/DL algorithms enable vehicles to learn from large
datasets, process sensor data, and make predictions about their
environment [4]. Applications of ML/DL in vehicles include
intrusion detection systems to identify malicious activities,
anomaly detection to identify unsafe driving behaviors, and
route planning optimization to ensure smooth traffic flow [5],
[6], [7], [8], [9]. For example, [10] proposes a Decision
Tree–based IDS is proposed using in-depth CAN traffic analysis to improve detection robustness in automotive networks.
Similarly, [11] presents an ML-driven ECU fingerprinting
system using SVM and ANN models for embedded intrusion
detection in vehicles. By leveraging ML/DL, IoV systems can
improve the safety, efficiency, and adaptability of the network,
enabling AVs to respond to real-world conditions dynamically
and intelligently.
One of the key challenges in IoV is the need to continuously
update and improve ML models without compromising data
privacy. Vehicles collect sensitive data, including location,
speed, driving habits, and interactions with other vehicles.
Sharing these data with centralized servers for training ML
models poses privacy concerns and, in some cases, the sheer
volume of data makes it impractical to transmit.
Federated Learning (FL) addresses this challenge by allowing vehicles to collaboratively train ML models without
sharing their raw data [12]. In IoV, FL enables AVs to improve
their performance in tasks such as intrusion detection, behavior
monitoring, and anomaly detection [13]. Since vehicles operate in diverse environments and encounter unique challenges,
FL allows the global model to be enhanced with data from
different driving scenarios. This collaborative learning process
makes the IoV system more adaptable to changing conditions
and more resilient against potential threats [13], [14], [15].

1558-0016 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

5386

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 27, NO. 5, MAY 2026

However, FL frameworks such as horizontal FL, vertical FL
and federated transfer learning [16], face significant security
challenges, especially from Adversarial Machine Learning
(AML) attacks [17], which can compromise both local and
global model performance. In FL, AML attacks exploit the
collaborative and decentralized nature of training, targeting
local training or global aggregation phases to introduce vulnerabilities into the system [18].
Model poisoning attacks are a highly disruptive form
of AML, in which a malicious participant manipulates the
local model updates, such as gradients or weights, prior to
aggregation in the federated learning process. The attacker’s
primary objective is to influence the global model’s learning
trajectory, often by injecting subtle but targeted deviations
that accumulate over time. This manipulation can lead to
degraded model performance or, in more severe cases, cause
the global model to misclassify critical input, such as failing to
detect behavioral anomalies in safety-critical applications like
autonomous vehicles. These attacks are particularly insidious
because they can remain undetected during training, thus
exploiting the decentralized trust model inherent in FL systems
[19], [20].
Digital Twin (DT) technology-a virtual replica of a physical
system such as an autonomous vehicle-can help detect and
mitigate AML attacks in FL [21].The DT models key subsystems, including intrusion detection, anomaly monitoring,
communication modules, and sensors, within a synchronized
virtual environment. By mirroring the operational state of the
physical vehicle, the DT can simulate realistic driving and
attack scenarios, evaluate model responses, and validate the
integrity of FL-trained models in real time. This continuous
simulation and evaluation capability improves the resilience
of the system by enabling rapid detection, diagnosis, and
mitigation of adversarial manipulation before it affects realworld operations [22], [23], [24], [25], [26].
Furthermore, DTs use synthetic adversarial data generated
by Generative AI (Gen-AI) to create Digital Generative Twins
(DGTs), which improve local model training with a variety
of attack patterns and changes, increasing adaptability to new
AML threats. This ongoing adversarial training strengthens
the robustness of the model and supports a better detection of
dynamic anomalies.
Motivation. There is an urgent need to address the growing
threat of AML attacks on AVs in next-generation IoV networks. As AVs increasingly rely on ML and DL models for
decision making, perception, and coordination, attacks such as
model poisoning can seriously compromise their safety and
performance. The widespread use and dynamic nature of IoV
environments make them more vulnerable to these threats.
This highlights the need for secure, adaptive, and reliable
learning systems that can protect AVs from malicious behavior
and maintain reliable operation under adversarial conditions.
Contributions. Motivated by this need, this work presents
several key contributions aimed at enhancing the security
and performance of AVs in IoV networks. As a case study
(see Section II), an Intrusion detection and anomaly Behavior
Monitoring (IBM) system, serving as a security component
of the AV, is developed and evaluated against AML attacks,

specifically model poisoning attacks, to assess its resilience
within a FL framework. The primary focus is to examine
how model poisoning attacks affect the IBM system and how
these attacks can be addressed by leveraging DGT. The main
contributions are as follows:
• Proposing a system that enables AVs to collaboratively
improve their IBM system using FL.
• Mitigating the risks posed by AML attacks by integrating
DT technology, which simulates vehicle behaviors and
detects model poisoning attack in a controlled environment, helping to safeguard the global model.
• Generating synthetic data by Gen-AI enhances the DT’s
knowledge base, helping to detect unknown anomalies
and emerging threats not seen in real-world data, providing an adaptive defense mechanism.
Assumption. In this study, we assume that secure communication is established between all critical components of
the system, including AVs and the Cloud, AVs and DTs,
AVs and Roadside Units (RSUs), and between DTs and the
Cloud. To ensure confidentiality, integrity, and authentication,
all communication channels leverage lightweight encryption
and authentication mechanisms that comply with the principles
of Zero Trust Architecture (ZTA). The DT is deployed on
an isolated virtual machine (VM) using isolated deployment
architectures, ensuring strict separation from the AV and protection against external interference or compromise. However,
we acknowledge that in large-scale IoV environments, bandwidth and latency constraints can significantly affect real-time
data transfer and synchronization between AVs, RSUs, and
DTs. Therefore, the DT and FL aggregator can be deployed
at the edge layer, such as RSUs, to minimize communication
latency and reduce dependency on centralized cloud resources.
This distributed design helps alleviate bandwidth congestion, ensures faster feedback loops for AV decision-making,
and enhances scalability and reliability in dynamic IoV
environments.
The structure of this paper is as follows: Section II explores
a case study focusing on intrusion detection and behavior
monitoring within IoV systems. Section III evaluates the effectiveness of the proposed defense mechanism through formal
verification. Section IV outlines the experimental scenarios
and setup, followed by a discussion of the results. Finally,
Section V summarizes the key findings and outlines the
conclusions and directions for future work.
II. C ASE S TUDY: I NTRUSION D ETECTION AND A NOMALY
B EHAVIOR M ONITORING IN AUTONOMOUS V EHICLES
U NDER M ODEL P OISONING ATTACKS
This case study focuses on improving the security and
safety of AVs in the IoV network using an IBM system as a
representative example of existing ML/DL-based applications
deployed in autonomous vehicles. The IBM system is used
to examine the impact of model poisoning attacks in a FL
setting and to evaluate mitigation strategies. To address these
attacks, the framework uses a real-time vehicle behavior
scoring system and DGT technology, enabling the detection,
validation, and recovery of compromised models. Using secure

SAFAEI et al.: DETECTING AND MITIGATING AML ATTACKS IN AUTONOMOUS VEHICLES

5387

Fig. 1. Proposed framework.

Fig. 2. Adversarial manipulation scenarios in FL with four attack types: GN, DD, MR, and RR.

LTE / 5G communication, cloud-based aggregation, and RSU,
the system ensures continuous monitoring and provides an
adaptive defense against evolving AML threats in connected
AVs.
A. System Model
The system model designed to improve the security and
safety of AVs in the IoV network is made up of several
interconnected components. These components work together
to form a robust framework for detecting and mitigating

anomalous behaviors, as well as addressing potential cybersecurity threats such as model poisoning attacks. As shown in
Fig. 2, this system is implemented within a network of AVs,
RSUs, cloud infrastructure, and DTs located at the edge of the
network, all connected through secure LTE/5G communication
channels.
Each AV is equipped with an DL-based IBM system,
which serves as the local model within the FL framework.
This system continuously monitors critical vehicle behaviors,
such as traffic light adherence, pedestrian lane crossings,

5388

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 27, NO. 5, MAY 2026

vehicle speed, sudden braking, and other safety-critical driving
behaviors.
In the context of autonomous vehicles, the Controller
Area Network (CAN) protocol is utilized for communication between the vehicle’s Electronic Control Units (ECUs).
The DL-based IBM system is integrated into this CAN
bus, which functions as an ECU to seamlessly monitor and
analyze real-time data for intrusion detection and anomaly
behavior monitoring. This ensures that the security system
operates within the vehicle’s existing communication framework, enabling effective real-time detection of anomalies.
The cloud serves as the central aggregation point within
the system, where local models from multiple vehicles are
collected and aggregated to form a global model. This global
model benefits from the diversity of data collected by individual vehicles, improving the system’s ability to detect a wide
range of abnormal behaviors and attacks across the network.
However, the system also considers the possibility of AML
attacks, particularly model poisoning attacks, where malicious
vehicles may inject compromised models into the aggregation
process to degrade the global model’s performance.
To address these potential threats, the RSUs and other components of the network infrastructure continuously evaluate the
behavior of each AV. Each vehicle is assigned a behavior score
based on its performance in real-world driving conditions,
such as adherence to safety standards and proper handling
of critical situations. Vehicles with low scores, which may
indicate potential AML attacks or anomalies, are flagged for
further analysis. These low-score vehicles undergo additional
testing in the DT environment.
The DT acts as a virtual testing and simulation environment
for vehicles that exhibit abnormal behavior or low performance scores. In this controlled environment, the vehicle’s
local model is subjected to a series of tests, including the
detection of potential model poisoning attacks or other cybersecurity threats. By incorporating real-time and synthetic data
generated by Gen-AI, DT can also identify unknown attack
vectors and evolving threats, ensuring that anomaly detection
models remain resilient even in the presence of advanced and
emerging threats.
Secure communication is essential for system operation, and
all interactions between vehicles, cloud, RSUs, and the DT
system are conducted over a secure LTE/5G network. This
ensures low-latency, high-speed data transmission for realtime monitoring and anomaly detection. The communication
framework incorporates encryption and authentication protocols to protect sensitive data and prevent unauthorized access,
ensuring the integrity of the system.
This system provides a comprehensive framework for securing AVs in the IoV network. By integrating DL-based intrusion
detection, anomaly behavior monitoring, cloud-based aggregation, and DT testing, the system enhances real-time detection
capabilities while mitigating the risks posed by model poisoning attacks and other cyber-security threats.
B. AML Attacks: Model Poisoning
Model poisoning attacks are a subset of AML techniques
that specifically target FL systems. In these attacks, adversaries

aim to corrupt the model by altering the local model updates
before they are aggregated into the global model. This can
degrade the performance of the global model, leading to false
positives or missing detection in systems.
A typical FL setup involves a collection of local models
θi , each trained in a private data partition Di located on the
autonomous vehicle AVi , where i = 1, 2, . . ., N. After local
training, these models share their weight updates ∆θi with the
central aggregator (cloud), which aggregates them into a global
model, denoted θg , according to:
N

θg(t+1) = θg(t) +

1 X (t)
∆θi
N

(1)

i=1

Generally model poisoning attacks manipulate the local model
parameters θi so that the updates ∆θi become poisoned ∆θi∗ ,
with the objective of negatively influencing the global model.
For a benign update, the local training loss function can be
represented as
1 X
l ( fθ (x) , y)
(2)
Li (θ) =
|Di | (x,y)∈D
i

∆θi∗ = ∆θi + δi

(3)

where fθ (x) is the prediction of the model with parameters
θ, l ( fθ (x) , y) is the loss function, and Di is the local dataset
of vehicle i, δi is the adversarial perturbation introduced by
the attacker, which varies depending on the specific attack
vector. The goal of δi is to maximize global loss or to
specifically degrade detection performance in a subset of
malicious activities, such as avoiding detection of specific
intrusions.
When poisoned updates are aggregated with benign updates,
the global model becomes compromised. The new global
model update after including the poisoned model is:
!
N−1
1 X
∗
(t+1)
(t)
∆θi + ∆θi
(4)
θg
= θg +
N
i=1

In our poisoning attack scenarios, we simulate four different types of adversarial manipulation: Gaussian noise (GN),
directional drift (DD), model reversal (MR) and random
replacement (RR). These attacks represent common strategies used to compromise FL systems by corrupting local
model updates prior to aggregation. Gaussian noise introduces
random perturbations to model parameters, while directional
drift systematically shifts updates in a specific direction to
bias the global model. Model reversal inverts the gradients
to counteract the learning process, and random replacement
substitutes legitimate models with completely unrelated or
malicious ones. Each of these techniques aims to degrade
the performance or manipulate the behavior of the global
model, thereby undermining the reliability of autonomous
vehicle decision making in IoV environments. Algorithm 1
illustrates the simulation of AML in FL, which incorporates
four poisoning strategies of the model. In this algorithm, a
zombie refers to a vehicle compromised by a model poisoning
attack. It is identified through our vehicle scoring system,
which will be discussed in Section II-D.

SAFAEI et al.: DETECTING AND MITIGATING AML ATTACKS IN AUTONOMOUS VEHICLES

Algorithm 1 AML Simulation in FL
1: Input: Global model θg , Local datasets {D1 , D2 , . . ., DN },
Total vehicles N, Simulation rounds R, Number of zombie
vehicles Z, Attack types A = {Gaussian, Drift, Reversal,
Replacement}, µ is drift intensity
2: Output: Poisoned local models {θi∗ }, Final global model
θgfinal
3: Initialize: θg ← random initialization
4: for each round r = 1 to R do
5:
Server distributes θg to all vehicles
6:
for each vehicle i ∈ {1, 2, . . ., N} in parallel do
7:
if vehicle i is a zombie (i ≤ Z) then
8:
Choose attack type ai ∈ A
9:
Apply attack based on ai :
10:
if ai = Gaussian then
11:
Sample noise η ∼ N (0, σ2 )
12:
θi∗ ← θg + η
13:
else if ai = Drift then
14:
Generate drift vector d toward malicious direction
15:
θi∗ ← θg + µd
16:
else if ai = Reversal then
17:
Train local model θi on Di with θg
18:
Estimate ∇Li from model
19:
Inverted gradient θi∗ ← θg − α∇Li
20:
else if ai = Replacement then
21:
θi∗ ← random model parameters
22:
end if
23:
else
24:
Train local model θi∗ on Di using θg
25:
end if
26:
Send θi∗ to the aggregator
27:
end for
28:
Aggregator updates global model θg ← Aggregate({θi∗ })
29: end for
30: return Final global model θgfinal , {θi∗ }

C. DL-Based IBM System
The DL-based IBM system is designed to improve the
security and safety of AVs in IoV. The primary function
of this system is to detect both intrusions (external cybersecurity threats) and anomalous behavior (unusual or unsafe
driving patterns) in real-time. The DL-based IBM system
operates as a local model onboard each vehicle, utilizing data
from various sensors and communication protocols, and is
periodically updated using federated learning.
The DL-based IBM system takes as input a stream of data
from the vehicle’s sensors and internal communication bus,
such as vehicle speed, GPS position, Traffic light adherence,
Pedestrian lane crossings, Sudden braking events, CAN bus
data for communication between ECUs, and network traffic
data for detecting cyber-security threats. Each feature in the
input data can be represented as a multidimensional vector:
h
i
Xt = x1(t) , x2(t) , · · · , xn(t)
(5)
where Xt is the input feature vector at time t, and n is the
number of features.

5389

The DL-based IBM system formulates intrusion and
anomaly detection as a classification task, with the aim of
labeling each observed behavior or network traffic instance as
normal or abnormal. This can be formalized as a binary classification task, where the output of the system is a probability
distribution over two classes:

P (y|Xt ) = softmax fφ (Xt )
(6)
where P (y|Xt ) represents the probability of the class y (normal
or anomalous behavior) given the input Xt , fφ is the deep
learning model parameterized by φ, softmax(.) is the softmax
function used to convert the output of the model into a
probability distribution.
The system is trained to minimize the binary cross-entropy
loss function:
m
1X
G (φ) = −
m
i=1


yi log P (yi |Xi ) + (1 − yi ) log (1 − P (yi |Xi )) (7)
where m is the number of training samples, yi is the true label
of the i-th sample (1 for anomalous, 0 for normal), P (yi |Xi )
is the predicted probability of the i-th sample belonging to
class yi .
D. Vehicle Scoring System (VSS)
To evaluate the safety and performance of AVs, a behaviorbased scoring system is proposed that continuously monitors
driving actions and assigns scores based on key performance
metrics. Our system integrates both internal (on-board system
data) and external (infrastructure-based observations) factors
to provide a comprehensive assessment of vehicle behavior.
The scoring is based on parameters such as the ability to
maintain a safe distance from other vehicles under varying
traffic conditions, adherence to speed limits with adaptive
control in different types of road and environmental conditions,
and effective handling of critical situations involving sudden
braking, obstacle avoidance, or interactions with pedestrians.
Although the present work focuses on logical-level indicators
relevant to AML detection, low-level physical attacks such
as CAN spoofing and ECU tampering [27] could also be
addressed in future extensions through the integration of
physical fingerprinting techniques, which are beyond the scope
of this study.
1) Internal Scoring System (ISS): The proposed ISS continuously monitors the behavior of the vehicle based on
sensor data, such as radar, LiDAR, and cameras. This system
evaluates key performance metrics, including safety distance,
speed control, and handling of critical situations. The internal
score S in (t) of AV i at time t is a weighted sum of various
behavior metrics.
S iin (t) = w1 × Di,sa f e (t) + w2 × Vi,opt (t) + w3 × Hi,crit (t) (8)
where Di,sa f e is a score related to the distance of the AV i from
other surrounding AVs. This score decreases if the vehicle
is dangerously close to other vehicles, Vopt is the optimal
speed score, where speed control is evaluated based on the
difference between vehicle speed and the recommended speed

5390

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 27, NO. 5, MAY 2026

for the segment or situation of the road, and Hcrit represents
the handling score for critical situations, where the vehicle’s
ability to react appropriately in sudden or dangerous situations
is evaluated. w1 , w2 , and w3 are weighting factors that reflect
the relative importance of each metric. Each of these metrics
is normalized between 0 and 1, with higher values indicating
better performance.
The safety distance metric D sa f e (t) can be modeled as a
function of current speed v(t) and distance to the closest
vehicle d(t):


d (t)
(9)
D sa f e (t) = 1 − exp −
v (t) + 
where  is a small positive constant to avoid division by zero.
This formula ensures that the score decreases as the vehicle
approaches others too quickly relative to its speed.
The optimal speed metric Vopt (t) measures the deviation
from the optimal speed vopt (t) for the given road segment.
It can be expressed as:
ˇ
ˇ
ˇ v(t) − vopt (t) ˇ
ˇ
(10)
Vopt (t) = 1 − ˇˇ
vopt (t) ˇ
here, v(t) is the actual speed of the vehicle at time t, vopt (t)
is the speed limit or the recommended speed for the type of
road and traffic conditions.
The handling in critical situations score Hcrit (t) is based on
how well the vehicle reacts to emergencies, such as sudden
braking or obstacle avoidance. It can be represented by a
binary or probabilistic function that assigns a high score if the
vehicle successfully avoids collisions and maintains control:
Hcrit (t) = P(successful response | critical event)

(11)

This probability can be learned from historical data or expert
rules, with high scores for successful reactions.
2) External Scoring System (ESS): The proposed ESS uses
road infrastructure, such as traffic cameras, speed detectors,
and connected sensors, to assess vehicle behavior from an
external perspective. The external score S ex (t) of AV i is
calculated in a similar manner, but with a focus on factors
that the infrastructure can measure, such as adherence to traffic
signals, speed limits, and lane discipline:
S iex (t) = w4 × T i,signal (t) + w5
× Li,lane (t) + w6 × Vi,comp (t)

(12)

where T signal is the traffic signal adherence score, which is 1
if the vehicle obeys traffic signals and 0 otherwise. Llane is the
lane discipline score, which evaluates how well the vehicle
stays in the lanes and makes the appropriate lane changes.
Vcomp is the speed compliance score that measures how well
the vehicle complies with the speed limits enforced by the
road infrastructure.
3) Combined Scoring System: The final score S (t) of AV
i at time t is a weighted combination of internal and external
scores:
S i (t) = α × S iin (t) + β × S iex (t)
(13)
where α and β are weighting factors that adjust the relative contribution of the internal and external systems to the

Algorithm 2 Anomaly Detection and Model Recovery in
DL-Based IBM Using Digital Twin
Require: DL-based IBM on vehicle: θv , ISS on vehicle: S vin ,
ESS on RSU: S vex , Threshold δ, Digital Twin IBM: θdt
1: Monitor driving behaviors (traffic light, pedestrian lane,
speed, braking, etc.) and collect input data x
2: Evaluate behavior scores using S vin and S vex
3: Predict anomaly using θv (x)
ˇ
ˇ
4: Compute score difference: ∆ = ˇS vin − S vex ˇ
5: if ∆ > ϕ then
6:
Send x and θv to the Digital Twin
7:
Compute ŷdt = θdt (x)
8:
Compute ŷv = θv (x)
9:
if |ŷdt − ŷv | > ϕ then
10:
θv is compromised
11:
Replace θv ← θdt
12:
else
13:
θv is safe
14:
end if
15: else
16:
Behavior normal, no action required
17: end if
overall score. The combined score provides a comprehensive
evaluation of vehicle behavior by incorporating both on-board
and external monitoring systems. Algorithm 2 illustrates the
process of identifying a suspicious AV using the vehicle
scoring system, followed by recovery of its compromised
model through validation and replacement through DT.
E. Digital Generative Twins (DGT)
DGT combines the concepts of digital twins and Gen-AI
to create virtual replicas of physical systems, processes, or
environments. DT is cutting-edge technology that creates a
dynamic, virtual replica of a physical system, enabling realtime monitoring, simulation, and analysis. This capability is
particularly crucial for complex environments like IoV, where
the coordination between autonomous vehicles, infrastructure,
and central control systems requires precision and adaptability.
Gen-AI complements DT technology by synthesizing data and
generating scenarios that mimic real-world conditions [28].
Different types of Gen-AI tools include Generative Adversarial Networks (GANs), Variational Autoencoders (VAEs),
transformer-based models such as GPT, and time series generators such as TimeGAN. When combined, DT and Gen-AI
form a robust framework that not only enhances system
performance but also strengthens security against sophisticated
adversarial threats, including AML and model poisoning.
DT technology operates by establishing a digital representation of real-world objects or systems, linked through
continuous data streams for synchronization. The essential
components include the data acquisition layer, the simulation
core, and the analysis and feedback loop. The data acquisition
layer collects real-time data from IoV sensors, communication
channels, and vehicle systems. The simulation core is a
computing module that models and predicts the behavior of the
system under various conditions using physical laws, learned

SAFAEI et al.: DETECTING AND MITIGATING AML ATTACKS IN AUTONOMOUS VEHICLES

behaviors, or a combination of both. The analysis and feedback
loop integrates predictive analytics and anomaly detection
algorithms to provide insights and corrective actions to the
physical system. Mathematically, a DT can be represented as:
DT = (X, Θ, Φ)

(14)

where X represents the state variables, such as vehicle position,
speed, sensor readings, Θ denotes the physical and digital
parameters of the system, and Φ represents the transfer functions or machine learning models mapping system behavior.
DGT is one of the effective solutions to address AML
attacks. In this study, DGT is used to simulate model poisoning
attacks, as shown in Algorithm 1, and to evaluate suspicious
AVs by testing the accuracy of the ML/DL models deployed
on them. This allows the system to train in advance and
become more resilient against model poisoning. By exposing
the learning framework to synthetic adversarial scenarios, the
system can better recognize and defend against malicious
patterns.

Algorithm 3 cGAN for Adversarial Attack Generation
Require: Clean weights Wc , real attack deltas ∆a , condition
vectors c, generator G, discriminator D, number of epochs
N, batch size B
1: Initialize parameters of G and D
2: for epoch = 1 to N do
3:
for each mini-batch of size B do
4:
Sample Wc , ∆a , and c from dataset
5:
Generate adversarial deltas ∆g ← G(Wc , c)
6:
Discriminator score for actual attack sa ← D(∆a , Wc , c)
7:
Discriminator score for generated attack sg ←
D(∆g , Wc , c)
8:
Compute discriminator loss:

1
BCE(sa , 1) + BCE(sg , 0)
LD =
2
9:
Update D using gradient ∇D LD
10:
Re-generate for generator update ∆g ← G(Wc , c)
11:
sg ← D(∆g , Wc , c)
12:
Compute generator loss:
LG = BCE(sg , 1)

F. Generating Unknown Attack for IoV Network Using cGAN
In this study, Conditional GAN (cGAN) is used to generate
sophisticated adversarial attack vectors that mimic realistic model manipulation. The cGAN consists of two neural
networks, a generator and a discriminator, that are trained
in opposition. The generator takes as input a clean model
weight vector and a condition vector representing the type
and strength of attack, and learns to output a plausible attack
delta that perturbs the clean model. During the same time, the
discriminator receives both real and generated attack deltas,
along with the corresponding clean weights and conditions,
and learns to distinguish between genuine and synthetic
perturbations. Through this adversarial training process, the
generator becomes increasingly skilled in producing attack
vectors that are indistinguishable from real ones (Algorithm 3).
III. L ATENCY-ACCURACY T RADEOFF
M ODELING IN FL FOR I OV
In IoV environments, AV decision-making requires accurate
and timely learning. In FL, the accuracy of the model is
directly influenced by both computation and communication
time, making it essential to design systems that optimize
these factors jointly to maintain real-time performance and
efficient use of resources. For example, delays in model
synchronization between AVs and the edge server during
critical maneuvers, such as lane-keeping corrections, steering
control, or emergency braking, can result in outdated decisions or missed anomaly detections. Therefore, maintaining
a balance between computational efficiency and low-latency
communication is vital to enable AVs to respond accurately and quickly to dynamic driving conditions in IoV
systems.
A. Computation Time
In each AV, the computation time is a critical factor
that affects the overall latency in the learning process. The

5391

Update G using gradient ∇G LG
end for
15: end for
16: return Trained generator G
13:
14:

computation time required for AV i to complete the local
training on Di samples is given by the following:
T comp,i =

C · Di
fi

(15)

where C is the number of CPU cycles required to process one
data sample, Di refers to the number of local data samples in
AV i, and fi is the CPU frequency (cycles per second, in GHz)
for AV i.
On the cloud side, computational time is primarily spent
aggregating model updates. Assuming the cloud has high
performance computing capabilities, the aggregation delay is
relatively small but increases with the number of participating
AVs N and model size S . The cloud-side aggregation time can
be approximated as
T agg = α · N · S

(16)

where α is a proportionality constant that represents the aggregation cost per model element. The end-to-end computation
time is thus:
T total-comp = max T comp,i + T agg
i

(17)

This expression highlights that the slowest AV dominates
the edge-side computation delay, and the total delay also
includes cloud aggregation time. Reducing T comp,i (by increasing fi , reducing Di , or simplifying the model) is essential
to ensure timely model updates and avoid delayed contributions, which negatively impact convergence and global model
accuracy.

5392

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 27, NO. 5, MAY 2026

B. Communication Time
It includes the transmission delay (T tx ), the propagation
delay (T prop ), the queue delay (T queue ), and the processing
delay (T proc ). In this study, we neglect the processing time,
as it is typically negligible compared to the transmission and
queueing delays in FL communication.
T comm,i = T tx,i + T prop,i + T queue,i + T proc,i

(18)

In FL, communication occurs in two phases: download in
which the cloud sends the global model to AVs and upload in
which AVs send local model updates to the cloud. Therefore,
the total communication time per round is as follows:
d
u
T total-comm,i = T comm,i
+ T comm,i

(19)

Each can be modeled using the same form, possibly with
different model sizes (S u and S d ) and bandwidth in the uplink
(Bu ) and downlink (Bd ).
The transmission delay is determined by the size of the
model and the communication bandwidth.
Si
(20)
T tx,i =
Bi
This term quantifies the time required to transmit the model
update from the AV i to the aggregator. Here, S i is the size of
the local model update in bits, and Bi represents the available
communication bandwidth in bits per second (bps).
The propagation delay represents the physical time required
for a signal to travel from the AV to the cloud.
di
(21)
v
where di is the distance and v is the signal propagation speed
in the medium (typically 3 × 108 m/s in free space). Although
relatively small compared to other delays, the propagation
delay becomes significant in scenarios where the cloud is
geographically distant, making edge server placement a critical
design decision.
The queue delay represents the time it takes for a message
to wait in the queue before being processed/transmitted.
ρi
T queue,i =
(22)
µi (1 − ρi )
T prop,i =

This component models the delay due to network congestion
and resource contention, where µi is the service rate (in
bits/s or packets/s), and ρi = λi /µi is the utilization of the
system with λi as the arrival rate. As the system approaches
saturation (ρi → 1), the queueing delay increases dramatically,
highlighting the need for dynamic scheduling and congestion
control mechanisms.
As explained above, in FL, both communication and computation efficiency critically influence the accuracy and performance of the local/global model. Communication delays,
caused by large model sizes, limited bandwidth, or long
transmission distances, can result in delayed updates that fail to
capture the current state of the environment, thus reducing the
accuracy of the model. On the computation side, constrained
resources in AVs can lead to delayed or too early stopped
local training, resulting in low-quality updates. Furthermore,
aggregation delays in the cloud, due to the heterogeneity and

complexity of the AV model, weaken the synchronization
between the AVs, slowing the convergence. Together, these
inefficiencies hinder the timely adaptation to dynamic road
conditions and reduce the overall effectiveness of the FL system. To ensure high model accuracy while respecting system
constraints, it is necessary to jointly optimize communication
and computation. An approach is to formulate accuracy A as
a function A = F(S , B, d, fi , Di ), and to define an optimization
problem that considers both communication and computation
delays.
P:
s.t.

max

{S ,B,d, fi ,Di ,θi }

A(S , B, d, fi , Di )

T total-comp,i + T total-comm,i
„ ƒ‚ …
„ ƒ‚ …

computation time

communication time

≤

τmax
„ƒ‚…

(23)

latency constraint

This formulation enables a multidimensional trade-off.
Increasing the size of the model can improve the accuracy,
but only if sufficient bandwidth and computational resources
are available to meet the latency constraint τmax . Optimizing
this balance is critical for high-accuracy and real-time learning
in IoV systems.
To analytically verify the latency-accuracy trade-off in
FL-based IoV, we consider two core theoretical insights:
(i) Impact of Computation Time on Accuracy, (ii) Impact of
Communication Time on Accuracy.
As shown in the optimization convergence proofs [29],
delayed updates increase gradient bias, leading to suboptimal
convergence. If T comp,i is large, AVs participate less frequently
or with delayed updates, thus reducing Ag . High communication latency causes longer FL rounds and reduces the
effective number of global updates within a training budget.
Let R denote the total number of rounds
 √of global aggregation. Given a convergence rate of O 1/ R [30], a smaller
number of rounds due to higher latency results in slower
accuracy improvements. This illustrates how communication
inefficiency directly affects the convergence behavior and final
performance of the global model in FL systems. Let ∆A denote
the accuracy degradation per unit of time delay. Then, the
expected accuracy loss due to latency is approximately:
∆Ag ∝

N
X

∆Acomp,i + ∆Acomm,i



(24)

i=1

where ∆Acomp,i = λ1 .T comp,i and ∆Acomm,i = λ2 .T comm,i . λ1
and λ2 are empirically or theoretically derived sensitivity
coefficients. Thus, reducing both T comp,i and T comm,i directly
improves the convergence and accuracy of the global model.
Optimization strategies such as dynamic frequency scaling,
selective AV participation, and compression of model updates
are used to balance this trade-off.
IV. E XPERIMENTAL S CENARIOS AND R ESULT A NALYSIS
This study presents a comparative analysis of FL performance under four types of model poisoning attacks, Gaussian
noise, directional drift, model reversal, and random replacement, as described in Algorithm 2. In this section, we analyze
the impact of varying the number of Zombie vehicles on FL
performance, demonstrating how an increased proportion of

SAFAEI et al.: DETECTING AND MITIGATING AML ATTACKS IN AUTONOMOUS VEHICLES

5393

TABLE I
S IMULATION S ETUP S UMMARY

compromised clients degrades model accuracy and convergence. We also highlight how the DT and Gen-AI components
improve the accuracy of detection and model recovery, emphasizing their critical role in strengthening FL-based security.
To ensure reproducibility and transparency, all experiments
were implemented using the Flower FL framework with a
PyTorch backend, and each AV, DT, and cloud aggregator
was simulated on independent VMs running Ubuntu 22.04.
The CICIoV2024 dataset, specifically designed for IoV environments, was used for both local and global training. Each
record in the dataset includes eight features (DATA 0–DATA 7)
representing the transmitted payload, an ID indicating the
message priority and type, and three labeling fields, label,
category and specific class, which identify whether the traffic
is benign or malicious and specify its attack category and
class. To simulate the heterogeneity of real-world vehicle data,
the dataset for each vehicle was partitioned from CICIoV2024
[31]. Data were split into 70% training, 10% validation, and
20% testing subsets. For fair comparison, all FL experiments
were carried out in 5 global rounds per scenario, with 100
total vehicles, of which 20%–60% were compromised (Zombie
vehicles). The model training employed a learning rate of
0.001, a batch size of 32, epoch 3, and a binary loss of
cross-entropy over five communication rounds. The detailed
simulation setup is summarized in Table I. To evaluate robustness, we compared several aggregation algorithms, including
FedAvg, FedAdam, Krum, and Trimmed Mean, demonstrating
how robust aggregation can mitigate poisoning impacts. The
F1 score was used as the main evaluation metric in all
scenarios and communication rounds, as it effectively captures
the trade-off between correctly detected attacks (TP), false
positives (FP), and false negatives (FN), providing a reliable
measure of the robustness of the model under adversarial
conditions.
2 × TP
F1 Score =
(25)
(2 × T P) + FP + FN

Zombie. The greatest degradation occurs with directional
drift and model reversal, where the F1 score drops sharply
from 0.95 to 0.25 by Round 2 and remains suppressed,
indicating that these attacks inject coherent adversarial updates
that successfully mislead the global model early in training.
This sudden drop suggests that the poisoned parameters were
integrated into the global model after Round 1, leading to
immediate performance collapse due to the absence of robust
aggregation defenses. In contrast, Gaussian noise results in
moderate degradation to 0.6 but stabilizes, reflecting its nondirectional, stochastic nature, which can be partially averaged
out by benign AV updates. Random replacement has minimal
impact, with F1 scores remaining near 0.9, as the entropy
introduced lacks the directional force necessary to consistently
degrade model performance. In this figure, the wider bands
for drift and reversal indicate higher variability and attack
instability, while narrower bands indicate more consistent
effects.

This study conducts eight different simulation scenarios. The
following is a detailed breakdown of each scenario and the
associated findings.

C. Scenario 3: 40% Zombie

A. Scenario 1: 20% Zombie
Fig. 3a reveals different behavioral patterns under four
attack strategies in an FL scenario with four AV and one

B. Scenario 2: 30% Zombie
In Fig. 3b, the FL scenario with 30% zombies demonstrates
how structured attacks can still be effective even when benign
AVs are in the majority. Directional drift reduces the F1
score to near zero in all rounds, indicating persistent and
successful model corruption. The model reversal maintains
high but slightly degraded F1 values, ranging from 0.8613
to 0.9352, showing partial resilience against inverse update
patterns. Gaussian noise begins at 0.3098 and peaks at 0.6279
in Round 4, reflecting unstable but recoverable behavior under
random perturbations. Random replacement shows significant
variability, rising from 0.3838 in Round 1 to 0.8172 in
Round 2, but later dropping to 0.5245 before ending at 0.6977.
These results indicate that while a higher number of AVs
can mitigate unstructured attacks, they are insufficient against
directional drift, which still causes complete collapse.

In Fig. 3c, the effects of adversarial strategies are analyzed
in an FL scenario where 40% of the total AV are zomobies.
Directional drift causes an immediate and persistent collapse in
performance, with F1 scores remaining near 0.0001 throughout
all rounds, indicating total model poisoning due to coherent
parameter manipulation. The reverse of the model leads to

5394

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 27, NO. 5, MAY 2026

Fig. 3. Experimental results based on different scenarios including DT and GenAI.

stable but degraded performance, with F1 scores ranging from
0.6651 to 0.6775, reflecting its consistent, yet less severe
impact. Gaussian noise yields highly unstable behavior, starting at 0.3148 in Round 1, peaking at 0.5134 in Round 3,
then dropping sharply to 0.2853 in Round 4, highlighting the
unpredictability of unstructured noise. Random replacement
shows increasing volatility, improving from 0.3332 in Round 1
to 0.6251 in Round 5, but with a sharp dip to 0.2889 in
Round 4, indicating inconsistent influence.
D. Scenario 4: 50% Zombie
In Fig. 3d, the FL configuration with the same number
of AV and zombies exposes the vulnerability of the system
to adversarial attacks. Directional drift forces the F1 score
to near-zero values in the first four rounds, with only a
minor increase to 0.0955 in Round 5, indicating near-total
model collapse under sustained coherent manipulation. The
model reversal maintains F1 scores in a tight band between
0.6658 and 0.6799, showing a consistent but moderate performance degradation. Gaussian noise starts at 0.6164, gradually
declines to 0.4077, and remains unstable throughout, reflecting
the unpredictable impact of non-targeted perturbations in a
balanced AV composition. Random replacement exhibits high
volatility, dropping from 0.3212 to 0.2031, recovering to
0.6299 in Round 3, and then again falling to 0.3257.
E. Scenario 5: 60% Zombie
In Fig. 3e, the FL setup with a number of zombies higher
than the number of AVs highlights the severe impact of the

increased adversarial ratio. Directional drift immediately drops
the F1 score to nearly zero in all rounds, with values fluctuating only between 0.0000 and 0.0001, indicating total and
sustained model collapse due to targeted manipulation. The
reversal of the model produces consistently degraded results,
maintaining F1 scores between 0.6444 and 0.6730, showing a
stable but significant performance loss. Gaussian noise causes
erratic performance, starting at 0.2022, peaking at 0.6824 in
Round 4, then decreasing to 0.5259, emphasizing instability
under random perturbations. Random replacement begins at
0.2197 and rises to 0.5621 before dipping to 0.5074, reflecting
inconsistent disruption. The low proportion of benign AVs prevents a meaningful correction, allowing adversarial influence
to dominate.
Table II presents the impact of different model poisoning
strategies on FL performance in five scenarios and multiple
training rounds. The results highlight how each type of attack
degrades the learning process to varying degrees.
F. Impact of Adversarial Ratio on FL Performance
Fig. 3f illustrates the variation of the F1 score as the percentage of Zombie vehicles increases dynamically from 20%
to 90% under four model poisoning strategies. As shown, the
model reversal maintains the highest F1 score in lower zombie
ratios (20–50%), close to 0.9, but experiences a gradual
decline beyond 60% due to increasing adversarial influence.
Random replacement achieves moderate stability up to 50%
before deteriorating as the number of compromised vehicles
grows. Gaussian noise demonstrates fluctuating performance

SAFAEI et al.: DETECTING AND MITIGATING AML ATTACKS IN AUTONOMOUS VEHICLES

5395

TABLE II
I MPACT OF M ODEL P OISONING T YPES ON FL P ERFORMANCE ACROSS F IVE S CENARIOS

with F1 scores between 0.3 and 0.6, indicating sensitivity
to random perturbations. Directional drift, on the other hand,
shows near-zero detection capability across all ratios, reflecting
its subtle manipulation that evades detection. Overall, the
figure highlights that as the proportion of Zombie vehicles
increases, the global model performance degrades across all
attack types, emphasizing the importance of robust aggregation
and anomaly detection mechanisms in FL for IoV security.
G. DT Integration and Effect
Integration of DT into the FL framework significantly
fortifies the system’s defense against AML attacks. Upon
identifying potentially zombies through the proposed scoring
system, the system isolates their parameter updates and historical data. These are then transmitted to the DT. The DT
retrains the latest global model using the Zombie’s local data
and compares the resulting parameters against those originally
submitted. If discrepancies indicative of manipulation are
detected, the DT overrides the malicious updates by pushing
the correct global model back to the Zombie, effectively mitigating the impact of the attack. To evaluate the effectiveness
of the proposed solution, we tested it using scenarios IV-C.
The results obtained presented in Fig. 3g present the impact
of our proposed scoring system and DT.
H. Gen-AI Enhanced Verification
In this scenario, we used two different approaches to assess
the resilience of the system by integrating Gen-AI with DT
validation, using datasets that were completely unseen during
model training. In the first approach, we introduced a new
dataset that was completely isolated from AV training and
testing. The DT used this dataset to train and evaluate a model.
Once the model achieved high accuracy with these previously
unseen data, the updated model parameters were sent to the
FL server for aggregation. The server then generated a new
global model, which was distributed to all AVs. To rigorously
evaluate the generalizability of the system, we performed
testing using a portion of the dataset that had never been
seen by the AVs or the DT during any stage of training.
AVs used this subset exclusively for testing, simulating realworld deployment where models must generalize to novel
scenarios. The new datase included targeted attacks on steering
mechanisms. Interestingly, the system maintained accurate F1
scores approaching 1 throughout all communication rounds
(Fig. 3h).
In the second approach, we utilized cGAN to synthesize
adversarial attacks in a more dynamic and intelligent manner

(Algorithm 3). The cGAN was trained using clean model
parameters and known attack deltas as input, along with
condition vectors representing different types and strengths
of attack. The generator in the cGAN learned to produce
realistic attack patterns tailored to specific conditions, while
the discriminator helped refine these outputs by distinguishing
real attack deltas from generated ones. This enabled the
creation of novel and targeted adversarial perturbations, which
were then injected into the Digital Twin. The DT trained
and validated the model with these synthetic attacks, and
after achieving satisfactory performance, the parameters were
forwarded to the FL server for further evaluation and testing by
the AVs. The results show that the adversarial model based on
cGAN maintained high F1 scores throughout the five rounds,
ranging from 0.87 to 0.91. Despite slight fluctuations, the
system remained robust and consistently resistant to attacks
generated (Fig. 3i).
I. DL-Based IBM Analysis
Table III presents the performance comparison of the proposed DL-based IBM against the Variational Autoencoder
(VAE) [32] in four attack scenarios under multiple FL aggregation strategies, including FedAvg, FedAdam, Krum and
Trimmed Mean. Under the FedAvg strategy, the DL-based
IBM maintains exceptionally high detection accuracy, ranging
from 99.6% in Scenario 1 to 97.9% in Scenario 5, with a
very low False Positive Rate (FPR) between 0.8% and 1.8%.
Similarly, Krum achieves near-identical performance, maintaining accuracy greater than 98.6% in all scenarios with FPRs
less than 1.3%, confirming its robustness against poisoning
attacks. The FedAdam variant also delivers stable accuracy
between 97.05%–98.01%, although with slightly higher FPR
values (1.5%–2.3%) due to adaptive updates. In contrast, the
Trimmed Mean method exhibits a noticeable drop in performance, with accuracy decreasing to 88.3%–89.5% and FPR
increasing to 3.3%, suggesting that its fixed trimming threshold may not adapt well to dynamic IoV environments. The
VAE baseline, which lacks federated aggregation and adversarial resilience, performs significantly worse, with accuracy
dropping from 90.6% in Scenario 1 to 43.1% in Scenario 5
and FPR exceeding 4.5% under heavy attack conditions. These
results collectively demonstrate that the DL-based IBM, when
combined with robust FL aggregation strategies, provides
superior accuracy and stability while minimizing false alarms.
The low FPR and consistent accuracy across scenarios confirm
the strong resilience and adaptability of the model in mitigating adversarial model poisoning attacks, ensuring trustworthy
learning in large-scale IoV environments.

5396

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 27, NO. 5, MAY 2026

TABLE III
P ERFORMANCE C OMPARISON OF DL-BASED IBM AND VAE U NDER D IFFERENT AGGREGATION M ETHODS ACROSS F IVE S CENARIOS

V. C ONCLUSION AND F UTURE W ORK
In this study, we have investigated the impact of AML
attacks, particularly model poisoning, on AVs that employ
ML/DL models within their systems. To counter these threats,
we have developed a framework that integrates a DL-based
IBM as the local model in a FL architecture, a vehicle scoring
system to identify suspicious vehicles, and a DT to validate
model integrity and learn emerging attack patterns. Within
this framework, the DT has been responsible for validating
the models of AVs flagged by the proposed vehicle scoring
system. If manipulated parameters have been detected, the
DT has replaced the compromised model in the suspicious
AV with the correct global model. The results have demonstrated a significant improvement in performance, with the F1
score reaching 99%. Furthermore, DT, in conjunction with
Gen-AI, has been used to train the global model on novel
attack patterns that AVs have not previously encountered.
This approach has ensured an adaptive and resilient defense
mechanism within IoV environments. As the results have
shown, the F1 score for detecting new attacks by AVs has
exceeded 87%, demonstrating a strong detection capability.
In future work, we plan to address the scalability limitations
associated with centralized components in our framework.
Specifically, our goal is to reduce dependency on a single FL
aggregator by exploring decentralized or hierarchical architectures, such as blockchain-based consensus mechanisms, to
improve scalability, robustness, and fault tolerance. Likewise,
as the current DT has operated as a centralized instance, we
will extend this design toward a federated or distributed DT
architecture, where multiple DT instances are deployed across
edge servers (e.g., roadside units). These distributed DTs will
collaboratively simulate, validate, and update models, thereby
improving system resilience, reducing communication latency,
and improving real-time decision-making. Furthermore, we
plan to implement adaptive aggregation strategies that dynamically adjust based on network conditions and to strengthen
vehicle trust assessment through fuzzy logic–based scoring,
thus improving interpretability, reliability and security in largescale IoV environments.
R EFERENCES
[1]
[2]
[3]

F. Yang, S. Wang, J. Li, Z. Liu, and Q. Sun, “An overview of Internet
of Vehicles,” China Commun., vol. 11, no. 10, pp. 1–15, Oct. 2014.
J. Contreras-Castillo, S. Zeadally, and J. A. Guerrero-Ibañez, “Internet
of Vehicles: Architecture, protocols, and security,” IEEE Internet Things
J., vol. 5, no. 5, pp. 3701–3709, Oct. 2018.
S. Yaqoob, G. Morabito, S. Cafiso, G. Pappalardo, and A. Ullah, “AIdriven driver behavior assessment through vehicle and health monitoring
for safe driving—A survey,” IEEE Access, vol. 12, pp. 48044–48056,
2024.

[4]

P. Sharma and H. Liu, “A machine-learning-based data-centric misbehavior detection model for Internet of Vehicles,” IEEE Internet Things
J., vol. 8, no. 6, pp. 4991–4999, Mar. 2021.
[5] A. Qayyum, M. Usama, J. Qadir, and A. Al-Fuqaha, “Securing connected & autonomous vehicles: Challenges posed by adversarial machine
learning and the way forward,” IEEE Commun. Surv. Tut., vol. 22, no. 2,
pp. 998–1026, 2nd Quart., 2020.
[6] L. Yang, A. Moubayed, and A. Shami, “MTH-IDS: A multitiered hybrid
intrusion detection system for Internet of Vehicles,” IEEE Internet
Things J., vol. 9, no. 1, pp. 616–632, Jan. 2022.
[7] S. Yaqoob, A. Hussain, F. Subhan, G. Pappalardo, and M. Awais, “Deep
learning based anomaly detection for fog-assisted IoVs network,” IEEE
Access, vol. 11, pp. 19024–19038, 2023.
[8] C. Bernardeschi et al., “HARDNESS: Hardware-supported post quantum
over-the-air software update and intrusion detection system for next
generation secure cars,” in Proc. Int. Conf. Appl. Electron. Pervading
Ind., Environ. Soc. Cham, Switzerland: Springer, 2024, pp. 439–447.
[9] N. Canino, P. Dini, S. Mazzetti, D. Rossi, S. Saponara, and E. Soldaini,
“Cybersecurity of automotive wired networking systems: Evolution,
challenges, and countermeasures,” Electronics, vol. 14, no. 3, p. 471,
Jan. 2025.
[10] N. Canino, P. Dini, S. Mazzetti, D. Rossi, and S. Saponara, “CANini:
In-depth traffic analysis for design and robustness evaluation of DTreebased IDS in automotive networking systems,” IEEE Access, vol. 13,
pp. 73236–73260, 2025.
[11] P. Dini, M. Zappavigna, E. Soldaini, and S. Saponara, “Embedded
machine learning-based voltage fingerprinting for automotive
cybersecurity,” IEEE Access, vol. 13, pp. 38342–38367, 2025.
[12] S. Zhang et al., “Federated learning in intelligent transportation systems:
Recent applications and open problems,” IEEE Trans. Intell. Transp.
Syst., vol. 25, no. 5, pp. 3259–3285, May 2024.
[13] H. Liu et al., “Blockchain and federated learning for collaborative
intrusion detection in vehicular edge computing,” IEEE Trans. Veh.
Technol., vol. 70, no. 6, pp. 6073–6084, Jun. 2021.
[14] X. Yuan et al., “FedComm: A privacy-enhanced and efficient
authentication protocol for federated learning in vehicular ad-hoc
networks,” IEEE Trans. Inf. Forensics Security, vol. 19, pp. 777–792,
2024.
[15] P. Rani et al., “Federated learning-based misbehaviour detection for
the 5G-enabled internet of Vehicles,” IEEE Trans. Consum. Electron.,
vol. 70, no. 2, pp. 4656–4664, May 2023.
[16] Q. Yang, Y. Liu, T. Chen, and Y. Tong, “Federated machine learning:
Concept and applications,” ACM Trans. Intell. Syst. Technol. (TIST),
vol. 10, no. 2, pp. 1–19, 2019.
[17] A. D. Joseph, B. Nelson, B. I. Rubinstein, and J. Tygar, Adversarial
Machine Learning. Cambridge, U.K.: Cambridge Univ. Press, 2018.
[18] A. Uprety and D. B. Rawat, “Mitigating poisoning attack in federated
learning,” in Proc. IEEE Symp. Ser. Comput. Intell. (SSCI), Dec. 2021,
pp. 01–07.
[19] H. Alsuwat, “Detecting data poisoning attacks using federated learning
with deep neural networks: An empirical study,” Int. J. Adv. Comput.
Sci. Appl., vol. 14, no. 11, p.688, 2023.
[20] Y. Li, Z. Guo, N. Yang, H. Chen, D. Yuan, and W. Ding, “Threats and
defenses in federated learning life cycle: A comprehensive survey and
challenges,” 2024, arXiv:2407.06754.
[21] E. C. Balta, M. Pease, J. Moyne, K. Barton, and D. M. Tilbury,
“Digital twin-based cyber-attack detection framework for cyber-physical
manufacturing systems,” IEEE Trans. Autom. Sci. Eng., vol. 21, no. 2,
pp. 1695–1712, Apr. 2024.
[22] C. Hu et al., “Digital twin-assisted real-time traffic data prediction
method for 5G-enabled Internet of Vehicles,” IEEE Trans. Ind. Informat.,
vol. 18, no. 4, pp. 2811–2819, Apr. 2022.

SAFAEI et al.: DETECTING AND MITIGATING AML ATTACKS IN AUTONOMOUS VEHICLES

[23] X. Yuan, J. Chen, N. Zhang, J. Ni, F. R. Yu, and V. C. M. Leung,
“Digital twin-driven vehicular task offloading and IRS configuration
in the Internet of Vehicles,” IEEE Trans. Intell. Transp. Syst., vol. 23,
no. 12, pp. 24290–24304, Dec. 2022.
[24] J. Liu, L. Zhang, C. Li, J. Bai, H. Lv, and Z. Lv, “Blockchain-based
secure communication of intelligent transportation digital twins system,”
IEEE Trans. Intell. Transp. Syst., vol. 23, no. 11, pp. 22630–22640, Nov.
2022.
[25] Y. Tao, J. Wu, Q. Pan, A. K. Bashir, and M. Omar, “O-RAN-based
digital twin function virtualization for sustainable IoV service response:
An asynchronous hierarchical reinforcement learning approach,” IEEE
Trans. Green Commun. Netw., vol. 8, no. 3, pp. 1049–1060, Sep. 2024.
[26] J. Guo, M. Bilal, Y. Qiu, C. Qian, X. Xu, and K.-K. Raymond
Choo, “Survey on digital twins for Internet of Vehicles: Fundamentals,
challenges, and opportunities,” Digit. Commun. Netw., vol. 10, no. 2,
pp. 237–247, Apr. 2024.
[27] P. Dini, E. Soldaini, and S. Saponara, “Design and test of an embedded
real-time compact voltage fingerprinting algorithm for enhanced automotive cybersecurity,” IEEE Access, vol. 13, pp. 73183–73201, 2025.
[28] H. Xu, F. Omitaomu, S. Sabri, S. Zlatanova, X. Li, and Y. Song,
“Leveraging generative AI for urban digital twins: A scoping review
on the autonomous generation of urban data, scenarios, designs, and 3D
city models for smart city advancement,” 2024, arXiv:2405.19464.
[29] T. Li, A. K. Sahu, A. Talwalkar, and V. Smith, “Federated learning:
Challenges, methods, and future directions,” IEEE Signal Process. Mag.,
vol. 37, no. 3, pp. 50–60, May 2020.
[30] H. Yang, J. Liu, and E. S. Bentley, “CFedAvg: Achieving efficient
communication and fast convergence in non-IID federated learning,”
in Proc. 19th Int. Symp. Model. Optim. Mobile, Ad hoc, Wireless Netw.
(WiOpt), Oct. 2021, pp. 1–8.
[31] E. C. P. Neto et al., “CICIoV2024: Advancing realistic IDS approaches
against DoS and spoofing attack in IoV CAN bus,” Internet Things,
vol. 26, Jul. 2024, Art. no. 101209.
[32] S. Li, Y. Cheng, W. Wang, Y. Liu, and T. Chen, “Learning to detect malicious clients for robust federated learning,” 2020, arXiv:2002.00211.

Mahmood Safaei received the Ph.D. degree in
computer science. He is currently an Assistant Professor with the Department of Computer Science,
The University of Akron, USA. His research focuses
on secure and trustworthy distributed systems, with
an emphasis on cyber-security for networked and
cyber-physical systems, autonomous vehicles, digital
twins, the Internet of Things, and trustworthy and
generative artificial intelligence. His work integrates
adversarial machine learning, federated learning
security, remote attestation, and resilient networking
architectures. He has served as a principal investigator and a co-principal
investigator on multiple nationally and internationally funded research
projects. His research interests include autonomous vehicles, digital twins,
the IoT, cyber-security, generative artificial intelligence, artificial intelligence,
and computer networking.

Ahmad Soleymani (Member, IEEE) received
the Ph.D. degree in computer science from the
Faculty of Engineering, Universiti Teknologi
Malaysia (UTM), Malaysia, in 2019. He was a
Research Fellow with the Centre for Vision, Speech,
and Signal Processing (CVSSP), University of
Surrey, Guildford, U.K., and the School of Electrical
and Electronic Engineering, University of Sheffield,
Sheffield, U.K. He was a Senior Research Fellow
with the Institute for Communication Systems
(ICS), University of Surrey. He is currently a Senior
Research Fellow with the Department of Computer Science, Birmingham
City University (BCU). His research interests include autonomous vehicles
networks, wireless sensor networks, the Internet of Things and Industrial
Internet of Things, mobile networks, artificial intelligence (AI), machine
learning, large language model, generative AI, quantum computing,
edge/fog/cloud computing, and AI radio access networks and open radio
access network environments.

5397

Shahla Asadi received the Ph.D. degree in information systems. She is currently an Assistant Professor
with the Department of Information Systems and
Business Analytics. She has held academic positions
as a Lecturer with the University of Gloucestershire,
a Senior Lecturer with the National University of
Malaysia, and a Post-Doctoral Research Fellow with
the Universiti Putra Malaysia. She has published
extensively in high-impact journals, including Technological Forecasting and Social Change, Computers and Industrial Engineering, Journal of Cleaner
Production, and IEEE T RANSACTIONS ON E NGINEERING M ANAGEMENT.
Her research interests focus on data analytics, recommendation systems,
and the Internet of Things (IoT) solutions, with an emphasis on enhancing
decision-making, improving information sharing, and ensuring quality control
in complex industrial contexts. Her interdisciplinary research closely aligns
with machine learning, data mining, artificial intelligence, and database
systems. Throughout her academic career, she has received several prestigious
awards in recognition of her scholarly contributions.

Mitra Safaei received the M.Sc. degree in internet
technology and information systems (data science)
from Leibniz University Hannover. Her master’s
thesis focused on acoustic-based methods for process supervision in industrial environments. She
is a Data Scientist and a Software Engineer with
experience in data analytics, machine learning, and
backend development. Her research and professional
interests include data science, artificial intelligence,
data mining, and applied machine learning. She has
worked extensively in interdisciplinary environments
and combines strong analytical thinking with practical engineering expertise.

Shidrokh Goudarzi (Member, IEEE) received the
Ph.D. degree in communication systems and wireless
networks from Malaysia-Japan International Institute of Technology (MJIIT), Universiti Teknologi
Malaysia (UTM), under a three-year full scholarship.
She is currently a Senior Lecturer in computer science with the School of Computing and Engineering,
University of West London, U.K. Previously, she
was with the Centre for Vision, Speech, and Signal
Processing (CVSSP), University of Surrey. She was
a Senior Lecturer with the Universiti Kebangsaan
Malaysia (UKM). From 2018 to 2020, she was a Post-Doctoral Fellow with
the School of Advanced Informatics, UTM. She has published more than 80
research articles in high-quality journals and conferences. She has secured
national and international funding awards, including grants funded by UKRI
and the Royal Society, as a PI and a Co-I. Her research interests encompass
wireless networks, artificial intelligence, machine learning, next-generation
communication systems, the Internet of Things (IoT), and mobile, distributed,
and cloud computing. She actively contributes to the research community as
an editor and a reviewer for several reputable scientific journals.
PAPER_TEXT
