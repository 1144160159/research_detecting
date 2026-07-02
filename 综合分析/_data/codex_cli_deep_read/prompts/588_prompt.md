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
# [588] A Proactive Triple-Mutation MTD Architecture Enhancing AI-Driven Intrusion Detection Against Intelligent Adversaries in CIoT Networks
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
编号：588
题名：A Proactive Triple-Mutation MTD Architecture Enhancing AI-Driven Intrusion Detection Against Intelligent Adversaries in CIoT Networks
年份：2026
DOI：10.1109/tce.2026.3679035
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2026.3679035.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：IoT、车联网、工业互联网与边缘安全
相关性：强相关，分数 15
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\588.txt
- 原始字符数：64137
- 本次发送字符数：64137
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

4705

A Proactive Triple-Mutation MTD Architecture
Enhancing AI-Driven Intrusion Detection Against
Intelligent Adversaries in CIoT Networks
Zan Zhou , Wei Dong, Xiping Li , Lin Yan , Graduate Student Member, IEEE, Hao Hao , Shukan Liu ,
Shujie Yang , Member, IEEE, Xiaoyan Zhang , and Changqiao Xu , Senior Member, IEEE
Abstract—With the widespread deployment of intelligent
consumer-electronics devices and the rapid expansion of consumer Internet-of-Things (CIoT) ecosystems that support nextgeneration intelligent systems—including smart homes, edge-AI
gateways, and wearable networks—the volume and heterogeneity
of device-generated network traffic have surged. To mitigate
the limitations of traditional static AI-driven network intrusion
detection systems (NIDS), proactive defence paradigms such as
Network Moving Target Defence (NMTD) have been incorporated
into device–edge–cloud architectures. Unfortunately, sophisticated adversaries may infer defence strategies and circumvent
these mechanisms—leading to what we term the drug resistance
of intelligent adversarial attacks. To counter this, we propose
a reinforcement learning–based proactive Triple-Mutation Moving Target Defense (TM-MTD) framework that simultaneously
mutates access proxies, IP addresses, and security strategies.
The lightweight edge-level salience optimization ensures accurate
detection in highly dynamic traffic environments, while the global
policy differential optimization strengthens the defense system’s
long-term resilience. Experimental results demonstrate that
TM-MTD significantly enhances security performance against a
variety of intelligent attack models, providing a robust defense
framework for next-generation intelligent consumer-electronics
systems.
Index Terms—Intrusion detection system, intelligent attack,
moving target defense, deep reinforcement learning, endogenous
security.

T

I. I NTRODUCTION
HE proliferation of intelligent consumer-electronics
devices, coupled with the rapid expansion of CIoT

Received 28 December 2025; revised 27 February 2026; accepted 22 March
2026. Date of publication 30 March 2026; date of current version 2 June
2026. This work was supported in part by the National Natural Science
Foundation of China under Grant 62401075 and Grant 62394322 and in
part by the Xiong’an New Area Science and Technology Innovation Special
Project under Grant 2025XAGG0036. (Corresponding authors: Hao Hao;
Shukan Liu.)
Zan Zhou, Wei Dong, Xiping Li, Lin Yan, Shujie Yang, Xiaoyan
Zhang, and Changqiao Xu are with the State Key Laboratory of Networking and Switching Technology and the School of Computer Science
(National Pilot Software Engineering School), Beijing University of Posts and
Telecommunications, Beijing 100876, China (e-mail: zan.zhou@bupt.edu.cn;
weygo@bupt.edu.cn; lcp.byr@bupt.edu.cn; lin.yan@bupt.edu.cn; sjyang@
bupt.edu.cn; xiaoyan@bupt.edu.cn; cqxu@bupt.edu.cn).
Hao Hao is with the Key Laboratory of Computing Power Network and
Information Security, Ministry of Education, Shandong Computer Science
Center (National Supercomputer Center in Jinan), Qilu University of Technology (Shandong Academy of Sciences), Jinan 250202, China (e-mail:
haoh@sdas.org).
Shukan Liu is with the Naval University of Engineering, Wuhan 430030,
China (e-mail: liusk@seu.edu.cn).
This article has supplementary downloadable material available at
https://doi.org/10.1109/TCE.2026.3679035, provided by the authors.
Digital Object Identifier 10.1109/TCE.2026.3679035

Fig. 1. Overall architecture of network with NIDS in CIoT environments.

ecosystems
underpinning
next-generation
intelligent
systems—such as smart homes, edge-AI gateways and
wearable networks—has sharply increased both the scale and
diversity of network traffic. Meanwhile, numerous industry
reports indicate that CIoT environments are now subject
to increasingly complex and frequent attack campaigns,
including botnets formed by compromised devices, advanced
malware targeting embedded consumer systems, and newer
forms of intelligent adversarial attacks [1]. According to a
2025 report by cloud-native security firm Zscaler, IoT-based
malware attacks against government systems surged by 370%
in the past year, while mobile threats grew by 147% [2]. In
response to emerging network attack threats, AI-based NIDS
solutions have experienced rapid advancements, showcasing
robust generalization capabilities, exceptional detection
accuracy, and high efficiency [3]. Figure 1 illustrates the
overall architecture of the NIDS within the CIoT environment.
It can be observed that the NIDS performs intrusion detection
by monitoring and analyzing traffic destined for the IoT
network, thereby enabling the identification and blocking of
malicious traffic before it reaches the IoT environment.
A. Challenges From Intelligent Adversarial Attacks
Despite the increasing use of advanced AI-driven NIDS
in CIoT ecosystems [4], [5], these systems have also led
to the rise of more sophisticated intelligent adversarial
threats. Specifically, intelligent adversarial attacks introduce
a “resistance” phenomenon, similar to drug resistance in
biology. When facing AI-driven NIDS, attackers continuously
analyze and adapt to the defense strategies, refining their methods to bypass detection. Surveys on IoT-related adversarial
machine-learning vulnerabilities reveal that these attacks are
growing in complexity, yet there is still a significant need for
more effective solutions in CIoT settings [6].

1558-4127 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

4706

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

Fig. 2. The feature distributions and characteristic analysis of records from UNSW-NB15 [8], [9]. UNSW-NB15 is a public network intrusion detection
dataset with 10 types of malicious/benign network traffic records. The 2D visualization and bar graph on the left-hand side are depicted based on over 40000
(out of 2 million) randomly sampled records with 36 features. On the right-hand side, Here we only exhibit 4 types of attacks for simplicity.

In order to provide a lucid demonstration of the viability
of intelligent attacks, we perform a straightforward analysis
using the well-established intrusion detection UNSW-NB15
dataset [7], as illustrated in Figure 2. It can be observed that,
due to diverse attack paradigms, such as Shellcode and DoS
attacks, malicious records exhibit considerable heterogeneity
among themselves, thereby providing ample opportunity for
intelligent adversaries to exploit. Attackers can adjust malicious traffic to circumvent defensive strategies.
B. Contributions
To address the limitations of existing NIDS technologies
when facing advanced intelligent adversaries, we propose a
novel TM-MTD approach that simultaneously mutates access
routes, IP addresses, and defense strategies. This method
reduces the ability of intelligent attackers to infer defense
strategies by reinforcing the defense tactics themselves.
As traffic from smart appliances and consumer IoT devices
typically passes through multiple proxy or edge nodes before
reaching backend services, our method introduces mutations
along this routing path, adding an extra layer of uncertainty
and disrupting long-term adversarial inference.
Specifically, this work offers contributions in three main
aspects:
• First, we systematically analyze the authentic threat
posed by intelligent adversarial attacks to prevalent
traffic-oriented defense mechanisms. Subsequently, we
formulate the endogenous security criteria and establish
a hierarchical model for our NMTD framework.
• Next, employing the binary bionic Harris hawks optimization (HHO) algorithm as a foundation, we introduce a

