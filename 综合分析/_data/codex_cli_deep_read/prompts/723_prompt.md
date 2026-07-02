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
# [723] Lightweight Multimedia Anomaly and Integrity Detection for Consumer IoT Using Knowledge Distillation
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
编号：723
题名：Lightweight Multimedia Anomaly and Integrity Detection for Consumer IoT Using Knowledge Distillation
年份：2025
DOI：10.1109/tce.2025.3644297
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2025.3644297.pdf
已有粗分类：IoT、车联网、工业互联网与边缘安全
二级关联：其他AI安全与跨域异常检测
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\723.txt
- 原始字符数：56675
- 本次发送字符数：56675
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

2465

Lightweight Multimedia Anomaly and Integrity
Detection for Consumer IoT Using
Knowledge Distillation
Fasee Ullah , Hamid Asmat, Arfat Ahmad Khan , Muhammad Ismail Mohmand , Farman Ali ,
Rayan Hamza Alsisi , Theyazn H. H. Aldhyani , and Daehan Kwak , Senior Member, IEEE

Abstract— The rapid growth of Consumer Internet of Things
(CIoT) devices has significantly increased real-time multimedia
data exchange, heightening vulnerability to attacks targeting
audio, video, and image content. This paper introduces
Multimedia Anomaly and Integrity Detection using Knowledge
Distillation (MAID-KD), a lightweight multi-task framework that
performs anomaly detection and integrity verification in CIoT
environments. MAID-KD leverages a Transformer-based teacher
model to extract rich spatio-temporal features from multimedia
streams, while a compact CNN-LSTM student model optimized
for edge deployment is trained through feature alignment,
soft-target distillation, and variational projection. Experimental
results demonstrate that MAID-KD achieves superior accuracy
and F1-score compared to state-of-the-art baselines, while
reducing model size and inference latency by over 60%. These
results highlight MAID-KD’s ability to deliver scalable, privacypreserving, and multimedia-aware security for CIoT devices such
as smart surveillance systems, health-monitoring wearables, and
connected home platforms.
Index Terms— Multimedia security, malware detection, intrusion detection system (IDS), CIoT, edge computing, knowledge
distillation, CNN-LSTM hybrid, privacy preservation, real-time
threat detection.

Received 5 August 2025; revised 18 October 2025; accepted 6 December
2025. Date of publication 15 December 2025; date of current version 25 March
2026. This work was supported in part by the Deanship of Scientific Research,
Vice Presidency for Graduate Studies and Scientific Research, King Faisal
University, Saudi Arabia, under Grant KFU253713; and in part by the
“Regional Innovation System and Education (RISE)” through the Seoul RISE
Center, funded by the Ministry of Education (MOE) and Seoul Metropolitan
Government under Grant 2025-RISE-01-018-01. (Corresponding authors:
Farman Ali; Daehan Kwak.)
Fasee Ullah is with the Department of Computing, Universiti
Teknologi PETRONAS, Seri Iskandar 32610, Malaysia (e-mail:
fasee.ullah@utp.edu.my).
Hamid Asmat is with the Department of Computer Science, University of
Haripur, Haripur 22620, Pakistan (e-mail: hamid@uoh.edu.pk).
Arfat Ahmad Khan is with the Department of Computer Science, Khon
Kaen University, Khon Kaen 40002, Thailand (e-mail: arfatkhan@kku.ac.th).
Muhammad Ismail Mohmand is with the Department of Computer Engineering and the Faculty of Engineering and Natural Sciences, Istanbul Atlas University, 34408 Istanbul, Türkiye (e-mail: muhammad.mohmand@atlas.edu.tr).
Farman Ali is with the Department of Applied AI, Sungkyunkwan
University, Seoul 03063, South Korea (e-mail: farman0977@skku.edu).
Rayan Hamza Alsisi is with the Department of Electrical Engineering,
Islamic University of Madinah, Madinah 41411, Saudi Arabia (e-mail:
ralsisi@iu.edu.sa).
Theyazn H. H. Aldhyani is with the Applied College, King Faisal University,
Al-Ahsa 31982, Saudi Arabia (e-mail: taldhyani@kfu.edu.sa).
Daehan Kwak is with the Department of Computer Science and Technology,
Kean University, Union, NJ 07083 USA (e-mail: dkwak@kean.edu).
Digital Object Identifier 10.1109/TCE.2025.3644297

I. I NTRODUCTION

T

HE rapid expansion of Consumer Internet of Things
(CIoT) ecosystems, including smart surveillance cameras,
voice-enabled home assistants, health-monitoring wearables,
and connected vehicles, has dramatically increased the volume
of multimedia data (e.g., video, audio, and images) transmitted
across heterogeneous consumer devices. These multimedia
streams carry high-value information and are susceptible
to attacks such as video feed tampering, deepfake audio
injection, data exfiltration, and unauthorized redistribution,
posing severe threats to user privacy and trust. As the
adoption of CIoT devices accelerates [1], [2], ensuring robust
security and privacy has become increasingly challenging.
These devices operate under strict computational and energy
constraints, making them attractive targets for sophisticated
attacks, including multimedia-specific exploits such as frame
injection, video/audio stream tampering, and steganographybased data hiding [3], [4].
Lightweight anomaly detection solutions have emerged as a
primary defense for CIoT environments; however, deploying
conventional deep learning models at the edge remains
challenging due to energy, latency, and memory limitations [5].
This is particularly critical for multimedia applications such
as live surveillance and smart home monitoring, where cloud
offloading is often infeasible. Complementary multimedia
security mechanisms such as encrypted data transmission,
steganography detection, and watermarking-based integrity
checks have been proposed, but integrating these into edge
frameworks is still in its early stages [4], [6]. Multimedia
streams often contain sensitive user information and can
be manipulated to bypass authentication systems or mislead
automated surveillance. Existing solutions, like watermarking
and multimedia encryption, provide partial protections but
remain difficult to integrate with lightweight anomaly
detection models. This gap highlights the need for unified
approaches that secure both the device and its multimedia
content without sacrificing real-time performance.
Knowledge Distillation (KD) has become a promising
strategy to enable lightweight models by transferring
knowledge from large teacher networks to compact student
models [7]. In the context of CIoT, KD enables ondevice anomaly detection and multimedia integrity verification
without transmitting raw multimedia data externally, thereby

1558-4127 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

2466

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

