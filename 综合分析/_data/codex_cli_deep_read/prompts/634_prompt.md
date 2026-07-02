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
# [634] Contrast Duality of Adversarial Learningin Network Intrusion: A Review
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
编号：634
题名：Contrast Duality of Adversarial Learningin Network Intrusion: A Review
年份：2025
DOI：10.1109/tai.2025.3641908
来源：IEEE Transactions on Artificial Intelligence
PDF：paper/10.1109_TAI.2025.3641908.pdf
已有粗分类：数据集、基准、综述与开源工具
二级关联：入侵检测与网络异常检测
相关性：中相关，分数 5
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\634.txt
- 原始字符数：106796
- 本次发送字符数：106796
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
3050

IEEE TRANSACTIONS ON ARTIFICIAL INTELLIGENCE, VOL. 7, NO. 6, JUNE 2026

Contrast Duality of Adversarial Learning
in Network Intrusion: A Review
Shalini Saini , Anitha Chennamaneni , and Babatunde Sawyerr

Abstract—AI-based solutions are instrumental in cybersecurity, harnessing their ability to analyze vast datasets, identify
complex patterns, and detect anomalies. However, attackers
can exploit these capabilities to plan and execute sophisticated
attacks, posing significant challenges to traditional security
measures. Adversarial attacks pose a concerning threat to cybersecurity, especially when targeting machine learning model
vulnerabilities. Adversarial learning exhibits a contrasting duality
in network intrusion detection, serving as both an advanced
offensive strategy for exploiting system weaknesses and a crucial
defensive tool for identifying and mitigating adversarial threats.
Our study presents an in-depth overview of focused adversarial
learning threats such as data poisoning, test time evasion, and
reverse engineering, and how adversarial training is applied as
a defense mechanism. The convergence of adversarial learning
attacks and defenses in network traffic data, alongside the
advancements in machine learning and deep learning techniques,
is still a relatively underexplored domain. Our research lays the
groundwork for strengthening defense mechanisms to address
the potential breaches in network security and privacy posed by
adversarial learning attacks. Through our in-depth analysis, we
identify domain-specific research gaps, such as the scarcity of
real-life attack data and the evaluation of AI-based solutions for
network traffic. Our focus on these challenges aims to stimulate
future research efforts toward the development of resilient AIbased defense strategies.
Impact Statement—Understanding the evolving nature of network intrusion attacks and defenses is paramount for organizations to proactively protect their networks, respond effectively
to security incidents, comply with regulations, foster innovation,
and continuously improve their cybersecurity practices in an
ever-changing threat landscape. Network intrusion attacks in
the healthcare, finance, and national security sectors can result
in compromised data privacy, financial losses, operational disruptions, threats to public safety, and national security risks.
Adversarial learning attacks and defenses are pivotal in securing
data and network operations by ensuring the reliability of outputs
from AI-driven cybersecurity applications. This review offers
a comprehensive analysis of adversarial learning attacks and

Received 17 July 2025; revised 24 September 2025 and 17 November 2025;
accepted 24 November 2025. Date of publication 9 December 2025; date of
current version 29 May 2026. This work was supported in part by the Air
Force Research Laboratory (AFRL) under Grant FA8750-23-C-0085. This
article was recommended for publication by Associate Editor Xiaoli Li upon
evaluation of the reviewers’ comments. (Corresponding author: Shalini Saini.)
Shalini Saini is with Texas A&M University-Central Texas, Killeen, TX
76549 USA (e-mail: shalini@umes.edu).
Anitha Chennamaneni is with Subhani Department of Computer Information Systems, Texas A&M University-Central Texas, Killeen, TX 76549 USA
(e-mail: anitha.chennamaneni@tamuct.edu).
Babatunde Sawyerr is with the Computer Science Department, University
of Lagos, Lagos 100213, Nigeria (e-mail: bsawyerr@unilag.edu.ng).
Digital Object Identifier 10.1109/TAI.2025.3641908

defenses, focusing on training, inference, and model analysis.
It provides an understanding of the dynamic nature of these
attacks, major threats and underscores the importance of ongoing research to strengthen network intrusion prevention and
detection through robust AI solutions.
Index Terms—Adversarial learning, artificial intelligence in
computer networks, artificial intelligence in cyber-security, deep
learning, machine learning.

I. INTRODUCTION

C

YBERSECURITY is critical in today’s interconnected
world, where cyber threats, such as malware, phishing,
ransomware, and data breaches, continue to evolve and pose
significant risks to individuals, organizations, and even national
security [5], [88]. The integration of embedded systems has
revolutionized critical sectors such as Healthcare, Automated
Vehicles, and National Defense, relying on advanced technology and data integrity for improved efficiency, safety, and security. Nonetheless, the integration has also exposed network
components more susceptible to cyber attacks and restricting
their practical and secure implementation [82], [115]. Current
trends indicate that approximately 67% of the world’s population has access to the internet, with social media platforms
playing a significant role in this accessibility [95]. However, this
increased connectivity has also expanded the attack surface for
adversaries, resulting in heightened cybersecurity threats. Notably, the economic impact of cyber attacks has grown substantially, with a global estimated loss of approximately $6 trillion
in 2021, doubling the costs recorded in 2015 [5]. Worldwide
end-user spending on security and risk management is projected to total $215 billion in 2024, an increase of 14.3% from
2023 [7].
The rapid progress in computational capabilities and the
utilization of big data have positioned machine learning as a
critical element in modern defense strategies. Nevertheless, the
susceptibility of ML/DL-based solutions to adversarial attacks
undermines current defense protocols. Developing adaptive defensive strategies that can effectively counter evolving threats
remains a persistent challenge [49]. Through our evaluation,
we identify the current research gaps in adversarial learning
pertaining to network intrusion detection systems (NIDS). Our
contribution lies in providing a baseline understanding of the
existing research breadth and presenting the potential future
directions in the field of ML/DL-based NIDS. The objective is
to facilitate the development of robust ML/DL-based NIDS that
effectively harness evolving technological capabilities, while

2691-4581 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

SAINI et al.: CONTRAST DUALITY OF ADVERSARIAL LEARNING IN NETWORK INTRUSION

3051

B. Our Contributions

Fig. 1. Data poisoning, test-time evasion, and reverse engineering adversarial learning attacks and defenses for ML/DL-based NIDS.

also demonstrating resilience against both known and emerging
security threats.

A. Research Objectives
Our work is driven by the growing need to understand the
influence of artificial intelligence (AI) methodologies, specifically, adversarial learning, and technological advancements on
innovative research and their practical implications for cybersecurity. To stay current and aligned with the evolving cybersecurity landscape and leverage emerging technologies, we aim
to achieve the following research objectives.
1) Presenting a taxonomy of adversarial learning, NIDS,
ML/DL techniques, attacker expertise, and NIDS datasets
to utilize in efficient adversarial attack and defense strategies.
2) Reviewing the existing research on employing adversarial
learning in data poisoning (DP), test-time evasion (TTE),
and reverse engineering (RE) attacks in network intrusion
domain.
3) Assessing available defense strategies against adversarial
attacks in NIDS, emphasizing their limitations and potential future directions.
As presented in Fig. 1, we explore ML/DL-based adversarial
attacks and defenses within the context of DP, test time evasion, and RE. Through analyzing these three key subdomains
in adversarial learning, we cover a comprehensive exploration
of adversarial attacks in machine learning from training data
manipulation to inference-time deception and model vulnerability analysis. We examine the various threats, attacks, and
possible defenses in which both attackers and defenders may
possess different levels of knowledge, such as white-box (full),
black-box (zero), and gray-box (partial) understanding of the
model, algorithm, and training data. DP can be instrumental in
training and test time evasion attacks. Similarly, RE can provide
significant details to sharpen the attacks. At the same time,
by analyzing the model’s vulnerabilities and threats to data
integrity, RE can be pivotal to develop robust defense mechanisms. Table I summarizes the primary categories of reviewed
attacks, their corresponding stages in the ML pipeline, and their
impacts on data and the model.

Our work provides a focused and in-depth review of adversarial learning within the context of network intrusion detection
systems (NIDS), specifically targeting three major subdomains:
1) DP; 2) TTE; and 3) model RE. We concentrate on the
network intrusion domain, where the implications of adversarial attacks are particularly severe and underexplored. We
explored the dual nature of adversarial learning, examining its application in both offensive strategies and defensive mechanisms under these subdomains of network intrusion
domain.
We systematically analyze research conducted between
2018 and 2024, capturing both foundational breakthroughs and
recent innovations. This timeframe allows us to review the
latest developments in the field and track how it has progressed. By synthesizing findings across these three attack vectors, we identify persistent vulnerabilities, evaluate the robustness of existing defenses, and highlight emerging trends and
gaps.
1) Comprehensive Analysis: We provide a detailed review
of existing literature, offering valuable insights into adversarial learning-based attacks and defenses in NIDS.
2) In-Depth Investigation: We examine DP, TTE, and RE
adversarial attacks on NIDS, identifying emerging trends
and novel techniques in this domain.
3) Highlighting Research Gaps: Our study identifies critical
gaps in the practical implementation of advanced ML/DL
methodologies for NIDS, focusing on real-world challenges.
4) Foundation for Future Research: We synthesize the current state of research and lay the groundwork for developing innovative, resilient defense mechanisms for realworld NIDS deployments.

C. How Our Work Is Different?
To the best of our knowledge, there is no existing exhaustive examination of adversarial learning attacks and defense
strategies within the network intrusion domain, complete with a
detailed exploration of DP, TTE, and RE. To address this critical
gap, we present the threats to various stages of machine learning
pipeline and potential defense strategies. Table II serves as a
quick reference to illustrate the scope of our work and highlights
the extent of its comprehensiveness compared with the reviewed
literature. We not only cover the necessary background on
adversarial learning and NIDS for a domain specific review,
but keep it broad enough to cover the various machine learning
pipeline threats (DP, test time evasion, and RE), and how those
can have different severity impact with the attacker’s knowledge
(black/white/gray box).
It is important to note that the existing literature predominantly concentrates on adversarial attacks and defenses in image, audio, and video domains. In contrast, research specifically
dedicated to adversarial learning in the context of NIDS is
limited, accounting for less than 10% of all adversarial learning
research.

3052

IEEE TRANSACTIONS ON ARTIFICIAL INTELLIGENCE, VOL. 7, NO. 6, JUNE 2026

TABLE I
REVIEWED ADVERSARIAL ATTACKS

Attack Category

ML Pipeline Stage

Target

Primary Goal

Data poisoning

Training phase

Training data and model

Compromise the model’s learning process

Test-time evasion

Inference phase

Model predictions (output)

Misclassify during inference

Reverse engineering

Any phase

Model parameters and behavior

Extract insights to facilitate further attacks

TABLE II
COMPARISON OF RECENT SURVEYS IN ADVERSARIAL LEARNING AND ADVERSARIAL LEARNING IN NIDS

ML/DL in

Reference

NIDS

Adversarial
Learning
in NIDS

NIDS

Adversarial

Adversarial

NIDS

Data

Test-Time

Reverse

Taxonomy

Attacks

Defenses

Datasets

Poisoning

Evasion

Engineering

Black Box/
White Box/
Grey Box

Challenges
in NIDS
Adversarial
Learning

Zhang et al., 2020 [118]

None

None

None

High

Low

None

None

None

None

B/W

None

Aldweesh et al., 2020 [12]

Medium

None

Medium

High

None

Medium

None

None

None

None

High

Miller et al., 2020 [64]

None

None

None

High

High

None

High

High

High

B/W/G

Medium

Han et al., 2021 [40]

High

High

None

High

High

Low

None

High

None

B/G

Low

Alatwi and Morisset, 2021 [11]

Low

High

None

Medium

Medium

Medium

High

High

Low

B/W/G

High

Chakraborty et al., 2021 [30]

Medium

Low

High

High

High

None

High

High

Low

B/W/G

Low

Zhou et al., 2022 [120]

None

None

None

High

High

None

Low

Low

None

B/W

None

Jmila and Khedher, 2022 [48]

High

Medium

Medium

High

High

Low

Low

Low

None

B/W/G

High

McCarthy et al., 2022 [59]

High

High

Low

High

High

Low

None

High

None

B/W/G

High

Apruzzese et al., 2022 [18]

High

High

None

High

None

None

High

High

High

B/W/G

None

He et al., 2023

High

High

High

High

High

Low

None

High

None

B/W

High

Vitorino et al., 2023 [105]

High

High

None

High

High

None

High

High

High

B/W/G

High

Ibitoye et al., 2023 [45]

High

High

Medium

High

High

None

High

High

High

B/W/G

Low

Alotaibi and Rassam, 2023 [13]

Medium

High

Medium

High

High

Medium

High

High

None

B/W/G

High

Our work

High

High

High

High

High

High

High

High

High

B/W/G

High