streamlined edge-level adaptation mechanism. This mechanism efficiently determines the alternative feature set for
the defense strategy of each edge proxy node, ensuring
commendable detection accuracy against a spectrum of
traffic attacks.
• Lastly, we introduce a reinforcement learning (RL)-based
mechanism to maximize differentiation in the deployment
of defense strategies. This entails the development of
a novel actor-critic (AC) proximal policy optimization
(PPO) framework featuring multiple sub-actors to address
the challenge of dimension expansion in detecting abnormal traffic in more diverse CIoT network.
The paper is structured as follows: We commence with
a systematic review of related works in Section II. Then,
the threat model and framework of the proposed TM-MTD
solution are briefly illustrated in Section III and IV, respectively. Following that, Section V formulates the problem. In
Section VI, we provide a comprehensive depiction of our
hierarchical active defense solution. Section VII presents the
experimental results using representative datasets. Section VIII
discss the limitations and challenges of deploying TM-MTD.
Lastly, we conclude and outline potential future directions in
Section IX.
II. R ELATED W ORKS
Active defenses such as NMTD are introduced to proactively disrupt the initial phase of information gathering,
thereby enhancing protection against traffic-centric attacks in
IoT environments [10]. NMTD defenders strategically alter
the attack surfaces of target systems, rendering attacks theoretically ineffective [11]. As illustrated in Figure 3, existing
NMTD schemes often involve only two tiers of periodic

ZHOU et al.: PROACTIVE TRIPLE-MUTATION MTD ARCHITECTURE

4707

While existing defense mechanisms have made significant
strides in addressing intelligent attacks, they often focus
solely on increasing the complexity of intrusion detection
strategies. However, these approaches still face challenges in
dynamic and resource-constrained CIoT environments, where
high resource demands and the need for frequent system
updates limit their applicability. In contrast, the proposed
TM-MTD framework shifts the focus to enhancing dynamic
heterogeneity in defense strategies, incorporating simultaneous
mutations of access proxies, IP addresses, and security policies. This approach prevents attackers from converging on a
single defense strategy, ensuring long-term resilience.
III. T HREAT M ODEL

Fig. 3. The core idea of the proposed triple-mutation NMTD framework.

dynamic mutation, namely route redirection between users and
proxies and IP address hopping [12]. While effective against
conventional attack methods such as stealthy infiltration and
eavesdropping harvesting, these strategies have limitations.
Thus, solutions like [13], [14], [15] that employ fixed, singular
defense strategies are inadequate.
Given that the interaction between attackers and defenders
inherently aligns with the principles of game theory, numerous
game-based NMTDs have been developed [16], [17]. Reference [18] presents a Markov game–based defense timing strategy for moving target defense in satellite computing systems,
improving security efficiency under resource and traffic constraints. Reference [19] develops a four-stage attack–defense
game model that yields Nash-equilibrium secure control strategies to improve system resilience. However, as intelligent
adversarial attackers deepen their understanding of defense
systems, the generated adversarial samples evolve through iterative learning, making it extremely challenging and impractical
to clearly characterize attack strategies in advance. Consequently, prior knowledge-supported methods such as game
theory [20], [21] are not applicable.
Recent advancements in artificial intelligence have significantly enhanced the ability to counter intelligent attacks [22].
AI has been increasingly utilized to improve the performance
of NIDS by boosting detection accuracy and efficiency. For
instance, [23] presents a knowledge distillation-based framework for NIDS that achieves similar performance with reduced
complexity, size, and inference time. Similarly, [24] introduces
a method for smart-home network intrusion detection using
graph attention and SHAP for feature selection.
AI also strengthens the adaptability and intelligence of
moving target defense architectures [25]. For example,
[26] proposes a reinforcement learning-based framework to
enhance the resilience of defense agents against adversarial
attacks, while [27] uses reinforcement learning with behavioral
fingerprinting to guide the selection of MTD techniques
against heterogeneous malware on single-board devices.

In this paper, therefore, instead of introducing more complex
security technologies or defense architectures, we strengthen
the dynamism of the NMTD defense strategy so that intelligent
adversarial attacks, which rely on reasoning and adaptive
countermeasures, are substantially hindered in inferring the
underlying defensive mechanisms. Intelligent attackers leverage AI technologies, such as deep learning and reinforcement
learning, to enhance their inferential abilities, generating highprecision attack samples that can bypass defense systems
through prolonged attack-defense interactions.
A. Signals for Inference
Intelligent attackers rely on observable feedback signals to
infer defense strategies, including binary detection feedback,
confidence score variations, attack success rates, and packet
loss patterns. These signals reveal the defender’s actions and
allow attackers to refine their strategies. For example, attackers
can track attack success rates over time to identify system
vulnerabilities.
B. Objective
Attackers aim to finely adjust the generated attack sample
xadv (i.e., malicious traffic data) based on the original attack
sample xorg through AI means to maximize the likelihood of
NIDS misclassifying malicious data, ultimately bypassing the
defense system.
C. Capability
Unlike adversarial examples in the field of computer vision,
network traffic features often have specific value ranges due to
the constraints of real network environments. Otherwise, the
attack may be invalid, which aligns with common knowledge.
Hence, we can depict this constraint as xorg − xadv p ≤ ,
where  denotes the upper bound of deviation between original and adversarial samples. The deviation is quantified by
p-norm.
D. Attacker Cost and Budget
The attacker iteratively refines adversarial samples based on
feedback signals, adjusting the attack strategy to bypass the
defense system. The cost of this iterative process is directly
tied to the complexity and adaptability of the defense. As

4708

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

Fig. 4. The structure and offense-defense confrontation of TM-MTD.

defenses become more dynamic and difficult to predict, the
attacker is forced to explore a larger space of potential configurations, resulting in higher computational costs and longer
convergence times. Thus, the effectiveness of the defense
system not only depends on its detection capabilities but also
on how resource-intensive it makes the attacker’s adaptation
process.
Based on the analysis presented above, we can define the
threat model of intelligent adversarial attacks addressed in this
paper as follows:
 
x̃adv = min L f xadv , y
s.t.

xadv
org

x

− xadv p ≤ ,

(1)

where y denotes the target label. f (·) represents the attackers’
model. L(·) is the loss function of victim NIDS.
IV. T HE OVERVIEW OF P ROPOSED M ETHOD
In response to the threats posed by intelligent adversarial
attacks, we propose an innovative secure framework known as
TM-MTD. The system leverages a hierarchical architecture,
as depicted on the left-hand side of Figure 4. The core
concept entails initiating defense adaptation at the edge level
to select optimal independent abstract features for constructing the mutation space of MTD. Subsequently, based on
cross-domain defense adaptation across the entire network,
it generates a defense strategy characterized by substantial
inner heterogeneity and robust detection performance. Consequently, when confronted with multiple intelligent adversarial
paradigms [28], [29], [30], the defense system is adept at
confusing sophisticated adversaries to the maximum extent
through shuffling, thereby impeding adversarial traffic samples
from bypassing defense measures through adversarial training.
This process encompasses the following sequential steps:
Step 1 (Data collection): Both flow-based and packet-based
information of traffic are collected from each proxy.
Step 2 (Feature extraction): Quantify and normalize the
features of network traffic to create NIDS feature matrices.
Step 3 (Edge-level defense adaptation): The defense
system conducts single-point feature optimization, further processing the initial feature set to form independent abstract

