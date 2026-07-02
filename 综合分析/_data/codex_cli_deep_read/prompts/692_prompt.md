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
# [692] GenFed-IDS: A Lightweight Federated Generative AI Framework for UAV Anomaly Detection in Rescue Operations
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
编号：692
题名：GenFed-IDS: A Lightweight Federated Generative AI Framework for UAV Anomaly Detection in Rescue Operations
年份：2026
DOI：10.1109/tce.2026.3658881
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2026.3658881.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：IoT、车联网、工业互联网与边缘安全、其他AI安全与跨域异常检测
相关性：强相关，分数 14
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\692.txt
- 原始字符数：43705
- 本次发送字符数：43705
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3658881

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. XX, NO. XX, 2025

1

GenFed-IDS: A Lightweight Federated Generative AI Framework for
UAV Anomaly Detection in Rescue Operations
Hafiz Muhammad Attaullah, Muhammad Ehsan, Shakila Basheer, Ala Saleh Alluhaidan

Abstract—Unmanned Aerial Vehicles are increasingly deployed
in consumer applications such as logistics, disaster recovery,
and surveillance, yet their wireless communication links remain
highly vulnerable to cyber-attacks. Traditional intrusion detection systems (IDS) often struggle in UAV environments due to
resource constraints, dynamic network conditions, and scarcity
of labeled datasets. To address these challenges, we propose
a Generative AI-enabled lightweight IDS framework tailored
for UAV communication networks. The framework integrates
hybrid Convolutional Neural Network–Gated Recurrent Unit
(CNN-GRU) autoencoders with generative augmentation and
knowledge distillation, achieving high accuracy while maintaining computational efficiency. Explainability is incorporated
via SHapley Additive exPlanations (SHAP) analysis to ensure
trustworthy and interpretable decision-making. Experimental
evaluations on a multimodal UAV dataset demonstrate stateof-the-art performance with 99.49% accuracy, 99.48% recall,
and AUROC of 0.9999, alongside a student model that reduces
model size, inference latency, and memory footprint by nearly
50%. Comparative results confirm that the proposed framework
outperforms recent IDS baselines in both detection capability and
lightweight deployment, offering a practical and scalable solution
for next-generation UAV communication networks.
Index Terms—IDS, UAV, Generative AI, Federated Learning,
Variational Autoencoder, Cyber-Physical Security.

I. I NTRODUCTION

U

NMANNED Aerial Vehicles (UAVs) are rapidly transforming modern communication and consumer electronics ecosystems. From smart city surveillance and disaster
recovery to logistics and agriculture, UAVs are increasingly
deployed in critical and consumer-centric applications [1].
These UAV systems rely heavily on wireless communication
links for command-and-control, navigation, and cooperative
tasks.
As illustrated in Fig. 1, a UAV-assisted rescue system
typically consists of a UAV platform equipped with highresolution cameras, first-aid payloads, and communication
modules. The UAV communicates securely with the Ground
Hafiz Muhammad Attaullah (ORCID: 0000-0002-4647-2607) is with the
Faculty of Computing and Informatics, Multimedia University, Cyberjaya,
Malaysia (email: attaullah@ieee.org).
Muhammad Ehsan (ORCID: 0009-0004-2494-4484) is with the Centre
of AI and Cyber Security, The ICT Global, Cyberjaya, Malaysia (email:
m.ehsan.ops@gmail.com).
Shakila Basheer (ORCID: 0000-0001-9032-9560) and Ala Saleh Alluhaidan
(ORCID: 0000-0001-6829-9705) is with the Department of Information
Systems, College of Computer and Information Sciences, Princess Nourah
bint Abdulrahman University, Riyadh 11671, Saudi Arabia (emails: sbbasheer@pnu.edu.sa, ASALIuhaidan@pnu.edu.sa).
The authors extend their appreciation to the Deanship of Scientific Research
and Libraries in Princess Nourah bint Abdulrahman University for funding
this research work through the Program for Supporting Publication in TopImpact Journals, Grant No. (SPTIF-2025-32).
Corresponding author: Shakila Basheer.

Fig. 1: Architecture of UAV-assisted rescue operations showing communication links between UAV, Ground Control Station, rescue payload, and command center.

Control Station (GCS) via a dedicated wireless link, ensuring
real-time command-and-control as well as data transmission.
Simultaneously, the UAV interacts with rescue payloads and
on-site devices such as first-aid kits and sensors through direct
communication links. The GCS, in turn, coordinates with
the central rescue command center, which oversees mission
planning and operational decisions. This architecture enables
rapid situational awareness, efficient coordination, and timely
delivery of emergency services in disaster-stricken or hard-toreach environments.
However, their open wireless medium and distributed architecture make them highly vulnerable to cyber-attacks [2].
UAV systems are vulnerable to a broad spectrum of adversarial
threats to both cyber and physical layers. On the cyber level,
the adversaries can use communication channels to interfere
with the telemetry and mission data by jamming, hacking,
or spoofing. Physically, UAVs may be tampered with or
their payload altered. Moreover, data security and operational
security are also important because mission-critical information should be confidential, authentic, and tamper-resistant
throughout rescue operations. The physical attacks to cyber
and data-oriented threats hierarchical nature of UAV threat
models requires effective security solutions that can be adapted

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3658881

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. XX, NO. XX, 2025

