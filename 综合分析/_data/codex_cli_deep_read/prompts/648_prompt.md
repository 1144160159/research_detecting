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
# [648] Divergence-Regularized Federated GANs for Effective Cyber-Attack Detection on Non-IID and Unlabeled Edge Activity Data
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
编号：648
题名：Divergence-Regularized Federated GANs for Effective Cyber-Attack Detection on Non-IID and Unlabeled Edge Activity Data
年份：2026
DOI：10.1109/tii.2026.3666264
来源：IEEE Transactions on Industrial Informatics
PDF：paper/10.1109_TII.2026.3666264.pdf
已有粗分类：联邦学习、隐私保护与分布式协同
二级关联：恶意流量、暗网与攻击检测
相关性：中相关，分数 6
已有代码状态：候选不可访问；FedGAD

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\648.txt
- 原始字符数：55891
- 本次发送字符数：55891
- 是否截断：False

代码包：
- 仓库：FedGAD
  - URL：https://github.com/TII-25-8978/FedGAD
  - 状态：failed
  - 本地目录：source\FedGAD
  - 顶层结构：
  - 主要语言：
  - README 标题：
  - README 运行线索：
  - 关键文件：{}
  - 数据集线索：

论文正文包开始：
<<<PAPER_TEXT
5004

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 6, JUNE 2026

Divergence-Regularized Federated GANs for
Effective Cyber-Attack Detection on Non-IID
and Unlabeled Edge Activity Data
Zeseya Sharmin , Graduate Student Member, IEEE, Md. Palash Uddin ,
Yong Xiang , Senior Member, IEEE, Feifei Chen , Jine Tang, and Yushu Zhang , Senior Member, IEEE

Abstract—Edge computing enables real-time Internet of
Things data processing by bringing computation closer
to data sources, but its distributed architecture creates
cybersecurity vulnerabilities requiring privacy-preserving
attack detection mechanisms capable of handling
heterogeneous data distributions. This article proposes
federated generative adversarial divergence (FedGAD), a
plug-and-play modular framework that enhances existing
federated learning methods through Jacobian-based
regularization and dynamic complexity-aware weighting
to address cyber-attack detection in non-independent
and identically distributed (IID) and unlabeled edge data
environments. Unlike existing approaches suffering from
mode collapse and training instability, FedGAD maintains
statistical consistency across distributed nodes through
gradient-based stability mechanisms, supported by
rigorous theoretical analysis establishing convergence
guarantees and mode coverage properties. We conduct
comprehensive experiments comparing FedGAD against
four federated generative learning baselines federated
trustworthy (FedTrust), anomaly detection generative
adversarial network (ADGAN), federated generative
adversarial network for intrusion detection system
(FedGAN-IDS), and federated temporal sequential recurrent
generative network (FedTSRGNet) and four regularizationbased methods federated averaging (FedAvg), federated
proximal (FedProx), learning with collaborative aggregation
method (LeCam), and Jensen Shannon (JS) Divergence
on telemetry data of networks - internet of things
(ToN_IoT) and Communications Security Establishment
in Canadian Institute for Cybersecurity - Intrusion
Detection System (CSE_CIC_IDS) datasets, demonstrating
FedGAD’s superiority with accuracy improvements up to
3.5%, achieving 100% mode coverage compared to 25%
Received 15 December 2025; revised 28 January 2026; accepted 15
February 2026. Date of publication 3 March 2026; date of current version
5 June 2026. This work was supported by the Australian Research
Council under Grant LP190100594 and Grant DP220100983. Paper
no. TII-25-8978. (Corresponding author: Yong Xiang.)
Zeseya Sharmin, Md. Palash Uddin, Yong Xiang, and Feifei Chen
are with the School of Information Technology, Deakin University, Geelong, VIC 3220, Australia (e-mail: z.sharmin@deakin.edu.au; m.uddin@
deakin.edu.au; yong.xiang@deakin.edu.au; feifei.chen@deakin.edu.
au).
Jine Tang is with the School of Artificial Intelligence, Hebei University
of Technology, Tianjin 300401, China (e-mail: tangjine@hebut.edu.cn).
Yushu Zhang is with the School of Computing and Artificial Intelligence, Jiangxi University of Finance and Economics, Nanchang
330013, China (e-mail: zhangyushu@jxufe.edu.cn).
Code is available online at: https://github.com/TII-25-8978/FedGAD.
Digital Object Identifier 10.1109/TII.2026.3666264

for baseline methods while maintaining computational
efficiency for resource-constrained edge deployments.
Index Terms —Cyber-attack detection, edge computing (EC), federated learning (FL), generative adversarial
networks, Jacobian regularization, non-independent and
identically distributed (IID) data.

I. INTRODUCTION
DGE computing (EC) processes data locally at edge
servers, enabling real-time processing for Internet of
Things (IoT) applications [1]. This reduces latency, conserves
bandwidth, and enhances privacy for autonomous vehicles,
healthcare systems, smart grids, and remote monitoring. The
global EC market is projected to reach USD 155.90 billion
by 20301 or USD 5132.29 billion by 2034.2 However, EC’s
distributed architecture is susceptible to denial of service (DoS)
attacks, man-in-the-middle attacks, and advanced persistent
threats [2], [3], necessitating intelligent detection mechanisms
for EC environments.
Traditional centralized intrusion detection system (IDS) [4]
are inadequate for EC, requiring centralized data collection that
violates privacy and creates scalability bottlenecks [5], while
struggling with high-dimensional, unlabeled, non-independent
and identically distributed (IID) data from diverse edge devices [6]. Federated learning (FL) addresses these limitations by
enabling collaborative model training across edge nodes without
data sharing [7]. Using federated averaging (FedAvg) [8], FL
aggregates local models to create a global model. However, classical FL performs poorly on non-IID and unlabeled data, leading
to suboptimal detection performance. Recent machine learning
advances show promise in automating attack detection [9], but
fail under unlabeled and non-IID conditions. To overcome these
challenges, researchers have integrated generative adversarial
networks (GANs) with FL [10], [11], where generators model
data distributions and discriminators distinguish real from synthetic samples to compensate for data imbalances.
Traditional centralized detection systems face the following
three fundamental challenges in ECs:

E

1 [Online]. Available: https://www.grandviewresearch.com/press-release/
global-edge-computing-market
2 [Online].
Available:
https://www.precedenceresearch.com/edgecomputing-market

1941-0050 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html
for more information.

SHARMIN et al.: DIVERGENCE-REGULARIZED FEDERATED GANS FOR EFFECTIVE CYBER-ATTACK DETECTION ON NON-IID