features. Based on HHO algorithm, it leverages DL models
(e.g., MLP, CNN, LSTM) to select advantageous features and
construct the mutation space of NMTD.
Step 4 (Global-level defense adaptation): Subsequently,
to enhance the system’s endogenous security, unlike existing
NMTDs focusing solely on single-point strategy optimization,
the defenders engage in network-wide differentiated strategy
generation. While ensuring excellent overall defensive performance, TM-MTD maximizes the diversity of defense strategies
to confuse intelligent adversaries, preventing the convergence
of adversarial sample models.
Step 5 (Strategy deployment): The heterogeneous defense
strategies are strategically allocated to each proxy to counter
intelligent deduction while maintaining robust and effective
performance during periodic shuffling.
Step 6 (Security awareness): Furthermore, we continuously monitor the network security posture and establish
a trigger threshold θ. If the situation changes beyond the
threshold (i.e., T hr > θ), the defense system will be triggered
and dynamically reconfigured, ensuring the adaptability and
resilience of the defense mechanism.
The TM-MTD mechanism effectively disrupts the consistency of feedback signals available to attackers by introducing
heterogeneous defense strategies, temporal instability, and
inter-proxy variability. Specifically, dynamic mutations of
access proxies, IP addresses, and defense strategies prevent
attackers from building stable models of the defense system,
hindering their ability to predict defensive actions and adjust
attack strategies accordingly. The diversity of defense strategies ensures attackers cannot generalize from one interaction
to the next, making it difficult for attackers to exploit consistent
patterns in the defense behavior.
V. P ROBLEM F ORMULATION
This section provides a concise clarification of TM-MTD’s
system model. Next, we formulate the problem based on
the Markov decision process (MDP) [31]. Consequently, the
task of selecting the optimal feature composition becomes
synonymous with finding the optimal policy within this
MDP. Since our proposal incorporates both malicious traffic
detection and endogenous security into its considerations,

ZHOU et al.: PROACTIVE TRIPLE-MUTATION MTD ARCHITECTURE

we enhance the accuracy of evaluating feature composition
(defense strategy) by incorporating augmented endogenous
security criteria when defining the reward function.
Figure 4 illustrates the fundamental structure and confrontation process of NMTD against malicious traffic initiated
by sophisticated attackers. In this setup, where the network
system channels service flows through multiple edge proxy
servers, adversaries begin by infiltrating spies (compromised
users or forged requests) to infiltrate and gather information
from the targeted proxies. Subsequently, these spies relay the
collected information, enabling the Botnet to weaponize the
malicious traffic and initiate the attack. Conversely, NMTD
defenders periodically reassign users among different proxies
while assessing the accumulated malice of each user over
time. This efficient strategy leads to the elimination of stealthy
spies after several rounds of interaction, rapidly depleting
the attackers’ resources and ultimately terminating the attacks
within a short timeframe.
Leveraging the proposed active defense architecture, which
prioritizes endogenous security enhancement while addressing
salience and variance objectives, we can cast the NMTD policy
optimization problem following MDP. We define a five-tuple
< S, A, P, R, γ > to represent this formulation: S signifies
the state space, A represents the action space, P denotes the
state transfer matrix, which characterizes the likelihood of the
current state S t ∈ S transitioning to the subsequent state S t+1,0
after the adoption of action At ∈ A at round t; R(S t , At )
denotes the reward function associated with the state-action
pair (S t , At ); and γ serves as a time discount factor, balancing
future and current rewards within the decision-making process.
A. State Space
To enable the mutation of defense strategies, time is divided
into slots represented by t ∈ [1, T ]. Each t represents the
smallest unit of time during which TM-MTD evaluates policy
earnings based on the current state of the defense system and
transitions to the next slot’s defense strategy.
The current state comprises three key components: the
adjacency matrix Dt , the global defense strategy deployment
F t , and the detection importance W t . This state is represented
as S t = (Dt , F t , W t ).
t
0
The first term, denoted as Dt = {di,i
0 |∀i, i ∈ N}, represents
the connection paths between proxy nodes. Here, 1 signifies
availability, while 0 signifies unavailability. Given the relative
stability of these connection relations despite different actions,
we simplify the analysis in subsequent sections by setting
t
0
di,i
0 = 1 for all i and i in N, and t in T .
The second term, denoted as F t = { fi,t j |∀i ∈ N, j ∈ M},
represents the present defense strategy, encompassing feature
selections for all proxies within the system at time slot t.
Specifically, fi,t j = 1 indicates that proxy i has chosen the
jth feature, while fi,t j = 0 signifies the opposite.
The third term, denoted as W t = {wti, j |∀i ∈ N, j ∈ M},
signifies the importance of features in detecting malicious
traffic. Each wti, j is a time-varying value within the range
[0, 1]. When wti, j is close to 1, it indicates that feature j holds
significant importance as a detection dimension. Conversely,
when wti, j deviates from 1, feature j becomes less relevant for
adversary identification.

4709

Additionally, taking into account the constrained sensing
and computational capabilities of network edge nodes in realworld scenarios, we impose restrictions on the number of
features that a single proxy can select as follows:
M
X

fi,t j ≤ Ci ,

∀i ∈ N

(2)

j=1

where M is the number of features in the optional feature set
and N denotes the number of proxy nodes.
B. Action Space
For each edge proxy server, the defender can adjust the
defense strategy Fit by adding, preserving, or removing one or
more features during time slot t. We denote these operations
as atomic actions 1, 0, −1, respectively. Consequently, the
TM-MTD action is represented as a multidimensional boolean
composite vector At = Ati , · · · , AtN for all t ∈ T . Here,
Ati = ati,1 , · · · , ati,M represents the malicious traffic detection
formula for proxy i, with each ati, j , where 1 ≤ i ≤ N and
1 ≤ j ≤ M, constituting an atomic action.
We denote the action space as A. Its size grows exponentially with the number of edge proxy servers and features,
reaching 3N×M , which is infeasible for large-scale network
traffic protection. Moreover, edge-side computational constraints and state conflicts introduce numerous illicit actions.
For instance, ati, j = 1 is invalid when fi,t j = 1, as a feature
cannot be selected twice. Section VI addresses these issues by
removing illicit actions and reducing action-space complexity
to ensure computational feasibility.
C. State Transition
The alterations in the feature composition of proxies are
construed as state transitions within the defense framework.
Given that the state at the next time slot, denoted as S t+1 ,
solely depends on the current state, S t , and the action taken,
At , this transition process possesses the Markov property. Consequently, we represent the probability of this state transition
as Pr(S t+1 , Rt+1 |S t , At ). To illustrate, consider a scenario with
a single-proxy system encompassing three feature dimensions,
where the current strategy deployment is F t = 0, 1, 1. In
the event that action At = 1, 0, −1 is executed, the resulting
strategy deployment becomes F t+1 = F t + At = 1, 1, 0. This
At