2

to changing environments and resource-limited UAV platforms
[3].
Secure and trustworthy UAV communication is thus essential in ensuring safe integration of UAVs in consumer and
industrial ecosystems. One of the effective defenses against
such attacks has been the Intrusion Detection Systems (IDS)
that monitors the communication traffic and detects anomalies
in it [4]. In this regards, the main protection of this study is
the communication and network level UAV channels against
jamming, spoofing, and packet-level manipulation, and the
reduction of the effects of compromised FL clients.
However, traditional IDS systems have major limitations in
UAV networks because of resource limitations, high mobility,
dynamic topology, and lack of attack datasets. Conventional
ML- and DL-based IDS methods are based on large labeled
datasets, fixed signatures, or complicated deep models, which
are not applicable to UAV networks. UAV-specific data is
limited and unbalanced, UAVs are in a highly dynamic wireless environment, and onboard devices have severe energy
and computation constraints. In addition, most IDS systems
are black boxes, which are not interpretable, which is a
requirement of mission- and safety-critical UAV operations.
Generative AI (GenAI) solves these issues with the help
of Variational Autoencoder (VAE), generative adversarial networks (GANs), diffusion models, and lightweight Transformers. It is capable of generating realistic attack traffic to alleviate
the problem of data scarcity, train compact latent features to
effectively detect anomalies, and adapt to unknown attacks
through generative-discriminative training. GenAI also enables
explainable IDS, revealing abnormal patterns, which makes
systems reliable and deployable in UAV settings.
This paper presents a Generative AI-based Intrusion Detection Framework that is specific to UAV communication
networks. An edge-deployed lightweight anomaly detection
model is trained using quantization and pruning to be energyefficient.
The major contributions of this paper are:
• We propose a GenAI-enabled IDS for UAV networks,
integrating lightweight VAE-based representation learning with GAN-driven data augmentation.
• We develop a resource-efficient detection pipeline using
pruning, quantization, and knowledge distillation for realtime UAV deployment.
• We enhance trustworthiness via explainability, employing SHapley Additive exPlanations (SHAP) and attentionbased insights for interpretable decisions.
• We conduct comprehensive evaluations, showing higher
accuracy, lower latency, and reduced energy use than
existing ML/DL baselines.
The remainder of the paper is organized as follows: Section
II reviews related work; Section III details the proposed
methodology; Section IV presents the experimental setup;
Section V discusses results; and Section VI concludes the
paper.

based on pre-defined patterns or attack signatures to detect
malicious activities and are therefore effective in known
threats but not in zero-day or new attacks. Anomaly-based
IDS observe system behavior or communication patterns and
indicate anomalies in behavior as possible intrusions. These
systems can identify new and emerging attacks and evolving
attacks, but they are usually characterized by high false alarm
rates because of dynamic environments. Hybrid IDS are a
combination of the two methods that use signature databases
and anomaly detection modules to enhance accuracy and
resilience, but these systems are generally more resourceintensive.
Recent research has investigated the design of IDS in
the IoT, UAVs, and Industry 5.0 application with growing
interest in explainability, data privacy, and generative models.
Indicatively, the article in [5] introduced a federated multiparty computation (FMPC)-based collaborative CNN model
to perform privacy-aware pneumonia diagnosis, which showed
high accuracy and maintained data confidentiality. Though the
method is mostly aimed at healthcare IoT, the role of federated
and privacy-preserving learning is emphasized in the context
of UAV communication systems. On the same note, [6] created
a explainable and robust IDS by integrating BiLSTM and
BiGRU models with SHAP-based feature attribution, which
is highly robust to poisoning attacks. Although this research
offers a basis to reliable IDS, its analysis is confined to
conventional IoT data without UAV-specific modification.
Within the context of consumer IoT security, a new framework was proposed in the article by [7] that combines offpolicy Proximal Policy Optimization (PPO) reinforcement
learning with GAN-based augmentation of DDoS detection in
healthcare IoT systems. This method showed better flexibility in changing conditions, yet its healthcare-specific dataset
shows that it is necessary to adapt to UAV conditions. In [8]
a strong generative collaborative IDS was suggested, which
integrates federated learning (FL) with differential privacy and
generative models, demonstrating encouraging outcomes on
heterogeneous edge IoT data. Nevertheless, the UAV telemetry and multi-modal communication data were not tackled
completely. Equally, a study by [9] explored a clusteringbased anomaly detection system that is improved with multicritic GANs to semi-supervised IDS to facilitate the successful
detection of rare attacks in semi-labeled datasets. This method
is particularly applicable to UAV traffic in which labeled
datasets are scarce, but UAV-specific validation has not been
studied.
Another emerging line of work focuses on adversarial
robustness and explainability. In [10], the authors presented
NonsaliencyCrossover, an explainable AI-driven adversarial
example generation strategy for IDS, where SHAP-guided
perturbations were used to evaluate and strengthen model
robustness. While promising, the study remains constrained
to conventional IoT datasets, highlighting the opportunity to
extend adversarial robustness research to UAV-based IDS.
A trustworthy intrusion detection system leveraging explainable AI was built for in-vehicle networks in [11], where
standard deep learning models displayed modest accuracy with
better interpretability and robustness. Subsequently, a GAN-