1) privacy violations through mandatory data centralization;
2) scalability bottlenecks due to bandwidth constraints;
3) inability to handle unlabeled and heterogeneous non-IID
data from diverse edge devices.
While FL addresses privacy, existing FL-GAN approaches
suffer from mode collapse under non-IID conditions, failing to
capture attack pattern diversity, especially for rare sophisticated
attacks. This worsens with unlabeled data common in edge
deployments.
Despite this integration, FL-GAN approaches face fundamental issues with non-IID data. Heterogeneous client distributions
prevent GANs from learning unified representations of global
data diversity. This leads to mode collapse, where generators
produce limited output varieties, failing to capture complete data
distributions [12]. The problem intensifies in federated settings
due to the absence of global labels. This can cause training
instability and poor generalization [13]. Existing solutions like
mini-batch discrimination and feature matching introduce computational overhead or require labels, making them unsuitable
for resource-constrained edge environments [14].
To overcome these challenges, this article proposes federated
generative adversarial divergence (FedGAD), which advances
beyond existing FL-GAN frameworks by directly addressing
the three fundamental limitations in ECs by preserving privacy
through fully decentralized training. This ensures scalability
via efficient model aggregation without raw data transmission
and handling unlabeled non-IID data through unsupervised adversarial learning with heterogeneity-aware mechanisms. We
achieve these solutions through the following four key technical
contributions.
1) We introduce a differential geometric regularization technique that directly regularizes the generator’s Jacobian
matrix to prevent mode collapse and enhance attack pattern diversity. Unlike prior works [15] that apply Jacobian
regularization to supervised discriminative models, we
pioneer its integration within unsupervised federated adversarial training, demonstrating its effectiveness in maintaining statistical consistency between heterogeneous local and global distributions without requiring labeled
data.
2) Unlike the fixed regularization coefficients in federated
temporal sequential recurrent generative network (FedTSRGNet) [16] and federated generative adversarial network for intrusion detection system (FedGAN-IDS) [11],
we propose a dynamic weighting mechanism that adapts
regularization strength to local data complexity at each
edge node. This heterogeneity-aware approach effectively mitigates the non-IID induced mode collapse that
plagues existing static methods.
3) We provide rigorous mathematical analysis establishing
the following:
a) Lipschitz continuity guarantees through gradient
penalty stability (Theorem 4.1);
b) almost-sure convergence to stationary points under
federated settings (Theorem 4.2);
c) enhanced mode coverage proofs (Theorem 4.3).
This theoretical foundation distinguishes our work from
empirically driven approaches.

5005

4) We design FedGAD as a modular framework that can be
seamlessly integrated with existing federated methods,
enhancing their performance without architectural modifications. To validate this extensibility, we conduct comprehensive experiments integrating FedGAD with four
state-of-the-art approaches, such as federated trustworthy
(FedTrust) [17], anomaly detection generative adversarial
network (ADGAN) [18], FedGAN-IDS [11], and FedTSRGNet [16], demonstrating consistent performance
improvements over their original implementations across
multiple evaluation metrics and heterogeneity scenarios.
The rest of this article is organized as follows. Section II
provides a critical analysis of the literature. We then present our
proposed FedGAD approach in Section III. Section IV derives
theoretical convergence guarantees. In Section V, we provide
the experimental setup and results on real-world public datasets.
Finally, Section VI concludes this article.
II. RELATED WORK
Recent years have seen significant efforts to improve cyberattack detection in EC environments using FL- and GAN-based
approaches. These techniques aim to address the limitations
of centralized, rule-based systems in decentralized, privacysensitive, and heterogeneous settings. This section critically examines the existing literature, identifies its fundamental limitations, and positions our contributions within the current research
landscape.
A. FL for Intrusion Detection
Several studies have proposed FL-based IDS solutions tailored for EC. Rajarajan et al. [19] introduced an explainable federated framework for secure and privacy-preserving
IDS in vehicular edge networks, highlighting the importance of interpretability under adversarial conditions. Similarly,
Friha et al. [20] proposed a decentralized FL-based IDS for
edge devices, and Chen et al. [21] presented a multimodal
privacy-preserving FL approach for critical IoT systems. Recent
advances include a comprehensive framework [22] that has
been developed for an optimal FL-based intrusion detection
specifically optimized for IoT environments. However, these
approaches share a critical limitation: they rely on the standard
FedAvg aggregation [8], which assumes relatively homogeneous
data distributions. Under severe non-IID conditions common
in EC, where different nodes observe vastly different attack
patterns, model updates can diverge significantly, leading to
biased global models and degraded detection accuracy [23], [24].
Furthermore, these methods require substantial labeled data for
supervised training, which is often unavailable or expensive to
obtain in dynamic edge environments.
B. Federated GANs and Mode Collapse
To handle data distribution challenges, researchers have integrated GANs into FL frameworks [17]. Xiong et al. [10]
proposed a distributed generative model for heterogeneous
data using local generators, while Tabassum et al. [11]
introduced FedGAN-IDS, a privacy-preserving framework

5006

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 6, JUNE 2026

combining GANs with FL for intrusion detection. Recent survey
work [25] analyzing FL-based intrusion detection in medical
IoT highlighted FLIDS systems achieving over 99% detection
accuracy through GAN-FL integration.
Despite these promising results, FedGAN-IDS suffers from
fundamental mode collapse under non-IID conditions, where
local generators training on skewed distributions fail to learn
comprehensive global data representations, producing synthetic
samples that cluster around dominant modes while missing
rare attack types particularly severe in cybersecurity where rare
sophisticated attacks (e.g., advanced persistent threats) are precisely the patterns that must be detected. Various strategies have
been explored to mitigate mode collapse, but face critical limitations for edge deployments. Mini-batch discrimination [14]
introduces significant computational overhead unacceptable for
resource-constrained edge nodes. Feature matching requires
careful hyperparameter tuning and can destabilize in federated
settings with heterogeneous hardware. Unrolled GANs [26]
improve stability but incur 3–5× higher gradient computation,
making them impractical for edge devices. Spectral normalization [27] constrains discriminator Lipschitz constants but
lacks adaptive mechanisms for varying data distributions across
clients.
C. FL With Regularization
Federated proximal (FedProx) [23] addresses heterogeneity
through proximal terms that limit local model deviation from
the global model. While effective for supervised learning with
labeled data, FedProx provides no mechanism for handling
mode collapse in generative models; its proximal regularization operates on model parameters rather than data manifolds.
SCAFFOLD [28] uses control variates to correct client drift
but similarly assumes supervised objectives and fails to address
generative training instabilities.
D. Regularization Techniques in Federated GANs
Regularization has emerged as a critical mechanism for
stabilizing federated GAN training, though existing approaches
remain limited in simultaneously addressing mode collapse,
convergence guarantees, and edge deployment requirements.
Gradient penalty methods, such as WGAN-GP [12] enforce
Lipschitz continuity but are poorly suited to federated settings. Federated GAN-based approaches, such as FedTrust [17],
ADGAN [18], and FedGAN-IDS [11]. More recently, FedTSRGNet [16] combines bidirectional long short-term memory (Bi-LSTM), temporal convolutional networks (TCN), and
GANs for cyber-attack detection. However, it employs only
static regularization without adaptation to local data complexity,
providing no theoretical analysis of convergence properties or
mode coverage guarantees. Our work fundamentally differs in
the following:
1) introducing adaptive Jacobian regularization that dynamically adjusts to local distribution heterogeneity;
2) providing rigorous theoretical guarantees for convergence
and mode coverage;
3) demonstrating through ablation studies that our regularization mechanism specifically addresses mode collapse

TABLE I
COMPARISON OF FEDGAD WITH RELATED WORKS