sequence is succinctly denoted as S t → S t+1 , Rt+1 , encapsulating the state transition and the associated reward.
Nonetheless, despite the deterministic nature of the transition rules governing F t , the presence of the dynamic variable
W t renders the state transition of TM-MTD’s S t inherently
non-deterministic. Consequently, in the subsequent section,
we propose the utilization of a Reinforcement Learning
(RL)-based mechanism to address this inherent uncertainty.
D. Endogenous Security-Involved Reward Function
The reward function represents the security profit of defenders with a particular state-action pair. maximizing the average
reward for the whole process is the ultimate goal of optimization problems. As TM-MTD jointly requires high detection

4710

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

accuracy against malicious traffic and endogenous security
of the defense system itself, we define the reward function
Rtπ (S t , At ) as the sum of total strategy salience and global
strategy difference, which can be denoted as Gg (S t ) and
Gd (S t ), respectively.
Since the features are not completely independent from each
other, we decoupled the correlation between the features of the
original dataset using Independent Component Analysis (ICA)
before calculating the salience of each feature.
The global difference is calculated using the Pearson Correlation Coefficient of the proxy nodes’ deployment features.
Pearson Correlation measures the linear relationship between
two variables, ranging from -1 (perfect negative correlation)
to 1 (perfect positive correlation), with 0 indicating no correlation. Since we aim to maximize the uncorrelation between
defense strategies, the goal is to minimize this coefficient. The
details are as follows:
N

Gd (S t ) = 1 −

N

XX
1
|ρ(sti ∗ wti , stj ∗ wtj )|
N(N − 1)
j=¬i

(3)

i=1

where ρ(X, Y) is the Pearson correlation coefficient between
X and Y.
The strategy salience index, denoted as Gg (S t ), quantifies
the cumulative salience of the deployed features. It is defined
as follows:
N
M
1 XX t
si, j · wti, j ,
Gg (S t ) =
NM

(4)

all proxies in the system, aimed at countering the impact of
intelligent attacks.
"
#
X
 0
∗
t
t
t
t
π = arg maxπ E
ζ R S , A | S = s, A
(6)
t∈T

where A ∼ π · | S , ζ represents the discount factor. It is
important to note that ζ serves a different purpose compared to
the previously discussed weighting parameter λ, as it controls
the emphasis on future rewards in the optimization process,
while λ governs the trade-off between different objectives in
the defense strategy.
t

t



F. Problem Formulation
Considering the dual security perspectives inherent in
TM-MTD, the optimization problem aimed at finding the optimal solution for defense strategy deployment can be formally
defined as:
" ∞
#
X
t
t+τ
τ
τ
Maximize : Eπ
ζ R(S , Aπ ) | S ∈ S
t=0

Subject to :

M
X

fi,t j ≤ Ci ,

j=1
fi,t j ∈ (0, 1),

∀i ∈ N
∀i ∈ N,

j∈M

(7)

VI. H IERARCHICAL D EFENSE F RAMEWORK

i=1 j=1

where wti, j signifies the salience (detection accuracy) of the jth
feature on the ith proxy at round t, with values in the range
of [0, 1]. A higher value of Gg (S t ) indicates that the defense
strategies of proxy servers are more precise and effective in
eliminating malicious spies.
Hence, the ultimate composite reward can be formulated
through the weighted synthesis of equations (3) and (4),
expressed as:
Rt (S t , At ) = (1 − λ) · Gtg + λ · Gtd − R̃br

(5)

where λ ∈ [0, 1] serves as an adaptable weight parameter that
harmonizes the objectives of endogenous security enhancement and detection performance optimization. R̃br is the base
reward. Subtracting base reward is one of the common practices in reinforcement learning that can improve the stability
and effectiveness of training. If the reward is kept positive, it
may lead to an over-concentration of the reward signal, making
the training unstable. In our setup, base reward is defined as
the top 20% of the randomly generated strategies.
E. Optimization Goals
The primary objective of the defense strategy is to enhance
the accuracy and efficiency of detection and elimination of
malicious traffic. In essence, the selected features should maximize the evaluation scores of attacker malice while minimizing
those of normal users. Here, we utilize π(At |S t ) to denote the
probability of selecting an action At (i.e., a defense strategy)
in a given state S t . The secondary optimization goal is to
maximize the overall disparity among defense strategies across

In this section, we provide a comprehensive exposition of
the TM-MTD framework. The proposed hierarchical active
defense framework comprises two key layers: an edge-level
feature selection layer, which focuses on optimizing detection
salience at the individual edge proxy nodes, and a global
strategy adaptation layer, which seeks to bolster the system’s
inherent security by maximizing strategy disparities among the
proxy nodes.
A. Edge-Level Defense Adaptation
The growing complexity of network services and advances
in network-awareness technologies have dramatically
expanded traffic feature dimensions, many of which are
irrelevant or ineffective for detection. Thus, an effective
defense strategy must begin with a suitable feature extraction
or selection mechanism.
In the CIoT environment, each proxy node must adaptively
select an effective set of traffic features under limited computational resources and in response to dynamically evolving attack
behaviors. This presents a high-dimensional, non-convex feature selection problem, which is well-suited to HHO due to its
strong exploration capability, fast convergence, and low computational overhead. Compared to Genetic Algorithms (GA),
Particle Swarm Optimization (PSO), and traditional greedy
methods, HHO offers significant advantages. It converges more
quickly by balancing exploration and exploitation effectively,
while also reducing computational complexity. In contrast, GA
and PSO are prone to slower convergence and local minima,
and greedy methods lack the global search capability needed
for high-dimensional problems.

ZHOU et al.: PROACTIVE TRIPLE-MUTATION MTD ARCHITECTURE

4711

In our system, each HHO agent represents a candidate
defense configuration, i.e., a specific subset of traffic features
activated for intrusion detection at an edge proxy. The position of an agent corresponds to a concrete feature-selection
strategy, and the population collectively explores alternative configurations to avoid easily inferable defenses. The
exploration–exploitation mechanism of HHO maps naturally to
defensive behaviors: global exploration encourages proactive
diversification of feature sets to resist intelligent adversarial
probing, while local exploitation refines high-performing configurations that exhibit strong detection salience.
We have orchestrated the deployment of a cohort of Q
agents, each responsible for periodic updates to their respective
solutions denoted as Xqt , q ∈ Q, working collectively towards
the attainment of the optimal outcome. To commence this
collaborative effort, we initialize two critical parameters: the
escape energy E and the escape probability f . The energy term
E characterizes the intensity of defense strategy adjustment,
that is, the tendency of an edge node to actively explore
alternative feature-selection configurations rather than merely
refining its current strategy. Notably, f is a stochastic variable
that assumes values within the range of 0 to 1. Over the
course of iterations, the escape energy E undergoes dynamic
adjustments, as defined by the equation:

t
,
E = 2E0 1 −
T

Algorithm 1 Edge-Level Defense Adaptation (EDA)

(8)