II. R ELATED W ORK
There are three broad classes of IDS, namely: signaturebased, anomaly-based, and hybrid. Signature-based IDS are

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3658881

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. XX, NO. XX, 2025

3

TABLE I: Summary of Key IDS Approaches Relevant for Generative Federated UAV and IoT Security
Ref.

Model / Approach
FedAvg, DNN

[16]
[17]

FedGen+, Generative Fed Distillation, GANs
FedGAN, WGAN-GP

Dataset Used
X-IIoTID, edge IIoTset, WUSTL-IoT-2021
Edge/IoT datasets
IVN/CAN bus datasets

[18]
[19]
[8]

FFCNN collaborative DL IDS

UAVIDS

DP-GAN, FL

Edge-IIoTset,
CIC,
TON-IoT
UAV network traffic

Human-in-the-Loop + GAN
[20]
[21]
[22]
[23]
[24]

GAN-based adversarial training
Generative Few-Shot Learning
(CDDPM, CNNBiGRU)
CNN-LSTM hybrid, IoMT
edge IDS
Conceptual Survey (GenAI,
Fed, Semantic Comms)

UAVIDS, IoFT attack
traces
CICIDS2017, CICDDoS2019
CSE-CIC-IDS2018
UAVNet,
UAVIDS,
IoT UAV datasets

Key Focus
Federated IDS with high accuracy,
privacy, and scalability
Handles non-IID, robust generative
distillation
FL GAN for privacy-preserving attack sample generation
Real-time collaborative UAV-IDS,
zero-day attack detection
FL + GAN with differential privacy
for collaborative IDS
Combines HITL and GAN to improve IDS
Robust adversarial UAV-IDS via
GAN augmentations
Few-shot generative rare-class detection
Real-time and edge-friendly blended
DL IDS
Reviews emerging GenAI, FL, and
challenges in UAV/IoT IDS

based IDS targeting automobile CAN networks was proposed
in [12], obtaining increased detection rates by adversarial
sample augmentation and deep feature extraction. Cloud-based
cybersecurity solutions harnessing CNN architectures were
given in [13], concentrating on remote detection in automotive
contexts with balanced computational costs and detection effectiveness. Collaborative blockchain-enabled IDS frameworks
boosting IoT and cloud network security while preserving
privacy were introduced in [14], merging anomaly detection
with distributed ledger technology. Lastly, a hybrid semisupervised GRU model was applied for anomaly detection
in vehicular networks in [15], demonstrating effective feature
representation and elevated accuracy in challenging traffic
settings.
A broader survey of related IDS approaches is summarized
in Table I. Several frameworks have integrated federated learning with GANs and differential privacy to enhance scalability,
data protection, and robustness across distributed IoT environments [8], [16]–[18]. Collaborative UAV-specific IDS models,
such as FFCNN-based architectures, have been proposed to
support real-time detection and zero-day attack identification
[19], though explainability and generative augmentation are
still lacking. Other studies have introduced Human-in-theLoop IDS enhanced by GAN-generated synthetic samples
[20], and adversarial training strategies to improve UAV IDS
robustness [21]. Furthermore, few-shot generative learning
approaches [22] and CNN-LSTM hybrid IDS frameworks [23]
have advanced anomaly detection in IoT networks but remain
resource-intensive for UAV deployment.
Finally, conceptual surveys [24] highlight the promise of
generative AI and federated learning in UAV and IoT security
but do not offer much experimental validation.
Overall, while recent works demonstrate significant progress
in IDS design for IoT and UAV networks, challenges remain
in addressing data scarcity, dynamic UAV communication
environments, adversarial robustness, and explainability. This
motivates our proposed Generative AI-enabled IDS framework
that specifically targets UAV communication networks with a

Limitations
FL vulnerable to poisoning attacks, limited explainability for UAV/IoT settings
Requires strong aggregation, limited
UAV evaluation, mostly IoT focus
Focus on IVN, limited UAV or multimodal IoT applicability
Missing generative augmentation, lacks
explainability components
Less explored in resource-constrained
UAV-edge environments
HITL scalability issues, needs constant
human feedback
Lacks formal FL privacy validation, attack scope narrow
Not UAV-specific, no integrated federation or GenAI pipeline
Lacks GenAI and federated learning,
focused on IoMT only
High-level overview, limited experimental UAV results

lightweight, energy-efficient, and interpretable design.
III. P ROPOSED M ETHODOLOGY
The proposed Generative AI-enabled IDS framework for
UAV communication networks is illustrated in Fig. 2. The system is composed of four stages: (i) data preprocessing, feature
engineering, and cross-validation setup; (ii) teacher–student
learning using a hybrid CNN–GRU autoencoder distilled into a
lightweight model; (iii) evaluation through federated learning,
explainable AI, and ablation studies; and (iv) export and
deployment for UAV applications. This design ensures resource efficiency while maintaining robustness against evolving threats.
First we design a lightweight Variational Autoencoder as
the core of our Generative Encoder Module (GEM). Let x̂t ∈
Rd denote the normalized feature vector corresponding to a
UAV traffic window. The encoder network f ϕ : Rd → R2k
projects x̂t into a mean vector µϕ(x̂t) ∈ Rk and a log-variance
vector log σ 2 ϕ(x̂t ) ∈ Rk which parameterize the approximate
posterior distribution as in Eq. (1) and 2:
x′ =