D. Structural Overview
The subsequent sections of this article are structured
as follows.
Section II reviews related work in the field, discussing prior
contributions and identifying how our study distinguishes itself.
Section III provides a comprehensive background on network
intrusion, including a taxonomy of adversarial learning, crafting
adversarial samples, and utilizing in adversarial attacks and defenses in NIDS. It also provides the attack categories, attacker’s
knowledge and an overview of subdomains we cover, establishing the foundation for the subsequent analysis. Section IV outlines the research methodology, explaining the rationale behind
the selection and inclusion of the works we review. Section V
presents our core review, analysis, and results of adversarial
learning attacks and defenses, focusing on DP, TTE, and RE.
Section VI discusses the limitations and challenges encountered
within the scope of our review. Section VII offers a broader
discussion, summarizing key insights, and Section VIII presents
the conclusion with the proposed future directions.
II. RELATED WORK
Initial adversarial learning vulnerabilities were primarily
studied within the computer vision domain. However, it is
crucial to recognize domain-specific nuances when assessing
potential attacks and defenses in cybersecurity. Table II provides a summary of related works, evaluating their coverage of
adversarial learning, adversarial attacks, and countermeasures,
and assessing their alignment with network intrusion-specific
knowledge. We review the related work aligned with our research scope and discuss how our contribution stands out in
the field.
Zhang et al. explored natural language processing (NLP) targeted adversarial attacks, and compared algorithms and models
across various domains [118]. Rosenberg et al. highlighted the
divergence between adversarial learning attacks and defenses
in image-based systems and those specific to cybersecurity,
emphasizing the distinct nature of data features involved [80].
Unique challenges in network intrusion detection include managing high volumes of real-time data, minimizing false positives and false negatives, inspecting encrypted communications,
adapting to evolving attack techniques, mitigating adversarial
manipulation of detection models, ensuring scalability in large
networks, and detecting insider threats. While new defense
methods are continually evolving to address these challenges,
the need for NIDS to swiftly and accurately detect specific
threats in real time remains a significant challenge. There is
a limited research addressing these challenges, including adversarial learning vulnerabilities, exploitation opportunities in
ML/DL models, feasible threat surfaces and attack vectors, and
countermeasures against adversarial attacks in network intrusion domain.

SAINI et al.: CONTRAST DUALITY OF ADVERSARIAL LEARNING IN NETWORK INTRUSION

There are numerous directions and focuses in the field of
adversarial learning attacks and defenses with a goal to compiling the knowledge to develop robust solutions and proposing potential directions to strengthen domain knowledge. For
instance, Zhou et al. explored adversarial attacks and defenses
in deep learning within the cybersecurity domain, focusing on
Advanced Persistent Threats (APT). Their research centered on
constructing a framework detailing a five-stage APT lifecycle
for AL attacks and defenses. While they applied this framework
to domains such as image, video, audio, and text, the exclusion
of network traffic data discussions limits its applicability to
network intrusion [120]. In another recent survey on NIDS
adversarial attacks, He et al. emphasized critical issues arising
from outdated benchmark datasets and the difficulty in generating authentic network features due to data instability. Moreover,
the impracticality of modifying features for attacks lies in their
inability to be transferable. They also discussed the scarcity of
defense mechanisms against packet-level attacks [41].
Jmila and Khedher studied shallow ML classifiers’ efficacy
in assessing robustness, enhancing them with Gaussian data
augmentation. Their research suggested tailoring methods, parameters, and datasets specific to network intrusion detection
scenarios, noting performance degradation with certain datasets
and attack types [48]. A survey by McCarthy et al. explored
functionality-preserving adversarial attacks and defenses in the
area of poisoning, evasion and transferability attacks in cybersecurity domain [59]. Vitorino et al. summarized the state-ofthe-art approaches focusing on adversarial learning strategies
for generating realistic adversarial examples to analyze and
protect real-life scenarios. However, their work identified that
more than 75% of the reviewed research used known common
methods and lacked novel strategies to generate adversarial
samples [105].
Ibitoye et al. categorized NIDS attacks into problem and
feature space, with feature space representing data variables and
problem space denoting input types such as files or images. The
study also mapped specific ML methods, such as supervised
learning, to distinct ML task categories such as classification
[45]. In a study, Apruzzese et al. revealed the limitations of utilizing deep learning methods for practical NIDS attacks. They
discussed that feature-space attacks for NIDS are impractical
in practice due to the difficulty of deriving adversarial traffic
from features [18]. Alotaibi and Rassam examined adversarial
machine learning attacks and defense strategies by analyzing
individual research works, presenting each strategy as outlined
in specific studies rather than categorizing them into broad
groups [13].
III. BACKGROUND AND TAXONOMY
A. Adversarial Learning
Approximately a decade ago, researchers identified adversarial learning as a significant vulnerability in neural networks.
Adversarial learning pertains to their susceptibility to small,
imperceptible changes in input data, as well as the manipulation of decision boundaries, which can lead to misclassifications [20], [39], [97]. In past few years, adversarial learning has grown as a field of great research interest because

Fig. 2.

3053

2018–2023: Adversarial learning research trends [84].

of its wide applicability and impact on artificial intelligencebased solutions in different domains. As depicted in Fig. 2,
the field of adversarial learning has experienced a significant
five-fold growth in the past five years. However, research in
adversarial learning in network intrusion is still limited [84].
Search results may exhibit bias based on keyword selection
and the emphasis on titles and abstracts. Nonetheless, they
offer a foundational insight into trends within the research
area.

B. Crafting Adversarial Samples and Their Contrast
Utilization in Attack and Defense
Adversarial examples are crafted inputs designed to deceive
machine learning models by introducing subtle, imperceptible
perturbations that lead to incorrect predictions. Given a model
f (x) that predicts a label y for an input x, an adversarial attack
can be formulated as follows.
Objective: Generate an adversarial example x such that
x = x + δ
where δ is a small perturbation added to the original input x.
Fast Gradient Sign Method (FGSM): FGSM perturbs the
input x in the direction of the gradient of the model’s loss
function J(x, y; θ), calculated with respect to x. The method
is defined as
x = x +  · sign(∇x J(x, y; θ))
where  is the perturbation magnitude, ∇x J is the gradient of
the loss with respect to x, and sign(·) represents the gradient’s
direction.
Generative Adversarial Networks (GANs): A GAN comprises a generator G and a discriminator D. The generator G
creates synthetic data x , aiming to make it indistinguishable
from real data x, while the discriminator D seeks to differentiate
between real and generated data. The GAN’s objective is




min max Ex∼pdata (x) log D(x) +Ez∼pz (z) log(1−D(G(z)))
G

D

3054

where pdata (x) represents the real data distribution, z is a noise
vector sampled from pz (z), G(z) generates synthetic data, and
D(x) outputs the probability that x is real.
In adversarial learning, the generator G is trained to produce
inputs x that maximize the misclassification rate of a target
model f . By optimizing x to exploit the vulnerabilities of f .
Transferability and Immobility: The transferability of an
adversarial perturbation enables it to deceive multiple different
models. The immobility reflects a model’s unique strength, as
its specific robustness prevents attacks from transferring from
other models.
C. NIDS ML Pipeline Vulnerabilities
DP: An attacker injects malicious or misleading data into
a machine learning model’s training data to corrupt model’s
behavior. Adversarial data is injected through flipping target
class labels (label-flipping attack), manipulating features but
keeping the class label unchanged (clean-label attack), inserting
backdoors, or flooding with noisy data to evade detection of
specific attacks or to degrade the system’s overall accuracy.
TTE: An attacker creates malevolent network traffic that circumvents detection during inference, all without changing the
training data. These attacks capitalize on vulnerabilities in the
trained model by subtly adjusting input features such as packet
size, timing, or payload patterns to influence the model’s actions
and produce inaccurate outputs.
RE: An attacker reconstructs a copy of the model by
querying it or reconstructing input features from the outputs.
Surrogate model without authorization can lead to the theft of
intellectual property. Membership Inference Attacks can expose
sensitive information in the training data violating the data
privacy.
We analyze all three NIDS subdomains as DP affects the
training phase, TTE targets the inference phase, and RE primarily impacts inference but can also reveal vulnerabilities from the
training phase.
D. Adversarial Learning Attacks
Adversarial attacks fall into different categories based on
methodologies and approaches, which directly influence the
strategies employed by attackers to create adversarial examples
and exploit vulnerabilities [117], [120]. Targeted attacks aim to
evade detection for specific malicious activities, while untargeted attacks disrupt the system by triggering false alarms or
misclassifying normal traffic as malicious [29], [120].
1) Untargeted Attacks: Cause misclassification (f (x ) =
f (x)).
2) Targeted Attacks: Force the model to predict a specific
target class yt (f (x ) = yt ).
Attacker’s knowledge of model and the training data categorizes attacks as black-box (no knowledge), white-box (full
knowledge), and gray-box (partial knowledge) attacks. Fig. 3
illustrates the categories in relation to the attacker’s knowledge,
attack surface, and impact severity.
Black-box: A black-box approach assumes that the adversary
has no access to the internal parameters or gradients of the

IEEE TRANSACTIONS ON ARTIFICIAL INTELLIGENCE, VOL. 7, NO. 6, JUNE 2026

target model or training data. Instead, the attacker can only
query the model with inputs x and observe the outputs f (x),
where f is the unknown decision function. In the context to
adversarial learning, it can be challenging to craft efficient
adversarial samples without the knowledge of gradients. Blackbox approach can also be computationally expensive to make a
large number of queries to gain some meaningful insight.
White-Box: A white-box approach assumes that the adversary has complete knowledge of the target model, including its
architecture, algorithms, internal parameters, and access to the
training data. For example, the attacker can observe and utilize
the function f (x; θ), where θ denotes the model parameters,
and may also exploit the training data distribution Dtrain to
manipulate adversarial learning.
Gray-Box: In a gray-box approach, the adversary has partial
knowledge of the target model. This typically includes access
to the training data distribution Dtrain or some information
about the model architecture or hyperparameters, but not the
exact internal parameters θ of the deployed model. The attacker
may exploit this limited knowledge to train a surrogate model
fˆ(x; θ̂) that approximates the behavior of the target model
f (x; θ).
Model manipulation attacks involve exploiting the transferability of adversarial attacks between models, corrupting the
model, deceiving model through feedback mechanisms, and
introducing malicious patterns during dynamic updates [43],
[50]. Other major classifications are based on network traffic
manipulation strategies: feature-based, flow-based, and packetbased [81].
Hybrid adversarial attacks on deep learning models involve
combining multiple attack techniques to compromise model
integrity and performance. These attacks can include a combination of evasion and poisoning techniques, as well as targeting
strategies [37]. Adaptive adversarial attacks continuously adapt
to countermeasure updates and target NIDS feedback timing
to compromise the system’s learning process and effectiveness
[110]. Adversarial NIDS attacks include strategic manipulation
of network traffic, subtle perturbations to evade detection algorithms, generative attacks that generate malicious traffic resembling benign patterns, and stealth attacks that hide malicious
activities within legitimate traffic to avoid detection. [11], [91],
[96], [103], [111].

E. Adversarial Learning Defenses
Adversarial learning defenses have advanced over the years,
encompassing techniques and strategies to fortify machine
learning models against attacks. Approaches such as adversarial training, detection/filtering, gradient masking, and randomized smoothing can provide effective defenses. Training-based
defenses enhance adversarial robustness through adversarial
training, robust feature extraction, model architecture modifications, compression and quantization, and diverse loss functions.
These techniques enhance models against attacks by improving
training data, resilient feature extraction, network architecture
adjustments, model simplification, and optimization diversity

SAINI et al.: CONTRAST DUALITY OF ADVERSARIAL LEARNING IN NETWORK INTRUSION

Fig. 3.

3055

Attacker’s knowledge, attack surface and attack’s severity in case of black-box, gray-box, and white-box scenarios.

[23], [119]. Input transformation and reconstruction-based defenses enhance adversarial robustness by altering and reconstructing input data, guarding against perturbations and boosting model generalization. Ensemble-based defenses strengthen
robustness by using multiple models, diversifying ensemble
members through varied training to collectively improve defense efficacy against attacks [102].
Randomized Smoothing introduces random noise to input
data during training and inference to enhance the model’s
decision boundaries and reduce vulnerability to adversarial
perturbations [34]. Example distributions to differentiate and
eliminate adversarial samples are another defense mechanism
[114].
Targeted adversarial defenses are more efficient for domainspecific scenarios. However, more generalized approach can
expand the applicability of these defense strategies.
F. Machine Learning in Network Intrusion Detection
Since the late 1990s and early 2000s, early applications of
machine learning focused on network intrusion detection and
malware detection through file analysis and behavioral patterns.
Over time, advanced machine learning techniques have found
extensive applications in anomaly detection, threat intelligence,
fraud detection, and spam filtering. Deep learning, a subset of
machine learning, leverages neural networks to autonomously
extract features and patterns from raw data, enhancing cybersecurity capabilities [24], [93]. Signature-based detection and
anomaly-based detection are two broad categories of network
intrusion detection methods [11], [47]. Signature-based network intrusion detection systems (SNIDS) detect intrusions by
matching network traffic against preinstalled attack signatures.
They are effective in detecting known attacks but struggle with
unknown or new attacks [52]. Anomaly-based network intrusion detection systems (ADNIDS) detect intrusions by identifying deviations from normal network patterns. They are effective
in detecting unknown or new attacks but may have higher falsepositive rates [47], [67].