Fig. 1. Overview of the proposed FedGAD pipeline. (a) Attacker injects
malicious data into the edge server that communicates with edge/IoT
devices. (b) Both labeled and unlabeled data are collected for training.
(c) Generator combines Bi-LSTM and TCN blocks to capture temporal dependencies, while the discriminator distinguishes real and fake
samples. The overall loss combines adversarial and reconstruction
objectives.

by achieving 100% mode coverage versus 0% missing
modes compared to FedTSRGNet’s incomplete coverage.
Table I provides a systematic comparison of FedGAD and representative prior works. Unlike existing approaches, FedGAD
combines the following:
1) distribution-aware adaptive regularization;
2) theoretical convergence guarantees for nonconvex federated adversarial training;
3) mode collapse mitigation without labeled data requirements;
4) computational efficiency suitable for edge deployment.
III. PROPOSED METHODOLOGY
This section presents the proposed FedGAD framework for
cyber-attack detection in heterogeneous and unlabeled edge
data environments. Building upon the FedTSRGNet baseline,
FedGAD introduces Jacobian-based regularization and adaptive
weighting mechanisms to overcome instability and mode collapse commonly encountered in federated generative adversarial
networks. We provide detailed architectural descriptions, algorithmic procedures with step-by-step explanations, and comprehensive complexity analysis. The overall architecture and
federated training pipeline are illustrated in Fig. 1.
A. FedTSRGNet and Motivating Limitations
FedTSRGNet integrates a temporal sequence recurrent network with a GAN in an FL setting for cyber-attack detection. As
shown in Fig. 1, it comprises a generator G and a discriminator
D. The generator processes input data through an embedding
layer, followed by a Bi-LSTM encoder with TCN blocks using
rectified linear unit (ReLU) activation, weight normalization,

SHARMIN et al.: DIVERGENCE-REGULARIZED FEDERATED GANS FOR EFFECTIVE CYBER-ATTACK DETECTION ON NON-IID

and dilated convolutions, along with dropout and sequentially
synthesis data (SSD) modules for sequential synthesis. The
discriminator evaluates both real (labeled or unlabeled) and generated samples, applying a regularizer λ to guide training. The
model leverages multiple loss functions (LG , LD , LSSD , Lreg ,
Ltotal ) to learn and generate synthetic attack patterns effectively.
Despite the strengths of FedTSRGNet, it suffers from performance degradation in the presence of non-IID and unlabeled
data, which are inherent in real-world edge environments. In
particular, the generator in the GAN component tends to experience mode collapse, generating a narrow set of outputs that fail
to represent the full diversity of cyber-attack patterns. This problem is further exacerbated by the absence of global labels and
highly skewed local data distributions across clients, resulting
in unstable training and suboptimal global model performance.
B. Problem Formulation and Design Objective
Let i = {1, 2, . . . , N } be the set of participating edge nodes,
(i) i
where each node i ∈ N holds a local dataset Di = {xj }nj=1
drawn from a unique distribution pi (x). Due to variations in
infrastructure, attack types, and local contexts, the divergence
between any two local distributions is typically large, formally
expressed as DKL (pi (x)|pj (x))  0 for i = j, where DKL denotes the Kullback–Leibler divergence [29]. This divergence
results in non-IID conditions that significantly hinder the effectiveness of classical FL techniques and exacerbate instability
in adversarial training. The original FedTSRGNet employs a
generator network Gθ : Rd → Rm parameterized by θ, which
generates synthetic data from a latent dimension space d, and
a discriminator network Dφ : Rm → [0, 1] parameterized by φ,
which attempts to differentiate between real and generated data
in the dimension feature space m. Under non-IID conditions,
adversarial training becomes unstable, and the generator tends
to collapse, producing only a few repetitive patterns. To address
this, we propose an enhanced architecture called FedGAD that
incorporates geometric regularization and an adaptive training
protocol.
C. FedGAD Architecture
FedGAD extends FedTSRGNet through the following three
key architectural innovations.
1) Generator architecture: The generator Gθ employs a
hybrid architecture combining embedding layers (dimension demb = 128), Bi-LSTM layers (hidden size hlstm =
256), and TCN blocks with exponentially increasing dilation rates {1, 2, 4, 8}. This design captures both longterm temporal dependencies through Bi-LSTM and finegrained local patterns through dilated convolutions. The
SSD (sequential synthesis data) module generates synthetic samples through attention mechanisms, enabling
focus on relevant attack signatures.
2) Discriminator with Jacobian regularization: Unlike standard discriminators, our discriminator Dφ incorporates
gradient computation layers that enable Jacobian penalty
calculation. The architecture consists of the following:
a) input processing layers (Conv1D, BatchNorm);
b) feature extraction blocks;

5007

Algorithm 1: Model Training in FedGAD (Client-Side).
Require: Local dataset Di , local epochs E, learning rates
ηG , ηD , global parameters θ(t) , φ(t) , base regularization
λbase
(t+1)
(t+1)
Ensure: Updated local parameters θi
, φi
,
complexity measure Ci
1: // Phase 1: Initialization
(t)
(t)
2: θi ← θ(t) , φi ← φ(t) Download global
parameters
3: // Phase 2: Compute local data complexity
4: Compute local distribution complexity Ci via kernel
density estimation:

5: Ci = |D1i | x∈Di ∇x log p̂i (x)22
6: // Phase 3: Receive adaptive weight from server
7: Receive λJ,i from server based on (2)
8: for epoch e = 1 to E do
9:
// Phase 4: Data sampling
10:
Sample mini-batch Bi ⊂ Di of real attack patterns
11:
Sample latent vectors Z ∼ N (0, Id ) from latent
distribution
12:
// Phase 5: Generator update
13:
Generate fake samples: x̃ = Gθ(t) (z) for z ∈ Z
i
14:
Compute generator loss:
LG = Ez [log(1 − Dφ(t) (Gθ(t) (z)))]
i

15:
16:
17:
18:
19:
20:
21:
22:
23:
24:

(t)

i

(t)

Update generator: θi ← θi − ηG ∇θ LG
// Phase 6: Discriminator update with Jacobian
penalty
Compute adversarial loss:
=
Lorig
D
−Ex∈Bi [log Dφi (x)] − Ez [log(1 − Dφi (Gθi (z)))]
Compute Jacobian
penalty:

RJ = |B1i | x∈Bi ∇x Dφi (x)22
Update discriminator:
(t)
(t)
+ λJ,i RJ ]
φi ← φi − ηD ∇φ [Lorig
D
end for
// Phase 7: Upload to server
(t+1)
(t+1)
, φi
, and Ci to central server
Upload θi
(t+1)
(t+1)
returnUpdated parameters θi
, φi
, complexity
Ci

c) gradient computation module for ∇x Dφ (x);
d) classification head outputting probability scores in
[0,1].
This design ensures efficient gradient flow for both adversarial training and regularization.
3) Adaptive weighting module: Each edge node computes local complexity Ci using kernel density estimation over mini-batches, approximating ∇x log pi (x)22 .
¯ σC )
The central server maintains running statistics (C,
and computes node-specific weights via (2), enabling
heterogeneity-aware regularization strength adjustment.
D. FedGAD Regularized Training
FedGAD expands the FedTSRGNet framework by integrating
Jacobian-based regularization into the discriminator to improve

5008

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 6, JUNE 2026

Algorithm 2: Model Aggregation in FedGAD (ServerSide).
Require: Edge nodes N = {1, . . . , N }, communication
rounds T , base regularization λbase , scaling parameter α,
convergence threshold 
Ensure: Global generator Gθ∗ and discriminator Dφ∗
1: // Phase 1: Initialization
2: Initialize θ(0) , φ(0) randomly
3: Initialize C¯ ← 0, σC ← 1
4: for round t = 0 to T − 1 do
5:
// Phase 2: Broadcast to clients
6:
Broadcast θ(t) , φ(t) to all nodes i ∈ N
7:
// Phase 3: Compute and broadcast adaptive weights
8:
for each node i ∈ N do
9:
Compute adaptive weight using (2):
¯
10:
λJ,i = λbase · (1 + α · Ciσ−C C )
11:
Send λJ,i to node i
12:
end for
13:
// Phase 4: Wait for client updates
14:
Execute Algorithm 1 at each client
(t+1)
(t+1)
, φi
, Ci } from all i ∈ N
15:
Receive {θi
16:
// Phase 
5: Update global complexity statistics
N
Ci
17:
C¯ ← N1
 i=1

N
1
¯2
18:
σC ←
(Ci − C)
N

19:
20:
21:
22:
23:
24:
25:
26:
27:

i=1

// Phase 6: Weighted aggregation

|Di | (t+1)
θ(t+1) = N
i=1 |D| θi

|Di | (t+1)
φ(t+1) = N
i=1 |D| φi
// Phase 7: Convergence check
if θ(t+1) − θ(t) 2 + φ(t+1) − φ(t) 2 <  then
break Convergence achieved
end if
end for
return Gθ(T ) , Dφ(T )

training stability and prevent mode collapse. During each
communication round t, edge node i downloads the current
global model parameters θ(t) and φ(t) from the central server.
The node then computes a local distribution complexity measure
Ci using kernel density estimation, which captures the inherent
heterogeneity of its local data distribution pi (x). During local
training, the generator continues to update its parameters using
the standard adversarial loss. In contrast, the discriminator
incorporates a Jacobian regularization term defined as


(1)
RJ (x; φ) = λJ Ex∼pdata ∇x Dφ (x)22
where λJ > 0 is the regularization coefficient. This term
penalizes large gradients and encourages Lipschitz continuity,
thereby preventing sharp decision boundaries and supporting
smoother transitions between data modes. To accommodate
varying degrees of heterogeneity across nodes, we introduce an
adaptive weighting scheme where the regularization coefficient
for each node is computed as


Ci − C¯
(2)
λJ,i = λbase · 1 + α ·
σC


where Ci = |D1i | x∈Di ∇x log pi (x)22 with C¯ and σC
represent the global mean and standard deviation of local
complexity scores, respectively. This dynamic adjustment
ensures that edge nodes with more complex or diverse data
distributions receive proportionally stronger regularization.
(t+1)
are updated via
Now, the generator parameters θi
(t+1)

θi

(t)

= θi − ηG ∇θ Ez∼pz [log(1 − Dφ(t) (Gθ(t) (z)))] (3)
i

i

(t+1)
are updated
and the regularized discriminator parameters φi

via
(t+1)

[b]φi

(t)

(t)

= φi − ηD ∇φ [Lorig
D (φi ) + λJ,i Ex∼Di
[∇x Dφ(t) (x)22 ]]
i

(4)

where ηG and ηD are the learning rates for the generator and discriminator, respectively, and Lorig
D (φ) =
repre−Ex∼pdata [log Dφ (x)] − Ez∼pz [log(1 − Dφ (Gθ (z)))]
sents the standard adversarial loss. After local training, each
node transmits its updated parameters and complexity measure
to the central server. The server performs weighted aggregation
based on the size of each node’s dataset
θ

(t+1)

N
N


|Di | (t+1)
|Di | (t+1)
(t+1)
θi
φ
=
, φ
=
|D|
|D| i
i=1
i=1

(5)


where |D| = N
i=1 |Di | is the total number of samples across
all nodes. The server also updates the global statistics of the
complexity measures to be used in the next communication
round. The training process, as illustrated in Algorithm 1,
and the aggregation procedure, as illustrated in Algorithm
2, continue iteratively until the convergence criteria are
satisfied. These criteria include stabilization of generator
and discriminator loss values and minimal improvements
in model performance across successive rounds. This
convergence assessment helps avoid over training and
reduces unnecessary communication overhead, making the
approach suitable for real-time or resource-constrained edge
deployments.
E. Complexity Analysis
In this section, we provide detailed computational and communication complexity analysis.
1) Computational Complexity: We analyze the computational overhead of FedGAD at both client and server sides,
demonstrating that while the Jacobian penalty doubles discriminator computation, the overall complexity remains tractable
for edge deployments with mini-batch approximations reducing
quadratic costs to linear operations.
Client-side computation: Each client performs the following
operations per training round.
1) Complexity estimation: Computing Ci via kernel density
estimation requires O(n2i · m) operations for ni local
samples and m-dimensional features. In practice, we use
mini-batch approximation, reducing this to O(B · ni · m)
where B is the batch size.
2) Generator update: Forward pass through Bi-LSTM and
TCN layers costs O(E · B · (h2lstm + k · htcn )) where E is

SHARMIN et al.: DIVERGENCE-REGULARIZED FEDERATED GANS FOR EFFECTIVE CYBER-ATTACK DETECTION ON NON-IID

local epochs, hlstm is LSTM hidden size, k is TCN kernel
size, and htcn is TCN hidden channels. Backward pass has
identical complexity.
3) Discriminator update: Standard forward–backward pass
costs O(E · B · |φ| · m) where |φ| is discriminator
parameter count. Jacobian penalty computation adds
O(E · B · |φ| · m) for gradient calculation via automatic
differentiation.
4) Total client complexity: O(B · ni · m + E · B · (|θ| +
2|φ| · m)) where |θ| represents generator parameters.
Server-side computation: The server performs computing C¯
and σC costs O(N ) for N clients. Computing λJ,i for all clients
costs O(N ) for weight calculation. Then, weighted averaging
of parameters costs O(N · (|θ| + |φ|)) calculated for model
aggregation. Total server complexity is O(N · (|θ| + |φ|)) per
round.
2) Communication Complexity: Communication costs dominate FL overhead by each client exchanges (|θ| + |φ|) parameters and a scalar complexity value, totaling O(|θ| + |φ|)
per client per round. For T rounds and N clients: O(T ·
N · (|θ| + |φ|)). FedGAD maintains identical communication
complexity to FedTSRGNet and FedProx since regularization
is computed locally. This contrasts with approaches requiring
auxiliary model exchanges. The 2× computational overhead
in discriminator updates is offset by: 1) faster convergence,
reducing required rounds T by 30%–40% (see Fig. 5) and 2)
improved mode coverage, eliminating the need for post hoc augmentation. Empirically, FedGAD achieves convergence in 50
epochs versus 80–100 for baselines, yielding net computational
savings.
IV. THEORETICAL RESULT ANALYSIS
This section provides formal guarantees and analytical insights into the stability, convergence, and effectiveness of
the proposed FedGAD framework. We demonstrate that the
Jacobian-based regularization enforces Lipschitz continuity in
the discriminator, stabilizing adversarial training and mitigating
mode collapse. We further prove that, under standard assumptions on gradient boundedness and learning rates, FedGAD converges to a stationary point of the regularized mini–max objective. Finally, we analyze the computational and communication
complexities and establish theoretical support for FedGAD’s
ability to enhance mode coverage under non-IID and unlabeled
data conditions.
Assumptions: Our theoretical analysis relies on the following standard assumptions from FL and optimization literature
[23], [28].
1) Bounded gradients: There exists Gmax such that
∇θ LG (θ)2 ≤ Gmax and ∇φ LD (φ)2 ≤ Gmax for all
θ, φ.
2) Bounded variance: Local gradient variance is bounded:
E∇Li − ∇L22 ≤ σ 2 for all clients i.
3) Smoothness: Loss functions are L-smooth: ∇L(w1 ) −
∇L(w2 )2 ≤ Lw1 − w2 2 .
4) Learning
rate conditions:
∞ 2 Learning rates √satisfy
∞
η
=
∞
and
t=1 t
t=1 ηt < ∞ (e.g., ηt = η0 / t).