x − xmin
,
xmax − xmin



qϕ (zt |x̂t) = N zt ; , µϕ(x̂t), , diag(σ 2 ϕ(x̂t )) .

(1)
(2)

Latent samples are obtained via the reparameterization trick
as Eq. (3):
zt = µϕ (x̂t) + σϕ(x̂t ) ⊙ ϵ,

ϵ ∼ N (0, Ik ),

(3)

which enables gradient backpropagation through stochastic
sampling. The decoder gθ : Rk → Rd reconstructs the input
by generating a probability distribution over x̂t , as shown in
(4):

pθ (x̂t |zt ) = N µθ (zt ), σx2 Id .

(4)

The VAE is optimized by minimizing the negative Evidence
Lower Bound (ELBO), given in (5):

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3658881

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. XX, NO. XX, 2025

4

Fig. 2: Comprehensive methodology pipeline of the proposed framework, highlighting the steps.

h
i

LV AE = Eqϕ (z|x̂) ∥x̂t − µθ (zt )∥22 + β DKL qϕ (z|x̂t ) ∥ p(z) ,
(5)
where p(z) = N (0, I) is the isotropic Gaussian prior and
DKL represents the Kullback–Leibler divergence. The explicit
form of the KL divergence is expressed in (6) and compression
in (8):

f (zt ) = sign

N
X

!
αi exp

− γ∥zt − zi ∥22



−ρ ,

(11)

i=1

f (x) = φ0 +

d
X

φj xj ,

j=1
k

 1X
1 + log σj2 − µ2j − σj2 .
DKL qϕ (z|x̂t ) ∥ p(z) =
2 j=1
(6)

LGAN = Ex∼pdata [log D(x)]

 (7)
+ Ez∼pz (z), y∼p(y) log(1 − D(G(z | y))) .


θcompressed = QINT8 Pκ θteacher



,

(8)

Unlike conventional VAEs, our GEM integrates a supervised
contrastive loss that improves latent space discriminability
for IDS tasks. Specifically, given a batch of embeddings
{z1 , . . . , zB } with labels {y1 , . . . , yB }, we enforce that embeddings of the same class are pulled closer, while embeddings
of different classes are pushed apart, as defined in (9):

Lcon =

B
X
−1 X
exp(sim(zi , zp )/τ )
log PB
, (9)
|P(i)|
a=1 exp(sim(zi , za )/τ )
i=1
p∈P(i)

where P(i) is the set of positive indices sharing the same
z⊤ z
label as i, sim(zi , zj ) = ∥zii∥∥zjj ∥ is cosine similarity, and τ is
a temperature parameter controlling separation sharpness.
The complete GEM objective is thus defined in (10):
LGEM = LV AE + λLcon ,

φj =

X
S⊆{1,...,d}\{j}


|S|! (d − |S| − 1)!
fS∪{j} (x) − fS (x) .
d!
(12)

The complete pipeline is outlined in Algorithm 1, ensuring
accuracy, efficiency, and transparency in system. So, building
on these gaps, we propose a generative discriminative IDS
tailored for UAV networks. Traffic flows are first segmented
and normalized (Eq. (2)–(3)), followed by a lightweight VAE
that learns compact embeddings via reconstruction and KL
divergence (Eq. (5), Eq. (6)). A supervised contrastive loss
(Eq. (9)) further enforces class separation, leading to the joint
GEM objective (Eq. (10)).
To address scarcity and imbalance, conditional GAN augmentation (Eq. (7)) synthesizes realistic attack traffic, which
is classified using a CNN–GRU–Attention model under crossentropy training. In our federated setup, the T-TIS dataset was
partitioned across 10 virtual UAV clients, where each trained
locally for 5 epochs before aggregation. Approximately 2 000
( 1.8×) synthetic samples per attack class were generated.
For deployment, teacher networks are distilled and compressed (Eq. (8)) into a lightweight θcompressed model. Inference
relies on kernel-based anomaly scoring (Eq. (11)) with SHAP
explanations (Eq. (12)) for interpretability.

(10)

with λ balancing reconstruction fidelity against discriminative structure. This ensures that the learned latent codes is
compact for deployment on UAV and sufficiently structured
to enable downstream anomaly detection.

IV. E XPERIMENTAL S ETUP
This section describes the experimental design, datasets,
pre-processing pipeline, and evaluation metrics employed to
validate the proposed GenAI-enabled UAV IDS framework.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3658881

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. XX, NO. XX, 2025