Different machines and deep learning models can be valuable
for NIDS, but their usefulness depends on meeting specific
security goals and having the necessary resources. Convolutional neural networks (CNNs) enable the learning of hierarchical representations of network traffic patterns, improving the
ability to identify anomalies [19], [58]. Deep neural networks
(DNNs) are more generalized and can process various types
of data, including numerical, categorical, or textual data [56],
[58], [71], [106], [108]. Recurrent neural networks (RNNs)
are suitable for processing sequential data, making them applicable in NIDS for analyzing network traffic over time and
detecting anomalies based on deviations from learned temporal
patterns [16].
Autoencoders and variational autoencoders (VAEs) are unsupervised deep learning models used in NIDS to learn efficient
representations of normal network traffic. By training autoencoders on normal traffic, deviations or intrusions can be detected by measuring the reconstruction error [53], [65]. Graph
neural networks (GNNs) hold promise for network intrusion detection due to their ability to handle complex dependencies and
relationships in network data [107]. Specialized deep learning
architectures for NIDS that combine multiple layers to capture
complex patterns and relationships in network traffic data, can
enhance intrusions and anomaly detection capabilities [116].
Transfer learning techniques have been applied in NIDS by
utilizing pretrained deep learning models. These models, originally trained on large-scale datasets such as ImageNet, are finetuned on network traffic data to leverage the learned representations [32]. Federated Learning in NIDS revolutionizes network intrusion detection by enabling decentralized devices to
collaboratively train models. This approach enhances detection
accuracy and robustness without compromising data privacy or
requiring data centralization [8].
G. Network Intrusion Benchmark Datasets
Ensuring the relevance of benchmark datasets is vital for
adapting to evolving threat scenarios. Algorithms may not yield

3056

IEEE TRANSACTIONS ON ARTIFICIAL INTELLIGENCE, VOL. 7, NO. 6, JUNE 2026

TABLE III
NETWORK INTRUSION DATASETS, RELATED WORKS, AND BRIEF DETAILS

Dataset

Related Works

Brief Details

KDD99

[15], [38], [99], [100]

Early, widely used dataset; suffers from redundancy (75%) and outdated attack scenarios.

NSL-KDD

[77], [89]

Improved KDD99 by removing redundancy; simulated dataset, lacks real-world applicability.

Kyoto 2006+

[38], [94]

Real-world traffic dataset; includes normal, known, and unknown attacks using honeypots and sensors.

ISCX 2012

[38], [75], [92], [100]

Real-world flow-based dataset covering DoS, DDoS, Brute-force, and Infiltration attacks.

UNSW-NB15

[2], [66]

Modern dataset blending real activities and synthetic attacks; nine attack types such as Fuzzers, DoS, and Exploits.

CIDDS-001

[78]

Virtual cloud-based dataset; features DoS, Port Scan, Ping Scan, and Brute-force attacks.

CICIDS2017

[89]

Flow-based dataset with normal and attack instances (e.g., DoS, DDoS, Brute-force, Port Scan).

CSE-CIC-IDS2018

[3], [89]

Covers seven attack types, including Brute-force, Botnet, and Web attacks, with modern scenarios.

CICDDoS2019

[90]

Focused on DDoS attacks with realistic background traffic; valuable for modern DDoS research.

CIC IoT 2023

[69]

Tailored for IoT; includes attack types such as DDoS, Recon, Spoofing, and Mirai.

desired results if the data lacks reliability or fails to accurately represent the threats, impeding the development of robust
models against adversarial attacks. Several network intrusion
benchmark datasets have been developed over the years to
cater to the diverse and evolving requirements of network intrusion detection and prevention strategies. Table III presents
a summary of the major datasets commonly utilized in reviewed research works. The KDD99 dataset, one of the oldest
and widely utilized datasets in NIDS research, represents four
fundamental attack scenarios of DoS, Probe, R2L, and U2R.
While it played a crucial role in early research, the dataset
suffers from highly redundant data (above 75%) and outdated
attack scenarios. [15], [38], [99], [100]. NSL-KDD is essentially KDD99 dataset without redundant data. Both datasets,
KDD99 and NSL-KDD, are simulated virtual network datasets
and do not accurately represent real-world data. Consequently,
they are not reliable for reflecting modern real-world attacking
scenarios [77], [89]. Kyoto 2006 dataset was built capturing
real-world network traffic as not-labeled data. Using honeypots,
darknet sensors, email server, web crawler and network security mechanisms to detect attempts of unauthorized use, Kyoto
2006 dataset includes normal, known and unknown attacking
instances [38], [94].
ISCX 2012 is a real-world, flow-based labeled dataset to
represent actual network attack scenarios in four major categories of DoS, DDoS, Brute-force, and Infiltration [38], [75],
[92], [100]. UNSW-NB15 dataset was created using the IXIA
PerfectStorm tool at UNSW to simulate a mix of real modern
normal activities and synthetic attack scenarios. The dataset
consists of nine types of attacks, including Fuzzers, Analysis, Backdoors, DoS, Exploits, Generic, Reconnaissance, Shellcode, and Worms [2], [66]. CIDDS-001 dataset (2017) was
developed in a virtual cloud-based environment by executing
DoS, Port Scan, Ping Scan, and Brute force attacks [78]. CICIDS2017 dataset is also labeled flow-based dataset with normal and attack instances representing DoS, DDoS, Brute-force,
Port Scan, Bot, Web Attack, and Infiltration attacks [89]. CSECIC-IDS2018 consists of seven attacking scenarios of Bruteforce, Heartbleed, Botnet, DoS, DDoS, Web Attack, and Infiltration of the network from inside [3], [89]. CICDDoS2019
is a labeled flow-based dataset, specific to more recent DDoS

attacks with emphasizing on generating realistic background
traffic [90]. CICIoT2023 dataset presents seven distinct attacks,
namely DDoS, DoS, Recon, Web-based, Brute Force, Spoofing,
and Mirai [69].
IV. RESEARCH METHODOLOGY
To conduct a comprehensive search for research publications
across multiple research repositories, we employed a strategic
approach that involves the utilization of multiple keywords
and phrases. By carefully selecting and combining relevant
terms, we aim to cast a wide net and ensure the inclusion of
diverse and pertinent literature. Our search strategy involves
identifying key concepts and themes related to our research
topic and constructing queries that encompass these facets. To
ensure a thorough analysis, we consulted renowned research
databases, including IEEE Xplore, ACM Digital Library, and
SpringerLink. We also utilized Google Scholar for the existing
work in the field, additionally querying Base and arXiv. In
addition to these databases, we leveraged Dimensions.ai.1 for
its comprehensive research insights, allowing us to gather a
broader perspective on the relevant literature [6]. Fig. 4 shows
a step by step to identify, filtering, screening, retrieving, and
selecting the studies specific to the scope of the article.
Our base search was built around adversarial learning attacks and defenses in network intrusion detection systems,
and then we narrowed it down towards DP, TTE, and RE. We
further categorized these topics into black-box, white-box, and
gray-box adversarial learning attacks and defenses in NIDS.
To achieve an extensive coverage of relevant publications in
adversarial machine learning, a combination of the adversarial
learning keyword with other appropriate terms such as perturbation, evasion, inference, model inversion, model stealing, and model poisoning was employed. Additionally, concepts closely tied to network intrusion detection, including
anomaly detection, cyberattack, and wireless and IoT networks,
were taken into account to ensure a comprehensive scope.
We executed around hundred initial AL-ML-DL-NIDS queries,
and then we iterated and refined our search queries, incorporating synonyms, related terms, and variations to capture a
1 https://app.dimensions.ai/discover/publication

SAINI et al.: CONTRAST DUALITY OF ADVERSARIAL LEARNING IN NETWORK INTRUSION

Fig. 4.

3057

PRISMA framework for identification, screening, eligibility, and inclusion/exclusion of the studies.

TABLE IV
RESEARCH LITERATURE- INCLUSION AND EXCLUSION CRITERIA
Inclusion Criteria

Key Considerations

Relevance to adversarial learning in NIDS

Papers directly address adversarial learning techniques in the context of network intrusion detection systems

Focus on adversarial attacks and defenses

Papers discuss adversarial attacks (e.g., data poisoning, test-time evasion, reverse engineering) and defenses specific to NIDS

Methodological alignment

Papers focusing on machine learning, deep learning, and AI methodologies in the context of NIDS

Specific attack types

Papers investigating data poisoning, backdoor attacks, test-time evasion, and reverse engineering attacks in NIDS

Diversity of defense strategies

Papers exploring various defense mechanisms against adversarial attacks in NIDS

Attacker’s knowledge and their impact

Papers discussing black box, white box, and gray box adversarial attacks and defenses in NIDS

Dataset utilization

Papers utilizing NIDS datasets or proposing new datasets for research purposes

Exclusion Criteria
Irrelevant topics

Papers not directly related to adversarial learning in NIDS

General machine learning or deep learning studies

Papers that do not specifically focus on NIDS or adversarial learning in the context of network security

Nontechnical papers

Non-technical papers, such as opinion pieces, editorials, or reviews without novel research contributions

Outdated material

Papers published before a certain date (e.g., more than 5 years old) to focus on the most recent research

Language and publication quality

Poorly written or low-quality papers, as well as papers not published in reputable journals or conferences

broader range of relevant publications. Through this meticulous
process of applying inclusion and exclusion criteria as per Table IV, we optimized the retrieval and compilation of research
publications for this work, enabling us to gather a comprehensive and diverse collection of relevant studies from various
sources.
V. RESULTS: ADVERSARIAL ATTACKS AND DEFENSES
IN NIDS
Our work encompasses a comprehensive analysis of adversarial attacks and defenses within NIDS, focusing specifically
on three critical attack vectors: 1) DP; 2) TTE; and 3) RE. We
further categorize these attacks based on the adversary’s level
of knowledge, white-box, black-box, and gray-box, providing a
detailed exploration of their methodologies, impacts, and corresponding defense strategies. The following sections discuss
each of these attack categories, emphasizing their relevance to
modern NIDS frameworks.

A. DP Attacks and Defenses
Data manipulation attacks pose a significant threat to deep
learning neural network classifiers by undermining their integrity and detection capabilities [87], [104]. Adversaries utilize various techniques in these attacks, including DP, where
malicious data is injected to corrupt the NIDS’s training process. Additionally, adversaries manipulate the training data
and process itself during the learning phase, weakening the
NIDS’s ability to accurately identify threats. Furthermore, attacks on feature extraction distort the representations of network data, making it harder for NIDS to identify malicious
activities [63], [98].
DP attacks can manipulate network data by targeting port
numbers, protocol types, or payload content to disrupt operations or deceive detection systems. For instance, Featurebased poisoning alters attributes to evade detection or induce
false positives/negatives [104]. Packet-based poisoning alters

3058

Fig. 5.

IEEE TRANSACTIONS ON ARTIFICIAL INTELLIGENCE, VOL. 7, NO. 6, JUNE 2026

Data poisoning adversarial learning attacks and defenses for ML/DL-based network intrusion detection systems.

individual packets, while flow-based poisoning manipulates
traffic flows. Attackers can disrupt flows, introduce delays,
and exploit flow-based protocol vulnerabilities. Content-based
poisoning inserts malicious payloads. In techniques such as
DNS poisoning, manipulation of DNS data occurs to deceive
queries, steering users towards malicious websites through the
false association of domain names with incorrect IP addresses.
In Fig. 5, we illustrate how adversarial learning can be utilized
both as a DP attack and a defense against DP attacks.
Backdoor DP Attacks: A backdoor attack can inject trigger
patterns or perturbations into the training data or modify the
model’s architecture or parameters to manipulate the DL-based
NIDS, causing it to exhibit malicious or unexpected behavior.
Backdoor DP causes a model to misclassify test-time samples
that contain a trigger. In this threat model, the attacker exerts
control over the data by introducing poisons during the training
phase and strategically inserting triggers during the inference
phase [86].
Black-Box DP Attacks: A study by Kuppa et al. showed
that by running manifold approximation on samples collected
at attacker end for query reduction and understanding various
thresholds set by underlying anomaly detector, an attacker can
use spherical adversarial subspaces to generate attack samples.
This black-box attack methodology is particularly effective
when targeting anomaly detection systems that lack clearly
defined decision boundaries between normal and abnormal
classes, relying on a set of thresholds on anomaly scores to
guide the decision-making process [53].
Ning et al. demonstrated that a stealthy backdoor blackbox DP attack could be implemented with as low as 0.5%
of the training data. In the loss-free digital attack scenario,
this achieves an average attack success rate of over 91.1%. In
physical attacks using lossy images, a trigger as small as 1% of
the original image activates the backdoor with a success rate of
over 78.5% under a 0.5% poison ratio [70]. A study by Li et al.
achieved a success rate of 93.5% with their backdoor DP and
RE attack on 54 deep learning image-based mobile apps. The
attack incurred only a modest latency overhead of less than 2 ms