5009

A. Gradient Penalty Stability
Theorem IV.1 (Gradient Penalty Stability): The Jacobian regularization term RJ (x; φ) promotes Lipschitz continuity in the
discriminator function, thereby stabilizing the adversarial training dynamics.
Proof: Consider the discriminator function Dφ : Rm →
[0, 1]. For any two points x1 , x2 ∈ Rm , the mean value theorem
guarantees the existence of a point ξ ∈ [x1 , x2 ] such that
Dφ (x2 ) − Dφ (x1 ) = ∇x Dφ (ξ)T (x2 − x1 ).

(6)

Applying the Cauchy–Schwarz inequality
|Dφ (x2 ) − Dφ (x1 )| ≤ ∇x Dφ (ξ)2 x2 − x1 2 .

(7)

By minimizing the regularization term E[∇x Dφ (x)22 ], we
effectively bound the gradient magnitude, ensuring that
|Dφ (x2 ) − Dφ (x1 )| ≤ Lx2 − x1 2

(8)

where L = maxx ∇x Dφ (x)2 represents the Lipschitz constant. This constraint prevents the discriminator from exhibiting
sharp transitions that could lead to gradient vanishing or explosion, thereby maintaining stable training dynamics.

B. Convergence Guarantee
Theorem IV.2 (Convergence Guarantee): Under Assumptions 1–4 and Jacobian regularization with adaptive weighting,
the federated training process converges almost surely to a
stationary point (θ∗ , φ∗ ) of the regularized mini–max objective
min max Ei∼N [Lorig
D (θ, φ; Di ) + λJ,i RJ (φ; Di )]
θ

φ

(9)

satisfying limt→∞ E[∇L(θ(t) , φ(t) )2 ] = 0.
Proof: Let θ(t) and φ(t) denote the global generator and
discriminator parameters at communication round t, with the
regularized discriminator objective defined as
orig
Lreg
D (φ) = LD (φ) + RJ (x; φ)

(10)

RJ (x; φ) = λJ Ex∼pdata [∇x Dφ (x)22 ].

where
The Jacobian
L-Lipschitz continuous where L =
term ensures Dφ is 
maxx ∇x Dφ (x)2 ≤ λ−1
J (from optimization of RJ ). This
provides strong convexity with parameter μ ≥ λJ for the discriminator objective. Lyapunov function construction is defined
as
Vt = E[θ(t) − θ∗ 22 + φ(t) − φ∗ 22 ]

(11)

where (θ∗ , φ∗ ) is a stationary point. Under FedAvg aggregation
[see (5)] with learning rates ηG , ηD and Assumptions 1–3, the
expected one-step change satisfies
E[Vt+1 − Vt ] ≤ −2ηt μVt + ηt2 (σ 2 + LG2max )

(12)

where σ 2 bounds federated update variance (Assumption 2), L
is smoothness constant (Assumption 3), and ηt = min(ηG , ηD ).
Rearranging and summing over T = 1, . . . , t, we get
T

t=1

η t Vt ≤

T
σ 2 + LG2max  2
V1
+
ηt .
2μ
2μ
t=1

(13)

5010

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 6, JUNE 2026


With
learning rate conditions from Assumption 4: ∞
t=1 ηt = ∞
2
η
<
∞,
we
have
and ∞
t
t=1
T
η t Vt
= 0 ⇒ Vt → 0 almost surely.
(14)
lim t=1
T
T →∞
t=1 ηt
Parameter convergence Vt → 0 combined with gradient continuity (ensured by Lipschitz continuity from Theorem 4.1)
implies
(t)
(t)
lim E[∇Lreg
D (θ , φ )2 ] = 0

t→∞

(15)

establishing almost sure convergence to a stationary point. 
Remark on nonconvexity: While GANs involve nonconvex
objectives in θ, our proof establishes convergence to stationary
points (local minima or saddle points) rather than global optima for standard in the nonconvex optimization literature [30].
The Jacobian regularization provides sufficient smoothness and
bounded curvature to guarantee this convergence property,
which is practically sufficient as evidenced by our experimental
results.
C. Computational Complexity and Communication
Efficiency
The integration of Jacobian regularization introduces additional computational overhead, primarily during the discriminator update phase. Computing the gradient ∇x Dφ (x) requires
backpropagation through the discriminator network, resulting
in a computational complexity of O(|φ| · m) per sample, where
|φ| is the number of parameters in the discriminator and m is
the feature dimensionality. However, this computational cost
is compensated by improved training stability and a reduced
number of communication rounds needed to reach convergence, yielding overall efficiency gains in federated settings.
The communication complexity remains unchanged compared
to the original FedTSRGNet framework, as the regularization
is applied locally at each edge node without requiring extra
parameter exchange. Thus, the total communication cost per
round remains O(|θ| + |φ|), corresponding to the generator and
discriminator model parameters exchanged between the server
and edge nodes.
D. Theoretical Guarantees for Mode Coverage
Theorem IV.3 (Enhanced Mode Coverage): The Jacobianregularized discriminator promotes improved mode coverage by
preventing the generator from collapsing to a limited subset of
the data manifold.
Proof: Consider the generator’s objective function under the
regularized discriminator
LG (θ) = Ez∼pz [log(1 − Dφ∗ (Gθ (z)))]

(16)

where φ∗ denotes the optimal discriminator parameters under
FedGAD’s regularization scheme.
The regularization ensures bounded gradients in the discriminator (see Theorem 4.1), prevents sharp decision boundaries
that could constrain the generator’s output to narrow modes.
Specifically, Lipschitz continuity guarantees
∇x Dφ (x1 ) − ∇x Dφ (x2 )2 ≤ LLip x1 − x2 2

(17)