Algorithm 1 Proposed GenFed-IDS: Generative Federated
Learning Framework
Require: UAV Dataset (T-TIS) X = {x1 , . . . , xN }, Labels
Y , Clients K
Ensure: Intrusion label ŷ, Explanation report E
// Phase 1: Preprocessing & Representation Learning
0: Xnorm ← Normalize(X) using Eq. (1)–(3)
0: Initialize VAE Encoder Eϕ , Decoder Dθ
0: while not converged do
0:
Compute reconstruction loss LV AE via Eq. (5)
0:
Compute regularization DKL via Eq. (6)
0:
Compute contrastive loss Lcon via Eq. (9)
0:
Update ϕ, θ ← ∇(LV AE + λLcon )
0: end while
// Phase 2: Generative Augmentation & Distillation
0: Train cGAN minimizing LGAN via Eq. (7)
0: Zsyn ← G(z|y) {Generate synthetic latent samples}
0: Daug ← Latent(Xnorm ) ∪ Zsyn
0: θT eacher ← TrainHybridModel(Daug )
0: θStudent ← Distill(θT eacher )
0: θdeploy ← PruneAndQuantize(θStudent ) using Eq. (8)
// Phase 3: Federated Learning & Robustness
0: for round r = 1 to R do
0:
for client k = 1 to K in parallel do
0:
θk ← LocalUpdate(θdeploy , Dk )
0:
end for
0:
θdeploy ← FedAvg({θ1 , . . . , θK })
0: end for
0: θf inal ← AdversarialTrain(θdeploy , FGSM/PGD)
// Phase 4: Inference (On-Device)
0: for new sample xt do
0:
zt ← Eϕ (xt ) {Encode input}
0:
score ← OC-SVM(zt ) using Eq. (11)
0:
if score < 0 then
0:
ŷ ← Intrusion
0:
E ← SHAP(xt , θf inal ) using Eq. (12)
0:
else
0:
ŷ ← Benign
0:
end if
0:
return ŷ, E
0: end for=0

A. Simulation Environment

All experiments were conducted on a workstation equipped
with an Intel Core i7-11800H (2.40 GHz, 8-core), 32 GB
RAM, and an NVIDIA RTX 3070 GPU (8 GB VRAM).
The implementation was carried out using Python 3.10 with
PyTorch 2.0 and supporting libraries including Scikit-learn,
Imbalanced-learn, LightGBM, and SHAP. Model quantization
and pruning experiments were conducted using ONNX Runtime and TensorFlow Lite for embedded deployment. The
complete software–hardware configuration is summarized in
Table II.

5

TABLE II: System Specifications for Experimentation
System Aspect
CPU
GPU
Operating System
RAM
Language
Libraries

Specification
Intel Core i7 (2.40 GHz, 8-core)
NVIDIA RTX 3070 (8 GB)
Windows 11
32 GB
Python 3.13
PyTorch, Scikit-learn, Pandas, NumPy, SHAP

TABLE III: Details of the T-TIS Dataset
Category
Total Samples
Target Labels
Benign
DoS Attack
Replay Attack
Evil Twin Attack
False Data Injection (FDI)
Total No. of Features

Details
Cyber: ∼54,000; Physical: ∼45,000
0: Benign, 1: DoS, 2: Replay, 3: Evil Twin, 4: FDI
Cyber: 1–9426
Physical: 9427–13717
Cyber: 13718–25389
Physical: 25390–26363
Cyber: 26364–38370
Physical: 38371–39344
Cyber: 39345–45028
Physical: 45029–50502
Cyber: 50503–53976
Physical: 53977–54784
Cyber: 37
Physical: 16

B. Dataset
We utilized the T-TIS [25], which captures both cyber and
physical telemetry of unmanned aerial vehicles under benign
and adversarial conditions as mentioned in Table III. The
dataset is collected through a UAV testbed comprising a drone,
controller, and monitoring tools, where four major cyberattacks were executed as dependent variable: de-authentication
denial-of-service (DoS), replay attacks, false data injection
(FDI), and evil twin attacks. It contains two complementary
views as Independent variables: a cyber dataset with 37
features (e.g., packet statistics, protocol metadata, and timing
information) and a physical dataset with 16 features (e.g.,
altitude, velocity, and positional data).
The dataset is well-organized and has distinct indices of
benign and attack samples, as described in the original publication, and includes over 54,000 cyber and 45,000 physical
records. In our experiments, we combined both cyber and
physical modalities to create a multimodal feature space, so
that the IDS could take advantage of cross-domain associations
between network traffic and UAV flight behavior. To maintain
the distribution of minority classes and increase resistance to
overfitting, we used stratified k-fold cross-validation to divide
the data into training, validation, and testing subsets.
C. Evaluation Metrics
The proposed UAV IDS performance is evaluated by standard classification measures, i.e. Accuracy (ACC), Precision
(PR), Recall (RE), and F1-score (F1). These are based on
the entries of the confusion matrix: True Positives (TP), True
Negatives (TN), False Positives (FP), and False Negatives
(FN).
The corresponding formulations are using Eq. 13 to 16:
ACC =

TP + TN
,
TP + TN + FP + FN

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

(13)

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3658881

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. XX, NO. XX, 2025

6

TABLE IV: Model architecture and training configuration for UAV IDS.
Dataset

Input Features

Hybrid Modules

UAV-IDS (T-ITS)

37

CNN (1D, 64) → MaxPool → GRU (128) → Autoencoder (128/64), MLP (64) (teacher); CNN (16) + GRU (32), Linear (student, pruned+quantized)