and resulted in a maximum accuracy decrease of 1.4% [56]. Xu
et al. utilized Neural Machine Translation (NMT) demonstrating the feasibility of successful targeted backdoor DP attacks
on black-box NMT systems with low poisoning rates of 0.006%
for the language translation datasets [113].
White Box DP Attacks: Venkatesan et al. conducted a study
on white-box flow-based poisoning availability attacks targeting a network scanning classifier. Using synthetic network data
from the CyberVan testbed, they demonstrated that placing
poisoned samples near 10% of high-confidence points with
20% DP reduced the model accuracy from 95% to below 50%
[104]. A label flipping attack aims to identify a subset of
N examples, where flipping their labels maximizes a specific
objective function chosen by the attacker. In a white-box attack scenario, with the complete knowledge of the algorithm
and data impact, Paudice et al. showed that classification error
can be up to six times higher with 20% of DP through label
flipping [73].
Wang et al. noted that a simple modification of the crossentropy loss yields stronger poisoning attacks when using projected gradient ascent [109]. Alrawashdeh et al. demonstrated
that an attacker can generate stealthy white-box adversarial
samples using L-BFGS and FGSM Methods, and can also inject
the trigger for backdoor DP attacks to degrade the model’s
accuracy. For instance, the researchers analyze the dataset to
identify the triggers with the highest predictive power for selecting the correct labels. By manipulating these labels, attackers can effectively boost the success rate of their malicious
activities [14].
Gray Box DP Attacks: Tolpegin et al. investigated targeted
DP attacks in federated learning (FL) systems, where malicious
participants (Insider Attacker) aim to poison the global model
with mislabeled data. The attack is agnostic to the specific DNN
architecture, loss function, or optimization function employed.
It necessitates corrupting the training data, while the learning
algorithm itself remains unchanged in this gray-box attack. The
study reveals significant drops in accuracy and recall, even with
a small number of malicious participants [101].

SAINI et al.: CONTRAST DUALITY OF ADVERSARIAL LEARNING IN NETWORK INTRUSION

He et al. proposed a gray-box attack, Liuer Mihou, to use
a surrogate deep learning model to modify the packet delay
and injecting random packets in Kitsune network attack dataset
and their own IoT dataset to generate stealthy adversarial samples by iterative operations to minimize the anomaly score
to stay undetected by anomaly-based NIDS such as Kitsune
[4], [42], [65]. An example of a gray-box backdoor DP attack
was presented by Shafahi et al., termed as Clean-label Attack.
In this scenario, the attacker possesses information about the
model and its parameters but lacks insight into the training
data. Through the manipulation of feature collisions, attackers
can influence the classification process, resulting in a backdoor
effect where the target class is erroneously classified as the base
class [87]. Another study by Severi et al. showcased a backdoor
attack where an attacker, armed solely with knowledge of the
feature space, could launch a potent attack by adding a small
set of poisoned samples, constituting just 1% of the training
data [86].
DP Defenses: To defend against DP attacks in deep learningbased cybersecurity solutions, there are several known strategies to mitigate the risks. For example, data sanitization techniques preprocess and filter input data to remove or mitigate the
effect of poisoned samples, while adversarial training exposes
the model to adversarial examples during training to enhance
its robustness. Model verification ensures the integrity of the
trained model, ensemble learning combines predictions from
multiple models for increased resilience, input validation detects, and filters out suspicious samples. Additionally, robust
optimization techniques promote the learning of generalized
and robust features.
Chen at al. introduced De-Pois that trained a mimic model
using GANs to imitate the behavior of a target model trained
on clean samples. By comparing the predictions of the mimic
model and the target model, De-Pois could detect poisoned
samples without prior knowledge of the machine learning algorithms or poisoning attack types [31]. A defense strategy
proposed by Alrawashdeh et al. targeted white-box DP and
backdoor DP attacks through activation function and neuron
pruning, that could reduce the initial average loss of accuracy
around 80% (10% to 2%) for Deep Belief Network (DBN) and
around 85% (14% to 2%) for generative adversarial network
(CoGAN) for NSL-KDD and ransomware datasets [14]. Another defense approach called Nested Training for NIDS was
introduced by Venkatesan et al., using a diversified ensemble
of classifiers trained on different subsets of the data. By leveraging disagreement among classifier predictions, the approach
effectively mitigates DP attacks, with up to 30% of the training
data being poisoned [104].
Schwarzschild et al. observed that models trained with
Stochastic gradient descent (SGD) are significantly harder to
poison, rendering poisoning attacks less effective in practical
settings [85]. A defense strategy for label-flipping attacks, Paudice et al. proposed relabeling of suspicious points that may be
indicative of malicious behavior [73]. Investigating the robustness of SGD against various DP attacks, Wang et al. demonstrated that SGD maintains optimal convergence rates on excess

3059

risk even in the presence of DP [109]. Introducing the DPAFL system, a two-phase defense mechanism for intrusion detection in federated learning, Lai et al. initially employed relative
weight differences to compare participants’ models, unveiling
unique patterns that differentiate attackers from benign participants. Subsequently, the aggregated model was tested with the
dataset to pinpoint attackers when accuracy dropped. DPA-FL
identified and removed attackers within twelve rounds, even
with a limited number of malicious actors. Study demonstrated
that DPA-FL achieved 96.5% accuracy in defending against
poisoning attacks and improved F1-score by 20% to 64% under
backdoor attacks [54].
Table V represents the reviewed adversarial DP literature for
various DP attacks and defenses employed against the known
and potential adversarial attacks. Label-flipping poisoning is
most common adversarial attack while detecting adversarial
samples and filtering is one of the common defense strategies.
Recent research trends indicate a growing preference among
scholars for employing deep learning approaches over conventional machine learning methods. Regarding the suitability
of the utilized IDS datasets, our analysis revealed that CICIDS2017 has garnered significant attention across multiple studies. This dataset, encompassing 80 network flow features and
incorporating prevalent attack types such as Web-based, Brute
force, DoS, DDoS, Infiltration, Heartbleed, Bot, and Scan,
stands out as a contemporary and comprehensive resource for
intrusion detection research [1], [89].
B. Test Time Evasion Attacks and Defenses
TTE attacks aim to deceive or manipulate a model’s behavior
during the inference phase, often by crafting adversarial examples or exploiting vulnerabilities in the model’s decisionmaking process. The goal of the adversary is to intentionally
deceive, bypass, or undermine the detection and defense mechanisms [25], [26], [39], [97].
Decision boundary manipulation is a primary TTE attack,
where attackers deliberately manipulate the decision boundary
of a machine learning model during testing. Attackers strategically modify input data to shift or distort the decision boundary,
leading the model to make incorrect predictions. The model can
be manipulated into making erroneous predictions (untargeted)
or a specific misclassification (targeted), potentially causing
security and reliability concerns. Adversarial inputs at testtime can exploit vulnerabilities in the detection algorithms or
models to evade detection or mislead the system into classifying
malicious activities as benign.
Fig. 6 demonstrates the fundamental approach of TTE attacks
and how adversarial learning can be utilized as a defense mechanism against TTE attacks.
Black Box TTE Attacks: Aiken et al. addressed ML-based
NIDSs deployed in Software-defined networks (SDNs), highlighting their vulnerability to adversarial attacks. In this blackbox setting, an attacker has access to a single host within
a network, with no direct access to the NIDS itself, or the
classifiers used. Through experiments on a SYN Flood DDoS

3060

IEEE TRANSACTIONS ON ARTIFICIAL INTELLIGENCE, VOL. 7, NO. 6, JUNE 2026

TABLE V
ADVERSARIAL LEARNING - DATA POISONING ATTACKS AND DEFENSES
Research Ref.

Attack(s)

Defense(s)

ML/DL Method(s)

Dataset(s)

Kuppa et al., 2019 [53]

Data poisoning

–

OC-SVM, isolation forests, manifold approximation

CSE-CIC-IDS2018, CICFlowMeter

Paudice et al., 2019 [73]

Label flipping poisoning

Label sanitization

SVM, K-NN

BreastCancer, MNIST, Spambase

Alrawashdeh and Goldsmith, 2020
[14]

Backdoor data poisoning

Adaptive function and pruning

DNN, DBN, CoGAN, L-BFGS &
FGSM

ISCX NSL-KDD, Ransomware

Chen et al., 2020 [33]

Label flipping poisoning

Federated learning

GRU-SVM, SGD, DNN

KDD-CUP1999,
WSN-DS

Tolpegin et al., 2020 [101]

Targeted label flipping poisoning

Clustering model gradients

Federated learning, DNN

CIFAR10, Fashion-MNIST

Xu et al., 2020 [113]

Targeted parallel data poisoning

–

LSTM, ConvS2S, CNN

TORCHTEXT
(IWSLT2016),
News-Commentary v15

Chen et al., 2021 [31]

Data poisoning

Attack-Agnostic Defense, DeepkNN

GAN, CNN, MSE

MNIST, CIFAR-10,
House Pricing

Li et al. 2021 [56]

Backdoor poisoning

–

DNN

Google Play Store, TinyImageNet

Ning et al., 2021 [70]

Clean-label data poisoning backdoor attack

Supervised and unsupervised poison sample detection

AE, NN

MNIST, CIFAR10, ImageNet10,
GTSRB

Schwarzschild et al., 2021 [85]

Data poisoning, hidden trigger
backdoor

–

SVM, NN, transfer learning

CIFAR10,
TinyImageNet

Severi et al., 2021 [86]

Clean-label backdoor poisoning

Spectral signatures, HDBSCAN,
isolation forest

NN, random forest, linear SVM

EMBER, Contagio Malware Dump,
DREBIN

Venkatesan et al., 2021 [104]

Backdoor data poisoning

Nested training for sanitization

Linear SVM, NIDS

CyberVAN, MNIST

Wang et al., 2021 [110]

Label flipping poisoning

Stochastic approximation

CNN, RKHS, robust learning

MNIST, CIFAR10

Lai et al., 2023 [54]

Label-flipping, and backdoor attacks

Federated learning (DPA-FL)

IDS, reinforcement learning, DQN,
CNN

CIC-IDS2017

Fig. 6.

CIC-IDS2017,

Fourclass,

CIFAR100,

Test time evasion adversarial learning attacks and defenses for ML/DL-based network intrusion detection systems.

attack scenario, they demonstrated a significant reduction in
NIDS detection accuracy using evasion attacks on their SDN
NIDS Neptune, which used supervised learning on network
flow statistics to train and classify live traffic. It was developed
with the core goal of detecting DDoS attacks, most notably
synchronize (SYN) floods to enable evaluation of adversarial
evasion attacks based on attack detection accuracy. Among the
classifiers tested, K-nearest neighbors (KNN) proved the most
robust, with a single feature perturbation lowering detection
accuracy from 100% to 50%. Logistic regression (LR), random
forest (RF), and support vector machine (SVM) classifiers were
more susceptible to the same perturbations [9].
White Box TTE Attacks: Pioneer work of Biggio et al. introduced a gradient-based evasion technique to deceive SVMs
and neural networks classifiers [25]. Goodfellow et al. also
made significant contributions to the initial research by utilizing
the fast gradient sign method to generate adversarial examples,

successfully causing several classifiers to misclassifying the
output. For instance, a shallow softmax classifier was assessed,
exhibiting an error rate of 99.9% alongside an average confidence level of 79.3% [39].
Melis et al. were able to show that the robot vision of a
humanoid called “iCub” was fooled by adversarial examples
crafted from iCubWorld28 image dataset. They implemented
multiclass SVM versions to demonstrate that stealthy adversarial examples forced the model to misclassify [61]. Ayub et al.
demonstrated the feasibility of a white-box model evasion
attack in intrusion detection, where the attack relies on specific
parameters used in the trained model rather than the training dataset. They employed CICIDS 2017 and TRAbID 2017
datasets to implement the multilayer perceptron (MLP) model
achieving a baseline accuracy of approximately 99% in classifying attack and benign data. Adversarial samples resulted in
a significant decrease in model accuracy, ranging from 20% to

SAINI et al.: CONTRAST DUALITY OF ADVERSARIAL LEARNING IN NETWORK INTRUSION

3061

TABLE VI
ADVERSARIAL LEARNING - TEST TIME EVASION ATTACKS AND DEFENSES
Research Ref.

Attack (s)

Defense(s)

ML/DL Method(s)

Dataset(s)

Biggio and Roli, 2018 [26]

Poisoning at inference

Reactive and proactive defences

ANN, SVM, RF, decision trees

MNIST

Chen et al., 2019 [32]

Transferability, hard-label attacks

Stateful detection defenses

NN, AE, query blinding, FGSM

CIFAR-10, CINIC-10, TinyImageNet

Ayub et al., 2020 [22]

Model evasion

–

MLP, NN, JSMA

CIC-IDS2017, TRAbID2017

Mehanaz et al., 2020 [60]

Model inversion, attribute inference

–

Decision tree, DNN

General society survey, adult census income

Pawlicki et al., 2020 [74]

Misclassification

–