where t signifies the current time slot, T corresponds to the
maximum iteration rounds, and E0 ∈ [−1, 1] stands for the
initial energy value, where specifically, E0 = 2 f − 1. Here,
t refers to the time slot in the HHO iteration process for
selecting the most optimal feature set, which has a different
meaning from the t used to represent the number of rounds in
the MDP model discussed earlier.
1) Global Search and Partial Exploration Phases: Based
on the varying values of E, the HHO algorithm operates
through the Global Search and Partial Exploration phases.
The details of these two phases, including the associated
mathematical formulations, are provided in Appendix A (see
Supplementary Material). These equations describe how the
solutions Xqt of each agent are updated to Xqt+1 in the HHO
algorithm.
2) Edge-Level Defense Adaptation (EDA) Algorithm:
Based on the final outcome achieved after T iterations, defenders can assess the significance of each feature and choose those
feature dimensions where the result equals 1. Consequently,
a candidate feature set is established for formulating the
maliciousness elimination formula through a novel edge-level
salience optimization algorithm denoted as EDA. The pseudocode for EDA is presented in Algorithm 1.
To determine the significance of each feature dimension
for the edge server, EDA employs a metric called salience
denoted as W, which is calculated as W = 1 − acc, where
acc represents the accuracy obtained after removing specific
feature during the training process. Subsequently, utilizing the
calculated detection importance for each feature, a subset of
features is generated to serve as the candidate defense strategy
space for the proxy.

B. Endogenous Difference Maximization Mechanism of
Global Strategy Deployment
In this section, we introduce an RL-based mechanism
aimed at enhancing global endogenous security throughout
the deployment of defense strategies. However, the issue of
dimensionality, often referred to as the curse of dimensionality, presents a significant challenge, making it impractical
to directly employ established RL methods such as PPO in
the context of NMTDs. To address the challenge posed by
the rapidly growing complexity in feature selection, we have
devised two distinct modules with specific responsibilities: one
for reducing the action space and the other for facilitating
action selection.
1) Sparse and Illicit Problems of Action: Building upon
the MDP model elucidated in Section V, it is theoretically
plausible to employ the widely adopted PPO algorithm for the
optimization of defense strategy deployment. However, two
critical issues have emerged from this approach.
Firstly, each feature associated with an edge proxy entails
three atomic actions, represented as ai, j ∈ −1, 0, 1. This results
in an action space whose size is exponentially related to the
product of the edge proxy servers and the total number of
features, potentially reaching as high as 3N×M . Consequently,
model training consumes a substantial amount of computational resources and time.
Secondly, a significant number of illicit actions have been
identified. To illustrate, consider a scenario with three features
on a proxy. If the state at time t is F t = 0, 0, 1, with
a constraint of C1 = 1 allowing up to one feature to be
deployed on this edge proxy, there exist illicit actions such
as At1 = −1, 0, 0 and At2 = 1, 0, 0. The former erroneously
attempts to remove the non-existent 1 st feature, while the latter

4712

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

violates the constraint by transforming F t to F t+1 = 1, 0, 1.
These illicit actions consume redundant resources, impeding
model training efficiency. Consequently, a direct application
of the PPO algorithm is deemed impractical.
2) Action Space Reduction Module: In our system model
(as elaborated in Section V), it’s noteworthy that each action
is a composite of individual sub-actions denoted as ati, j .
Consequently, our approach deviates from the selection of
actions from the set A; instead, we form a comprehensive
action by aggregating these pertinent sub-actions.
Additionally, upon reexamining the reward formulation, we
observe that the reward is not determined by the specific action
type (i.e., addition, retention, or removal), but rather by the
system states before and after action execution, as discussed in
[32]. Accordingly, we redefine the action representation such
that an action ati, j indicates whether feature j is deployed on
edge proxy server i (ati, j = 1) or not (ati, j = 0). This reformulation substantially reduces the dimensionality of the action
space from 3N×M to N × M, while completely eliminating
the first category of invalid actions, thereby improving both
tractability and training stability.
3) Sub-Action Selection Module: To address the second
challenge related to invalid actions, we design a sub-action
selection module that generates a feasible set of sub-actions
while explicitly respecting the computational resource constraint Ci at each edge proxy. This module employs neural
networks to output the probability distributions over all candidate sub-actions associated with each proxy.
It is worth noting that the reduction of the action space
fundamentally changes the action representation. Specifically,
at each time step t, the action is no longer a single atomic
decision but a set of sub-actions, to which the system reward
Rt is jointly assigned. This structural change necessitates corresponding modifications to both action selection and parameter
update mechanisms in the PPO framework.
The first enhancement concerns the action selection strategy.
In standard PPO, actions are sampled directly from a policy
distribution. In our setting, the proposed sub-action selection
module is used to construct a valid sub-action set that satisfies
resource constraints, generating an optimal and executable
defense configuration for each edge proxy.
The second enhancement focuses on parameter updates.
Although the executed action At is a sub-action set, the
policy parameters are associated with individual sub-actions
ati, j . In conventional PPO, the transition tuple (S t , At , p(At |
S t ), Vµ (S t ), Rt ) is stored for policy and value updates, where
Vµ (S t ) denotes the Critic output. However, the reward Rt
assigned to the entire set At cannot be directly used to update
each constituent sub-action. To resolve this issue, we introduce
a scaling mechanism that allocates rewards ri,t j and value
estimates vti, j to individual sub-actions in proportion to their
selection probabilities. The exact formulations of this scaling
process are presented below.
p(ati, j |S t )
Rt
ri,t j = P
t)
p(a|S
t
a∈A
p(ati, j |S t )
t
vi, j = P
V (S t )
t) µ
p(a|S
t
a∈A

(9)

Consequently, the updates for all ati, j ∈ At are consolidated.
To clarify, the GDA involves multiple updates for a sequence
of sub-actions within an episode, rather than performing
individual updates for each action.
Next, we are tasked with determining the sub-action
composition—namely, the features—for each edge proxy. The
process begins by transforming the one-dimensional array of
all sub-action selection probabilities generated by the neural
network into a two-dimensional array p(ati, j |S t ). The selection
probability for each feature j on proxy i is normalized through
Eq. (10):
p(ati, j |S t )
, i ∈ {1, . . ., N}
p(ati, j |S t ) = P M
t
t
j=0 p(ai, j |S )

(10)

Thus, based on the computed probabilities, we proceed to
select Ci features from the total M options for the composition
of features on proxy i. The culmination of these iterations
yields the complete action At .
4) Global Defense Adaptation (GDA) Algorithm: Subsequently, we amalgamate the aforementioned modules to
formulate our multi-update sub-action PPO algorithm aimed
at global difference maximization.
The core of GDA lies in Generalized Advantage Estimation
(GAE), which more accurately estimates the advantage of
a given action relative to the expected outcome. The GAE
formula computes the weighted sum of time-difference errors
over future steps, allowing the system to incorporate both
immediate and future rewards. This helps improve training
stability by reducing variance in advantage estimates. GAE is
calculated as follows:
Ĥt = δt + (γξ)δt+1 + (γξ)2 δt+2 + · · · + (γξ)B−t−1 δB−1 ,

(11)

where B signifies the size of the experience replay memory, γ
represents the discount factor within the range of 0 to 1, ξ is
a pre-defined GAE parameter, and δt is the Time-Difference
Error (TD-Error), defined as follows:
t
δt = ri,t j + γvt+1
i, j − vi, j .

(12)

δt is computed as the difference between the reward at time t
and the predicted value of the system’s state. This error helps
to evaluate how much better or worse the system’s current
action was compared to the expected action. The goal is to
minimize this error, ensuring that the system’s actions lead to
better long-term outcomes.
The definition of the loss function J actor for the Actor
network can be expressed as:


(13)
Jθactor = E min rθt Ĥt , clip(rθt , 1 − , 1 + )Ĥt ,