reducing privacy risks. However, hybrid frameworks that
combine KD with multimedia encryption or federated learning
still face issues like task interference and model inversion
attacks, particularly when teacher models are trained on
multiple detection objectives simultaneously [8], [9], [10].
A key limitation of existing approaches is the isolated
treatment of anomaly detection and integrity verification
as separate tasks, which hinders their ability to detect
blended or multi-stage attacks where abnormal data patterns
overlap with tampered multimedia content [11]. Single-task
solutions also struggle to adapt across heterogeneous consumer
platforms where multimedia data types and attack surfaces
vary significantly [12]. These gaps underscore the need for
a unified, multi-task approach tailored for consumer-grade
devices that also protects multimedia data integrity.
The core research problem addressed in this work
is how to design a lightweight and privacy-preserving
framework capable of jointly performing multimedia anomaly
detection and integrity verification under the computational
and bandwidth constraints of consumer IoT environments.
To address these challenges, this study proposes a Multimedia
Anomaly and Integrity Detection using Knowledge Distillation
(MAID-KD) framework that consolidates anomaly detection
and multimedia integrity verification in a single student
model optimized for CIoT devices. The teacher model
leverages a Transformer-based encoder to capture long-range
dependencies from multimedia-rich data, while the student
employs a CNN-LSTM hybrid architecture to preserve spatiotemporal representations in a lightweight form. Knowledge
transfer is performed using teacher-guided feature alignment
and probabilistic variational projection, with a multi-objective
optimization function balancing classification, reconstruction,
and distillation losses. This design enables MAID-KD to
provide strong detection accuracy while maintaining minimal
computational and memory overhead, making it suitable
for real-time deployments in multimedia-intensive CIoT
environments such as smart surveillance systems, connected
home cameras, and health-monitoring wearables.
The proposed MAID-KD framework focuses on
multimedia-centric security, unlike existing KD-based
IoT solutions such as FLEKD [13], and DTKD-IDS [14],
which primarily rely on network traffic data. MAID-KD
introduces a unified multi-task distillation system that
performs both anomaly detection and multimedia integrity
verification within a single lightweight model. It further
incorporates a variational knowledge projection module to
handle uncertainty in multimedia data, enabling the student
model to detect blended or tampered content efficiently under
resource constraints. These design choices distinguish MAIDKD as a novel, real-time solution tailored for consumer IoT
environments.
The contributions of this work are as follows:
• A unified anomaly detection and multimedia integrity
verification framework using task-aware knowledge
distillation.
• A training pipeline that prevents raw multimedia
data exposure while enabling flexible deployment on
consumer hardware.

A detailed evaluation of accuracy, adaptability, multimedia data integrity, and privacy across multiple multimedia
attack scenarios.
The remainder of this paper is organized as follows:
Section II reviews related work on the use of KD in secure
IoT settings. Section III details the proposed MAID-KD
framework and its underlying algorithms. Section IV presents
the experimental setup. Results are explained in Section V.
Finally, Section VI concludes the paper.
•

II. R ELATED W ORK
Security and privacy in Consumer Internet of Things
(CIoT) environments have become increasingly critical with
the rise of multimedia data exchange through devices such
as wearables, smart appliances, and connected vehicles.
Early studies emphasized securing multimedia content in
consumer electronics using cryptographic and biometric
mechanisms [15], [16]. These foundational methods focused
on protecting audio-visual data streams and consumer privacy
across home networks. More recently, multimedia-centric
threats, such as data tampering and covert exfiltration, have
emerged in CIoT environments, motivating stronger protection
for user identity, behavior, and content integrity [17], [18].
Recent work has proposed specialized tampering detection
frameworks for images and video using multiscale attention
and spatio-temporal analysis [19], [20], as well as deep
learning-based methods for audio deepfake detection [21].
These advances are essential to preserve the authenticity of
multimedia data generated by CIoT devices.
Blockchain and federated learning (FL) are increasingly
adopted for distributed multimedia security. For instance,
redactable blockchain frameworks, such as TMRB, address
immutability and content redaction needs in multimedia
scenarios [22]. FL integrated with blockchain has been shown
to improve trust and privacy by eliminating the need for central
data aggregation [23], [24]. Similarly, Zero-Trust Architecture
(ZTA) approaches leverage AI-driven profiling to verify
interactions in real-time [14], [25], offering a robust framework
for hostile environments where multimedia traffic must
be authenticated continuously. Complementary watermarking
techniques, such as secure watermarking schemes tailored for
IoT devices [26], [27], have also been employed to protect
ownership and detect content manipulation in multimedia
streams.
KD is widely explored for enabling lightweight edge
models capable of processing multimedia data streams locally.
Multi-branch KD frameworks have been shown to perform
intrusion detection and malware analysis without cloud
dependency [28], [29]. Unified KD-based models capable
of handling multiple detection objectives simultaneously are
of particular relevance to multimedia-driven CIoT, where
blended attacks are common. Recent reviews also emphasize
the importance of maintaining content integrity during KD
training for regulatory and consumer trust [30].
Agent-based and situationally aware Intrusion Detection
Systems (IDS) have also emerged as promising solutions
for multimedia environments. For example, privacy-preserving
agent IDSs adapt dynamically using contextual multimedia

ULLAH et al.: LIGHTWEIGHT MULTIMEDIA ANOMALY AND INTEGRITY DETECTION FOR CONSUMER IoT

2467

Fig. 2. Deployment Phase: The trained student model (MAID-KD) performs
real-time threat predictions using live IoT data.

Fig. 1.
Training Phase: The teacher model guides the student using
knowledge distillation, while a multi-objective loss function optimizes the
student parameters.

features [31], while deep feature extraction and compression
have been proposed to reduce resource consumption on edge
devices [32], [33], [34]. Additionally, cryptographic compression and watermarking techniques have been integrated
with GANs and hybrid storage schemes to enable secure
multimedia model transmission across CIoT networks [35],
[36]. These advancements collectively highlight the evolving
nature of multimedia security challenges and the growing
focus on integrating lightweight, multi-task learning models
for real-time protection in CIoT applications.
Existing methods are useful in certain domains. However,
they are insufficient for real-time multimedia security in CIoT.
Federated learning and blockchain provides high latency and
communication overhead, which makes them unsuitable for
low-power edge devices. The main difference between KDbased intrusion detection systems and the watermarking and
encryption techniques is that network traffic is the primary
target of intrusion detection, and the integrity of multimedia
content is not addressed, while watermarking and encryption
tools guarantee authenticity but do not detect anomalies in the
traffic. Such limitations support the importance of having a
single, lightweight, and privacy-aware solution that combines
anomaly detection and multimedia integrity checking of
resource-constrained CIoT devices.
III. T HE P ROPOSED M ODEL
A. Overview of the Proposed MAID-KD Framework
The MAID-KD framework enhances multimedia security
in CIoT devices by enabling on-device threat detection under
resource constraints. As shown in Fig. 1 and Fig. 2, MAIDKD has two phases. In the Training Phase, heterogeneous
multimedia IoT data (video, audio, images, telemetry) are