Random Forest, K-NN Classifier,
IDS ANN, SVM

CIC-IDS2017

Pierazzi et al., 2020 [76]

Problem-space and feature-space
manipulation

–

SVM, greedy algorithm, Stochastic
gradient descent

AndroZoo, VirusTotal, DREBIN

Han et al., 2021 [40]

Traffic mutation

Adversarial training, feature reduction

MLP, DT, LR, KitNET, traffic obfuscation, GAN, IF, Lasso Regression

Kitsune, CIC-IDS2017

Talty et al., 2021 [98]

Poisoning at inference

Feature engineering

Random forest, MLP, SVM, logistic regression, KNN classification,
SGD, FGSM, PGD

KDD-CUP1999, ISCX, NSL-KDD

Li et al., 2022 [55]

Misclassification

Adversarial training, randomization, projection, detection

DNN, AE, GAN, KDE, LID, ODD,
ReBeL, FGSM, Logic Regression

MNIST, CIFAR10

Merzouk et al., 2022 [62]

Feature manipulation

–

FGSM

ISCX, NSL-KDD, UNSW-NB15, CIDDS001

Zhang et al., 2022 [117]

Poisoning at inference

Model voting, adversarial training, query
detection

NIDS, DNN, MLP, CNN, C-LSTM,

CIC-IDS2017, CSE-CIC-IDS2018

Debicha et al., 2023 [36]

Botnet

Adversarial training, anomaly detection

MLP, random forest, K-NN

CTU-13, CSE-CIC-IDS2018

Debicha et al., 2023 [35]

Missclassification

Robust classification and anomaly detection

DNN, FGSM, PGD, DeepFool,
Carlini & Wagner, Fusion Rules

ISCX, NSL-KDD, CIC-IDS2017

Hore et al., 2023 [44]

Packet manipulation

–

DT, RF, ML, DNN, SVM, LR

CIC-IDS2017, CSE-CIC-IDS2018

Bostani and
2024 [27]

Malware

–

SVM, optimization

DREBIN, AndroZoo

Moonsamy,

30%, for both datasets. As a potential defense strategy, reducing
the amplitude of the gradient may enhance the model’s generalization ability. By doing so, the model becomes more robust
and less susceptible to adversarial attacks, ultimately improving its overall performance and ability to generalize to unseen
data [22].
Gray Box TTE Attacks: Biggio et al. employed a gradientbased evasion method demonstrating the vulnerability of these
classifiers to adversarial attacks. The effectiveness of attacks
against classification algorithms such as SVMs and neural networks revealed that adversarial samples have a high probability
of evading detection, even if the adversary only possesses a
copy of the classifier learned from a small surrogate dataset.
For example, utilizing a small subset (20%) of the PDF corpus
samples from the Contagio dataset, adversaries were able to
craft adversarial examples that successfully evaded the target
classifiers’ ability to distinguish between legitimate and malicious PDF files [25].
We present the summary of the reviewed work in the area
of adversarial TTE, including the attacks, defenses, Ml/DL
methodologies, and datasets utilized in Table VI.
TTE Defenses: Test time evasion adversarial learning defenses focus on detecting and mitigating adversarial examples
that are specifically crafted to deceive the model at the time
of testing. By incorporating techniques such as input sanitization, defensive distillation, or ensemble methods, these defenses strive to improve the model’s ability to accurately classify inputs even in the presence of adversarial perturbations.
Papernot et al. introduced an adversarial defensive technique
called defensive distillation. They were able to show empirically that defensive distillation reduced the success rate of
adversarial sample crafting from 95.89% to 0.45% against a

deep neural network classifier trained on the MNIST dataset,
and from 87.89% to 5.11% against another classifier trained on
the CIFAR10 dataset [72].
Pawlicki et al. used test time neuron activations to detect
adversarial attacks, employing four evasion attack algorithms:
1) fast gradient sign; 2) basic iterative method; 3) Carlini and
Wagner attack; and 4) projected gradient descent. They collected neural activations from an ANN trained on a subset of the
CICIDS2017 dataset and adversarial examples. By training and
testing five ML classifiers, they achieved a recall of 0.99 for adversarial attacks with RF and nearest neighbour classifier algorithms [74]. Debicha et al. developed a transfer learning-based
adversarial detector and evaluated the effectiveness of employing multiple strategically placed detectors in IDS. Through the
implementation of state-of-the-art models with several evasion
attacks, they demonstrated that combining multiple detectors
enhances the detectability of adversarial traffic [35].
As presented in Table VI, most common TTE attack is the
use of adversarial samples during inference. This attack manipulates the model’s behavior, potentially leading to misclassification. On defense mechanisms, adversarial training is the basic
strategy, which involves augmenting the training process by
incorporating adversarial examples, which are carefully crafted
input samples designed to deceive the model. By exposing
the model to these adversarial examples during training, it
learns to recognize and appropriately respond to such attacks.
Adversarial training improves model generalization, enhances
its ability to handle perturbations, and makes it more robust
against attacks, reducing vulnerabilities and manipulation of
predictions. However, attackers can still adapt and craft sophisticated attacks that can bypass the defenses learned through
adversarial training. Therefore, it is crucial to continuously re-

3062

Fig. 7.

IEEE TRANSACTIONS ON ARTIFICIAL INTELLIGENCE, VOL. 7, NO. 6, JUNE 2026

Reverse engineering adversarial learning attacks and defenses for ML/DL-based network intrusion detection systems.

search and develop new defense strategies to stay ahead of evolv
ing attack techniques. On methodologies applied, researchers
applied various ML/DL and preferring neural networks, which
is aligned with the overall trend in Adversarial-NIDS field. TTE
research is utilizing a wide array of IDS datasets, including
established primary datasets such as KDD-CUP1999 and NSLKDD, alongside contemporary datasets such as UNSW-NB 15,
Kitsune, CIC-IDS 2017, CSE-CIC-IDS2018, and ISCX, covering both historical and modern-day attack scenarios.
C. RE Attacks and Defenses
RE attacks exploit the ML pipeline by analyzing feature engineering, extracting sensitive training data, and deducing model
architecture, parameters, and internal representations. There are
various RE approaches applicable in the field of NIDS. For
example, investigating network protocols to understand their
structure, behavior, and vulnerabilities aids in effectively detecting and preventing attacks targeting specific protocols. Furthermore, RE techniques assist in malware analysis and signature
extraction, enhancing NIDS capabilities in detecting known and
unknown threats. Binary code analysis supports vulnerability
identification, understanding system responses, and overall security enhancement of NIDS. Fig. 7 shows how adversaries use
RE approach for attacks and how the same approach can serve
to build a defense strategy against adversarial attacks.
Model inversion attacks involve extracting sensitive information and insights about the training data by reverse-engineering.
These attacks pose a significant risk to privacy and require protective measures to safeguard the confidentiality of the model
and its data.
A RE attack gains knowledge or extracts information about
the underlying detection model or its internal workings to understand and exploit the model’s vulnerabilities, weaknesses,
or decision-making mechanisms [52]. Nayan et al. addressed
the vulnerabilities of on-device model extraction and offered
a systematic classification of model extraction attacks and defenses [68]. By analyzing the model’s structure, parameters,
or outputs, the attacker aims to deduce valuable information,

such as feature representations, detection rules, and sensitive
training data. Atwell et al. investigated the threat of reverse
TCP attacks to gain remote access to end-user networks by
exploiting the connection process [21]. Breier et al. demonstrated the potential of RE in neural networks through fault
attacks. By flipping the sign bit, fault attack manipulated intermediate values, thereby enabling the recovery of proprietary model parameters [28]. Attackers leverage RE to exploit vulnerabilities and create potent adversarial examples.
On defensive side, RE can serve legitimate purposes, such as
model interpretation, debugging, auditing, accountability, and
transparency [46].
Black Box RE Attacks: By exploring model inversion
attacks, Mehnaz et al. investigated adversaries who can use
known nonsensitive attributes to infer sensitive attributes. Two
new attack methods, confidence modeling-based and confidence score-based, are introduced. Decision tree and deep neural network models trained on real datasets are evaluated for
such attacks. Vulnerability to model inversion attacks is identified within specific attribute-based groups, such as gender or
race [60].
Gray Box RE Attacks: In a gray-box backdoor attack called
DeepPayload, Li et al. introduced a practical RE attack scenario
where the attacker has access to the compiled DNN model
in the app, and does not have access to the original training
data or metadata used for training. Using RE, a decompiled
DNN model into a data-flow graph, an attacker can inject a
payload consisting of a resize operator, trigger detector, and
output selector. The modified model, incorporating the injected
components, altered its behavior based on the trigger presence probability, allowing for the attacker’s desired output.
This attack uses bytecode reverse-engineering by directly manipulating the dataflow graph to inject malicious logic directly
into deployed DNN model. The study reveals that this attack
effectively triggers the malicious payload with a high success
rate (93.5%), with minimal latency overhead (2 ms) and accuracy decrease (1.4%). This RE attack focuses on distributed
or deployed models beyond developers’ control. Unfortunately,

SAINI et al.: CONTRAST DUALITY OF ADVERSARIAL LEARNING IN NETWORK INTRUSION

existing defense techniques require training or testing with
extensive sample sets, making them unsuitable for deployed
models [56].
RE Defenses: RE was employed by Wang et al. to detect
and prevent backdoor attacks on deep neural networks. They
identified hidden triggers within DNNs and developed three defense methods: 1) an early filter for adversarial inputs; 2) neuron
pruning-based model patching; and 3) unlearning. The detection of backdoor injection is based on anomaly measurement of
infected and clean model by how much the label with smallest
trigger deviates from the remaining labels. To mitigate these
attacks, they analyzed three methods, including an early filter
for adversarial inputs, a model patching algorithm based on
neuron pruning, and another based on unlearning. By pruning
30% of neurons reduces attack success rate to nearly 0% with
the slight reduction of classification accuracy by 5.06%. Training the DNN model with reverse engineered triggers proved
effective in unlearning the original trigger, resulting in an attack
success rate of less than 6.70% and a maximum reduction in
classification accuracy of 3.6% [106].
Asnani et al. presented threat of model parsing for generative
models (GMs). The objective is to infer network architectures
and training loss functions from generated images to address
concerns related to the misuse of GMs. Their proposed framework consists of two networks: 1) the fingerprint estimation
network (FEN); and 2) the parsing network (PN). These networks estimate fingerprints from images and predict the corresponding model parameters. A dataset of 100 000 images
from 116 GMs was collected to demonstrate parsing of the
hyperparameters [19].
Table VII presents an overview of studied RE ML/DL methods applied for adversarial attacks and defenses. As we observe
that standard definition of protocols and identification and malware analysis can be used as defense mechanisms for protocol
manipulation and malware attacks. Model and data information
can be reverse engineered through model extraction, model
inversion, and model parsing by using deep neural networks
and generative adversarial networks.
There are security concerns associated with RE the architecture of a DNN model by exploiting the memory access
pattern of a processor during DNN execution. To counter such
attacks, Liu et al. proposed a defensive mechanism that combines techniques such as oblivious shuffle, address space layout
randomization (ASLR), and dummy memory accesses. This
defense aimed to obfuscate the memory access pattern and
minimize the risk of such attacks with minimal overhead. The
effectiveness of this proposed defense was evaluated through
a modified attack on an existing model. The results illustrated
that the incorporation of these techniques notably heightened
the complexity of the attack while keeping memory access overhead low. Moreover, the defense mechanism was scalable, made
it applicable to larger DNN models by effectively mitigating
RE attacks that might exploit memory access patterns [58].
The defense strategy presented by Xiang et al. introduces an
optimization-based approach to counter RE, applicable both
before and during classifier training. This defense primarily
targets backdoor attacks by estimating the recognized pattern

3063