Dropout

Optimizer (lr)

Batch / Epochs†

0.3 (linear/MLP), 0.0 (CNN/GRU)

Adam (1e-4)

64 / 30 (CV)/10 (student)

† Epochs: 30 per fold main/teacher, 10 for student, all with early stopping. Data standardized, 5-fold CV, post-training (std) with quantization and pruning.

TABLE V: Performance validation of the proposed model
Metric
Accuracy
Precision
Recall
F1-score
AUROC
Validation Loss
FPR
FNR
MCC
Cohen’s Kappa

Value
0.99488
0.99490
0.99488
0.99488
0.99999
0.01415
0.00743
0.00521
0.99325
0.99428

TABLE VI: Confusion Matrix (Predicted vs Actual)
Predicted
Benign
DoS
Replay
Evil Twin
FDI

PR =

TP
,
TP + FP

(14)

RE =

TP
,
TP + FN

(15)

2 · P R · RE
,
(16)
P R + RE
Besides, Receiver Operating Characteristic (ROC) curves,
Area Under the Curve (AUC), and Confusion Matrices (CM)
are used to offer a holistic and comparative analysis.

Benign
2742.8
0.00
0.00
0.00
0.00

DoS
0.00
2511.4
36.60
0.00
0.00

Actual
Replay
0.20
17.40
2559.4
0.40
0.40

Evil Twin
0.00
0.00
0.00
2231.0
0.00

FDI
0.20
0.40
0.20
0.20
856.0

F1 =

Fig. 3: Teacher model validation loss across 5 folds and the
distilled student model’s validation accuracy.

V. R ESULTS AND D ISCUSSION
To test the performance of the proposed Generative AIenabled IDS model, the UAV data was strictly tested with
several evaluation metrics. All clients were trained locally in
5 epochs per round and global aggregation through FedAvg
was done in 20 communication rounds. As summarized in
Table V. The model had a very high accuracy of 99.49%
per cent, precision, recall and F1-score values were all above
0.994, which means that the model has balanced and reliable
classification. The model has a better discriminatory power
between benign and malicious traffic as indicated by the
AUROC of 0.999 Moreover, the low false positive rate (FPR
= 0.00743) and false negative rate (FNR = 0.00521) prove its
strength against both types of misclassification. The Matthews
Correlation Coefficient (MCC = 0.99325) and Cohen Kappa
(0.99428) support the consistency of predictions in different
types of attacks, and the low validation loss indicates the
consistency of model convergence.
The confusion matrix in Table VI gives more information
on the classification results of the five traffic classes, which are
Benign, DoS, Replay, Evil Twin, and False Data Injection. The
diagonal dominance of the matrix indicates the near-perfect
classification accuracy of all categories with only 0.2-0.4 cases
per category being misclassified, mostly between Replay and
DoS attacks. Notably, the model was able to identify all
the cases of Evil Twin and FDI attacks with insignificant
error rates, which proves the effectiveness of the model in
identifying advanced threats. All in all, these findings confirm

the capability of the model to provide very accurate, reliable,
and secure intrusion detection in real-life UAV communication
conditions.
In order to further evaluate the learning behavior, Fig. 3
shows the validation loss curves of the 5-fold cross-validation
of the teacher model.
The loss consistently decreases with epochs, confirming
smooth convergence and stable generalization across all folds.
In parallel, the same figure presents the validation accuracy
of the distilled student model. The model rapidly improves
within the first few epochs and stabilizes above 99% accuracy,
highlighting the effectiveness of knowledge distillation in
achieving lightweight yet highly accurate intrusion detection.
To interpret the decision-making of the proposed IDS,
SHAP analysis was used to identify the most important
features across all attack classes. Fig. 4 shows the top 10
features contributing to the classification of benign and malicious traffic. Features such as ip.id_x, data.len_x, and
frame.len_x had the highest impact on the model output,
showing their key role in distinguishing between normal and
abnormal UAV communications.
The color-coded bars represent contributions for each attack
category as defined in the confusion matrix (Class 0: Benign,
Class 1: DoS, Class 2: Replay, Class 3: Evil Twin, Class
4: FDI). The results indicate that while some features (e.g.,
ip.id_x) are dominant across multiple classes, others (e.g.,
tcp.window_size_x and wlan.duration_x) provide

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3658881

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. XX, NO. XX, 2025

7

detection capability, the distilled student model also demonstrated lightweight characteristics with reduced model size,
faster training and inference times, and lower GPU memory
usage.
These findings prove that the suggested framework does
not only promote the accuracy of detection but also fulfills the
essential need of resource efficiency, which is very appropriate
in UAV communication networks.
VI. C ONCLUSION

Fig. 4: SHAP summary plot of the top 10 most influential
features for benign and attack classes.
TABLE VII: Model performance and lightweight capacity
comparison between Teacher and Student models.
Attribute
Model Size
Parameters
Training Time
Total Training Time
Inference Latency
GPU Memory Usage

Teacher Model

Student Model

Unit

6.5
1.58
0.85
5.4
0.83
64

3.2
0.86
0.43
3.6
0.41
37