pθ ati, j |S t
t

 , similar to vt . πθ is updated using the
where rθ =
pθold ati, j |S t

stochastic gradient descent (SGD) method, where the gradient
is the negative of ∇Jθactor .
The loss function J critic for Critic network is defined as:


J critic (µ) = E (V̂treturns − Vµ (S t ))2 ,
(14)
where the parameters of the target value V̂treturns for the
TD-Error are determined as Ĥt +vt , and Vµ is updated utilizing
the gradient ∇J critic (µ).

ZHOU et al.: PROACTIVE TRIPLE-MUTATION MTD ARCHITECTURE

Algorithm 2 Global Defense Adaptation (GDA)

4713

the experience replay memory, a probability distribution step
has also been incorporated.
Within each episode k, the initial state is reset to S 0 .
Subsequently, during each epoch t, we employ the strategy πθold
and the current state S t to generate action At . This includes
determining the selection probability p(ati, j |S t ) for each subaction ati, j ∈ At , as well as estimating the state value Vµ (S t )
through the Critic network.
After executing each sub-action ati, j ∈ At , we observe the
resultant state S t+1 and the corresponding reward Rt . For
each sub-action ati, j ∈ At , we calculate the reward ri,t j and the
value vti, j in accordance with formula (9), while considering
the
probabilities.
This information is stored as
˝ t associated
˛
S , ati, j , p(ati, j |S t ), vti, j , ri,t j in the experience replay memory
denoted as B. Subsequently, we perform B random sampling
operations from B to compute the gradients for both the Actor
and Critic networks.
VII. P ERFORMANCE E VALUATION
In this section, we conduct a comprehensive evaluation of
the security performance of our proposed TM-MTD solution. We begin by providing a detailed exposition of the
experimental setup. Next, we conduct training convergence
and stability experiments, followed by an analysis of the
weighting parameter λ selection. We then evaluate the defense
performance of our TM-MTD methodology against a series
of baselines, followed by an ablation study to validate the
contributions of each mutation component. Finally, we perform
latency experiments under varying numbers of proxies to
assess the scalability of the system.
A. Experimental Environment

Fig. 5. The architecture of GDA’s training process.

The loss function for the Actor network is designed to
optimize the policy by encouraging actions that lead to higher
rewards while maintaining stability in learning. The Critic
network evaluates the state value function, helping to improve
the accuracy of the reward predictions. The combination of
these two networks enables the system to both select the best
actions and accurately predict the outcomes of those actions.
The pseudo-code detailing the proposed global difference
maximization algorithm is presented in algorithm 2.
5) The Architecture of GDA’s Training Process: As
depicted in Figure 5, our GDA architecture has been extended
to accommodate sub-action selection and iterative updates
within the training process. Specifically, we have introduced
an additional sub-action generation step into the Actor-Criticbased composite neural networks. Prior to storing samples in

To conduct a series of traffic active defense experiments,
we construct the testing environment based on a workstation
equipped with Intel i9-10940X CPU, 128GB RAM, two
RTX3090 24GB GPUs, and Windows 10-21H1 OS. All the
programs are realized based on Python 3.9 with PyTorch.
The experimental configuration comprises a primary server,
designated as the global control node, and a network of
ten accessible proxy servers functioning as edge nodes.
Our method’s efficacy is evaluated against benchmark intrusion detection datasets rooted in flow-based network traffic: UNSW-NB15 [7] and CICIoT2023 [33]. UNSW-NB15
encompasses an extensive collection of approximately 250,000
network traffic samples, characterized by a feature set of 49
attributes and the inclusion of 10 distinct attack paradigms. In
contrast, CICIoT2023 comprises over 680,000 network traffic
samples, distinguished by an feature space comprising 46
attributes and a comprehensive coverage of 7 distinct attack
categories.
B. Convergence and Training Stability Analysis
After the edge nodes identify satisfactory candidate feature
sets Fit , ∀i ∈ N, the RL-based GDA algorithm is initialized
at the control server and trained for K = 1000 episodes. The
batch size U is set to 256, the discount factor γ is 0.95, and
each update cycle includes eight gradient update iterations.

4714

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

Fig. 6. The training stability of the proposed algorithm.

Both the Actor and Critic networks use learning rates of
0.0003, with the PPO clipping parameter fixed at 0.2. A single
hidden layer with 512 neurons is employed for all networks.
All hyperparameters are kept identical across experiments to
isolate the impact of the adaptive parameter λ.
To examine convergence, training stability, and the sensitivity of the weighting parameter λ, we analyze the evolution of
defense salience, strategy difference, and cumulative reward
under different values of λ. As illustrated in Figures 6(a)
and 6(b), all tested configurations demonstrate stable convergence after an initial exploration phase, indicating that the
learning process does not suffer from divergence or oscillation. Among these configurations, λ = 0.15 leads to faster
convergence and achieves higher steady-state salience while
maintaining a sufficient level of global strategy differentiation.
As shown in Figure 6(c), the configuration with λ = 0.15
shows the fastest convergence and the most stable reward
plateau, with reduced variance in the later stages of training
compared to other values of λ. Overall, these results indicate
that the proposed GDA algorithm converges reliably across
different parameter settings, with λ = 0.15 offering an optimal
balance between convergence speed, stability, and long-term
performance.

Fig. 7. The attack success rate against different NMTDs.

Fig. 8. The proxy-specific accuracy degradations against intelligent attacks.

C. Evaluation of Defense Performance
To further examine the general defense performance of
TM-MTD against different intelligent adversaries, we compare
the performance of TM-MTD with other types of NMTD technologies: Dynamite defense [34], randomly selected solution
[35] and static optimal solution [36]. The random approach
utilizes randomly generated defense strategies alongside agent
switching, while the static approach deploys the best defense
strategy for each proxy after RL. The Dynamite method uses
dynamic strategy adjustment based on adversarial feedback.
Besides, we also launch three intelligent adversarial attacks,
including both glass box and closed box paradigms. The
adopted adversarial attacks include boundary attack [28], EAD
attack [30] and LInfFMN attack [29].
We evaluated four defense methods—Our Method, Dynamite, Random, and Static—across three different adversarial
attack types: Boundary Attack, EAD Attack, and LInfFMN
Attack under the UNSW-NB15 and CICIoT2023. The
attacker’s attack success rate (ASR) was used as the key
metric, and the results are shown in Figures 7.
The results demonstrate that our proposed method consistently achieves the lowest attack success rate in all six
attack-defense configurations. Notably, our method significantly reduced the LInfFMN attack success rate to 4.76%
under the CICIoT2023 dataset. While a brief fluctuation in

attack success rate above the Dynamite and Random methods
was observed for Boundary Attack against our method, the
value remained within an acceptable range.
Among all attack types, EAD attacks proved to be the most
effective, achieving an attack success rate of 83.6% against
the Static defense method. In contrast, our method reduced the
EAD attack success rate to 63.4%, the lowest among the four
defense strategies, highlighting the superiority of our approach
in handling strong adversarial attacks.
These results underscore the effectiveness of our method in
mitigating a wide range of adversarial attacks, and its strong
performance even under challenging scenarios with higherdimensional datasets and more sophisticated attack types.
The heatmaps in Figures 8 continue to depict the varying
impact of attacks on different proxy nodes. We define accuracy
loss as the metric for evaluating defense strategies, calculated
by subtracting the accuracy under adversarial attacks from the
original accuracy of the NIDS model. Under the Boundary
and LInfFMN attacks, the four defenses exhibit relatively
balanced Accuracy Loss. Notably, the EAD attack results in
significantly high accuracy loss for some of the proxy nodes
where our strategy is deployed, in some cases even surpassing
or closely approaching the losses observed with the other two
methods. However, its overall defensive performance remains
substantially superior to other approaches. This underscores