employed in the attack. Upon identifying backdoor poisoning
and the target class, the estimated backdoor pattern is used
to pinpoint and eliminate the poisoned data directly from the
training set [112].
VI. LIMITATIONS AND CHALLENGES
Our objective is to provide a comprehensive and active reference in the field of adversarial learning attacks and defenses
for network intrusion detection systems; however, there are
challenges and limitations within our work. First, the availability of comprehensive literature covering all relevant aspects
of adversarial learning is limited, hindering direct comparisons
and in-depth analysis of research breadth of the topic. While
there have been significant advancements in the broader field of
adversarial learning attacks and defenses, the specific subareas
of deep learning, network intrusion, DP, TTE, and RE have seen
relatively fewer studies. Additionally, our focused approach on
a shorter time frame may result in a narrower scope of research
discussed. Furthermore, the dynamic and rapidly evolving nature of the field presents challenges in effectively capturing the
latest advancements in adversarial learning, emphasizing the
need for future studies to stay current.
VII. DISCUSSION
Research in adversarial learning within the network domain
continues to evolve, focusing on advancing attack detection
capabilities and developing more robust defense strategies.
The relevance of existing older yet popular NIDS datasets
for advanced ML/DL algorithms remains a concern. ML/DLgenerated synthetic data may address challenges of data
scarcity, scalability, and attack rarity effectively. Majority of
existing research studies highly rely on outdated data sources.
These outdated data sources suffer from a high percentage
of duplicate records and highly imbalanced attack categories.
Accurate data interpretation is crucial in ML-based NIDS for
representing normal and attack scenarios. While diverse attack
datasets help identify and mitigate threats, adversaries exploit
this knowledge to craft deceptive attacks. Challenges such
as limited availability, imbalanced class distribution, evolving
techniques, and privacy concerns hinder the effectiveness of
network attack datasets. Keeping datasets up-to-date becomes
a challenge due to evolving techniques and the need for real
attack instances [15], [89], [100]. To compare the scope, applicability, and limitations of these datasets, Ghurab et al. analyzed the benchmark datasets (KDD99, NSL-KDD, Kyoto
2006+, ISCX 2012, UNSW-NB15, CIDDS-001, CICIDS2017,
CSE-CIC-IDS2018), and recommended to utilize more recent
datasets representing modern-day attacks [38]. However, another study by Alshamy et al. presented that 66% of studied
39 NIDS ML-DL classification research works (2017-2020)
utilized KDD99/NSL-KDD datasets with 46% using KDD99
dataset [15]. Similarly, an evaluation of ML-DL performance
study by Pektas and Acarman showed that 80% of 10 studies
(2008-2018) utilized KDD99/NSL-KDD datasets, while a 2020
review by Thakkar et al. presented that all 6 studied research
work for ML-DL NIDS utilized NSL-KDD datasets [75], [100].

3064

IEEE TRANSACTIONS ON ARTIFICIAL INTELLIGENCE, VOL. 7, NO. 6, JUNE 2026

TABLE VII
ADVERSARIAL LEARNING - REVERSE ENGINEERING ATTACKS AND DEFENSES
Research Ref.

Attack(s)

Defense(s)

ML/DL Method(s)

Dataset(s)
CSIC 2010,

Antunes et al., 2011 [17]

Protocol Manipulation

Standard Protocol Identification

Moore Reduction

Alabdulmoshin et al., 2014
[10]

Spam

Randomized diversification

Adversarial Learning, Linear SVM

UCI datasets

Atwell et al., 2016 [21]

Reverse TCP Attacks, Social Engineering, Zero Day

Security Policy, Security Awareness, Incident Response

TCP analysis

Click (Port 80 HTTP), VirusTotal

Tramer et al., 2016 [102]

Model Extraction, Model Inversion

–

NN, Decision Trees, SVM

Digits, Adult, Statlog (German
Credit Data), Steak Survey

Papernot et al., 2017 [71]

Misclassification

Reactive and Proactive - Gradient
Masking

DNN

MNIST, GTSRB

Liu et al., 2019 [57]

Model Extraction and Inversion

Address Space Layout Randomization (ASLR), DumMA

DNN, CNN

Memory Access Patterns

Wang et al., 2019 [108]

Model Manipulation

L-AWA-maxKL

DNN

MNIST

Wang et al., 2019 [106]

Backdoor Attacks - BadNets & Trojan

Filtering, Neuron Pruning

DNN

MNIST, GTSRB, Youtube Face,
PubFig

Breier et al., 2021 [28]

Fault Attacks

–

NN

TinyImageNet, CIFAR-10

Li et al., 2021 [56]

Injected Backdoor Attack

–

DNN

Google Play Store

Ismael and Thanoon, 2022
[46]

Malware

Standard malware identification

Malware Analysis

CIC-MalMem-2022

Asnani et al., 2023 [19]

Model Parsing

Fingerprint Estimation Network
(FEN), Parsing Network (PN)

Generative Models (GM), CNN,
GAN, VAE

MNIST, GTSRB, Tiny ImageNet,
CelebA, FaceForensics++

Salient Person,
FTCDATA

Ring et al. compared 34 datasets, representing research works
on dataset generation or utilization, focusing on features per
dataset [79]. For a thorough evaluation of ML/DL classifiers,
Sarhen et al. introduced a standardized NetFlow-based feature set consisting of 43 features. They tailored NIDS datasets
(UNSW-NB15, BoT-IoT, ToN-IoT, CSE-CIC-IDS2018) using
the define standard NetFlow-based features to enhance the consistency in comparing the performance evaluation [1], [83]. The
growing importance of deep learning in enhancing predictive
modeling and decision-making makes them attractive for NIDS.
However, adversarial research specific to ML/DL-based NIDS
remains limited compared with non-NIDS domains. The challenges of adapting image-specific learning algorithms to NIDS
have driven the exploration of domain-specific methods [41],
[51], [80].
VIII. CONCLUSION AND FUTURE DIRECTIONS
Machine learning and deep learning models excel at adapting to evolving threats and detecting subtle anomalies, making them invaluable for dynamic cybersecurity environments.
However, their reliance on substantial computational resources
can hinder real-time detection in high-speed networks. Limited interpretability further challenges understanding their decisions, emphasizing the need for current, realistic network
datasets to detect adversarial attacks and develop robust defenses. Future research on optimizing ML/DL models through
lightweight architectures, incorporating explainability techniques, and integrating traditional approaches such as rulebased systems and ensemble methods can enhance NIDS
performance and reliability. The limited interpretability of
evolving machine learning methods in NIDS hinders intrusion validation and resource optimization in security-focused
systems.
Adversarial learning in NIDS presents critical challenges and
opportunities for future research directions.

1) Dataset Quality and Realism: Develop authentic datasets
reflecting current attack scenarios and employ ML/DLgenerated synthetic data and data augmentation techniques to tackle data scarcity and scalability challenges
effectively.
2) Interpretability: Employ explainable AI techniques to
validate detected intrusions, support expert analysis, and
optimize resource allocation.
3) Domain-Specific Algorithms: Develop adversarial learning algorithms tailored to the unique characteristics of
network data.
4) Real-World Evaluation: Bridge the gap between theory
and practice by testing real-world environments to ensure
usability and effectiveness.
5) Zero-Day Threat Detection: Explore novel techniques
and threat intelligence to handle to zero-day threats effectively.
Achieving robust generalization and accurate predictions for
adversarial threats remains a critical challenge in NIDS domain.
There is a significant gap in NIDS-specific DP, TTE, and RE.
Our work emphasizes the need for continuous evaluation and
advancement of adversarial learning techniques to ensure defenses remain effective against evolving adversarial threats in
network intrusion domain.
REFERENCES
[1] Cisco IOS netflow version 9 flow-record format - white paper.
(2011). Accessed: Jan. 10, 2024. [Online]. Available: https://
www.cisco.com/en/US/technologies/tk648/tk362/technologies_white_
paper09186a00800a3db9.pdf
[2] Unsw-nb15 dataset. (2015). Accessed: Jan. 9, 2024. [Online]. Available: https://research.unsw.edu.au/projects/unsw-nb15-dataset
[3] Cse-cic-ids2018. (2018). Accessed: Dec. 20, 2023. [Online]. Available:
https://www.unb.ca/cic/datasets/ids-2018.html
[4] Kitsune network attack dataset. (2019). Accessed: Dec. 20,
2023. [Online]. Available: https://archive.ics.uci.edu/dataset/516/
kitsune+network+attack+dataset

SAINI et al.: CONTRAST DUALITY OF ADVERSARIAL LEARNING IN NETWORK INTRUSION

[5] Why is cybersecurity important? (2021). Accessed: Nov. 29, 2023.
[Online]. Available: https://cybersecurityonline.utulsa.edu/blog/why-iscybersecurity-important-top-six-reasons/
[6] Linked research data from idea to impact (2022). Accessed: Feb. 24,
2023. [Online]. Available: https://www.dimensions.ai/
[7] Gartner forecasts global security and risk management spending
to grow 14% in 2024. (2023). Accessed: Nov. 29, 2023. [Online].
Available:
https://www.gartner.com/en/newsroom/press-releases/
2023-09-28-gartner-forecasts-global-security-and-risk-managementspending-to-grow-14-percent-in-2024
[8] S. Agrawal et al., “Federated learning for intrusion detection system:
Concepts, challenges and future directions,” Comput. Commun., vol.
195, pp. 346–361, 2022.
[9] J. Aiken and S. Scott-Hayward, “Investigating adversarial attacks
against network intrusion detection systems in SDNS,” in Proc. IEEE
Conf. Netw. Function Virtualization Softw. Defined Networks (NFVSDN), Piscataway, NJ, USA: IEEE Press, 2019, pp. 1–7.
[10] I. M. Alabdulmohsin, X. Gao, and X. Zhang, “Adding robustness
to support vector machines against adversarial reverse engineering,”
in Proc. 23rd ACM Int. Conf. Conf. Inf. Knowl. Manage., 2014,
pp. 231–240.
[11] H. A. Alatwi and C. Morisset, “Adversarial machine learning in
network intrusion detection domain: A systematic review,” 2021,
arXiv:2112.03315.
[12] A. Aldweesh, A. Derhab, and A. Z. Emam, “Deep learning approaches
for anomaly-based intrusion detection systems: A survey, taxonomy,
and open issues,” Knowl.-Based Syst., vol. 189, 2020, Art. no. 105124.
[13] A. Alotaibi and M. A. Rassam, “Adversarial machine learning attacks
against intrusion detection systems: A survey on strategies and defense,” Future Internet, vol. 15, no. 2, p. 62, 2023.
[14] K. Alrawashdeh and S. Goldsmith, “Defending deep learning based
anomaly detection systems against white-box adversarial examples and
backdoor attacks,” in Proc. IEEE Int. Symp. Technol. Soc. (ISTAS),
Piscataway, NJ, USA: IEEE Press, 2020, pp. 294–301.
[15] R. Alshamy and M. Ghurab, “A review of big data in network intrusion
detection system: Challenges, approaches, datasets, and tools,” J.
Comput. Sci. Eng., vol. 8, no. 7, pp. 62–74, 2020.
[16] S. Amutha, R. K. R. Srinivasan, and M. Kavitha, “Secure network
intrusion detection system using NID-RNN based deep learning,”
in Proc. Int. Conf. Advances in Comput., Commun. Appl. Inform.
(ACCAI), Piscataway, NJ, USA: IEEE Press, 2022, pp. 1–5.
[17] J. Antunes, N. Neves, and P. Verissimo, “Reverse engineering of
protocols from network traces,” in Proc. 18th Work. Conf. Reverse
Eng., Piscataway, NJ, USA: IEEE Press, 2011, pp. 169–178.
[18] G. Apruzzese, M. Andreolini, L. Ferretti, M. Marchetti, and M. Colajanni, “Modeling realistic adversarial attacks against network intrusion
detection systems,” Digit. Threats: Res. Pract. (DTRAP), vol. 3, no. 3,
pp. 1–19, 2022.
[19] V. Asnani, X. Yin, T. Hassner, and X. Liu, “Reverse engineering of
generative models: Inferring model hyperparameters from generated
images,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 45, no. 12, pp.
15477–15493, Dec. 2023.
[20] A. Athalye, L. Engstrom, A. Ilyas, and K. Kwok, “Synthesizing robust
adversarial examples,” in Proc. Int. Conf. Mach. Learn., PMLR, 2018,
pp. 284–293.
[21] C. Atwell, T. Blasi, and T. Hayajneh, “Reverse TCP and social
engineering attacks in the era of big data,” in Proc. IEEE 2nd Int.
Conf. Big Data Secur. Cloud (BigDataSecurity), IEEE Int. Conf. High
Perform. Smart Comput. (HPSC), IEEE Int. Conf. Intell. Data Secur.
(IDS), Piscataway, NJ, USA: IEEE Press, 2016, pp. 90–95.
[22] M. A. Ayub, W. A. Johnson, D. A. Talbert, and A. Siraj, “Model
evasion attack on intrusion detection systems using adversarial machine
learning,” in Proc. 54th Annu. Conf. Inf. Sci. Syst. (CISS), Piscataway,
NJ, USA: IEEE Press, 2020, pp. 1–6.
[23] T. Bai, J. Luo, J. Zhao, B. Wen, and Q. Wang, “Recent advances in adversarial training for adversarial robustness,” 2021, arXiv:2102.01356.
[24] T. Ban, T. Takahashi, and J. Takeuchi, “Malicious packet classification
based on neural network using Kitsune features,” in Proc. Intell.
Syst. Pattern Recogn.: Second Int. Conf. (ISPR), Hammamet, Tunisia:
Springer Nature, Mar. 2022.
[25] B. Biggio et al., “Evasion attacks against machine learning at test
time,” in Proc. Mach. Learn. Knowl. Discovery Databases: Euro.
Conf. (ECML PKDD), Prague, Czech Republic: Springer, Sep. 2013,
pp. 387–402.
[26] B. Biggio and F. Roli, “Wild patterns: Ten years after the rise of
adversarial machine learning,” Pattern Recognit., vol. 84, pp. 317–331,
Dec. 2018.

3065