processed by a Transformer-based teacher model to learn
rich spatio-temporal and cross-modal representations, while a
lightweight CNN+LSTM student model is trained in parallel
on smaller data batches. Knowledge is distilled through
high-level features and soft targets, limiting the student’s
exposure to raw data and reducing privacy risks. In the
Deployment Phase, the trained student runs locally on CIoT
edge devices to analyze live multimedia streams, performing
anomaly detection and anomaly type classification without
teacher support or cloud dependency. This approach minimizes
computational and bandwidth overhead while maintaining
multimedia data confidentiality and integrity across CIoT
environments.
B. System Model
We consider a distributed CIoT network comprising N edge
nodes, D = {d1 , d2 , . . . , d N }, where each node processes
multimedia data (e.g., video, audio, telemetry) under strict
resource constraints. The framework combines a high-capacity
teacher model Tφ , trained offline on large-scale CIoT datasets,
with a lightweight student model Sθ deployed on edge devices.
The objective is to transfer knowledge from Tφ to Sθ for
anomaly detection and anomaly type classification, while
maintaining user data privacy.
Each node di observes input-label pairs
( j)

( j)

i
,
Zi = {(xi , yi )}nj=1

(1)

( j)

where xi ∈ Rd represents multimedia feature vectors and
( j)
yi ∈ C denotes the corresponding labels.
The global task set is defined as
T = {Tanom , Ttype },

(2)

covering both anomaly detection and anomaly type classification. By distilling Tφ ’s knowledge into Sθ across T in (2),
the framework provides robust protection against multimediadriven blended attacks in CIoT environments.
C. Teacher-Guided Feature Transformation
Let the input x ∈ Rd represent multimedia data such as
video frames, audio streams, and telemetry packets commonly
found in CIoT environments. These heterogeneous inputs are
drawn from a distribution X and often include blended attack
patterns, making robust representation learning essential.
To address this, we define the teacher model Tφ : Rd → HT
and the student model Sθ : Rd → H S as parameterized
mappings that transform the input x into their respective latent
spaces HT and H S .

2468

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

The teacher generates a high-level embedding of the input
using a linear projection followed by a non-linear activation,
as shown in Equation (3)
FT (x) = σ (WT x + bT ),

(3)

where WT ∈ Rk×d and bT ∈ Rk denote the trainable weights
and biases. Analogously, the student performs a similar
transformation into its latent space shown in Equation (4)
F S (x) = σ (W S x + b S ),

(4)

where W S ∈ Rk×d and b S ∈ Rk are the student parameters.
To ensure the student embedding space remains consistent
with the teacher, we minimize the squared ℓ2 -norm distance
between FT (x) and F S (x) as defined in Equation (5)
1F = ∥FT (x) − F S (x)∥22 .

(5)

This objective is averaged across the data distribution, as in
Equation (6), to obtain the empirical alignment loss
J1 (θ ) = Ex∼X [1F ] .

(6)

To further improve generalization, a regularization term based
on the Frobenius norm of the student’s weight matrix is added
to Equation (7)
R1 (θ ) = λ1 · J1 (θ ) + α∥W S ∥2F ,

(7)

where λ1 balances the alignment term and α penalizes large
weights.
In addition to latent feature alignment, the student also
mimics the teacher’s output distribution using temperaturescaled softmax logits in Equations (8) and (9)


Tφ (x)
,
(8)
ŷT = softmax
τ


Sθ (x)
ŷ S = softmax
,
(9)
τ
where τ > 0 is the temperature parameter that softens class
probabilities. The divergence between the softened outputs
is measured using the scaled Kullback–Leibler divergence
Equation (10)
LKD = τ 2 · KL( ŷT ∥ ŷ S ).

(10)

Together, the feature alignment loss R1 (θ) from Eq. (7) and
the knowledge distillation loss LKD from Eq. (10) establish a
dual-objective function that enforces structural similarity in the
latent space and consistency at the decision level. Algorithm 1
outlines the teacher-guided feature transformation process.
It aligns the student’s lightweight multimedia representations
with the teacher’s richer embeddings by minimizing featurelevel and output-level discrepancies. The algorithm iteratively
updates student parameters using feature alignment loss,
KL-divergence on softened probabilities, and regularization,
resulting in a compact yet accurate student model.