ZHOU et al.: PROACTIVE TRIPLE-MUTATION MTD ARCHITECTURE

TABLE I
R ESULTS OF THE A BLATION S TUDY

Fig. 9. The everage delay under different numbers of proxies.

the strength of our defense, emphasizing that it does not rely
solely on the absolute superiority of a single strategy but leverages multiple diverse defense tactics to collectively confound
attackers, thereby establishing long-term resilience. Detailed
experiments on accuracy loss are presented in Appendix B
(see Supplementary Material).
D. Ablation Study on the Impact of Mutation Components
To better understand the individual contributions of each
mutation component in our proposed TM-MTD framework,
we conducted an ablation study by progressively removing
the three mutation components: IP mutation, route mutation,
and strategy mutation. The experiments were conducted using
the most powerful of the three attacks, the EAD attack. The
results of this experiment, including the ASR and accuracy
loss, are summarized in Table I.
The ablation study results demonstrate that each mutation component contributes to the overall performance of
TM-MTD. Removing the strategy mutation results in the
largest increase in both ASR (83.3%) and accuracy loss
(63.3%), highlighting the critical role of strategy mutation
in preventing attackers from converging on a single defense
strategy. The removal of IP and route mutations also leads
to increases in ASR and accuracy loss, but to a lesser extent,
emphasizing their importance in enhancing defense robustness.
The full three-mutation setting yields the best defense
performance with an ASR of 63.3% and an accuracy loss of
46.3%. These results confirm the superiority of our method,
with each mutation playing a significant role in balancing
attack success rate and accuracy loss. More detailed experimental results can be found in Appendix C (see Supplementary
Material).
E. Impact of Proxy Number on Average Delay
We conducted an experiment to evaluate the impact of
varying the number of proxies on the average delay for
four aforementioned defense methods. The results, illustrated
in Figure 9, show that as the number of proxies increases

4715

from 6 to 10, the average delay for all four methods also
increases. This increase is expected as the additional proxies
introduce more network overhead and require more time for
communication and feature processing.
Notably, our method and Dynamite exhibit slightly higher
delays compared to the Random and Static methods for the
same number of proxies. However, the incremental increase in
delay is relatively small, approximately 5 milliseconds, which
is within an acceptable range for most real-time systems. This
suggests that while our method may introduce some overhead
due to its dynamic nature, it remains efficient and practical for
CIoT environments, where system responsiveness is crucial.
Furthermore, the experiment demonstrates that the proposed
method maintains reasonable scalability with respect to the
number of proxies. The increase in delay remains moderate
even as the number of proxies grows, indicating that our
method can handle larger-scale deployments effectively. This
scalability is crucial for ensuring that the defense mechanism
can be deployed in diverse CIoT settings with varying numbers
of edge proxies, without compromising system performance to
an unacceptable extent.
VIII. L IMITATIONS
While the proposed TM-MTD framework offers enhanced
protection against intelligent adversarial attacks, its deployment in CIoT environments presents several practical challenges. Although experiments have shown that the overhead
of TM-MTD is generally minimal and within an acceptable
range, it is important to consider that CIoT devices are
typically resource-constrained. In highly complex scenarios,
this may lead to more noticeable delays, particularly for lowend devices with limited processing power.
Failure modes include the diminishing returns of frequent
mutations under extreme attack scenarios. While TM-MTD
improves defense adaptability, excessively high mutation frequencies can lead to less effective defense over time as the
system suffers from excessive overhead. Additionally, the
use of dynamic IP hopping may complicate log auditing
and forensic analysis, raising concerns about traceability and
transparency, which are critical in regulated environments.
Ethically and operationally, the heterogeneity of defense
strategies in TM-MTD may introduce operational complexity,
especially when managing diverse CIoT devices. Ensuring
compatibility and efficient operation across heterogeneous
devices with different capabilities can increase the administrative burden for network operators. These challenges must be
carefully managed to maintain the reliability and transparency
of the system while providing robust security.
IX. C ONCLUSION
This article proposes a novel triple-mutation network
moving target defense solution with endogenous security
enhancement, designed to counter and suppress the increasingly diverse and sophisticated intelligent attacks emerging
in CIoT environments. To reinforce defense systems’ ability
to resist exploitation without compromising performance, our
hierarchical TM-MTD architecture integrates a lightweight
bionic algorithm at each edge node. This self-adaptive mechanism efficiently extracts defense strategies while ensuring

4716

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

minimal resource usage. Moreover, we utilizes a sub-action
reinforcement learning mechanism to manage the strategic deployment across edge nodes, thereby enhancing the
long-term effectiveness of the defense architecture in highly
dynamic CIoT networks. Experimental results on benchmark
intrusion detection datasets and IoT datasets also highlight that
the TM-MTD solution can significantly enhance the resistance
against multiple intelligent adversarial attacks.
R EFERENCES
[1]