[27] H. Bostani and V. Moonsamy, “Evadedroid: A practical evasion attack on machine learning for black-box android malware detection,”
Comput. Secur., vol. 139, 2024, Art. no. 103676.
[28] J. Breier, D. Jap, X. Hou, S. Bhasin, and Y. Liu, “Sniff: reverse
engineering of neural networks with fault attacks,” IEEE Trans. Rel.,
vol. 71, no. 4, pp. 1527–1539, Dec. 2022.
[29] N. Carlini, et al., “On evaluating adversarial robustness,” 2019,
arXiv:1902.06705.
[30] A. Chakraborty, M. Alam, V. Dey, A. Chattopadhyay, and D.
Mukhopadhyay, “A survey on adversarial attacks and defences,” CAAI
Trans. Intell. Technol., vol. 6, no. 1, pp. 25–45, 2021.
[31] J. Chen, X. Zhang, R. Zhang, C. Wang, and L. Liu, “De-pois: An
attack-agnostic defense against data poisoning attacks,” IEEE Trans.
Inf. Forensics Secur., vol. 16, pp. 3412–3425, 2021.
[32] S. Chen, N. Carlini, and D. Wagner, “Stateful detection of black-box
adversarial attacks,” 2019, arXiv:1907.05587.
[33] Z. Chen, N. Lv, P. Liu, Y. Fang, K. Chen, and W. Pan, “Intrusion
detection for wireless edge networks based on federated learning,”
IEEE Access, vol. 8, pp. 217463–217472, 2020.
[34] J. Cohen, E. Rosenfeld, and Z. Kolter, “Certified adversarial robustness
via randomized smoothing,” in Proc. Int. Conf. Mach. Learn., PMLR,
2019, pp. 1310–1320.
[35] I. Debicha, R. Bauwens, T. Debatty, J.-M. Dricot, T. Kenaza, and W.
Mees, “TAD: Transfer learning-based multi-adversarial detection of
evasion attacks against network intrusion detection systems,” Future
Gener. Comput. Syst., vol. 138, pp. 185–197, Jan. 2023.
[36] I. Debicha, B. Cochez, T. Kenaza, T. Debatty, J.-M. Dricot, and W.
Mees, “ADV-bot: Realistic adversarial botnet attacks against network
intrusion detection systems,” Comput. Secur., vol. 129, 2023, Art. no.
103176.
[37] X. Du et al., “A hybrid adversarial attack for different application
scenarios,” Appl. Sci., vol. 10, no. 10, p. 3559, 2020.
[38] M. Ghurab, G. Gaphari, F. Alshami, R. Alshamy, and S. Othman, “A
detailed analysis of benchmark datasets for network intrusion detection
system,” Asian J. Res. in Computer Sci., vol. 7, no. 4, pp. 14–33, 2021.
[39] I. J. Goodfellow, J. Shlens, and C. Szegedy, “Explaining and harnessing
adversarial examples,” 2014, arXiv:1412.6572.
[40] D. Han et al., “Evaluating and improving adversarial robustness of
machine learning-based network intrusion detectors,” IEEE J. Sel.
Areas Commun., vol. 39, no. 8, pp. 2632–2647, Aug. 2021.
[41] K. He, D. D. Kim, and M. R. Asghar, “Adversarial machine learning
for network intrusion detection systems: a comprehensive survey,”
IEEE Commun. Surveys Tuts., vol. 25, no. 1, pp. 538–566, Firstquarter
2023.
[42] K. He, D. D. Kim, J. Sun, J. D. Yoo, Y. H. Lee, and H. K. Kim, “Liuer
Mihou: A practical framework for generating and evaluating grey-box
adversarial attacks against NIDS,” 2022, arXiv:2204.06113.
[43] J. Heo, S. Joo, and T. Moon, “Fooling neural network interpretations
via adversarial model manipulation,” Adv. Neural Inf. Process. Syst.,
vol. 32, pp. 2921–2932, 2019.
[44] S. Hore, J. Ghadermazi, D. Paudel, A. Shah, T. K. Das, and N. D.
Bastian, “Deep PackGen: A deep reinforcement learning framework
for adversarial network packet generation,” 2023, arXiv:2305.11039.
[45] O. Ibitoye, R. Abou-Khamis, A. Matrawy, and M. O. Shafiq, “The
threat of adversarial attacks on machine learning in network security–
A survey,” 2019, arXiv:1911.02621.
[46] M. F. Ismael and K. H. Thanoon, “Investigation malware analysis
depend on reverse engineering,” in Proc. Int. Conf. Data Sci. Intell.
Comput. (ICDSIC), Piscataway, NJ, USA: IEEE Press, 2022, pp. 251–
256.
[47] A. Javaid, Q. Niyaz, W. Sun, and M. Alam, “A deep learning approach
for network intrusion detection system,” in Proc. 9th EAI Int. Conf.
Bio-Inspired Inf. Commun. Technol. (Formerly BIONETICS), 2016, pp.
21–26.
[48] H. Jmila and M. I. Khedher, “Adversarial machine learning for network
intrusion detection: A comparative study,” Comput. Netw., vol. 214,
2022, Art. no. 109073.
[49] A. R. Khan et al., “Deep learning for intrusion detection and security
of internet of things (IoT): current analysis, challenges, and possible
solutions,” Secur. Commun. Netw., vol. 2022, no. 1, p. 4016073,
2022.
[50] B. Kim, Y. E. Sagduyu, K. Davaslioglu, T. Erpek, and S. Ulukus,
“Channel-aware adversarial attacks against deep learning-based wireless signal classifiers,” IEEE Trans. Wireless Commun., vol. 21, no. 6,
pp. 3868–3880, Jun. 2022.

3066

[51] T. Kim and W. Pak, “Deep learning-based network intrusion detection
using multiple image transformers,” Appl. Sci., vol. 13, no. 5, p. 2754,
2023.
[52] C. Kruegel, D. Mutz, W. Robertson, G. Vigna, and R. Kemmerer,
“Reverse engineering of network signatures,” in Proc. AusCERT Asia
Pacific Inf. Technol. Secur. Conf., Gold Coast, Australia, 2005.
[53] A. Kuppa, S. Grzonkowski, M. R. Asghar, and N.-A. Le-Khac, “Black
box attacks on deep anomaly detectors,” in Proc. 14th Int. Conf.
Availability, Reliability Security, 2019, pp. 1–10.
[54] Y.-C. Lai et al., “Two-phase defense against poisoning attacks on
federated learning-based intrusion detection,” Comput. Secur., vol. 129,
2023, Art. no. 103205.
[55] Y. Li, M. Cheng, C.-J. Hsieh, and T. C. M. Lee, “A review of adversarial attack and defense for classification methods,” Amer. Statistician,
vol. 76, no. 4, pp. 329–345, 2022.
[56] Y. Li, J. Hua, H. Wang, C. Chen, and Y. Liu, “Deeppayload: Blackbox backdoor attack on deep learning models through neural payload
injection,” in Proc. IEEE/ACM 43rd Int. Conf. Softw. Eng. (ICSE),
Piscataway, NJ, USA: IEEE Press, 2021, pp. 263–274.
[57] H. Liu and B. Lang, “Machine learning deep learning methods intrusion
detection systems: A survey,” Appl. Sci., vol. 9, no. 20, p. 4396, 2019.
[58] Y. Liu, D. Dachman-Soled, and A. Srivastava, “Mitigating reverse
engineering attacks on deep neural networks,” in Proc. IEEE Comput.
Soc. Annu. Symp. VLSI (ISVLSI), Piscataway, NJ, USA: IEEE Press,
2019, pp. 657–662.
[59] A. McCarthy, E. Ghadafi, P. Andriotis, and P. Legg, “Functionalitypreserving adversarial machine learning for robust classification in
cybersecurity and intrusion detection domains: A survey,” J. Cybersecurity Privacy, vol. 2, no. 1, pp. 154–190, 2022.
[60] S. Mehnaz, N. Li, and E. Bertino, “Black-box model inversion attribute
inference attacks on classification models,” 2020, arXiv:2012.03404.
[61] M. Melis, A. Demontis, B. Biggio, G. Brown, G. Fumera, and F. Roli,
“Is deep learning safe for robot vision? adversarial examples against
the ICUB humanoid,” 2017, arXiv:1708.06939.
[62] M. A. Merzouk, F. Cuppens, N. Boulahia-Cuppens, and R. Yaich,
“Investigating the practicality of adversarial evasion attacks on network
intrusion detection,” Ann. Telecommun., vol. 77, no. 11, pp. 763–775,
2022.
[63] A. Michel and R. Ewetz, “Gradient-based adversarial attack detection
via deep feature extraction,” in Proc. SoutheastCon, Piscataway, NJ,
USA: IEEE Press, 2022, pp. 213–220.
[64] D. J. Miller, Z. Xiang, and G. Kesidis, “Adversarial learning targeting
deep neural network classification: A comprehensive review of defenses
against attacks,” Proc. IEEE, vol. 108, no. 3, pp. 402–433, Mar. 2020.
[65] Y. Mirsky, T. Doitshman, Y. Elovici, and A. Shabtai, “Kitsune: An
ensemble of autoencoders for online network intrusion detection,”
2018, arXiv:1802.09089.
[66] N. Moustafa, B. Turnbull, and K.-K. R. Choo, “An ensemble intrusion
detection technique based on proposed statistical flow features for
protecting network traffic of internet of things,” IEEE Internet Things
J., vol. 6, no. 3, pp. 4815–4830, Jun. 2019.
[67] A. Bou Nassif, M. Abu Talib, Q. Nasir, and F. M. Dakalbab, “Machine
learning for anomaly detection: A systematic review,” IEEE Access,
vol. 9, pp. 78658–78700, 2021.
[68] T. Nayan, Q. Guo, M. A. Duniawi, M. Botacin, S. Uluagac, and
R. Sun, SoK: “All you need to know about,” “On-Device,” ML
“model extraction-the gap between research and practice,” in Proc.
33rd USENIX Secur. Symp. (USENIX Secur.), 2024, pp. 5233–5250.
[69] E. C. P. Neto, S. Dadkhah, R. Ferreira, A. Zohourian, R. Lu, and A. A.
Ghorbani, “CICIoT2023: A real-time dataset and benchmark for largescale attacks in IoT environment,” Sensors, vol. 23, no. 13, p. 5941,
2023.
[70] R. Ning, J. Li, C. Xin, and H. Wu, “Invisible poison: A blackbox clean
label backdoor attack to deep neural networks,” in Proc. Conf. Comput.
Commun. (INFOCOM), Piscataway, NJ, USA: IEEE Press, 2021,
pp. 1–10.
[71] N. Papernot, P. McDaniel, I. Goodfellow, S. Jha, Z. Berkay Celik, and
A. Swami, “Practical black-box attacks against machine learning,” in
Proc. ACM Asia Conf. Comput. Commun. Security, 2017, pp. 506–519.
[72] N. Papernot, P. McDaniel, X. Wu, S. Jha, and A. Swami, “Distillation as
a defense to adversarial perturbations against deep neural networks,” in
Proc. IEEE Symp. Security Privacy (SP), Piscataway, NJ, USA: IEEE
Press, 2016, pp. 582–597.
[73] A. Paudice, L. Muñoz-González, and E. C. Lupu, “Label sanitization
against label flipping poisoning attacks,” in Proc. Workshops: Nemesis

IEEE TRANSACTIONS ON ARTIFICIAL INTELLIGENCE, VOL. 7, NO. 6, JUNE 2026