MB
Million
s/epoch
min
ms/sample
MB

class-specific insights. This shows that the model not only
achieves high accuracy but also learns meaningful feature
representations relevant to UAV intrusion detection.
Further, Table VII compares the performance and
lightweight capacity of the teacher and student models. The
results show that the student model is almost half the size of
the teacher model (3.2 MB vs. 6.5 MB) with fewer parameters
(0.86M vs. 1.58M). Training and inference are also faster for
the student model, with training time per epoch reduced from
0.85s to 0.43s and inference latency reduced from 0.83ms to
0.41ms per sample. In addition, the student model consumes
less GPU memory (37 MB compared to 64 MB). These results
confirm that the knowledge-distilled student model achieves a
much lighter footprint while maintaining competitive performance.
Finally, to highlight the efficiency gains and novelty, a
comparative analysis between the proposed model and baseline
IDS models was conducted in terms of the standard evaluation
metrics along with model size, computational cost, and memory footprint. As shown in Fig. 5, the proposed CNN-GRUAE framework significantly outperforms recent state-of-the-art
IDS models, including GAN-MCNN-DFS, ANN, CNN, XAIDNN, and SEMI-GRU.
In particular, the proposed model achieved the highest
accuracy (99.49%), precision (99.49%), recall (99.48%), and
F1-score (99.48%), surpassing the closest baseline (GANMCNN-DFS) by margins of 4–7%. The recall improvement is
especially important for UAV network security, as it minimizes
the chances of undetected attacks. While achieving superior

This paper has suggested a Generative AI-based lightweight
intrusion detection system that is specific to UAV communication networks. The model combines hybrid CNN-GRU
autoencoders with knowledge distillation to obtain high detection accuracy and low computational overhead. The strength
of the framework was proven by extensive experiments with
an accuracy, precision, recall, and F1-score of 99.49% and
almost perfect values of the AUROC. The confusion matrix
proved that there was little misclassification between benign
and attack classes, which proved the effectiveness of the
proposed approach.
Cross-validation revealed that the convergence was stable,
and the SHAP-based explainability demonstrated the most
significant features that influenced the classification decisions.
The distilled student model was very resource-efficient, decreasing model size, training and inference time, and GPU
memory consumption. In addition, the comparative analysis
with the current baseline IDS models showed that the proposed framework was superior in terms of performance and
efficiency.
The proposed IDS framework offers an effective and practical solution for securing UAV networks against evolving
threats. In the future, we plan to extend this work by incorporating real-time deployment on UAV platforms and exploring
reinforcement learning-based adaptive defense strategies.
R EFERENCES
[1] L. Gupta, R. Jain, and G. Vaszkun, “Survey of important issues in uav
communication networks,” IEEE Communications Surveys & Tutorials,
vol. 18, no. 2, pp. 1123–1152, 2016.
[2] A. Awadallah, K. Eledlebi, M. J. Zemerly, D. Puthal, E. Damiani,
K. Taha, T.-Y. Kim, P. D. Yoo, K.-K. Raymond Choo, M.-S. Yim, and
C. Y. Yeun, “Artificial intelligence-based cybersecurity for the metaverse: Research challenges and opportunities,” IEEE Communications
Surveys Tutorials, vol. 27, no. 2, pp. 1008–1052, 2025.
[3] B. Neupane, J. Jang, and D. S. Kim, “Explainable intrusion detection
systems: A survey,” IEEE Access, vol. 10, pp. 43 110–43 141, 2022.
[4] H. M. Attaullah, S. Memon, O. F. Erkan, and R. Khawar, “Iot based
systems and services: Recent security concerns and feasible solutions,”
in 2024 IEEE 1st Karachi Section Humanitarian Technology Conference
(KHI-HTC), IEEE. IEEE, 2024, pp. 1–6.
[5] A. A. Siddique, W. Boulila, M. S. Alshehri, F. Ahmed, T. R. Gadekallu,
N. Victor, M. T. Qadri, and J. Ahmad, “Privacy-enhanced pneumonia
diagnosis: Iot-enabled federated multi-party computation in industry
5.0,” IEEE Transactions on Consumer Electronics, vol. 70, no. 1, pp.
1923–1939, 2024.
[6] D. Javeed, T. Gao, P. Kumar, and A. Jolfaei, “An explainable and
resilient intrusion detection system for industry 5.0,” IEEE Transactions
on Consumer Electronics, vol. 70, no. 1, pp. 1342–1350, 2024.
[7] J. Yang, V. Govindarajan, L. Y. Por, Z. A. Shaikh, Q. Xin, P. Bhattacharya, A. A. Khan, and Y. Wang, “Ddos attack detection in consumer
iot-based healthcare systems using improved off-policy proximal policy
optimization and generative adversarial network,” IEEE Transactions on
Consumer Electronics, pp. 1–1, 2025.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3658881

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. XX, NO. XX, 2025

8

Fig. 5: Comparison of the proposed framework with baseline IDS models from recent studies across performance metrics