Y. Jia et al., “Analyzing consumer IoT traffic from security and privacy
perspectives: A comprehensive survey,” Frontiers Comput. Sci., vol. 20,
no. 7, Jul. 2026, Art. no. 2007809.
[2] Zscaler ThreatLabz. (2025). Mobile, IoT, and OT Risks Converge in the
Public Sector. [Online]. Available: https://www.zscaler.com/mx/blogs/
security-research/mobile-iot-and-ot-risks-converge-public-sector
[3] H. Dong and I. Kotenko, “Cybersecurity in the AI era: Analyzing the
impact of machine learning on intrusion detection,” Knowl. Inf. Syst.,
vol. 67, no. 5, pp. 1–52, May 2025.
[4] J. Li, M. S. Othman, H. Chen, and L. M. Yusuf, “Optimizing IoT
intrusion detection system: Feature selection versus feature extraction
in machine learning,” J. Big Data, vol. 11, no. 1, p. 36, Feb. 2024.
[5] S. B. Sharma and A. K. Bairwa, “Leveraging AI for intrusion detection
in IoT ecosystems: A comprehensive study,” IEEE Access, vol. 13,
pp. 66290–66317, 2025.
[6] H. Khazane, M. Ridouani, F. Salahdine, and N. Kaabouch, “A holistic
review of machine learning adversarial attacks in IoT networks,” Future
Internet, vol. 16, no. 1, p. 32, Jan. 2024.
[7] N. Moustafa and J. Slay, “UNSW-NB15: A comprehensive data set for
network intrusion detection systems (UNSW-NB15 network data set),”
in Proc. Mil. Commun. Inf. Syst. Conf. (MilCIS), Nov. 2015, pp. 1–6.
[8] N. Moustafa, J. Slay, and G. Creech, “Novel geometric area analysis
technique for anomaly detection using trapezoidal area estimation on
large-scale networks,” IEEE Trans. Big Data, vol. 5, no. 4, pp. 481–494,
Dec. 2019.
[9] M. Sarhan, S. Layeghy, N. Moustafa, and M. Portmann, “NetFlow
datasets for machine learning-based network intrusion detection
systems,” in Proc. 10th EAI Int. Conf., 13th EAI Int. Conf. Wireless
Internet (WiCON), 2021, pp. 117–135.
[10] Z. Rehman, I. Gondal, M. Ge, H. Dong, M. Gregory, and Z. Tari,
“Proactive defense mechanism: Enhancing IoT security through
diversity-based moving target defense and cyber deception,” Comput.
Secur., vol. 139, Apr. 2024, Art. no. 103685.
[11] Swati, S. Roy, J. Singh, and J. Mathew, “Securing IIoT systems against
DDoS attacks with adaptive moving target defense strategies,” Sci. Rep.,
vol. 15, no. 1, p. 9558, Mar. 2025.
[12] Z. Li, Z. Zhou, T. Zhang, and X. Xing, “MARL-MOTAG: Multi-agent
reinforcement learning based moving target defense to thwart DDoS
attacks,” in Proc. Int. Conf. Netw. Netw. Appl. (NaNA), Dec. 2022,
pp. 316–321.
[13] Y. Zhou, G. Cheng, Z. Ouyang, and Z. Chen, “Resource-efficient lowrate DDoS mitigation with moving target defense in edge clouds,”
IEEE Trans. Netw. Service Manage., vol. 22, no. 1, pp. 168–186,
Feb. 2025.
[14] M. Torquato, P. Maciel, and M. Vieira, “Evaluation of time-based virtual
machine migration as moving target defense against host-based attacks,”
J. Syst. Softw., vol. 219, Jan. 2025, Art. no. 112222.
[15] M. A. Ribeiro, M. S. P. Fonseca, and J. de Santi, “Detecting and
mitigating DDoS attacks with moving target defense approach based
on automated flow classification in SDN networks,” Comput. Secur.,
vol. 134, Nov. 2023, Art. no. 103462.
[16] Y. Tang, J. Sun, H. Wang, J. Deng, L. Tong, and W. Xu, “A method of
network attack-defense game and collaborative defense decision-making
based on hierarchical multi-agent reinforcement learning,” Comput.
Secur., vol. 142, Jul. 2024, Art. no. 103871.

[17] M. Bose, P. Paruchuri, and A. Kumar, “Adaptive moving target defense
in web applications and networks using factored MDP,” in Proc. 17th
Int. Conf. Commun. Syst. Netw. (COMSNETS), Jan. 2025, pp. 602–613.
[18] L. Zhang, Y. Guo, S. Leng, X. Cao, F. Li, and L. Fang, “Defense timing
selection for MTD in periodic satellite computing systems: A Markov
game approach,” J. Comput. Sci., vol. 87, May 2025, Art. no. 102583.
[19] D. Du, Y. Zhang, B. Xu, and M. Fei, “Optimal secure control of
networked control systems under false data injection attacks: A multistage attack-defense game approach,” IEEE/CAA J. Autom. Sinica,
vol. 12, no. 4, pp. 821–823, Apr. 2025.
[20] E. Nowroozi, M. Mohammadi, P. Golmohammadi, Y. Mekdad, M. Conti,
and S. Uluagac, “Resisting deep learning models against adversarial
attack transferability via feature randomization,” IEEE Trans. Services
Comput., vol. 17, no. 1, pp. 18–29, Jan. 2024.
[21] L. Jia et al., “Game theory and reinforcement learning for anti-jamming
defense in wireless communications: Current research, challenges, and
solutions,” IEEE Commun. Surveys Tuts., vol. 27, no. 3, pp. 1798–1838,
Jun. 2025.
[22] V. M. Baeza, R. Parada, L. Concha Salor, and C. Monzo, “AI-driven
tactical communications and networking for defense: A survey and
emerging trends,” 2025, arXiv:2504.05071.
[23] M. Umair et al., “Knowledge distillation for lightweight and explainable
intrusion detection in resource-constrained consumer devices,” IEEE
Trans. Consum. Electron., vol. 71, no. 4, pp. 12157–12165, Nov. 2025.
[24] M. Fu, P. Wang, S. Liu, X. Chen, and X. Zhou, “FIR-GNN: A
graph neural network using flow interaction relationships for intrusion
detection of consumer electronics in smart home network,” IEEE Trans.
Consum. Electron., vol. 71, no. 2, pp. 4892–4902, May 2025.
[25] T. Zhang et al., “Moving target defense meets artificial-intelligencedriven network: A comprehensive survey,” IEEE Internet Things J.,
vol. 12, no. 10, pp. 13384–13397, May 2025.
[26] R. Ebrahimi, Y. Chai, W. Li, J. Pacheco, and H. Chen, “RADAR:
A framework for developing adversarially robust cyber defense AI
agents with deep reinforcement learning,” MIS Quart., vol. 49, no. 4,
pp. 1385–1416, Dec. 2025.
[27] A. H. Celdrán et al., “RL and fingerprinting to select moving target
defense mechanisms for zero-day attacks in IoT,” IEEE Trans. Inf.
Forensics Security, vol. 19, pp. 5520–5529, 2024.
[28] W. Brendel, J. Rauber, and M. Bethge, “Decision-based adversarial
attacks: Reliable attacks against black-box machine learning models,”
2017, arXiv:1712.04248.
[29] M. Pintor, F. Roli, W. Brendel, and B. Biggio, “Fast minimum-norm
adversarial attacks through adaptive norm constraints,” in Proc. 35th
Conf. Neural Inf. Process. Syst. (NeurIPS), 2021, pp. 20052–20062.
[30] P. Chen, Y. Sharma, H. Zhang, J. Yi, and C. Hsieh, “EAD: Elastic-net
attacks to deep neural networks via adversarial examples,” in Proc. AAAI
Conf. Artif. Intell., vol. 32, no. 1, Apr. 2018, pp. 10–17.
[31] M. L. Puterman, “Markov decision processes,” in Stochastic Models,
Handbooks in Operations Research and Management Science, vol. 2.
Elsevier, 1990, pp. 331–434, doi: 10.1016/S0927-0507(05)80172-0.
[32] H. Hao, C. Xu, W. Zhang, S. Yang, and G.-M. Muntean, “Taskdriven priority-aware computation offloading using deep reinforcement learning,” IEEE Trans. Wireless Commun., vol. 24, no. 10,
pp. 8114–8128, Oct. 2025.
[33] E. C. P. Neto, S. Dadkhah, R. Ferreira, A. Zohourian, R. Lu, and
A. A. Ghorbani, “CICIoT2023: A real-time dataset and benchmark
for large-scale attacks in IoT environment,” Sensors, vol. 23, no. 13,
p. 5941, Jun. 2023.
[34] J. Chen, O. Gungor, Z. Shang, E. Li, and T. Rosing, “DYNAMITE:
Dynamic defense selection for enhancing machine learning-based intrusion detection against adversarial attacks,” in Proc. IEEE Secur. Privacy
Workshops (SPW), May 2025, pp. 213–219.
[35] A. Stavrou, D. Fleck, and C. Kolias, “On the move: Evading distributed
denial-of-service attacks,” Computer, vol. 49, no. 3, pp. 104–107, Mar.
2016.
[36] M. Wang, Y. Lu, and J. Qin, “A dynamic MLP-based DDoS attack
detection method using feature selection and feedback,” Comput. Secur.,
vol. 88, Jan. 2020, Art. no. 101645.
PAPER_TEXT