for some LLip controlled by λJ . According to the implicit
function theorem, the generator’s update direction
Δθ ∝ −∇θ Ez [log(1 − Dφ (Gθ (z)))] = −Ez [JD · JG ] (18)
where JD = ∇x Dφ (Gθ (z)) and JG = ∇x Gθ (z) is influenced
by the discriminator’s gradient field ∇x Dφ .
The Jacobian regularization ensures this gradient field remains smooth and well-conditioned across the input space,
particularly in regions corresponding to rare attack patterns. This
prevents mode collapse by maintaining nonzero gradient flow
∇x Dφ (x)2 ≥  > 0 for some  even in low-density regions.
Consequently, the generator receives informative gradient signals across all data modes, encouraging exploration of broader
data manifolds. This enhances the diversity and representativeness of generated synthetic samples, leading to improved mode
coverage. Formally, let M = {M1 , . . . , MK } denote the set of
data modes. Under Jacobian regularization, the probability that
the generator outputs cover mode Mk satisfies
P(Gθ (z) ∈ Mk ) ≥ 1 − exp(−λJ · dk )

(19)

where dk = (Mk , Mothers ) measures separation between modes.
This exponential bound demonstrates that stronger regularization (λJ ↑) exponentially increases mode coverage
probability.

V. EXPERIMENTAL RESULT ANALYSIS
This section evaluates the performance of the proposed
FedGAD method, which is an extension of the FedTSRGNet
framework with gradient diversity regularization against eight
state-of-the-art baselines: four FL methods (FedTrust [17],
ADGAN [18], FedGAN-IDS [11], and FedTSRGNet [16])
and four regularization-based approaches (FedAvg [8], FedProx [23], learning with collaborative aggregation method
(LeCam) [31], and Jensen Shannon (JS) Divergence [32]). We
assess the models under both IID and non-IID data distributions, with both labeled and unlabeled data. Key performance
metrics include accuracy, precision, F 1 score, and ADS. ADS is
SSD )
, providing a comcalculated as: ADS = Precision+Recall+(1−L
3
prehensive measure combining classification performance with
generative quality [16].
A. Dataset and Distribution
To validate our proposed FedGAD approach, we conducted
comprehensive simulation studies using two public datasets:
Telemetry data of networks - internet of things (ToN_IoT) [33]
and CSE_CIC_IDS [34], utilizing NetFlow records as activity
log data [35]. The ToN_IoT dataset contains 1 379 274 flows
across eight categories (7 attack types, 1 normal) with 80.4%
attacks and 19.6% normal traffic. CSE_CIC_IDS comprises
8 392 401 flows across seven categories (6 attack types, 1 normal)
with 12.14% attacks and 87.86% benign traffic. Each dataset
was partitioned using an 80–20 split for training and testing.
We evaluated both IID and non-IID configurations across 100
clients: in IID scenarios, data was uniformly distributed (11 022
samples per client for ToN_IoT, 67 140 for CSE_CIC_IDS);
for non-IID distribution, we created 2500 shards (450 samples

SHARMIN et al.: DIVERGENCE-REGULARIZED FEDERATED GANS FOR EFFECTIVE CYBER-ATTACK DETECTION ON NON-IID

5011

TABLE II
ABLATION STUDY RESULTS ON TON_IOT (NON-IID, UNLABELED), VALUES
REPORTED AS MEAN ± STD

each) for ToN_IoT and 8400 shards (800 samples each) for
CSE_CIC_IDS following [8].
B. Configuration and Implementation Details
All simulation experiments were executed using Python version 3.12.4 on a Lenovo T14S workstation featuring a 12th Generation Intel Core i5-1235 U processor operating at 1.30 GHz,
equipped with 16.0 GB of RAM, and running on a GPU server.
We have considered 100 epochs E, a batch size B of 32,
100 clients N , 0.001 learning rate η, regularizer effect λ, 0.01
for doing the experiments. Additional hyperparameters: base
regularization λbase = 0.01, scaling parameter α = 0.5, latent
dimension d = 100, Bi-LSTM hidden size hlstm = 256, TCN
hidden channels htcn = 128, dropout rate = 0.3. These values
were selected through preliminary grid search on validation sets.
C. Ablation Studies
To isolate the contributions of individual components, we
conduct comprehensive ablation experiments comparing the
following, providing the details in Table II.
1) FedGAD-Full: Complete proposed method with Jacobian
regularization and adaptive weighting.
2) FedGAD-NoAdapt: Fixed regularization (λJ,i = λbase for
all clients).
3) FedGAD-NoReg: No Jacobian regularization (equivalent
to FedTSRGNet baseline).
4) FedGAD-L2Reg: Standard L2 parameter regularization
instead of Jacobian.
D. Comparative Performance and Loss Analysis
The comprehensive evaluation across ToN_IoT and
CSE_CIC_IDS datasets demonstrates FedGAD’s superiority
under all configurations.
Table IV showing consistent
improvements when integrated with four state-of-the-art
FL methods, achieving average gains ranging from +2.13% to
+2.75% across all scenarios. The most significant improvements
occur in challenging non-IID unlabeled settings, where
FedGAN-IDS achieves +3.5% (0.830 to 0.865) on ToN_IoT
and +4.0% (0.810 to 0.850) on CSE_CIC_IDS, followed by
ADGAN, FedTrust, and FedTSRGNet with +2.2%–2.5% gains.
This validating that our FedGAD specifically addresses
mode collapse under extreme data heterogeneity. Even
high-performing methods like FedTSRGNet benefit from
integration, improving from 0.950 to 0.965 (+1.6%) in IID
labeled settings, with consistently low standard deviations
(±0.007 to ±0.013) confirming robustness and reproducibility.
Notably, improvement magnitude correlates with data

Fig. 2. Total loss comparison showing FedGAD’s consistently superior
performance across all scenarios in both IID and non-IID in unlabeled
FL settings.

heterogeneity, as non-IID unlabeled configurations show
15%–30% larger relative gains compared to IID labeled
settings, demonstrating that FedGAD stabilizes generator
training under client data heterogeneity and serves as an
effective plug-and-play regularization technique across diverse
FL architectures. As shown in Figs. 2 and 3, FedGAD
consistently achieves 12%–17% improvement in total loss with
balanced optimization of individual loss components (G-Loss,
D-Loss, SSD Loss, and Reg Loss), indicating stable training
dynamics and superior mode coverage across diverse edge data
environments (see Table III).
E. Stability and Generalization Analysis
This evaluation demonstrates FedGAD’s stability under diverse network conditions and attack patterns. The consistent performance superiority across both ToN_IoT and CSE_CIC_IDS
datasets, which have different class distributions and attack
types, validates FedGAD’s generalizability. Fig. 4 presents
the performance degradation analysis, where degradation is
calculated as the percentage difference between IID labeled and
non-IID unlabeled accuracy for each method [36], [37] using the
−Accnon-IID-Unlabeled
× 100.
formula: Degradation (%) = AccIID-Labeled
AccIID-Labeled
Unlabeled non-IID performance maintenance with minimal
degradation (typically 2%–4% reduction compared to IID
scenarios) indicates strong resilience to data heterogeneity,
a critical requirement for practical FL deployments in
cybersecurity applications.
1) Mode Collapse Intensity: This comprehensive evaluation
quantifies mode collapse using multiple established metrics
from the generative modeling literature. Missing modes counts
how many attack categories are completely absent from generated samples, with FedGAD achieving zero missing modes
while FedProx fails to generate 3 out of 8 attack types. Mode
coverage percentage indicates the proportion of original data
modes successfully captured, where FedGAD achieves 100%
coverage compared to 62.5% for FedProx, as described in
Table V.