[8] W. Yao, H. Zhao, and H. Shi, “Privacy-preserving collaborative intrusion
detection in edge of internet of things: A robust and efficient deep
generative learning approach,” IEEE Internet of Things Journal, vol. 11,
no. 9, pp. 15 704–15 722, 2024.
[9] H. Wang, F. Kandah, T. Mendis, and L. Medury, “Clustering-based
intrusion detection system meets multicritics generative adversarial
networks,” IEEE Internet of Things Journal, vol. 12, no. 11, pp. 16 112–
16 128, 2025.
[10] J. Zhang, Q. Dai, X. Zhou, and L. Chen, “Nonsaliencycrossover: A
novel adversarial example generation strategy for ids using explainable
ai,” IEEE Internet of Things Journal, vol. 12, no. 18, pp. 38 680–38 696,
2025.
[11] H. Lundberg, N. I. Mowla, S. F. Abedin, K. Thar, A. Mahmood, M. Gidlund, and S. Raza, “Experimental analysis of trustworthy in-vehicle
intrusion detection system using explainable artificial intelligence (xai),”
IEEE Access, vol. 10, pp. 102 831–102 841, 2022.
[12] G. Xie, L. T. Yang, Y. Yang, H. Luo, R. Li, and M. Alazab, “Threat
analysis for automotive can networks: A gan model-based intrusion
detection technique,” IEEE Transactions on Intelligent Transportation
Systems, vol. 22, no. 7, pp. 4467–4477, 2021.
[13] G. Loukas, T. Vuong, R. Heartfield, G. Sakellari, Y. Yoon, and D. Gan,
“Cloud-based cyber-physical intrusion detection for vehicles using deep
learning,” IEEE Access, vol. 6, pp. 3491–3508, 2018.
[14] O. Alkadi, N. Moustafa, B. Turnbull, and K.-K. R. Choo, “A deep
blockchain framework-enabled collaborative intrusion detection for protecting iot and cloud networks,” IEEE Internet of Things Journal, vol. 8,
no. 12, pp. 9463–9472, 2021.
[15] G. ALMahadin, Y. Aoudni, M. Shabaz, A. V. Agrawal, G. Yasmin, E. S.
Alomari, H. M. R. Al-Khafaji, D. Dansana, and R. R. Maaliw, “Vanet
network traffic anomaly detection using gru-based deep learning model,”
IEEE Transactions on Consumer Electronics, vol. 70, no. 1, pp. 4548–
4555, 2024.
[16] S. I. Popoola, A. L. Imoize, M. Hammoudeh, B. Adebisi, O. Jogunola,
and A. M. Aibinu, “Federated deep learning for intrusion detection in
consumer-centric internet of things,” IEEE Transactions on Consumer
Electronics, vol. 70, no. 1, pp. 1610–1622, 2024.
[17] Z. Li, W. Yao, J. Luo, and Z. Huang, “Flow-based iot intrusion detection
via improved generative federated distillation learning,” IEEE Internet
of Things Journal, vol. 12, no. 10, pp. 14 797–14 811, 2025.
[18] M. Chen, B. Wu, H. Sun, and Z. Wang, “Fedgan-id: Federated-learningbased intrusion detection for in-vehicle network using gans,” IEEE
Internet of Things Journal, vol. 12, no. 17, pp. 36 155–36 167, 2025.
[19] H. Jalil Hadi, Y. Cao, S. Li, Y. Hu, J. Wang, and S. Wang, “Realtime collaborative intrusion detection system in uav networks using deep
learning,” IEEE Internet of Things Journal, vol. 11, no. 20, pp. 33 371–
33 391, 2024.
[20] Q. Zeng and F. Nait-Abdesselam, “Enhancing uav network security: A
human-in-the-loop and gan-based approach to intrusion detection,” IEEE
Internet of Things Journal, vol. 12, no. 12, pp. 20 870–20 884, 2025.
[21] T. Gaber, T. Ali, M. Nicho, and M. Torky, “Robust attacks detection
model for internet of flying things based on generative adversarial
network (gan) and adversarial training,” IEEE Internet of Things Journal,
vol. 12, no. 13, pp. 23 961–23 974, 2025.
[22] Z. Zhang, P. Wang, T. Zhang, M. Liu, and X. Zhou, “Trustworthy
generative few-shot learning-based intrusion detection method in internet
of things,” IEEE Transactions on Consumer Electronics, vol. 71, no. 1,
pp. 1992–2002, 2025.
[23] J. A. Alzubi, O. A. Alzubi, I. Qiqieh, and A. Singh, “A blended deep
learning intrusion detection framework for consumable edge-centric iomt
industry,” IEEE Transactions on Consumer Electronics, vol. 70, no. 1,
pp. 2049–2057, 2024.
[24] Z. Kaleem, F. A. Orakzai, W. Ishaq, K. Latif, J. Zhao, and A. Jamalipour,
“Emerging trends in uavs: From placement, semantic communications
to generative ai for mission-critical networks,” IEEE Transactions on
Consumer Electronics, pp. 1–1, 2024.
[25] S. C. Hassler, U. A. Mughal, and M. Ismail, “Cyber-physical intrusion
detection system for unmanned aerial vehicles,” IEEE Transactions on
Intelligent Transportation Systems, vol. 25, no. 6, pp. 6106–6117, 2024.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.
PAPER_TEXT