Algorithm 1 Teacher-Guided Feature Transformation
Result: Updated student parameters ω S
N , temperature
Input: Multimedia input set X = {xi }i=1
τ , learning rate η, teacher weights ωT , initial
student weights ω S , penalties λ, α
Output: Optimized student parameters ω S
Initialize student weights ω S := {M, c} ;
// Projection layer parameters
Set total loss L := 0 ;
// Initialize loss
accumulator
foreach sample xi in X do
Compute teacher embedding: zT := σ (Axi + a) ;
// Rich multimedia features
Compute student embedding: z S := σ (Mxi + c) ;
// Lightweight representation
for j := 1 to k do
Feature alignment error: δ j := (z T, j − z S, j )2
Accumulate feature loss: L := L + δ j
end
P
Regularization: R := p,q M 2pq
Teacher and student logits:
ℓT := T (xi ), ℓ S := S(xi ) Softened probabilities:
πT := softmax(ℓT /τ ),
S /τ )
Pπ S := softmax(ℓ
π
KL divergence: D := c πT,c log πT,c
S,c
Total loss: L := λ · L + α · R + τ 2 · D
end
for t := 1 to Tmax do
Gradient: ∇ω S := ∇ω S L ;
// Backpropagation
Parameter update: ω S := ω S − η · ∇ω S
end
return ω S ;
// Final trained student
network

D. Variational Knowledge Projection
In multimedia-centric CIoT environments, data streams such
as video frames, audio signals, and telemetry often contain
overlapping attack signatures. To enhance the robustness of the
student model against such blended anomalies, the extracted
features are projected into a probabilistic latent subspace using
variational inference. This enables the student model to learn
compact multimedia-aware representations while maintaining
uncertainty estimates for better generalization and resilience
against adversarial noise.
We define a variational posterior distribution qθ (z|x) over
the latent variable z ∈ Rm conditioned on the input sample
x ∈ Rd . As expressed in Equation 11, this posterior is modeled
as a multivariate Gaussian distribution
qθ (z|x) = N (z | µθ (x), 6θ (x))

(11)

where the mean vector µθ (x) and covariance matrix 6θ (x)
are derived from the student feature space F S (x). The mean
mapping is computed as
µθ (x) = Wµ F S (x) + bµ

(12)

ULLAH et al.: LIGHTWEIGHT MULTIMEDIA ANOMALY AND INTEGRITY DETECTION FOR CONSUMER IoT

where Wµ ∈ Rm×k and bµ ∈ Rm are learnable parameters.
Similarly, the covariance in Equation 13 is obtained using an
exponential activation to enforce positivity
6θ (x) = diag (exp(Wσ F S (x) + bσ ))

(13)

ensuring numerical stability and a valid Gaussian distribution.
Latent variable sampling follows Equation 14, where
the reparameterization trick introduces stochasticity while
preserving differentiability
1/2

z = µθ (x) + 6θ (x) ⊙ ϵ,

ϵ ∼ N (0, I)

(14)

This sampled latent vector z is subsequently decoded to
reconstruct the original feature embedding using Equation 15
Fz = ReLU(Wz z + bz )
∈ Rk×m and b

(15)

∈ Rk parameterize the decoder.

where Wz
z
The objective function in Equation 16 is designed to balance
the reconstruction fidelity of multimedia features and the
regularity of the latent space
h
i
LVAE = Ez∼qθ (z|x) ∥F S (x) − Fz ∥2 + β · KL (qθ (z|x)∥ p(z))
(16)
This loss combines two objectives: the first term preserves
the accuracy of reconstructed multimedia features, while
the second term regularizes the latent space to maintain
generalization and prevent overfitting. The first term ensures
that reconstructed features accurately reflect multimediaspecific information, while the second term enforces proximity
to a prior p(z) = N (0, I) as defined in Eq. 17:
p(z) = N (0, I)

(17)

Regularization through this KL-divergence prevents overfitting
and guarantees a well-structured latent space, which is critical
for detecting subtle anomalies in compressed multimedia
signals. This standard normal prior serves as a reference
distribution that stabilizes the latent representation and avoids
bias toward specific multimedia samples.
Finally, the scaled variational loss in Equation 18 is
integrated into the overall optimization objective of the student
J2 (θ ) = λ2 · LVAE

(18)

The coefficient λ2 adjusts the influence of the variational
projection during training, ensuring that the model learns
uncertainty-aware yet efficient feature representations.
where λ2 > 0 controls the contribution of this probabilistic
projection to the multi-objective optimization. The above
Equations 11 to 18 enhance the ability of the student model to
operate reliably in CIoT scenarios where privacy constraints
prohibit centralized multimedia data storage and real-time
anomaly detection must occur at the edge.
Algorithm 2 illustrates the variational projection of student
features. It constructs a probabilistic latent space using
variational inference to capture heterogeneous CIoT data
patterns. The algorithm estimates Gaussian distributions
over latent codes, applies the reparameterization trick for
sampling, and reconstructs multimedia features. By jointly
minimizing reconstruction error and KL-divergence, it ensures
robust, privacy-preserving, and uncertainty-aware student
representations.

2469

Algorithm 2 Variational Projection of Student Features
Result: Latent embedding z and reconstructed
multimedia-aware feature Fz
Input: Student multimedia features f (video, audio,
telemetry), projection weights Wµ , Wσ , Wz ,
biases bµ , bσ , bz , iterations K
Output: Projection loss J2
Initialize multimedia prior p(z) := N (0, I) ;
// Gaussian prior over latent space
for k := 1 to K do
Compute latent mean µ := Wµ f + bµ ;
// Encodes feature statistics from
multimedia data
Compute latent variance 6 := exp(Wσ f + bσ ) ;
// Ensures positive-definite
covariance
foreach sample ϵ ∼ N (0, I) do √
Compute latent code z := µ + 6 ⊙ ϵ ;
// Reparameterization trick
Decode multimedia-aware reconstruction
Fz := ReLU(Wz z + bz ) ;
// Reconstruction layer
Evaluate reconstruction loss r := ∥ f − Fz ∥2 ;
// Enforces fidelity in
multimedia features
end
Compute posterior q := N (z|µ, 6) ; // Latent
posterior distribution
Estimate KL-divergence D := KL(q∥ p(z)) ;
// Aligns latent codes with prior
for robust generalization
Combine total loss L := r + β · D ;
// Weighted reconstruction and
regularization
Backpropagate gradient ∇θ L ;
// Parameter
optimization
Update parameters θ := θ − η · ∇θ L ;
// Gradient descent step
end
Compute final objective J2 := λ2 · L ; // Scaled
variational loss
return J2 and reconstructed feature Fz

E. Multi-Objective Student Optimization
The optimization objective in the proposed framework
must ensure that the student model Sθ effectively captures
the teacher’s decision boundaries while preserving latentspace regularity and maintaining high classification accuracy.
To this end, we define a composite loss function comprising
three terms: knowledge distillation (KD), variational encoding
(VAE), and task-specific cross-entropy (CE).
The supervised classification loss is formulated as:
LCE = −

X
c∈C

yc log ŷ S,c

(19)

2470

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

where yc and ŷ S,c denote the ground-truth label and
predicted probability for class c, respectively. Minimizing LCE
guarantees discriminative training on hard labels and enforces
separability among anomaly categories and normal segments.
To unify the objectives, we define the total loss:
LTotal = λ1 LKD + λ2 LVAE + λ3 LCE

(20)

where LKD (Eq. 10) aligns soft decision boundaries,
LVAE (Eq. 16) enforces latent-space regularization, and
LCE enforces classPdiscrimination. The non-negative weights
3
λ1 , λ2 , λ3 satisfy
i=1 λi = 1, ensuring convexity of the
combined objective.
To mitigate instability due to noisy gradients from
heterogeneous multimedia inputs, we penalize large gradients
by introducing:
R2 (θ) = γ · ∥∇θ LTotal ∥22

(21)

where γ > 0 controls the smoothness of the optimization
trajectory. By the quadratic penalty in Eq. 21, we bound
the spectral norm of the Hessian Hθ , thereby improving the
Lipschitz continuity of the update step.
The parameter update for the student model is then
expressed as:
θ t+1 = θ t − η · ∇θ (LTotal + R2 (θ ))

(22)

where η is the learning rate. Under the assumption of βsmoothness of LTotal , the displacement of parameters satisfies:
1θt = θ t+1 − θ t
∥1θt ∥2 ≤ η(L 1 + L 2 + L 3 )

(23)
(24)

where L 1 , L 2 , L 3 are Lipschitz constants associated with LKD ,
LVAE , and LCE , respectively. Eq. 24 guarantees bounded step
sizes and avoids divergence when optimizing over highly
imbalanced multimedia datasets.
By leveraging the above bounds, the expected loss is shown
to converge exponentially:
E[LTotal ] ≤ L0 · e−ηt + ρ

(25)

where L0 is the initial loss value and ρ is the minimum
achievable floor determined by inherent data uncertainty. This
convergence property is critical for resource-constrained CIoT
devices, ensuring stable training even with non-stationary input
distributions.
Finally, the predictive performance of the student model for
each security task Ti is measured as:
N

i
1 X
I[ ŷ j = y j ]
AccTaski =
Ni

(26)

j=1

where Ni denotes the number of samples for task Ti and I[·]
is the indicator function. Eq. 26 explicitly quantifies the tasklevel accuracy, which is optimized jointly with the alignment
and regularization losses.
Through the integration of Eqs. 19–26, the student model
is trained to balance multimedia-aware feature alignment,
latent uncertainty modeling, and predictive accuracy, making
it robust for real-time deployments in CIoT environments.

Algorithm 3 Multi-Objective Optimization of Student
Parameters
Result: Optimized parameters θ t+1 and task accuracy
AccTaski
Input: Training data x, ground truth y; loss weights
λ1 , λ2 , λ3 ; gradient penalty γ ; learning rate η;
Lipschitz constant bound C; total iterations T
Output: Trained parameters θ
Initialize parameters θ := θ 0 ;
// Initial
student parameters
Set cumulative loss L := 0
for t := 1 to T do
Compute logits s := Sθ (x) ;
// Student
forward pass
Compute class probabilities ŷ := softmax(s) ;
// Prediction scores
P
Evaluate CE loss ℓ3 := − c yc log ŷc ;
// Classification objective
Retrieve KD loss ℓ1 := LKD ;
// Soft
boundary alignment
Retrieve VAE loss ℓ2 := LVAE ;
// Latent
regularization
Merge loss components: L := λ1 ℓ1 + λ2 ℓ2 + λ3 ℓ3
Compute gradient penalty: G := γ · ∥∇θ L∥2
Update parameters: θ ′ := θ − η · ∇θ (L + G)
Compute displacement: δ := ∥θ ′ − θ∥2
Clip update if unstable:
δ > ηC ⇒ θ ′ := θ − η · Cδ · ∇θ (L + G)
Apply parameter update θ := θ ′
end
foreach task i do
Predict labels: ŷ j := arg maxc Sθ (x j )
P i
Compute accuracy: ai := N1i Nj=1
I[ ŷ j = y j ]
end
|T |
return θ, {ai }i=1

Algorithm 3 performs joint optimization of the student
model by combining knowledge distillation, variational regularization, and classification objectives. It adaptively balances
these loss components, applies gradient penalty and Lipschitz
constraints for stability, and updates parameters using
stochastic gradient descent while monitoring convergence and
accuracy across tasks.

IV. E XPERIMENTAL S ETUP
The experimental setup validates the effectiveness of the
proposed MAID-KD framework across three dimensions:
knowledge transfer fidelity, multimedia feature representation
quality, and predictive accuracy under multi-task conditions.
These objectives are achieved through experiments
using a large-scale multimedia anomaly/tampering
detection dataset, teacher–student model architectures
of different capacities, and comprehensive evaluation
metrics.

ULLAH et al.: LIGHTWEIGHT MULTIMEDIA ANOMALY AND INTEGRITY DETECTION FOR CONSUMER IoT

A. Computational Environment
All experiments were carried out on a workstation equipped
with an NVIDIA RTX 3090 GPU (24 GB VRAM), an Intel
Core i9 CPU, and 64 GB RAM, running Ubuntu 22.04 LTS.
The models were implemented in PyTorch 2.1 with CUDA
12.1 and cuDNN 8.9 support. Python 3.11 was used for
all scripting. Fixed random seeds were applied throughout
the pipeline to ensure reproducibility. The configuration was
chosen to reflect real-world CIoT constraints, where edge
deployments must be memory and latency-efficient.

2471

TABLE I
H YPERPARAMETER S ETTINGS U SED FOR E XPERIMENTATION

B. Dataset
To evaluate multimedia security performance, we employed
the UCF-Crime dataset [37], a large-scale video anomaly
dataset widely used for multimedia tampering and intrusion
detection research. This dataset contains 1,900 untrimmed
surveillance videos (approximately 128 hours) collected
from real-world CIoT-like environments such as parking
lots, subway stations, and residential areas. The videos
span 13 anomaly categories, including vandalism, burglary,
tampering, fighting, robbery, and abuse, as well as a normal
category representing benign activities.
For our experiments, we split each video into fixed-length
segments of 64 consecutive frames sampled at 10 FPS. This
segmentation allows the MAID-KD framework to operate at
the sequence level while preserving spatio-temporal context.
Two multi-task learning objectives were defined: (i) Task 1
– anomaly detection: classify each segment as anomalous or
normal, and (ii) Task 2 – anomaly type classification: classify
anomalous segments into one of the 13 predefined anomaly
categories. The dataset was partitioned into training (70%),
validation (10%), and test (20%) splits, ensuring balanced
distribution of classes across splits.
The reason for selecting the UCF-Crime dataset is that
its surveillance videos closely resemble the multimedia
information produced by consumer IoT devices such as
home cameras and smart sensors. It has a variety of scenes,
anomalies, and environmental variations representing CIoT
operating conditions. Therefore, it gives a practical baseline
against which the performance of MAID-KD in identifying
multimedia anomalies and checking the integrity of content
can be assessed based on edge conditions.
C. Consumer IoT Testbed Configuration
The experimental environment was designed to replicate a
realistic CIoT deployment where multimedia data fromtributed
surveillance, esuch aseras and smart devices is processed
at heterogeneous edge nodes. Multiple virtual edge nodes
were instantiated, each holding a partition of the dataset
to simulate the non-IID (non-identically distributed) data
distribution common in CIoT. The teacher model was deployed
on a central node with high computational capacity, while
student models were trained and evaluated on resourceconstrained edge nodes. This setup enabled controlled
evaluation of communication overhead, latency, and scalability
in multimedia-intensive CIoT environments.

D. Implementation and Training Details
Both the teacher and student models were adapted for
sequential video frame analysis. The teacher network was
configured as a deep Transformer-based encoder capable
of capturing long-range spatio-temporal dependencies in
video sequences. The student model employed a lightweight
CNN-LSTM backbone optimized for edge deployment,
preserving essential spatio-temporal representations while
reducing computational cost. Models were implemented in
PyTorch, initialized using Xavier initialization, and trained
with the Adam optimizer. The learning rate followed a
cosine annealing schedule, and early stopping was triggered
based on validation loss. All experiments were conducted
for a fixed number of epochs with dropout and batch
normalization applied for regularization. Hyperparameters
used are summarized in Table I.

E. Evaluation Metrics and Baseline Schemes
The performance of the proposed MAID-KD framework
was evaluated using metrics capturing classification accuracy,
robustness, and resource efficiency for multimedia-aware
intrusion detection. The primary metrics include Accuracy,
Precision, Recall, and F1-score for both anomaly detection
and anomaly type classification tasks. AUC-ROC is used
to assess discriminative ability, while inference latency and
memory footprint quantify computational efficiency on edge
devices. These evaluation metrics were selected because they
represent both analytical performance and real-world usability
of the proposed framework. Accuracy and F1-score indicate
how reliably MAID-KD distinguishes between normal and
abnormal multimedia activities, while precision and recall
show how well it balances false alerts and missed detections.
Inference time and memory use measure its responsiveness
and efficiency on constrained IoT devices, confirming that
the framework can operate effectively in practical consumer
settings.
To evaluate the quality of knowledge transfer, the divergence
between teacher and student probability distributions was
analyzed. MAID-KD was compared against three competitive
baselines: FLEKD [13], VAD-MTL [38], and TAML [19],
each adapted for multimedia anomaly detection by replacing

2472

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

Fig. 3. Comparison of teacher and MAID-KD student models across accuracy, F1-score, and precision–recall AUC. Results show that the student closely
approximates the teacher’s performance while maintaining lightweight efficiency suitable for CIoT deployment.

their original feature extraction pipelines with video and audio
feature encoders.
V. R ESULTS
The results section provides a comprehensive evaluation of
the proposed MAID-KD framework in terms of performance,
efficiency, and scalability for multimedia anomaly detection
tasks. The analysis is divided into two subsections. The first
subsection evaluates the teacher and student models to assess
the effectiveness of the knowledge distillation process. The
second subsection compares the proposed MAID-KD student
model with baseline schemes, highlighting its performance
advantages.
A. Teacher Vs Student Analysis
This subsection presents a comparative evaluation of
the teacher and the MAID-KD student models across
multiple performance metrics, including accuracy, precisionrecall AUC, F1-score, loss convergence, inference time,
and model complexity. These analyses provide insights into
the knowledge distillation effectiveness and computational
advantages achieved by the MAID-KD student model.
This comparison demonstrates that the student model can
effectively process heterogeneous multimedia CIoT data (e.g.,
video segments, audio streams, and multimedia telemetry)
while maintaining strong predictive accuracy, a critical factor
for safeguarding multimedia-rich CIoT applications.
Figure 3(a) illustrates the accuracy comparison across
multiple runs. The teacher model consistently achieved higher
accuracy, with a mean accuracy of around 97%, while the
MAID-KD student model followed closely with approximately
95%. This confirms that the student model successfully
approximates the teacher’s predictive capability with only a
marginal drop in accuracy. Figure 3(b) presents the F1-score
comparison, where the teacher demonstrates higher
F1-scores with tighter confidence intervals, highlighting
superior balance between precision and recall. The student’s
F1-scores remain competitive, validating the effectiveness of
the MAID-KD knowledge distillation strategy. Figure 3(c)
shows the precision-recall AUC comparison. The teacher
achieves a slightly higher AUC (50.6%) compared to

Fig. 4. Loss convergence trends of teacher and MAID-KD student models
during training and validation. The student achieves faster convergence with
slightly higher final loss.

the student (49.4%), indicating improved discrimination
capability for positive multimedia anomaly classes (e.g.,
tampered frames and injected audio).
Figure 4 shows the loss convergence patterns during
training. The teacher model’s training and validation losses
decrease steadily, achieving lower final loss values. The
MAID-KD student model converges faster but stabilizes at
slightly higher loss values compared to the teacher. This
behavior is expected as the student trades off model capacity
for reduced complexity. Faster convergence and competitive
accuracy are particularly beneficial in CIoT deployments
where continuous multimedia streams must be analyzed and
anomalies detected in real time.
Figure 5 compares inference times, revealing a significant
efficiency gain for the student model. The teacher model incurs
an average inference time of 18.5 ms per video segment, while
the student achieves a much lower 7.3 ms, demonstrating
its suitability for resource-constrained multimedia edge
environments in CIoT systems.
Finally, Figure 6 compares model complexity in terms of
size and parameter count. The teacher model contains 120 MB
and 24 million parameters, while the student is significantly
lighter at 45 MB and 9 million parameters. This reduction

ULLAH et al.: LIGHTWEIGHT MULTIMEDIA ANOMALY AND INTEGRITY DETECTION FOR CONSUMER IoT

Fig. 5. Inference time comparison per video segment between teacher and
student models. The student achieves significantly lower latency.

Fig. 6. Model size (MB) and parameter count (Million) comparison between
teacher and student networks. MAID-KD achieves a smaller memory footprint
while preserving strong detection accuracy, optimizing for resource-limited
consumer devices.

highlights the efficiency gained through the MAID-KD
framework without severely compromising performance.
In summary, the MAID-KD student model demonstrates
competitive performance with substantial reductions in computational cost, memory footprint, and inference latency. These
improvements validate the proposed knowledge distillation
strategy as highly effective for deploying anomaly and
integrity detection models in multimedia-intensive CIoT
environments.
B. Baseline Scheme Comparison
This subsection compares the proposed student model
with three state-of-the-art baseline schemes: FLEKD [13],
VAD-MTL [38], and TAML [19]. All baseline models were
adapted for multimedia anomaly and integrity detection
by replacing their original feature extraction modules
with video feature encoders. Each scheme was trained
and evaluated under identical conditions for fairness. The
comparison focuses on key performance metrics, including
accuracy, precision, recall, F1-score, inference time, and
resource utilization, emphasizing the generalization ability and
efficiency of the proposed framework. Unlike the baselines,
MAID-KD maintains superior performance when analyzing
diverse multimedia data streams from CIoT devices, such
as real-time surveillance video and sensor-generated video
sequences.

2473

Fig. 7.
Performance comparison of MAID-KD and baseline schemes
(FLEKD, VAD-MTL, and TAML) across accuracy, precision, recall, and
F1-score. MAID-KD consistently achieves superior detection performance
with higher overall balance between accuracy and efficiency.

Fig. 8. Loss convergence analysis for MAID-KD and baseline schemes over
20 epochs. The proposed model converges faster and achieves lower final loss
values, highlighting its robust optimization and stability.

As shown in Figure 7, the proposed MAID-KD consistently
achieves the highest scores for all four evaluation metrics,
surpassing FLEKD, VAD-MTL, and TAML. The improved
accuracy illustrates that MAID-KD captures more discriminative patterns through its knowledge distillation pipeline.
Similarly, higher precision and recall values demonstrate the
ability to reduce both false positives and false negatives,
leading to a superior F1-score and balanced detection
performance in multimedia contexts.
Figure 8 shows the loss convergence trends. MAID-KD
converges substantially faster than the baseline schemes and
stabilizes at a lower final loss value. This faster convergence
not only reduces the number of epochs needed to reach
optimal performance but also highlights stronger optimization
and a more robust ability to generalize to unseen multimedia
data.
The inference time distribution in Figure 9 demonstrates
the efficiency of MAID-KD. It achieves significantly lower
inference latency compared to the baselines, making it suitable
for real-time multimedia CIoT applications. This improvement
is attributed to the compact architecture of MAID-KD, which
executes faster without sacrificing detection performance.
Lower inference latency allows MAID-KD to respond more
quickly to threats in multimedia-intensive deployments where
delayed detection can lead to serious breaches.

2474

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

accuracy and F1-score indicate that the performance gains of
MAID-KD compared to the baseline schemes are statistically
significant and not due to random variation.
D. Additional Practical Validation

Fig. 9. Inference time distribution of MAID-KD and baseline schemes.
MAID-KD demonstrates the lowest latency, confirming its real-time efficiency
for multimedia processing on CIoT edge devices.

To test the applicability of MAID-KD in real applications,
it was evaluated under three conditions: (i) video compression
and packet loss, (ii) lower resolution and frame rate, and
(iii) edge inference using a CPU. In all these environments,
MAID-KD maintained high accuracy. However, it exhibited
slight degradation at high compression and low frame rates,
and incurred sub–real-time latency under CPU-only execution.
These results demonstrate its capability and preparedness for
CE/CT devices such as smart cameras and wearables.
VI. C ONCLUSION

Fig. 10. Model size and parameter count comparison between MAID-KD
and baseline schemes. The lightweight architecture of MAID-KD enables
resource-efficient deployment without compromising performance accuracy.

Finally, Figure 10 compares model size and parameter
counts. MAID-KD achieves the smallest model size and
lowest parameter count among all schemes, making it the
most resource-efficient option. Its compact design facilitates
deployment on resource-constrained CIoT edge devices, where
memory and storage are limited. Despite this lightweight
design, MAID-KD consistently outperforms the larger,
more resource-intensive baseline schemes. Overall, these
results validate that MAID-KD delivers superior accuracy,
efficiency, and robustness, aligning with the requirements
of real-time multimedia anomaly and integrity detection in
CIoT environments. MAID-KD performs better because its
knowledge distillation and multi-task design reinforce each
other. Distillation helps the student model learn compact
yet expressive features from the teacher, while the multitask setup allows shared learning between anomaly detection
and integrity verification. This combination improves feature
quality and stability, leading to stronger accuracy and
efficiency than the baseline methods.
C. Statistical Validation
All experiments were repeated 5 times using various
random seeds to make the results more reliable. Mean and
standard deviation of each measure were calculated, and
95% confidence interval was obtained using the Student’s
t-distribution. The narrow intervals (from +1.2% to -1.2% ) in

This work introduces MAID-KD, a lightweight knowledge
distillation model for multimedia anomaly and integrity
detection in consumer IoT systems. It combines anomaly
detection and integrity verification in a single edge-optimized
model, achieving high accuracy with smaller model size and
lower latency. The results indicate that MAID-KD is more
efficient and robust than existing state-of-the-art baselines
in multimedia-intensive scenarios. Its privacy-conscious and
lightweight design allows it to be practically used in smart
surveillance, health wearables, and home-connected devices,
while providing low-latency, bandwidth-efficient operation.
Although the performance is impressive, it can degrade on
ultra-low-power devices, and slight privacy risks may still exist
when sensitive data is processed. The further research in the
field will concentrate on adaptive optimization and privacy
improvement to optimize the application of CIoT in the real
world.
MAID-KD has high accuracy and efficiency, but it still
has some limitations. The student model can perform poorly
when run on small, low-power hardware with limited memory
or without GPU acceleration. Also, although the framework
reduces the exposure of the data by storing the knowledge in
a distilled form, the partial privacy areas might still exist in
the process of dealing with sensitive multimedia content. The
existing results are based on the datasets. However, real-world
CIoT deployments can exhibit unexpected noise and nonhomogeneous data quality. Future work will explore extending
the framework to deepfake detection and multi-modal security
tasks, further strengthening multimedia integrity in nextgeneration CE applications.
The proposed MAID-KD framework is closely related to
consumer electronics (CE) and consumer technologies (CT).
Its privacy-conscious and lightweight design allows it to be
deployed on CE devices such as smart cameras, healthmonitoring wearables, and voice-activated home hubs to
handle real-time multimedia data processing. MAID-KD may
be executed directly on edge processors or embedded firmware
to perform on-device anomaly detection and multimedia
integrity checks without cloud support. This attribute lowers
latency, ensures user privacy, and enhances confidence in nextgeneration CE/CT systems.

ULLAH et al.: LIGHTWEIGHT MULTIMEDIA ANOMALY AND INTEGRITY DETECTION FOR CONSUMER IoT

R EFERENCES
[1] D. Pal, V. Vanijja, X. Zhang, and H. Thapliyal, “Exploring the
antecedents of consumer electronics IoT devices purchase decision: A
mixed methods study,” IEEE Trans. Consum. Electron., vol. 67, no. 4,
pp. 305–318, Nov. 2021.
[2] M. Sayad Haghighi, F. Farivar, A. Jolfaei, A. B. Asl, and W. Zhou,
“Cyber attacks via consumer electronics: Studying the threat of covert
malware in smart and autonomous vehicles,” IEEE Trans. Consum.
Electron., vol. 69, no. 4, pp. 825–832, Nov. 2023.
[3] S. Mukherjee, S. Mukhopadhyay, and S. Sarkar, “ParticleStego: A
steganographic algorithm for securing consumer electronics enabled
social Internet of Things (SIoT),” IEEE Trans. Consum. Electron.,
vol. 71, no. 2, pp. 2592–2602, May 2025.
[4] S. Hu, F. Zou, Y. Xiao, H. Ke, and J. Wang, “Integrating embedded
cyber-physical systems in smart energy for AI-enhanced real-time
crowd monitoring and threat detection,” IEEE Trans. Consum. Electron.,
vol. 71, no. 3, pp. 8363–8373, Aug. 2025.
[5] M. Koca, “Real-time security risk assessment from CCTV using hand
gesture recognition,” IEEE Access, vol. 12, pp. 84548–84555, 2024.
[6] T. Srour, A. M. El-Rifaie, M. A. M. El-Bendary, M. Eltokhy,
A. E. Abouelazm, and B. Neji, “Multimedia privacy protection: An
N-round cascaded cryptosystem based on merged multi-chaotic maps
under various image attacks,” Frontiers Comput. Sci., vol. 7, May 2025,
Art. no. 1551166.
[7] S. Yang, X. Zheng, Z. Xu, and X. Wang, “A lightweight approach
for network intrusion detection based on self-knowledge distillation,”
in Proc. ICC-IEEE Int. Conf. Commun., May 2023, pp. 3000–3005.
[8] B. Asal and A. B. Can, “Ensemble-based knowledge distillation for
video anomaly detection,” Appl. Sci., vol. 14, no. 3, p. 1032, Jan. 2024.
[9] D. Javeed, M. S. Saeed, I. Ahmad, P. Kumar, A. Jolfaei, and M. Tahir,
“An intelligent intrusion detection system for smart consumer electronics
network,” IEEE Trans. Consum. Electron., vol. 69, no. 4, pp. 906–913,
Nov. 2023.
[10] R. Chen, H. Xia, K. Wang, S. Xu, and R. Zhang, “KDRSFL: A
knowledge distillation resistance transfer framework for defending
model inversion attacks in split federated learning,” Future Gener.
Comput. Syst., vol. 166, May 2025, Art. no. 107637.
[11] G. Almahadin et al., “VANET network traffic anomaly detection using
GRU-based deep learning model,” IEEE Trans. Consum. Electron.,
vol. 70, no. 1, pp. 4548–4555, Feb. 2024.
[12] D. Wang, Q. Wang, Q. Hu, and K. Wu, “Temporal-spatial decoupled
self-supervised multi-task learning for video anomaly detection and
localization in intelligent transportation surveillance systems,” IEEE
Trans. Intell. Transp. Syst., early access, Apr. 21, 2025, doi:
10.1109/TITS.2025.3559166.
[13] J. Shen, W. Yang, Z. Chu, J. Fan, D. Niyato, and K.-Y. Lam, “Effective
intrusion detection in heterogeneous Internet-of-Things networks via
ensemble knowledge distillation-based federated learning,” in Proc. ICCIEEE Int. Conf. Commun., Jun. 2024, pp. 2034–2039.
[14] B. Xie, Z. Wang, Z. Zeng, D. He, and S. Chan, “DTKD-IDS: A
dual-teacher knowledge distillation intrusion detection model for the
industrial Internet of Things,” Ad Hoc Netw., vol. 174, Jul. 2025,
Art. no. 103869.
[15] P. Corcoran and A. Cucos, “Techniques for securing multimedia content
in consumer electronic appliances using biometric signatures,” IEEE
Trans. Consum. Electron., vol. 51, no. 2, pp. 545–551, May 2005.
[16] A. M. Eskicioglu and E. J. Delp, “An overview of multimedia content
protection in consumer electronics devices,” Signal Process., Image
Commun., vol. 16, no. 7, pp. 681–699, Apr. 2001.
[17] Z. Lv, L. Qiao, and H. Song, “Analysis of the security of Internet of
Multimedia Things,” ACM Trans. Multimedia Comput., Commun., Appl.,
vol. 16, no. 3s, pp. 1–16, Dec. 2020.
[18] W. Z. Khan, M. Y. Aalsalem, and M. K. Khan, “Communal acts of
IoT consumers: A potential threat to security and privacy,” IEEE Trans.
Consum. Electron., vol. 65, no. 1, pp. 64–72, Feb. 2019.
[19] L. Dong, W. Liang, and R. Wang, “Robust text image tampering
localization via forgery traces enhancement and multiscale attention,”
IEEE Trans. Consum. Electron., vol. 70, no. 1, pp. 3495–3507,
Feb. 2024.

2475

[20] N. Akhtar, M. Hussain, and Z. Habib, “DEEP-STA: Deep learningbased detection and localization of various types of inter-frame video
tampering using spatiotemporal analysis,” Mathematics, vol. 12, no. 12,
p. 1778, Jun. 2024.
[21] Z. Almutairi and H. Elgibreen, “A review of modern audio deepfake
detection methods: Challenges and future directions,” Algorithms,
vol. 15, no. 5, p. 155, May 2022.
[22] T. Zhang, “TMRB: Trusted multimedia scheme with redactable
blockchain,” IEEE Trans. Consum. Electron., vol. 71, no. 2,
pp. 3099–3107, May 2025.
[23] F. S. Alsubaei, “Smart deep learning model for enhanced IoT intrusion
detection,” Sci. Rep., vol. 15, no. 1, p. 20577, Jul. 2025.
[24] H. Peng, C. Wu, and Y. Xiao, “FD-IDS: Federated learning
with knowledge distillation for intrusion detection in nonIID IoT environments,” Sensors, vol. 25, no. 14, p. 4309,
Jul. 2025.
[25] C. Hazman, A. Guezzaz, S. Benkirane, and M. Azrour, “Enhanced IDS
with deep learning for IoT-based smart cities security,” Tsinghua Sci.
Technol., vol. 29, no. 4, pp. 929–947, Aug. 2024.
[26] R. Wazirali, R. Ahmad, A. Al-Amayreh, M. Al-Madi, and A. Khalifeh,
“Secure watermarking schemes and their approaches in the IoT
technology: An overview,” Electronics, vol. 10, no. 14, p. 1744,
Jul. 2021.
[27] K. Talathi and A. S. Biswas, “An efficient digital watermarking technique
for small scale devices,” 2025, arXiv:2506.06691.
[28] S. Ali, O. Abusabha, F. Ali, M. Imran, and T. Abuhmed, “Effective
multitask deep learning for IoT malware detection and identification
using behavioral traffic analysis,” IEEE Trans. Netw. Service Manage.,
vol. 20, no. 2, pp. 1199–1209, Jun. 2023.
[29] L. Ma, J. He, K. Lu, D. Wang, L. Yin, and Z. Li, “A contrastive learning
and knowledge distillation-based framework for efficient federated
intrusion detection in IoT,” Syst. Sci. Control Eng., vol. 13, no. 1,
Dec. 2025, Art. no. 2518963.
[30] A. K. Singh, D. Kundur, and M. Conti, “Introduction to the special
issue on integrity of multimedia and multimodal data in Internet of
Things,” ACM Trans. Multimedia Comput., Commun., Appl., vol. 20,
no. 6, pp. 1–4, Mar. 2024, doi: 10.1145/3643040.
[31] V. Rey, P. M. Sánchez Sánchez, A. Huertas Celdrán, and G. Bovet,
“Federated learning for malware detection in IoT devices,” Comput.
Netw., vol. 204, Feb. 2022, Art. no. 108693.
[32] K. Wang, A. Zhang, H. Sun, and B. Wang, “Analysis of recent deeplearning-based intrusion detection methods for in-vehicle network,”
IEEE Trans. Intell. Transp. Syst., vol. 24, no. 2, pp. 1843–1854,
Feb. 2023.
[33] A. Rehman et al., “Immersive embedded consumer model leveraging AI with zero-trust architecture for cyber-physical system,”
IEEE Trans. Consum. Electron., early access, Mar. 25, 2025, doi:
10.1109/TCE.2025.3554095.
[34] W. Lo, H. Alqahtani, K. Thakur, A. Almadhor, S. Chander, and
G. Kumar, “A hybrid deep learning based intrusion detection system
using spatial–temporal representation of in-vehicle network traffic,” Veh.
Commun., vol. 35, Jun. 2022, Art. no. 100471.
[35] X. Wang, A. Shankar, K. Li, B. D. Parameshachari, and J. Lv,
“Blockchain-enabled decentralized edge intelligence for trustworthy 6G
consumer electronics,” IEEE Trans. Consum. Electron., vol. 70, no. 1,
pp. 1214–1225, Feb. 2024.
[36] F. Ullah, N. Mohammad, L. Mostarda, D. Cacciagrano, and Y. Zhao,
“Q-P2FL: Quantum-enhanced federated edge intelligence for privacypreserving adversarial attack detection on consumer edge devices,”
IEEE Trans. Consum. Electron., vol. 71, no. 2, pp. 4914–4924,
May 2025.
[37] W. Sultani, C. Chen, and M. Shah, “Real-world anomaly detection in
surveillance videos,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., Jun. 2018, pp. 6479–6488.
[38] M.-I. Georgescu, A. Barbalau, R. T. Ionescu, F. S. Khan,
M. Popescu, and M. Shah, “Anomaly detection in video
via
self-supervised
and
multi-task
learning,”
in
Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun. 2021,
pp. 12742–12752.
PAPER_TEXT