5012

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 6, JUNE 2026

TABLE III
PERFORMANCE COMPARISON ACROSS DIFFERENT DATASETS AND METHODS

TABLE IV
COMPREHENSIVE ACCURACY COMPARISON ACROSS ALL SCENARIOS: ORIGINAL METHODS VERSUS FEDGAD REGULARIZATION

Fig. 3. Balanced optimization across all loss components demonstrating FedGAD’s stability in different datasets. (a) Ton IoT labeled. (b) Ton
IoT unlabeled. (c) Communications Security Establishment in Canadian Institute for Cybersecurity - Intrusion Detection System (CSE_CIC_IDS)
Labeled. (d) CSE CIC IDS unlabeled.
TABLE V
MODE COLLAPSE INDICATORS ON TON_IOT DATASET

Fig. 4. Performance degradation when transitioning from IID to non-IID
scenarios across different methods. Lower values indicate better stability to data heterogeneity.

2) Generalization Quality: This section compares the
distribution of generated samples against the real data
distribution for each attack type. Table VI demonstrates

that each FL method preserves the original class proportions
when generating synthetic cybersecurity data. Mode collapse
is evident when generated distributions significantly deviate
from real distributions, particularly when certain attack
types are underrepresented or completely missing. In
Table VI, FedGAD shows the closest alignment to real
data distributions across all attack categories, indicating
effective mitigation of mode collapse. For instance, while
baseline methods like FedProx severely undergenerate rare
attacks like Password (2.1% versus 15.6% real) and cross-site
scripting (XSS) (0.6% versus 10.0% real), FedGAD maintains

SHARMIN et al.: DIVERGENCE-REGULARIZED FEDERATED GANS FOR EFFECTIVE CYBER-ATTACK DETECTION ON NON-IID

5013

Fig. 5. Convergence analysis of FedGAD versus baseline methods. (a) Loss convergence. (b) Loss differences. (c) Magnitude comparison.
(d) Training versus validation loss. (e) Generalization gap with thresholds. (f) Final convergence behavior.

TABLE VI
GENERATED SAMPLE DISTRIBUTION VERSUS REAL DISTRIBUTION ON THE
TON_IOT DATASET

TABLE VII
FEDGAD VERSUS BASELINES ON TON_IOT NON-IID UNLABELED
STATISTICAL SIGNIFICANCE TESTS

proportions very close to the original dataset (14.9% and 9.7%,
respectively).

417 s per percentage point of accuracy improvement compared to 892–1247 s for competing approaches. This demonstrates the superior performance with better overall resource
utilization.

F. Convergence, Efficiency, and Computational
Overhead Analysis
The convergence analysis in Fig. 5(a)–(c) manifests
FedGAD’s superior performance, achieving the fastest convergence.3 Training dynamics in Fig. 5(d)–(f) show both losses
starting at 2.4 and decreasing together until epoch 50, where
validation loss plateaus at 0.95 while training loss continues to 0.90, with generalization gaps below 0.02 until epoch
50, then increasing to 0.05–0.10, demonstrating 15%–20%
better stability compared to baseline methods. Practical deployment evaluation on ToN_IoT dataset reveals FedGAD incurs modest computational overhead: 9.2% longer per-epoch
runtime (18.47 versus 16.91 s) and 6.8% higher peak GPU
memory (2847 MB versus 2665 MB), but achieves 4.7%
lower total communication cost and 18.1% faster time to convergence due to faster convergence (75 versus 100 rounds).
FedGAD achieves an efficiency score of 2.38, significantly
outperforming baseline methods (0.25–0.82). This requires only

3 Note that FedGAD achieves linear convergence O(1/t) compared to
√
O(1/ T ) for FedProx/LeCam and O((log n/n)2β/(2β+d) ) for JS divergence
methods.

G. Statistical Significance Testing
To validate the statistical significance of our results, we performed paired t-tests comparing FedGAD against all baseline
methods. Table VII presents the results for key performance
metrics on the ToN_IoT dataset in unlabeled non-IID scenario
(the most challenging configuration). All comparisons yield
p-values < 0.01, indicates highly significant improvements.
We also compute Cohen’s d effect sizes to measure practical
significance, with all comparisons showing large effect sizes
(d > 0.8), confirming that FedGAD’s improvements are both
statistically significant and practically meaningful.
VI. CONCLUSION
This article introduces FedGAD, an FL framework for cyberattack detection in distributed EC environments that addresses
key challenges, including data heterogeneity, limited labeled
data, and resource constraints. FedGAD makes four primary
contributions: First, it uses adaptive Jacobian-based regularization that adjusts to local data complexity, achieving 100% mode
coverage compared to 25%–62.5% for baseline methods. Second, it provides formal convergence proofs and stability guarantees for safety-critical deployments. Third, comprehensive experiments comparing FedGAD against four existing FL methods

5014

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 6, JUNE 2026

(FedTrust, ADGAN, FedGAN-IDS, and FedTSRGNet) and four
regularization-based approaches (FedAvg, FedProx, LeCam,
and JS Divergence) demonstrate substantial performance improvements: 2%–8% accuracy gains and up to 19.7% better
attack detection scores (ADSs) on ToN_IoT and CSE_CIC_IDS
datasets, with particularly pronounced improvements of up to
4% under challenging non-IID unlabeled scenarios. Fourth,
despite 2× computational overhead, it achieves 30%–40% faster
convergence (50 versus 80–100 epochs), resulting in net time
savings suitable for resource-constrained edge devices.
Several directions warrant future investigation. Multimodal
data integration could extend the framework beyond network
flow data to include system logs and behavioral analytics.
Lightweight architectures using model compression or approximation techniques could further reduce computational overhead.
Byzantine-robust aggregation would add protection against malicious clients. Continual learning mechanisms could enable
adaptation to evolving attack patterns without full retraining.
Privacy-preserving enhancements like differential privacy could
provide stronger guarantees against inference attacks. Finally,
evaluating cross-domain transferability across different EC environments would improve practical deployment capabilities.
REFERENCES
[1] W. Shi, J. Cao, Q. Zhang, Y. Li, and L. Xu, “Edge computing: Vision
and challenges,” IEEE Internet Things J., vol. 3, no. 5, pp. 637–646, Oct.
2016.
[2] R. Roman, J. Lopez, and M. Mambo, “Mobile edge computing, Fog et al.:
A survey and analysis of security threats and challenges,” Future Gener.
Comput. Syst., vol. 78, pp. 680–698, 2018.
[3] S. M. Asad et al., “Edge intelligence in private mobile networks for
next-generation railway systems,” Front. Commun. Netw., vol. 2, 2021,
Art. no. 769299.
[4] D. E. Denning, “An intrusion-detection model,” IEEE Trans. Softw. Eng.,
vol. SE-13, no. 2, pp. 222–232, Feb. 1987.
[5] S. Ma et al., “Privacy-preserving anomaly detection in cloud manufacturing via federated transformer,” IEEE Trans. Ind. Informat., vol. 18, no. 12,
pp. 8977–8987, Dec. 2022.
[6] P. Ruzafa-Alcázar et al., “Intrusion detection based on privacy-preserving
federated learning for the industrial IoT,” IEEE Trans. Ind. Informat.,
vol. 19, no. 2, pp. 1145–1154, Feb. 2023.
[7] K. Bonawitz et al., “Towards federated learning at scale: System design,”
Proc. Mach. Learn. Syst., vol. 1, pp. 374–388, 2019.
[8] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. y Arcas,
“Communication-efficient learning of deep networks from decentralized
data,” in Proc. Artif. Intell. Statist., 2017, pp. 1273–1282.
[9] M. Elkhodr, “An AI-driven framework for integrated security and privacy
in Internet of Things using quantum-resistant blockchain,” Future Internet,
vol. 17, no. 6, 2025, Art. no. 246.
[10] Z. Xiong, W. Li, Y. Li, and Z. Cai, “Distributed generative
model: A data synthesizing framework for multi-source heterogeneous
data,” IEEE Trans. Artif. Intell., vol. 7, no. 1, pp. 399–411, Jan.
2026.
[11] A. Tabassum, A. Erbad, W. Lebda, A. Mohamed, and M. Guizani, “Fedganids: Privacy-preserving IDS Using GAN and federated learning,” Comput.
Commun., vol. 192, pp. 299–310, 2022.
[12] I. Gulrajani, F. Ahmed, M. Arjovsky, V. Dumoulin, and A. C. Courville,
“Improved training of Wasserstein GANs,” in Proc. Adv. Neural Inf.
Process. Syst., vol. 30, 2017, pp. 1–11.
[13] I. Goodfellow et al., “Generative adversarial nets,” in Proc. Adv. Neural
Inf. Process. Syst., 2014, vol. 27, pp. 1–9.
[14] T. Salimans, I. Goodfellow, W. Zaremba, V. Cheung, A. Radford, and X.
Chen, “Improved techniques for training GANs,” in Proc. Adv. Neural Inf.
Process. Syst., vol. 29, 2016, pp. 1–9.