2018, UrbReas 2018, SoGood 2018, IWAISe 2018, Green Data Mining
2018 (ECML PKDD), Springer, Sep. 2019, pp. 5–15.
[74] M. Pawlicki, M. Choraś, and R. Kozik, “Defending network intrusion
detection systems against adversarial evasion attacks,” Future Gener.
Comput. Syst., vol. 110, pp. 148–154, Sep. 2020.
[75] A. Pektaş and T. Acarman, “A deep learning method to detect network
intrusion through flow-based features,” Int. J. Netw. Manage., vol. 29,
no. 3, 2019, Art. no. e2050.
[76] F. Pierazzi, F. Pendlebury, J. Cortellazzi, and L. Cavallaro, “Intriguing
properties of adversarial ML attacks in the problem space,” 2020,
arXiv:1911.02142.
[77] D. D. Protić, “Rev. Kdd Cup ‘99, Nsl-Kdd Kyoto 2006+ Datasets.
Vojnotehnički Glasnik/Mil,” Tech. Courier, vol. 66, no. 3, pp. 580–596,
2018.
[78] M. Ring, S. Wunderlich, D. Grüdl, D. Landes, and A. Hotho, “Flowbased benchmark data sets for intrusion detection,” in Proc. 16th Eur.
Conf. Cyber Warfare Security, ACPI, 2017, pp. 361–369.
[79] M. Ring, S. Wunderlich, D. Scheuring, D. Landes, and A. Hotho, “A
survey of network-based intrusion detection data sets,” Comput. Secur.,
vol. 86, pp. 147–167, Sep. 2019.
[80] I. Rosenberg, A. Shabtai, Y. Elovici, and L. Rokach, “Adversarial
machine learning attacks and defense methods in the cyber security
domain,” ACM Comput. Surveys (CSUR), vol. 54, no. 5, pp. 1–36,
2021.
[81] A. M. Sadeghzadeh, S. Shiravi, and R. Jalili, “Adversarial network traffic: Towards evaluating the robustness of deep-learning-based network
traffic classification,” IEEE Trans. Netw. Service Manag., vol. 18, no. 2,
pp. 1962–1976, Jun. 2021.
[82] S. Saini and N. Saxena, “Predatory medicine: Exploring and measuring the vulnerability of medical AI to predatory science,” 2022,
arXiv:2203.06245.
[83] M. Sarhan, S. Layeghy, and M. Portmann, “Towards a standard feature
set for network intrusion detection system datasets,” Mobile Netw.
Appl., pp. 1–14, vol. 27, no. 1, 2022.
[84] Research Publication Trends on Google Scholar from 2018 to 2023.
(2025). Accessed: Sep. 06, 2025. [Online]. Available: https://scholar.
google.com/
[85] A. Schwarzschild, M. Goldblum, A. Gupta, J. P. Dickerson, and T.
Goldstein, “Just how toxic is data poisoning? a unified benchmark for
backdoor and data poisoning attacks,” in Proc. Int. Conf. Mach. Learn.,
PMLR, 2021, pp. 9389–9398.
[86] G. Severi, J. Meyer, S. Coull, and A. Oprea, “Explanation-guided,”
“backdoor poisoning attacks against malware classifiers,” in Proc. 30th
USENIX Security Symp. (USENIX Security), 2021, pp. 1487–1504.
[87] A. Shafahi et al., “Poison frogs! targeted clean-label poisoning attacks
on neural networks,” Adv. Neural Inf. Process. Syst., vol. 31, pp. 6103–
6113, 2018.
[88] P. Shakarian, The sunburst hack was massive and devastating. (2021).
Accessed: Nov. 29, 2023. [Online]. Available: https://www.salon.
com/2021/01/04/the-sunburst-hack-was-massive-and-devastating--5observations-from-a-cybersecurity-expert_partner/
[89] I. Sharafaldin, A. Habibi Lashkari, and A. A. Ghorbani, “Toward
generating a new intrusion detection dataset and intrusion traffic
characterization,” in Proc. ICISS, 2018, pp. 108–116.
[90] I. Sharafaldin, A. Habibi Lashkari, S. Hakak, and A. A. Ghorbani,
“Developing realistic distributed denial of service (DDOS) attack
dataset and taxonomy,” in Proc. Int. Carnahan Conf. Secur. Technol.
(ICCST), Piscataway, NJ, USA: IEEE Press, 2019, pp. 1–8.
[91] Y. Shi and Y. E. Sagduyu, “Evasion and causative attacks with adversarial deep learning,” in Proc. IEEE Mil. Commun. Conf. (MILCOM),
Piscataway, NJ, USA: IEEE Press, 2017, pp. 243–248.
[92] A. Shiravi, H. Shiravi, M. Tavallaee, and A. A. Ghorbani, “Toward
developing a systematic approach to generate benchmark datasets for
intrusion detection,” Comput. Secur., vol. 31, no. 3, pp. 357–374,
2012.
[93] N. Shone, T. N. Ngoc, V. D. Phai, and Q. Shi, “A deep learning
approach to network intrusion detection,” IEEE Trans. Emerg. Topics
Comput. Intell., vol. 2, no. 1, pp. 41–50, Feb. 2018.
[94] J. Song, H. Takakura, Y. Okabe, M. Eto, D. Inoue, and K. Nakao,
“Statistical analysis of honeypot data and building of Kyoto 2006+
dataset for NIDS evaluation,” in Proc. First Workshop Building Analysis
Datasets Gathering Experience Returns Security, 2011, pp. 29–36.
[95] Percentage of global population accessing the internet by April 2024.
(2024). Accessed: Jun. 04, 2024. [Online]. Available: https://www.
statista.com/statistics/325706/global-internet-user-penetration/

SAINI et al.: CONTRAST DUALITY OF ADVERSARIAL LEARNING IN NETWORK INTRUSION

[96] H. Sun, T. Zhu, Z. Zhang, D. Jin, P. Xiong, and W. Zhou, “Adversarial
attacks against deep generative models on data: a survey,” IEEE Trans.
Knowl. Data Eng., vol. 35, no. 4, pp. 3367–3388, Apr. 2023.
[97] C. Szegedy, W. Zaremba, I. Sutskever, J. Bruna, D. Erhan, I. Goodfellow, and R. Fergus. Intriguing properties of neural networks, 2013,
arXiv:1312.6199.
[98] K. Talty, J. Stockdale, and N. D. Bastian, “A sensitivity analysis of
poisoning and evasion attacks in network intrusion detection system
machine learning models,” in Proc. IEEE Mil. Commun. Conf. (MILCOM), Piscataway, NJ, USA: IEEE Press, 2021, pp. 1011–1016.
[99] M. Tavallaee, E. Bagheri, W. Lu, and A. A. Ghorbani, “A detailed
analysis of the KDD cup 99 data set,” in Proc. IEEE Symp. Comput.
Intell. Security Defense Appl., Piscataway, NJ, USA: IEEE Press, 2009,
pp. 1–6.
[100] A. Thakkar and R. Lohiya, “A review of the advancement in intrusion
detection datasets,” Procedia Comput. Sci., vol. 167, pp. 636–645, Apr.
2020.
[101] V. Tolpegin, S. Truex, M. E. Gursoy, and L. Liu, “Data poisoning
attacks against federated learning systems,” in Proc. Comput. Security
(ESORICS): 25th Eur. Symp. Research Comput. Security (ESORICS),
Springer: Guildford, U.K., Sep. 2020, pp. 480–501.
[102] F. Tramèr, A. Kurakin, N. Papernot, I. Goodfellow, D. Boneh, and P.
McDaniel, “Ensemble adversarial training: attacks and defenses,” 2017,
arXiv:1705.07204.
[103] I. Y. Tyukin, D. J. Higham, and A. N. Gorban, “On adversarial
examples and stealth attacks in artificial intelligence systems,” in Proc.
Int. Joint Conf. Neural Netw. (IJCNN), Piscataway, NJ, USA: IEEE
Press, 2020, pp. 1–6.
[104] S. Venkatesan, H. Sikka, R. Izmailov, R. Chadha, A. Oprea, and M.
J. D. Lucia, “Poisoning attacks and data sanitization mitigations for
machine learning models in network intrusion detection systems,” in
Proc. IEEE Mil. Commun. Conf. (MILCOM), Piscataway, NJ, USA:
IEEE Press, 2021, pp. 874–879.
[105] J. Vitorino, I. Praça, and E. Maia, “SOK: Realistic adversarial attacks
and defenses for intelligent network intrusion detection,” Comput.
Secur., vol. 134, 2023, Art. no. 103433.
[106] B. Wang, et al., “Neural cleanse: Identifying and mitigating backdoor
attacks in neural networks,” in Proc. IEEE Symp. Secur. Privacy (SP),
Piscataway, NJ, USA: IEEE Press, 2019, pp. 707–723.
[107] Y. Wang, Y. Jiang, and J. Lan, “Intrusion detection using few-shot
learning based on triplet graph convolutional network,” J. Web Eng.,
vol. 20, no. 5, pp. 1527–1552, 2021.
[108] Y. Wang, D. J. Miller, and G. Kesidis, “When not to classify: Detection
of reverse engineering attacks on DNN image classifiers,” in Proc.
IEEE Int. Conf. Acoust., Speech Signal Process. (ICASSP), Piscataway,
NJ, USA: IEEE Press, 2019, pp. 8063–8066.
[109] Y. Wang, P. Mianjy, and R. Arora, “Robust learning for data poisoning
attacks,” in Proc. Int. Conf. Mach. Learn. (PMLR), 2021, pp. 10859–
10869.
[110] Z. Wang, M. Song, S. Zheng, Z. Zhang, Y. Song, and Q. Wang,
“Invisible adversarial attack against deep neural networks: An adaptive
penalization approach,” IEEE Trans. Dependable Secure Comput., vol.
18, no. 3, pp. 1474–1488, May/Jun. 2019.
[111] D. Warde-Farley and I. Goodfellow, “11 adversarial perturbations of
deep neural networks,” Perturbations, Optim., Statist., vol. 311, no. 5,
pp. 311–342, 2016.
[112] Z. Xiang, D. J. Miller, and G. Kesidis, “Reverse engineering imperceptible backdoor attacks on deep neural networks for detection
and training set cleansing,” Comput. Secur., vol. 106, 2021, Art. no.
102280.
[113] C. Xu, J. Wang, Y. Tang, F. Guzmán, B. I. P. Rubinstein, and T. Cohn,
“Targeted poisoning attacks on black-box neural machine translation,”
2020, arXiv:2011.00675.
[114] H. Xu et al., “Adversarial attacks and defenses in images, graphs
and text: A review,” Int. J. Autom. Comput., vol. 17, pp. 151–178,
Apr. 2020.
[115] C. Young, J. Svoboda, and J. Zambreno, “Towards reverse engineering
controller area network messages using machine learning,” in Proc.
IEEE 6th World Forum Internet Things (WF-IoT), Piscataway, NJ,
USA: IEEE Press, 2020, pp. 1–6.
[116] C. Zhang, X. Costa-Pérez, and P. Patras, “Tiki-taka: Attacking
and defending deep learning-based intrusion detection systems,” in
Proc. ACM SIGSAC Conf. Cloud Comput. Secur. Workshop, 2020,
pp. 27–39.

3067

[117] C. Zhang, X. Costa-Perez, and P. Patras, “Adversarial attacks against
deep learning-based network intrusion detection systems and defense
mechanisms,” IEEE/ACM Trans. Netw., vol. 30, no. 3, pp. 1294–1311,
Jun. 2022.
[118] W. E. Zhang, Z. Quan, A. Sheng, and C. Alhazmi, “Li. Adversarial
attacks on deep-learning models in natural language processing: A
survey,” ACM Trans. Intell. Syst. Technol. (TIST), vol. 11, no. 3, pp.
1–41, 2020.
[119] X. Zhang, J. Wang, T. Wang, R. Jiang, J. Xu, and L. Zhao, “Robust
feature learning for adversarial defense via hierarchical feature alignment,” Inf. Sci., vol. 560, pp. 256–270, Dec. 2021.
[120] S. Zhou, C. Liu, D. Ye, T. Zhu, W. Zhou, and P. S. Yu, “Adversarial
attacks and defenses in deep learning: From a perspective of cybersecurity,” ACM Comput. Surv., vol. 55, no. 8, pp. 1–39, 2022.

Shalini Saini received the Ph.D. degree from Texas
A&M University, College Station, TX, USA, in
2023, and the M.S. degree from the University of
Alabama, Tuscaloosa, AL, USA, both in computer
science.
She is currently an Assistant Professor in computer science with the University of Maryland Eastern Shore, Princess Anne, MD, USA. She previously served as an Assistant Research Scientist
with the Center of Cybersecurity Innovation (CCI),
Texas A&M University–Central Texas. Her research
interests include machine learning and deep learning approaches to enhance
privacy and security in cybersecurity solutions. She is particularly interested
in addressing privacy and security challenges in emerging technologies within
cybersecurity and healthcare. Her work has been published in numerous
peer-reviewed conferences and journals, covering topics such as network
security, AI-driven healthcare security, privacy in mobile health applications,
and vulnerabilities in voice anonymity systems.

Anitha Chennamaneni received the Ph.D. degree
in business administration and information systems
and computer science from the University of Texas,
Arlington, TX, USA, in 2006.
She is currently the Chair and Professor with Subhani Department of Computer Information Systems,
Texas A&M University-Central Texas, TX and the
Director of the Center for Cybersecurity Innovation, Killeen, TX. Her research interests include
cybersecurity, artificial intelligence, deep learning,
IS security and privacy, the Internet of Things,
digital forensics, and knowledge management. Her work has been published
in many peer-reviewed journals and conferences.

Babatunde Sawyerr received the M.Sc. degree in
computer science and Ph.D. degree in computer science from the University of Lagos, Lagos, Nigeria,
in 1997 and 2010, respectively.
He joined the University of Lagos as an Assistant
Lecturer in 1999 and advanced to the position of
Associate Professor in 2023. He serves as the colead
of the Knowledge Creation Pillar for AFRETECUNILAG. His international experience includes several visiting scholarships and he was a Fulbright
Scholar-In-Residence with Texas A&M UniversityCentral Texas, TX, USA during the 2023–2024. His research interests include
design and development of nature-inspired search and optimization algorithms
for both continuous and combinatorial problems, as well as artificial intelligence, machine learning, and their practical applications.
Dr. Sawyerr is a fellow of the Nigeria Computer Society (FNCS) and
a Senior ACM Member. He is on the editorial board of the International
Journal of Mathematical Sciences and Optimization: Theory and Applications
(IJMSO) and reviews other distinguished journals. He is a Founding Member
and Research Lead for the Machine Intelligence Research Group (MIRG) and
the Mathematical Analysis and Optimization Research Group (MANORG) at
his University.
PAPER_TEXT