[15] D. Liu et al., “Jacobian norm with selective input gradient regularization
for interpretable adversarial defense,” Pattern Recognit., vol. 145, 2024,
Art. no. 109902.
[16] Z. Sharmin, Y. Xiang, M. P. Uddin, F. Chen, Y. Zhang, and J. Tang, “Federated TSRN-enabled GANs for effective cyber attack detection in edge
computing,” IEEE Trans. Netw. Sci. Eng., vol. 12, no. 6, pp. 4787–4803,
Nov./Dec. 2025.
[17] M. Abdel-Basset, N. Moustafa, and H. Hawash, “Privacy-preserved generative network for trustworthy anomaly detection in smart grids: A federated
semisupervised approach,” IEEE Trans. Ind. Informat., vol. 19, no. 1,
pp. 995–1005, Jan. 2023.
[18] J. Qin et al., “A novel temporal generative adversarial network for electrocardiography anomaly detection,” Artif. Intell. Med., vol. 136, 2023,
Art. no. 102489.
[19] S. K. GK et al., “Explainable federated framework for enhanced security
and privacy in connected vehicles against advanced persistent threats,”
IEEE Open J. Veh., Technol., vol. 6, pp. 1438–1463, 2025.
[20] O. Friha, M. A. Ferrag, L. Shu, L. Maglaras, K.-K. R. Choo, and M.
Nafaa, “Felids: Federated learning-based intrusion detection system for
agricultural Internet of Things,” J. Parallel Distrib. Comput., vol. 165,
pp. 17–31, 2022.
[21] N. Chen et al., “Multimodal heterogeneous data sensing and communication integration for CIOT,” IEEE Trans. Consum. Electron., vol. 71, no. 3,
pp. 7454–7472, Aug. 2025.
[22] A. Karunamurthy, K. Vijayan, P. R. Kshirsagar, and K. T. Tan, “An optimal
federated learning-based intrusion detection for IoT environment,” Sci.
Rep., vol. 15, no. 1, 2025, Art. no. 8696.
[23] T. Li, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and V. Smith,
“Federated optimization in heterogeneous networks,” Proc. Mach. Learn.
Syst., vol. 2, pp. 429–450, 2020.
[24] Z. Lu, H. Pan, Y. Dai, X. Si, and Y. Zhang, “Federated learning with non-iid
data: A survey,” IEEE Internet Things J., vol. 11, no. 11, pp. 19188–19209,
Jun. 2024.
[25] J. Hernandez-Ramos et al., “Intrusion detection based on federated learning: A systematic review,” ACM Comput. Surv., vol. 57, pp. 1–65, 2023.
[26] L. Metz, B. Poole, D. Pfau, and J. Sohl-Dickstein, “Unrolled generative
adversarial networks,” in Proc. Int. Conf. Learn. Representations, 2017,.
[27] C. Xiaopeng, C. Jiangzhong, L. Yuqin, and D. Qingyun, “Improved training of spectral normalization generative adversarial networks,” in Proc.
2nd World Symp. Artif. Intell., 2020, pp. 24–28.
[28] S. P. Karimireddy, S. Kale, M. Mohri, S. Reddi, S. Stich, and A. T. Suresh,
“Scaffold: Stochastic controlled averaging for federated learning,” in Proc.
Int. Conf. Mach. Learn., 2020, pp. 5132–5143.
[29] S. Kullback and R. A. Leibler, “On information and sufficiency,” Ann.
Math. Statist., vol. 22, no. 1, pp. 79–86, 1951.
[30] S. Ghadimi and G. Lan, “Stochastic first-and zeroth-order methods for
nonconvex stochastic programming,” SIAM J. Optim., vol. 23, no. 4,
pp. 2341–2368, 2013.
[31] Y. Huang et al., “Personalized cross-silo federated learning on non-IID
data,” in Proc. AAAI Conf. Artif. Intell., 2021, vol. 35, no. 9, pp. 7865–7873.
[32] S. Ji et al., “Emerging trends in federated learning: From model fusion
to federated x learning,” Int. J. Mach. Learn. Cybern., vol. 15, no. 9,
pp. 3769–3790, 2024.
[33] A. Alsaedi, N. Moustafa, Z. Tari, A. Mahmood, and A. Anwar, “Ton_iot
telemetry dataset: A new generation dataset of IoT and IIOT for data-driven
intrusion detection systems,” IEEE Access, vol. 8, pp. 165130–165150,
2020.
[34] I. Sharafaldin et al., “Toward generating a new intrusion detection dataset
and intrusion traffic characterization,” in Proc. Int. Conf. Inf. Syst. Security.
Privacy, 2018, vol. 1, pp. 108–116.
[35] M. Sarhan, S. Layeghy, N. Moustafa, and M. Portmann, “Netflow datasets
for machine learning-based network intrusion detection systems,” in Proc.
Big Data Technol. Appl.: 10th EAI Int. Conf., 13th EAI Int. Conf. Wireless
Internet, 2021, pp. 117–135.
[36] Q. Li, Y. Diao, Q. Chen, and B. He, “Federated learning on non-IID data
silos: An experimental study,” in Proc. IEEE 38th Int. Conf. Data Eng.,
2022, pp. 965–978.
[37] Y. Zhao, M. Li, L. Lai, N. Suda, D. Civin, and V. Chandra, “Federated
learning with non-IID data,” 2018, arXiv:1806.00582.
PAPER_TEXT
