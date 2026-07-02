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
# [670] Entropy-regulated cross-modal generative fusion for multimodal network intrusion detection
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
编号：670
题名：Entropy-regulated cross-modal generative fusion for multimodal network intrusion detection
年份：2025
DOI：10.1016/j.inffus.2025.103581
来源：Information Fusion
PDF：paper/10.1016_j.inffus.2025.103581.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：无
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\670.txt
- 原始字符数：103780
- 本次发送字符数：103780
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Information Fusion 126 (2026) 103581

Contents lists available at ScienceDirect

Information Fusion
journal homepage: www.elsevier.com/locate/inffus

Entropy-regulated cross-modal generative fusion for multimodal network
intrusion detection
Xiangbin Wang a,b , Qingjun Yuan a,b ,∗, Wentao Yu a,c , Qianwei Meng a,b , Siqi Lu a,b , Wenqi He a,b ,
Chunxiang Gu a,b , Yongjuan Wang a,b ,∗∗
a

Information Engineering University, Zhengzhou, 450001, Henan, China

b Henan Key Laboratory of Network Cryptography Technology, Zhengzhou, 450001, Henan, China
c Institute of Computing Technology, Chinese Academy of Sciences, Beijing, 100190, China

ARTICLE

INFO

Keywords:
Generative artificial intelligence
Intrusion detection system
Multimodal fusion
Diffusion model
Cross-modal representation
Differential entropy

ABSTRACT
With the increasing popularity of network encryption protocols, analyzing encrypted traffic has become a
significant challenge for network security. In this context, deep learning methods have been widely applied
to intrusion detection and traffic classification tasks due to their powerful feature extraction capabilities.
However, these methods still face two main limitations: relying on unimodal feature extraction, which ignores
the multimodal characteristics of network traffic, or adopting simple static fusion strategies, which may
fail to capture the complex semantic associations between different modalities. These limitations make it
challenging for models to detect sophisticated attacks concealed within otherwise normal encrypted traffic.
To address this challenge, this paper introduces an Entropy-Regulated Cross-Modal Generative Framework
for Intrusion Detection (ER-CMGI), which combines the generative power of diffusion models with dynamic
information-theoretic optimization techniques. The framework integrates variational autoencoders(VAEs) with
a lightweight diffusion model for multimodal feature extraction and generation. It implements an adaptive
fusion mechanism using a hybrid entropy-based approach that combines both traditional low-entropy priority
and inverse entropy weighting through learnable mixing coefficients. The cross-modal generation consistency is
achieved through a lightweight diffusion model, which enables self-supervised learning via direct cross-modal
generation and comparison. This design enhances semantic alignment across heterogeneous modalities through
cross-modal generative learning. Experimental results show that the proposed model achieves F1 scores of
99.12% and 97.81% on two datasets, respectively. This study presents a dynamically adaptive and entropyguided framework for intrusion detection in network environments, which shows effectiveness in capturing
complex attack patterns. By integrating dynamic feature fusion with cross-modal semantic modeling, the
framework enhances detection accuracy and interpretability, offering a promising approach for improving
network security under evolving threat scenarios.

1. Introduction
With the widespread adoption of network encryption protocols
(e.g., TLS 1.3, QUIC), traditional intrusion detection systems (IDS)
based on plaintext analysis are facing unprecedented challenges in
effectiveness [1–3]. These conventional methods – including port scanning, fixed signature matching, and superficial traffic analysis – are increasingly ineffective. Attackers now exploit encrypted channels to conceal malicious payloads, which renders these approaches insufficient
for modern threats.

This challenge has driven the development of deep learning-based
detection methods. Researchers expect deep neural networks to automatically extract implicit features from encrypted traffic [4–6]. Early
studies applied Convolutional Neural Networks (CNNs) to analyze traffic statistical features [7,8]. Others used Recurrent Neural Networks
(RNNs) to model temporal patterns [9,10]. Additionally, graph neural
networks (GNNs) have been leveraged to capture non-Euclidean spatial
features in network traffic [11,12].
However, unimodal deep learning approaches have fundamental
limitations. First, their reliance on single-source feature representations
hinders comprehensive understanding of complex attacks. Second, they

∗ Corresponding author at: Information Engineering University, Zhengzhou, 450001, Henan, China.
∗∗ Corresponding author at: Information Engineering University, Zhengzhou, 450001, Henan, China.

E-mail addresses: Moskyes@outlook.com (X. Wang), gcxyuan@outlook.com (Q. Yuan), pinkywyj@163.com (Y. Wang).
https://doi.org/10.1016/j.inffus.2025.103581
Received 3 June 2025; Received in revised form 14 July 2025; Accepted 24 July 2025
Available online 6 August 2025
1566-2535/© 2025 Elsevier B.V. All rights are reserved, including those for text and data mining, AI training, and similar technologies.

Information Fusion 126 (2026) 103581

X. Wang et al.

often neglect the multidimensional characteristics inherent in cyber
attacks. Third, these methods fail to recognize cross-modal correlation patterns in covert attacks. For example, DDoS attacks exhibit
burst connection patterns at the flow level, whereas encrypted malware may reveal protocol anomalies at the byte level. Such heterogeneous, cross-layer features cannot be adequately captured by unimodal approaches. This limitation highlights opportunities for applying
multimodal learning in intrusion detection systems [13–16].
Existing multimodal intrusion detection approaches, despite their
preliminary progress, reveal two structural deficiencies. First, current
frameworks employ static weight fusion strategies. These strategies predetermine fixed contribution ratios across modalities. This rigid design
overlooks the dynamic nature of traffic feature uncertainty. Specifically, the information entropy of different modalities in encrypted traffic inherently fluctuates with protocol types and encryption intensity.
Second, contemporary methods attempt to integrate multimodal representations. However, they inadequately address the inconsistency in
the latent space between heterogeneous features. For example, discrete
byte sequences and continuous statistical metrics differ fundamentally
in their representation. This misalignment results in suboptimal crossmodal alignment. Such shortcomings critically undermine detection
accuracy under adversarial conditions.
The advancement of generative artificial intelligence (GenAI) models offers new insights to address these bottlenecks. By constructing
cross-modal generative channels, the semantic consistency in latent
space can enhance the robustness of feature fusion. For instance, diffusion models have proven effective in modeling complex mapping
relationships between high-dimensional discrete data (e.g., network
byte sequences) and low-dimensional continuous features (e.g., traffic
statistics) [17,18]. The progressive denoising process inherent to diffusion models aligns intrinsically with the incremental feature extraction
of anomalous signals in network traffic. Their Markov chain structure
can model hierarchical correlations between raw bytes and packet
length sequences, providing new possibilities to overcome the mode
collapse issue in traditional generative models. However, their potential
in cybersecurity remains underexploited.
The aforementioned challenges indicate that constructing an effective encrypted traffic intrusion detection system requires simultaneously meeting two core requirements: (1) the capability to adapt to
multimodal feature uncertainties across different encryption scenarios
dynamically and (2) the establishment of consistent mapping relationships in heterogeneous feature spaces to capture cross-modal attack
patterns. While traditional generative models possess the potential for
cross-modal transformation, their fixed generative paradigms struggle
to adapt to dynamically changing network environments and lack
mechanisms for quantifying information uncertainty.
To address these issues, this paper proposes an Entropy-Regulated
Cross-Modal Generative Framework for Intrusion Detection (ER-CMGI).
This framework systematically addresses two fundamental limitations
in existing methods by integrating the probabilistic generative capabilities of diffusion models with dynamic information-theoretic fusion
strategies. First, it achieves adaptive adjustment of multimodal contributions through an entropy-guided fusion mechanism that dynamically
weights different modalities based on their information content. Second, it establishes semantic alignment between heterogeneous modalities using cross-modal generation consistency constraints implemented
through diffusion models. These complementary innovations enable
the model to simultaneously capture both deterministic patterns and
high-entropy anomalies in encrypted traffic, significantly enhancing the
detection capability for sophisticated attacks. Our main contributions
are as follows:
1. We have developed an end-to-end multimodal feature learning
system for network traffic specifically designed to handle the complexity of encrypted traffic. This system combines a variational autoencoder
(VAE) with a lightweight diffusion model, enabling it to simultaneously
process various modal features such as byte sequences and packet

length sequences of traffic. This architecture, while extracting the
hidden patterns in network traffic, effectively overcomes the limitations
of traditional methods in handling heterogeneous traffic features. In
particular, the fusion strategy we designed, based on information entropy theory, establishes a unified processing framework for different
types of network features, thereby enhancing the detection ability of
encrypted malicious traffic.
2. We have proposed an adaptive feature fusion mechanism based
on differential entropy, specifically aimed at solving the problem of optimal weight allocation for network traffic features. Unlike traditional
methods that simply favor low-entropy features, our hybrid entropy
strategy can simultaneously utilize both deterministic network behavior
features and high-entropy features that may contain anomalous traffic
patterns. This mechanism dynamically adjusts fusion weights based
on the information content of each modality, effectively addressing
the heterogeneity and diversity of network traffic while providing an
interpretable basis for security decision-making.
3. We have designed a cross-modal generation consistency framework, utilizing a lightweight diffusion model as a semantic alignment
tool between different network traffic modalities. Rather than using
generative models for data augmentation, we employ them to enforce cross-modal semantic consistency. By comparing the consistency
between original modality data and cross-modal representations generated by the diffusion model, we guide the encoder to learn more discriminative feature representations. This approach establishes semantic
mappings between network traffic features such as byte sequences and
packet length distributions, improving the encoder’s ability to capture
traffic patterns through self-supervised cross-modal generation.
The remainder of this paper is organized as follows: Section 2
reviews related work, Section 3 details the ER-CMGI architecture, Section 4 presents comprehensive experimental evaluations, and Section 6
concludes the research.
2. Related work
2.1. Unimodal deep learning for network traffic recognition
Deep learning has emerged as a dominant paradigm in network
traffic classification, particularly for analyzing encrypted traffic, where
traditional payload inspection is no longer viable. These methods typically operate on a unimodal input – such as raw packet bytes, timing
sequences, or statistical features – and leverage models like CNNs,
RNNs, GNNs, and Transformers to classify traffic types (e.g., HTTP,
FTP, VoIP) or detect anomalies [19–24]. In recent years, distributed approaches have also been explored to improve scalability and efficiency,
especially in large-scale or real-time traffic analysis scenarios [25–27].
Compared to rule-based approaches, deep learning models offer greater
flexibility through automatic feature extraction, reduced reliance on
manual engineering, and firm performance on large-scale datasets.
Existing approaches can be broadly categorized into three directions: (i) feature-based methods that rely on manually extracted statistics (e.g., flow duration, packet size distributions), (ii) end-to-end models that learn hierarchical representations directly from raw traffic data
(e.g., byte sequences, header fields), and (iii) distributed frameworks
that integrate deep learning with federated learning to enable collaborative training while preserving privacy [25,28,29]. While these
methods have demonstrated effectiveness in specific settings, there
remains room for improvement in terms of generalization across diverse scenarios, particularly when dealing with multimodal information
integration.
Feature-based models, while computationally efficient, may face
challenges in encrypted scenarios where discriminative signals in statistical metadata are limited. End-to-end models, although capable of
capturing fine-grained patterns in raw data, typically focus on single
modalities and may not fully exploit the complementary information available across different data representations. For example, raw
2

Information Fusion 126 (2026) 103581

X. Wang et al.

Table 1
Comparison of multimodal network traffic analysis methods.

bytes excel at capturing semantic content but may have limitations
in representing temporal dynamics, while packet length sequences
effectively model behavioral patterns but provide less detailed payload
information.
Building upon these insights, our proposed multimodal framework
integrates two complementary modalities: raw packet bytes and packet
length sequences. Through an entropy-guided adaptive fusion mechanism and cross-modal generation consistency loss, our approach systematically combines the strengths of both modalities to enhance
overall performance. This integration is supported by a theoretically
grounded framework that employs Kullback–Leibler (KL) divergence
to ensure alignment between latent representations, enabling dynamic
adaptation to varying network conditions. The resulting method offers improved classification accuracy, enhanced robustness, and better
interpretability, making it well-suited for real-world security-sensitive
applications. Rather than replacing existing approaches, our framework
provides a complementary perspective that demonstrates the value of
principled multimodal integration in network traffic analysis.
2.2. Multimodal learning for network traffic recognition
Recent advances in multimodal deep learning have been applied
to encrypted traffic classification, aiming to improve accuracy by integrating complementary information from multiple data sources. Early
approaches such as AppNet [30] and MIMETIC [14] combine raw
packet bytes and packet length sequences using CNNs and recurrent
networks (e.g., LSTM, GRU) to extract modality-specific features before
applying simple fusion techniques like concatenation. These methods
were later extended to multi-task frameworks such as DISTILLER [15],
which performs joint classification across multiple traffic attributes.
More recently, Lin et al. proposed PEAN [16], leveraging a Transformer
encoder and bidirectional LSTM to jointly model byte sequences and
packet length dynamics.
A concurrent line of work introduces robustness considerations
into multimodal fusion. For instance, the Anti-Noise Network (ANNet) [31] proposes a representation enhancement strategy that operates
at the feature level rather than the input level, due to the numeric
nature of encrypted traffic. This method uses a probability masking
scheme to randomly discard or scale modal representations during the
training process, forcing the model to learn more robust patterns. In
addition, AN-Net uses mutual information estimation to select information modalities before fusion, thereby filtering out irrelevant or noisy
modalities. The final fusion is performed through average pooling over
the enhanced representations.
Despite their effectiveness, current multimodal approaches, including AN-Net, exhibit several key limitations. First, most methods employ
static fusion strategies – such as feature concatenation or fixed-weight
combinations – that cannot adapt to varying input characteristics. Second, these models process modalities independently during feature extraction, missing opportunities to exploit cross-modal correlations and
complementary semantic relationships inherent in network traffic data.
Third, existing approaches generally lack principled mechanisms for
uncertainty quantification, limiting their ability to provide confidence
estimates for predictions, particularly in ambiguous or adversarial scenarios. Finally, while AN-Net incorporates practical noise-robust techniques, its fusion mechanism relies on simple average pooling without
dynamic adaptation based on input context or information-theoretic
principles.
Our proposed framework addresses these limitations through several key innovations. We introduce an entropy-guided adaptive fusion
mechanism that dynamically integrates raw bytes and packet length
sequences based on their information content and contextual reliability.
The framework incorporates a cross-modal generation consistency loss
that explicitly models the latent interactions between modalities, while
KL divergence-based alignment ensures theoretical rigor in representation learning. This design provides several advantages over existing

Method

Core ideas

Strengths

Fusion strategy

AppNet [30]

Hybrid CNN-RNN
for TLS traffic
analysis

End-to-end learning;
Spatial–temporal
patterns

Feature
concatenation

MIMETIC [14]

Multimodal DL for
encrypted mobile
traffic with data
heterogeneity

Overcomes
single-modality
limits; Mobile
scenarios support

Intra- and
inter-modality
learning

DISTILLER [15] Multitask
multimodal
framework with
joint optimization

Multi-objective
optimization;
Unified framework

Late fusion with
fixed weights

AN-Net [31]

Anti-noise
architecture with
MI-based modality
selection

Noise robustness;
Intelligent filtering

Average pooling
after selection

ER-CMGI

Entropy-guided
cross-modal
generation with
diffusion models

Dynamic
adaptation;
Theoretical rigor;
Semantic
alignment

Adaptive entropy
weighting

methods: enhanced robustness to partial modality corruption, improved
generalization through principled uncertainty quantification, and reduced computational overhead via adaptive processing. By grounding the fusion strategy in information theory, our approach offers
both practical improvements and theoretical guarantees for multimodal
network traffic analysis.
Table 1 provides a comprehensive comparison of our ER-CMGI
framework with representative multimodal network traffic analysis
methods, highlighting the essential differences in core ideas, strengths,
and fusion strategies.
2.3. Generative methods in network traffic modeling
Generative modeling has also been applied in network traffic analysis, including basic data augmentation, fine-grained tracking reconstruction, and other aspects. These generation methods provide practical solutions to fundamental challenges such as data scarcity, privacy
constraints, and class imbalance by synthesizing real traffic samples
that closely resemble real network behavior.
One line of research explores the use of generative models for data
augmentation in intrusion detection systems. For example, Andresini
et al. [32] proposed a GAN-based framework that transforms traffic
flows into image-like representations to generate synthetic attack samples. This approach effectively mitigates the imbalance between benign
and malicious traffic, thereby improving generalization and detection
accuracy for previously unseen attacks.
Recent advances have further expanded the application of GANs
in intrusion detection systems, addressing specific challenges across
various network environments. GAN-LSTM architectures have been
developed for fog computing environments to address computational
constraints while maintaining detection accuracy [33]. In mobile ad
hoc networks (MANETs) [34], Multi-View Consistent GANs (MVCGANs) approaches generate consistent multi-view representations for
classifying various attack types. To address data imbalance, multicritics GAN clustering-based frameworks employ multiple discriminators
to improve synthetic data quality [35]. Furthermore, adaptive network intrusion detection systems utilize stacked Conditional Tabular
GANs (CTGANs) to address data drift issues in real-world deployments,
preventing catastrophic forgetting during model updates [36].
More recent efforts have focused on generating high-fidelity traffic
traces using diffusion models. Sivaroopan et al. introduced NetDiffusion [37], an end-to-end system that applies diffusion-based generation
3

Information Fusion 126 (2026) 103581

X. Wang et al.
Table 2
Key mathematical notation and symbols.

to network traffic synthesis. Compared to GANs, this method demonstrates better sample diversity and fidelity, making it particularly useful
when access to real attack data is limited due to privacy or legal
concerns.
Another emerging direction aims at reconstructing detailed packetlevel traffic from coarse-grained counter data — a task referred to as
network traffic super-resolution (TSR). Wang et al. proposed ZOOMSYNTH [38], which introduces a hierarchical architecture called CLTM,
composed of multiple Granular Traffic Transformers (GTTs) operating at different temporal resolutions. When available, rule-based constraints such as ACLs are incorporated to guide semantically meaningful
generation. Experimental results show that ZOOMSYNTH can produce
high-quality traffic traces and improve performance on downstream
tasks such as anomaly detection and service recognition.
While existing methods primarily focus on generating realistic traffic data for augmentation, addressing data imbalance, or handling
data drift challenges, our work explores a fundamentally different
direction: learning better multimodal representations through crossmodal generation consistency. Unlike previous approaches that use
generative models primarily for data synthesis or preprocessing, we
integrate lightweight diffusion models directly into the representation
learning process to enforce semantic alignment between heterogeneous
modalities. We introduce a cross-modal generation consistency loss
that encourages one modality’s encoder to generate features compatible with another modality’s representation space, thereby promoting
semantic coherence across modalities. This approach does not aim to replace existing generative frameworks for data augmentation but rather
complements them by emphasizing the role of internal cross-modal
representation learning in multimodal settings. This design ensures that
each modality’s encoder captures not only its intrinsic characteristics
but also maintains semantic compatibility with other modalities, resulting in more robust and transferable feature representations for intrusion
detection tasks.

Symbol

Definition

 = {𝑥𝑏 , 𝑥𝑙 }
𝑥𝑏 ∈ R𝑆×𝐹
𝑥𝑙 ∈ R𝑆
𝑧 𝑏 , 𝑧 𝑙 ∈ R𝑑
𝜇𝑏 , 𝜇𝑙 , 𝜎𝑏2 , 𝜎𝑙2
𝐻(𝑧)
̄
𝐻(𝑧)

Multimodal network traffic sample
Raw byte sequence modality
Packet length sequence modality
Latent representations for byte and length modalities
Mean and variance vectors of latent Gaussian distributions
Differential entropy of latent representation 𝑧
Sample-averaged differential entropy of latent representation 𝑧
Encoder networks for byte and length modalities
Cross-modal generators (length-to-byte, byte-to-length)
Noise prediction network in diffusion model
Noisy sample at time step 𝑡 in diffusion process
Alternative notation for diffusion process variables
Entropy-based fusion weights
Mixing coefficients for hybrid entropy strategy
Classification, KL divergence, and generation losses
Loss function weighting hyperparameters

𝑓𝑏 , 𝑓 𝑙
𝑙2𝑏 , 𝑏2𝑙
𝜖𝜃
𝑧̂ 𝑡
𝑥𝑡
𝑤𝑏 , 𝑤 𝑙
𝜆𝑏 , 𝜆 𝑙
class , KL , gen
𝜆KL , 𝜆gen

(1) Background Traffic Removal: Removing non-informative background traffic prior to detection enhances both detection efficiency and
precision by reducing false positives. We identify and eliminate the
following categories of background traffic:
a. Failed TCP handshakes (e.g., missing responses to SYN packets
or RST resets), primarily caused by scanning activities or misconfigurations, which generally lack malicious payloads;
b. Routine DNS queries via UDP port 53, representing a substantial
portion of benign DNS traffic and typically non-malicious in nature;
c. LLMNR/NBNS protocol traffic, employed for local network name
resolution, often regarded as network noise and seldom linked to
adversarial activities;
d. NTP and ICMP traffic, serving fundamental network maintenance
functions and rarely indicative of direct attack vectors.
(2) Flow Segmentation: Traffic segmentation is commonly performed at the packet-level, flow-level, or session-level granularity. In
this work, we segment raw network traffic into flows using the standard
five-tuple definition: {source IP, destination IP, source port, destination
port, protocol}.
We adopt flow-level segmentation as the foundational unit for our
analysis, motivated by two key advantages. First, in contrast to packetlevel representations – which treat each packet independently – flowlevel aggregation captures directional coherence and temporal dependencies within network communications. Second, compared to sessionlevel representations, flow-level structures are structurally simpler, as
they do not require maintaining bidirectional state information.
(3) Irrelevant Field Processing: Since our model relies on semantic
and behavioral features derived from raw network traffic for classification, it is essential to remove fields that are irrelevant to these
characteristics. This helps prevent potential negative impacts on the
training process and model generalization. Specifically, we eliminate
MAC addresses and IP addresses – fields that uniquely identify devices
– and replace their original values with ‘‘0x00’’.
(4) Multimodal Feature Extraction: For subsequent multimodal
learning, we select two complementary modalities: the raw bytes of
each flow and the packet length sequence. The rationale for this
selection is twofold. First, raw bytes encapsulate both protocol header
information and payload content, thereby capturing the semantic characteristics of network traffic. Second, packet length sequences reflect
temporal communication patterns, capturing observable behavioral
attributes of the flow.
Specifically, for raw bytes, we extract the first 𝑁 packets from each
flow, including 𝐻 bytes from the packet header and 𝑃 bytes from the
payload. This results in a total of 𝑁(𝐻 + 𝑃 ) bytes per flow. Any missing
data due to insufficient packet count are padded with ‘‘0x00’’. Similarly,
for the packet length sequence, we extract the lengths of the first 𝑀
packets per flow, padding with zeros when necessary.

3. Methodology
This section presents ER-CMGI, a multimodal framework for intrusion detection that effectively learns and integrates heterogeneous
network traffic features. As illustrated in Fig. 1, the model consists of
five core components: traffic preprocessing, latent representation learning, cross-modal consistency, entropy-guided fusion, and classification.
The processing pipeline begins by segmenting raw network traffic into
structured modalities, which are then encoded into probabilistic latent
representations using a VAE-based architecture. A lightweight diffusion model facilitates cross-modal consistency learning, where latent
representations from different modalities are compared and aligned
to ensure semantic coherence across modalities. An adaptive fusion
mechanism subsequently integrates these aligned representations by
leveraging entropy estimates to dynamically weight each modality
based on its information content. Finally, a classification head performs intrusion detection using the fused representations, achieving
high detection accuracy and robust generalization. Each component is
described in detail in the following subsections. The key mathematical
notations used throughout this paper are shown in Table 2.
3.1. Network traffic preprocessing
To enable effective identification of network traffic, it is essential
to preprocess the raw PCAP data. Preprocessing not only completes
the traffic segmentation but also removes background traffic that is
not significant for the classification task, and processes the traffic into
a format suitable for the input of deep learning models. Importantly,
the encryption status of the traffic does not impact the effectiveness
of the preprocessing pipeline. Our preprocessing framework consists of
four key components: Background Traffic Removal, Flow Segmentation,
Irrelevant Field Processing, and Multimodal Feature Extraction.
4

Information Fusion 126 (2026) 103581

X. Wang et al.

Fig. 1. Architecture overview of the ER-CMGI framework. The model consists of five key modules: (1) Network Traffic Preprocessing, (2) Latent Representation Learning, (3) CrossModal Transformation Generation, (4) Entropy-Guided Adaptive Fusion, and (5) Decision and Classification. Arrows indicate the flow of data and information across components.

Importantly, both modalities inherently preserve temporal information crucial for detecting attack patterns. The raw byte sequences maintain chronological packet ordering, capturing the temporal evolution
of communication content, while the packet length sequences represent time-ordered size variations that reflect communication rhythms
and behavioral patterns. This temporal structure enables our subsequent CNN architectures to exploit temporal dependencies: the twodimensional CNN for byte sequences models temporal correlations
across packets alongside spatial dependencies within packets, while the
one-dimensional CNN for packet length sequences captures temporal
dynamics such as periodicity and burstiness commonly exhibited by
specific applications or attack vectors.
These strategies ensure a comprehensive characterization of both
fine-grained payload patterns and high-level communication dynamics.
By integrating micro-level payload details with macro-level behavioral
traits, the two modalities effectively enrich the model’s understanding
of network traffic, thereby enhancing the effectiveness of multimodal
learning.
The selection of byte sequences and packet length sequences as our
primary modalities is motivated by their complementary advantages
in encrypted traffic analysis. Compared to alternative combinations
such as time intervals or header fields, our chosen modalities offer
superior encryption robustness (both remain observable under strong
encryption), semantic completeness (bytes capture protocol structures
while lengths capture behavioral patterns), and universal applicability
(extractable from any network traffic regardless of protocol type).
Time intervals, while providing temporal information, suffer from network jitter and deployment variability. Header-payload combinations
become ineffective in encrypted scenarios where payload content is
inaccessible.

structured and semantically meaningful representations. This section
presents the design of our probabilistic representation learning framework, which not only encodes heterogeneous modalities – namely byte
sequences and packet length sequences – into a shared latent space but
also quantifies the uncertainty associated with each modality’s learned
representation. These probabilistic representations serve as the foundational inputs for subsequent multimodal fusion and decision-making
modules.
3.2.1. Problem formalization
Let  = {𝑥𝑏 , 𝑥𝑙 } denote a multimodal network traffic sample, where
𝑥𝑏 ∈ R𝑆×𝐹 represents the byte sequence and 𝑥𝑙 ∈ R𝑆 denotes the
packet length sequence, with subscripts 𝑏 and 𝑙 indicating byte and
length modalities respectively. Here, 𝑆 refers to the number of packets
extracted from the flow, and 𝐹 indicates the byte feature dimension.
This module aims to learn probabilistic latent representations for
each modality, where the encoders parameterize Gaussian distributions
𝑧𝑏 ∼  (𝜇𝑏 , 𝜎𝑏2 ) and 𝑧𝑙 ∼  (𝜇𝑙 , 𝜎𝑙2 ) within a shared latent space, with
(𝜇𝑏 , 𝜎𝑏2 ) and (𝜇𝑙 , 𝜎𝑙2 ) being neural network outputs. Additionally, the information uncertainty of each modality’s latent representation is quantified using differential entropy. This provides a theoretical basis for
the subsequent cross-modal fusion and decision-making mechanisms.
3.2.2. Probabilistic encoder
The probabilistic encoding mechanism is based on a VAE architecture, comprising two distinct encoders: one dedicated to byte sequences and the other to packet length sequences. Although both
encoders are implemented using CNNs, they are designed to capture
modality-specific characteristics.
Specifically, the byte sequence encoder employs a two-dimensional
CNN to model both temporal correlations across packets and spatial dependencies within individual packets. This architecture enables
the extraction of fine-grained patterns such as protocol header structures or application-layer payload features. In contrast, the packet
length encoder utilizes a one-dimensional CNN to capture temporal

3.2. Representation learning
To effectively leverage multimodal network traffic data for deep
learning tasks, it is essential to first transform raw traffic samples into
5

Information Fusion 126 (2026) 103581

X. Wang et al.

dynamics in packet sizes—such as periodicity, burstiness, or rhythmic
communication patterns commonly exhibited by certain applications.
Both encoders consist of stacked convolutional layers followed by
batch normalization and pooling operations, progressively extracting
high-level abstract features. The final output of each encoder is projected into the shared latent space through fully connected layers.
As illustrated in Fig. 2, both unimodal encoders generate the mean
𝜇 and log-variance log 𝜎 2 of the latent vectors, which parameterize
multivariate Gaussian distributions. Using the reparameterization trick,
latent vectors are sampled as follows:
𝑧𝑏 = 𝜇𝑏 + 𝜖 ⊙ 𝜎𝑏 ,

𝜖 ∼  (0, 𝐈),

𝑧 𝑙 = 𝜇𝑙 + 𝜖 ⊙ 𝜎 𝑙 ,

𝜖 ∼  (0, 𝐈),

entropy patterns may carry complementary classification signals. The
theoretical foundation enables adaptive modality fusion that dynamically weights each modality based on its discriminative contribution to
the specific classification context, supporting informed decision-making
throughout the system while leveraging the full spectrum of available
information.
3.3. Cross-modal transformation generation
We propose a cross-modal transformation mechanism based on diffusion models, which enables bidirectional mapping between different
modalities of network traffic features by replacing the decoder in the
conventional VAE framework. This design aims to enhance modality complementarity and improve the quality of latent representation
learning.
The adoption of diffusion models over simpler generators such
as MLPs or CNNs is motivated by their strong theoretical foundation and practical advantages. Diffusion models excel at capturing
complex, multimodal distributions through an iterative denoising process [39], making them well-suited for modeling the intricate relationships among heterogeneous network traffic modalities. Unlike deterministic architectures that learn direct mappings, diffusion models
estimate the underlying score function of the data distribution [40],
enabling more flexible and robust cross-modal transformations. The
progressive denoising mechanism also provides implicit regularization,
which helps prevent overfitting to specific patterns [41]—a critical
property for generalization in security-sensitive applications. Furthermore, existing studies show that diffusion models achieve superior
sample quality and mode coverage in conditional generation tasks [42],
directly contributing to better cross-modal semantic alignment in our
framework.
Unlike traditional multimodal fusion approaches that rely on direct
feature concatenation or early/late fusion strategies, our method leverages diffusion models to generate the raw features of one modality from
the latent representation of another. This approach not only strengthens
semantic alignment across modalities but also enriches latent representations through cross-modal generation consistency constraints, thereby
promoting more robust and generalizable feature learning.

(1)

where 𝐈 represents the identity matrix.
This stochastic encoding strategy not only captures the distributional properties of the input data but also introduces a principled
mechanism for quantifying representational uncertainty.
3.2.3. Uncertainty quantification based on differential entropy
To quantify the information uncertainty embedded in the latent
representations, we leverage the concept of differential entropy from
information theory. For a multivariate Gaussian distribution derived
from a unimodal encoder, the differential entropy can be analytically
expressed as
1∑
log(2𝜋𝑒𝜎𝑖2 ),
2 𝑖=1
𝑑

𝐻(𝑧) =

(2)

where 𝑑 is the latent space dimension and 𝜎𝑖2 denotes the variance of
the 𝑖th dimension.
For practical computation, the average entropy per sample is simplified as
𝐻(𝑧) =

𝑑
1
1 ∑
log(2𝜋𝑒) +
log 𝜎𝑖2 .
2
2𝑑 𝑖=1

(3)

To ensure numerical stability during training, we apply a clamping
operation on the logarithmic variances:
𝐻(𝑧) =

𝑑
1
1 ∑
log(2𝜋𝑒) +
clamp(log 𝜎𝑖2 , 𝛼min , 𝛼max ),
2
2𝑑 𝑖=1

(4)
3.3.1. Lightweight diffusion model design
Diffusion models generate data by iteratively denoising samples that
are progressively corrupted with noise over a series of time steps. The
overall architecture is illustrated in Fig. 2. To enhance computational
efficiency for network traffic analysis, we design a lightweight variant
incorporating the following key optimizations:

where 𝛼min and 𝛼max are hyperparameters defining the lower and upper
bounds, respectively. The clamp function ensures that values remain
within a numerically stable range:
⎧min,
⎪
clamp(𝑥, min, max) = ⎨max,
⎪
⎩𝑥,

if 𝑥 < min
if 𝑥 > max

(5)
1. Optimized Time Steps: Instead of using hundreds to thousands
of iterations as in standard diffusion models, we reduce the
number of time steps to 𝑇 , significantly improving inference
speed while maintaining high-quality generation.
2. Linear Noise Scheduling: We adopt a linear noise schedule
where the noise level 𝛽𝑡 increases linearly from 𝛽1 to 𝛽𝑇 . This
balances sampling fidelity and convergence speed.
3. Conditional Diffusion Architecture: We adapt the diffusion
model for conditional generation, defined formally as:

otherwise.

Differential entropy offers a theoretically grounded and computationally efficient measure of uncertainty. It allows us to distinguish
between two types of uncertainty: aleatoric uncertainty, which stems
from inherent randomness in the data, and epistemic uncertainty,
which reflects the model’s lack of knowledge or confidence.
In the context of multimodal network traffic analysis, the uncertainty associated with each modality carries distinct semantic implications. High entropy in byte sequences may indicate encrypted content
or high variability in payload structures, which can serve as valuable discriminative features for certain classification tasks, particularly
in distinguishing encrypted malicious traffic from normal patterns.
Similarly, elevated entropy in packet length sequences may suggest irregular communication patterns or complex temporal behaviors, which
could be indicative of specific application types or malicious activities
rather than simply representing noise.
By jointly quantifying uncertainty across both modalities, the model
can assess the information content and discriminative potential of
each modality for a given traffic sample. Rather than treating high
entropy as inherently unreliable, this approach recognizes that different

𝑝𝜃 (𝑧̂ 0 |𝑧𝑐 ) =

∫

𝑝𝜃 (𝑧̂ 0∶𝑇 |𝑧𝑐 )𝑑 𝑧̂ 1∶𝑇 ,

(6)

where 𝑧̂ 0 denotes the generated target modality features (the
final clean output), 𝑧𝑐 is the conditional modality’s latent representation (either 𝑧𝑏 or 𝑧𝑙 ), and 𝑝𝜃 (𝑧̂ 0∶𝑇 |𝑧𝑐 ) is modeled via a
Markov chain:
𝑝𝜃 (𝑧̂ 0∶𝑇 |𝑧𝑐 ) = 𝑝(𝑧̂ 𝑇 )

𝑇
∏

𝑝𝜃 (𝑧̂ 𝑡−1 |𝑧̂ 𝑡 , 𝑧𝑐 ).

(7)

𝑡=1

Here, 𝑧̂ 𝑇 represents pure noise, and the chain progressively
denoises to produce the target features.
6

Information Fusion 126 (2026) 103581

X. Wang et al.

Fig. 2. The structure of the lightweight diffusion model.

4. Network Architecture: The core denoising network 𝜖𝜃 employs a lightweight U-Net structure consisting of multiple downsampling and upsampling blocks. The conditional information
𝑧𝑐 is integrated into the decoding process through conditional
injection techniques.

generators. Unlike traditional cycle-consistency constraints, this direct
generation loss is more computationally efficient while still promoting
strong alignment between modalities.
To accommodate the characteristics of each modality, we introduce
an adaptive weighting strategy based on a hybrid entropy mechanism.
Empirical analysis reveals that byte modality performs better with
higher entropy samples, while length modality is more reliable with
lower entropy samples.

3.3.2. Bidirectional cross-modal generator
To enable full bidirectional transformation between modalities, we
design two complementary generative components:

Based on these observations, we derive the optimal fusion weights
from information-theoretic principles. Let the classification performance of modality 𝑚 be correlated with its entropy 𝐻(𝑧𝑚 ). The optimal
weight should reflect both the entropy-performance relationship and
the modality’s information content. We formulate this as:

1. Byte-to-Length Generator (B2L): Given the byte modality latent representation 𝑧𝑏 ∈ R𝑑 as condition, we generate the length
modality features through the diffusion process. Starting from
noise 𝑧̂ 𝑇𝑙 ∼  (0, 𝐈), the reverse denoising process is learned as:
(
)
𝛽𝑡
1
𝑡
𝑡
𝑧̂ 𝑡−1
=
𝑧
̂
−
𝜖
(
𝑧
̂
,
𝑡,
𝑧
)
+ 𝜎𝑡 𝜉,
(8)
√
√
𝜃 𝑙
𝑏
𝑙
𝑙
𝛼𝑡
1 − 𝛼̄ 𝑡
∏𝑡
2
where 𝛼𝑡 = 1 − 𝛽𝑡 , 𝛼̄ 𝑡 =
𝑖=1 𝛼𝑖 , 𝜎𝑡 = 𝛽𝑡 , and 𝜉 ∼  (0, 𝐈) is
independent noise.
2. Length-to-Byte Generator (L2B): Conditioned on the length
modality representation 𝑧𝑙 , this generator reconstructs the corresponding byte representation through the diffusion process.
Starting from noise 𝑧̂ 𝑇𝑏 ∼  (0, 𝐈), the denoising process follows:
(
)
𝛽𝑡
1
𝑡
𝑡
𝑧̂ 𝑡−1
=
𝑧
̂
−
𝜖
(
𝑧
̂
,
𝑡,
𝑧
)
+ 𝜎𝑡 𝜉.
(9)
√
√
𝜃 𝑏
𝑙
𝑏
𝑏
𝛼𝑡
1 − 𝛼̄ 𝑡

𝑤𝑚 = 𝜆𝑚 ⋅

+(1 − 𝜆𝑚 ) ⋅

High-entropy priority

1∕𝐻(𝑧𝑚 )
∑
𝑗 1∕𝐻(𝑧𝑗 )
⏟⏞⏞⏞⏞⏞⏟⏞⏞⏞⏞⏞⏟

(12)

Low-entropy priority

where 𝜆𝑚 controls the balance between the two strategies based on
the modality-specific entropy-accuracy relationship. For byte modality,
𝜆𝑏 = 0.7 (favoring high entropy); for length modality, 𝜆𝑙 = 0.2 (favoring
low entropy). The practical implementation uses:
̄ 𝑏)
𝐻(𝑧
1
+ (1 − 𝜆𝑏 ) ⋅
,
̄
̄
̄ 𝑙)
𝐻(𝑧𝑏 ) + 𝜖
𝐻(𝑧𝑏 ) + 𝐻(𝑧
̄ 𝑙)
𝐻(𝑧
1
𝑤𝑙 = 𝜆𝑙 ⋅
+ (1 − 𝜆𝑙 ) ⋅
,
̄
̄
̄ 𝑙)
𝐻(𝑧𝑙 ) + 𝜖
𝐻(𝑧𝑏 ) + 𝐻(𝑧

𝑤𝑏 = 𝜆𝑏 ⋅

Given that the byte modality typically exhibits a significantly higher
feature dimension compared to the packet length modality, we incorporate feature expansion layers within the L2B generator. These
layers progressively increase the feature dimensions through grouped
convolutions and upsampling operations, ensuring an effective mapping from low-dimensional length features to high-dimensional byte
representations.
As illustrated in Fig. 3, the network adopts a two-dimensional
convolutional architecture with skip connections, which helps preserve
fine-grained structural details during the generation process.
Importantly, the proposed lightweight U-Net does not rely on computationally intensive attention mechanisms. Instead, it achieves efficient cross-modal alignment through carefully designed convolutional
layers and hierarchical skip connections, making it particularly suitable
for network traffic analysis applications.

(13)

̄
where 𝐻(𝑧)
represents the sample-averaged differential entropy of
modality 𝑧 (computed as the average of 𝐻(𝑧) across a batch of samples),
𝜆𝑏 and 𝜆𝑙 are blending coefficients that control the balance between
inverse entropy weighting (favoring high uncertainty) and standard
entropy weighting (favoring low uncertainty), and 𝜖 is a small constant
for numerical stability.
Finally, the weights are normalized to ensure they sum to one:
𝑤′𝑏 =

𝑤𝑏
,
𝑤𝑏 + 𝑤𝑙

𝑤′𝑙 =

𝑤𝑙
.
𝑤𝑏 + 𝑤𝑙

(14)

Accordingly, the weighted generation loss becomes:
gen = 𝑤′𝑏 ⋅ 𝑏gen + 𝑤′𝑙 ⋅ 𝑙gen .

(15)

This hybrid entropy-based adaptive weighting strategy enables the
model to flexibly adjust the relative importance of each modality
within the generation consistency constraint, thereby enhancing both
the accuracy and robustness of cross-modal transformation.

3.3.3. Cross-modal generation consistency constraint
Cross-modal generation consistency serves as a critical mechanism
to align latent representations across modalities and ensure accurate
reconstruction of original data. It is formulated as:
gen = 𝑏gen + 𝑙gen ,

𝐻(𝑧𝑚 )
∑
𝑗 𝐻(𝑧𝑗 )
⏟⏞⏞⏞⏟⏞⏞⏞⏟

(10)
3.4. Entropy-guided adaptive fusion

where
𝑏gen = ‖𝑥𝑏 − 𝑥̂ 𝑏 ‖22 ,

𝑥̂ 𝑏 = 𝑙2𝑏 (𝑧𝑙 ),

𝑙gen = ‖𝑥𝑙 − 𝑥̂ 𝑙 ‖22 ,

𝑥̂ 𝑙 = 𝑏2𝑙 (𝑧𝑏 ).

This section introduces a dynamic feature fusion strategy grounded
in information theory. By leveraging the differential entropy of latent representations, this module guides the optimal integration of
multimodal features, achieving adaptive decision optimization.

(11)

Here, 𝑧𝑏 = 𝑓𝑏 (𝑥𝑏 ) and 𝑧𝑙 = 𝑓𝑙 (𝑥𝑙 ) are latent representations obtained
from their respective encoders, and 𝑙2𝑏 and 𝑏2𝑙 denote the cross-modal
7

Information Fusion 126 (2026) 103581

X. Wang et al.

Fig. 3. The structure of the lightweight U-Net used in the diffusion model.

The first component is the classification loss, which serves as the
primary task objective and is computed using cross-entropy:

3.5. Entropy-guided adaptive fusion
This section introduces a dynamic feature fusion strategy grounded
in information theory. By leveraging the differential entropy of latent representations, this module guides the optimal integration of
multimodal features, achieving adaptive decision optimization.
Unlike traditional multimodal learning approaches that typically
rely on simple concatenation or element-wise averaging of features,
we propose an entropy-guided hierarchical fusion architecture. In the
first stage, modality-specific weights are computed using the hybrid
entropy weighting strategy that combines both traditional low-entropy
priority and inverse entropy weighting through learnable mixing coefficients. These weighted latent representations are then fused through
a nonlinear mapping network defined as:
(
)
𝑧fused =  [𝑤′𝑏 ⋅ 𝑧𝑏 ; 𝑤′𝑙 ⋅ 𝑧𝑙 ] ,
(16)

KL = KL(𝑞(𝑧𝑏 |𝑥𝑏 )‖𝑝(𝑧)) + KL(𝑞(𝑧𝑙 |𝑥𝑙 )‖𝑝(𝑧)),

(20)

(21)

where 𝑝(𝑧) =  (0, 𝐼) is the prior. This constraint improves the structure
and generalization ability of the latent space, reducing the risk of
overfitting to specific patterns.
The third component enforces cross-modal generation consistency
to ensure semantic alignment between different modalities. This loss is
defined as:
]
1 ∑[
‖𝑥𝑏,𝑖 − 𝑥̂ 𝑏,𝑖 ‖22 + ‖𝑥𝑙,𝑖 − 𝑥̂ 𝑙,𝑖 ‖22 ,
𝑁 𝑖=1
𝑁

gen =

(17)

This design enables the model to learn complex, nonlinear interactions
between modalities, thereby significantly enhancing its representational capacity compared to conventional linear fusion methods.
The entropy-guided fusion weights are dynamically computed for
each input sample based on the information content of individual
modalities. This adaptive mechanism automatically adjusts the contribution of each modality according to its reliability and discriminative
power, eliminating the need for manual parameter tuning. Compared
to fixed-weight schemes or simple concatenation-based fusion methods,
this approach provides dynamic adaptability to diverse traffic patterns
and improved robustness when individual modalities are corrupted by
noise or missing information.

(22)

where 𝑥̂ 𝑏,𝑖 = 𝑙2𝑏 (𝑧𝑙,𝑖 ) and 𝑥̂ 𝑙,𝑖 = 𝑏2𝑙 (𝑧𝑏,𝑖 ) denote the byte sequences
generated from the length latent representation and the packet length
sequences generated from the byte latent representation, respectively.
Here, 𝑧𝑏,𝑖 = 𝑓𝑏 (𝑥𝑏,𝑖 ) and 𝑧𝑙,𝑖 = 𝑓𝑙 (𝑥𝑙,𝑖 ) are the latent representations
obtained from their respective encoders.
This design ensures that latent representations from one modality can accurately reconstruct the other modality, cross-modal semantic alignment is maintained throughout the learning process, and
the lightweight diffusion generators effectively capture inter-modal
relationships. The cross-modal generation consistency approach enables self-supervised learning through direct cross-modal generation
and comparison, enhancing the model’s ability to learn meaningful
representations without additional labeled data.
The combination of these three loss components creates a balanced
training objective that promotes both discriminative classification performance and robust multimodal representation learning, ensuring the
model’s effectiveness across diverse network security scenarios.

3.6. Decision and classification
The decision-making component takes as input the fused representation 𝑧fused , which is generated by the entropy-guided fusion module,
and produces the final classification output through a linear mapping:
𝑝(𝑦 ∣ 𝑧fused ) = softmax(𝑊 ⋅ 𝑧fused + 𝑏).

𝐶

where 𝑦𝑖,𝑐 is the ground truth label and 𝑝𝑖,𝑐 is the predicted probability
for class 𝑐 of sample 𝑖.
The second component provides latent space regularization through
KL divergence, which encourages the latent representations of both
modalities to follow standard normal distributions:

where  denotes a multilayer perceptron (MLP) with two hidden layers
of dimension ℎ, each followed by a ReLU activation function and
Dropout regularization. Specifically,
 (𝑧) = 𝑊2 ⋅ Dropout(ReLU(𝑊1 ⋅ 𝑧 + 𝑏1 )) + 𝑏2 .

1 ∑∑
𝑦 log(𝑝𝑖,𝑐 ),
𝑁 𝑖=1 𝑐=1 𝑖,𝑐
𝑁

class = −

3.7. Theoretical foundation

(18)

It is important to note that the fused representation 𝑧fused has
already undergone multiple nonlinear transformations and Dropout
regularization within the fusion layers. As a result, we adopt a simple single-layer classifier to avoid over-parameterization and maintain
model efficiency, without compromising performance.
To train this classification framework effectively, we define a comprehensive loss function that jointly optimizes three key objectives to
ensure both classification accuracy and representation quality:

Although our model does not incorporate the traditional self-modal
reconstruction loss commonly used in VAEs, we provide a theoretical
justification demonstrating that the combination of cross-modal generation consistency loss and KL divergence establishes an equivalent
formulation to the Evidence Lower Bound (ELBO) in a multimodal
setting.
We establish a unified theoretical framework based on the following
objective function:

total = class + 𝜆KL KL + 𝜆gen gen .

unified = gen + 𝜆KL .

(19)
8

(23)

Information Fusion 126 (2026) 103581

X. Wang et al.

Table 3
Implementation details and hyperparameter settings.

Under appropriate conditions, minimizing this objective is mathematically equivalent to maximizing the multimodal variational lower
bound:
ELBO-joint = E[log 𝑝(𝑥𝑙 |𝑧𝑏 ) + log 𝑝(𝑥𝑏 |𝑧𝑙 )] − KL .

(24)

This equivalence relies on the assumption that the cross-modal
generation functions in our lightweight diffusion model are sufficiently
expressive. When the generators 𝑙2𝑏 and 𝑏2𝑙 have adequate representational capacity, the generation consistency losses can effectively
approximate the cross-modal log-likelihoods.
The key insight underlying our approach is that cross-modal generation consistency enforces a stronger constraint than traditional selfreconstruction. Specifically, our framework requires that latent representations from one modality must contain sufficient semantic information to accurately reconstruct data from another modality:
𝑙2𝑏 (𝑓𝑙 (𝑥𝑙 )) ≈ 𝑥𝑏

and 𝑏2𝑙 (𝑓𝑏 (𝑥𝑏 )) ≈ 𝑥𝑙 ,

Value

Parameter

Value

Packets per flow
Payload size
Latent dimension
Diffusion steps
Time embedding dim
Optimizer
Weight decay
LR scheduler
Early stop patience
𝜆KL
Byte entropy weight

20
256 bytes
64
10
32
Adam
5 × 10−4
ReduceLROnPlateau
10 epochs
0.05
0.7

Header size
Length features
Hidden dimension
UNet hidden dim
Convolution groups
Learning rate
Batch size
LR reduction factor
Gradient clipping
𝜆gen
Length entropy weight

54 bytes
5-dim
128
32
8
10−4
32
0.5
5.0
0.1
0.2

5 × 10−4 . The learning rate scheduling employs ReduceLROnPlateau
with a reduction factor of 0.5 and patience of 5 epochs. Early stopping
is applied with a patience of 10 epochs, and gradient clipping is set
to 5.0 for training stability. A batch size of 32 was selected based on
preliminary experiments balancing training efficiency, memory usage,
and model performance. Loss function weights are set to 𝜆KL = 0.05 and
𝜆gen = 0.1, while the hybrid entropy strategy uses mixing coefficients of
0.7 for raw byte modality and 0.2 for packet length sequence modality.
The lightweight diffusion model incorporates several architectural
optimizations to reduce computational overhead while maintaining
generation quality. The diffusion timesteps are reduced from the standard 1000 to 10 steps using a cosine_simple noise scheduling strategy.
The UNet noise predictor features a hidden dimension of 32 and time
embedding dimension of 32, significantly smaller than standard implementations. The architecture employs grouped convolutions (groups =
8) combined with pointwise convolutions to reduce parameter count,
while using GroupNorm instead of BatchNorm for improved efficiency.
For byte sequence generation, we adopt a depthwise separable convolution structure; for packet length sequence generation, we use 1D
convolutions with residual connections. All activation functions use
SiLU (Swish) to enhance training stability and convergence speed.

(25)

where 𝑓𝑏 (⋅) and 𝑓𝑙 (⋅) denote the byte and length encoders, respectively.
This cross-modal constraint provides three main theoretical advantages. First, it requires the latent space to capture shared semantic
concepts across modalities rather than modality-specific information.
Second, it acts as an implicit regularizer that prevents encoders from
learning artifacts or noise. Third, combined with KL divergence terms,
it facilitates alignment between different modal latent representations
through a shared prior distribution 𝑝(𝑧).
From an information-theoretic perspective, our formulation ensures
that the learned representations satisfy the following property:
𝐼(𝑍𝑏 ; 𝑍𝑙 ) ≥ 𝛼,

Parameter

(26)

where 𝐼(⋅; ⋅) denotes mutual information, and 𝛼 > 0 is a positive
constant. This guarantees that the latent representations from different
modalities share sufficient common information, establishing strong
cross-modal semantic alignment while preserving modality-specific
characteristics.
Therefore, our framework preserves the theoretical foundation of
variational inference while introducing a self-supervised learning mechanism through cross-modal generation constraints. This approach compensates for the absence of traditional self-modal reconstruction loss
and provides theoretical guarantees for multimodal representation
learning.

C. Benchmark models.
We compare against 9 existing approaches spanning unimodal and
multimodal learning paradigms:
Unimodal Models:
• 1D-CNN [45]: An end-to-end encrypted traffic classification
framework based on one-dimensional convolutional neural networks (1D-CNNs), which integrates raw input processing, feature extraction, and classification into a unified architecture to
automatically learn nonlinear relationships between input and
output.
• ACID [46]: A lightweight intrusion detection system that leverages low-dimensional embeddings learned by a compact neural
model with adaptive clustering, aiming to improve sensitivity to
subtle variations in traffic patterns through enhanced inter-class
separation.
• IIT [21]: A heterogeneous encrypted traffic classification model
employing dual multi-head self-attention encoders to jointly
model intra-flow packet dynamics and inter-flow traffic dependencies, thereby capturing both temporal and relational characteristics of network behavior from complementary perspectives.
• RFG-HELAD [47]: A robust fine-grained attack detection framework that combines contrastive learning, GAN-based adversarial defense, and Deep kNN-based out-of-distribution detection
to address the open-set problem and enhance resilience against
adversarial perturbations.
• FastTraffic [48]: A lightweight deep learning method for encrypted traffic classification that treats packets as text-like sequences, utilizes N-gram feature embedding to capture structured
and sequential patterns, and employs a compact three-layer MLP
for fast and resource-efficient inference.

4. Experiment
4.1. Experimental evaluation
A. Datasets.
We evaluate our ER-CMGI model on two publicly available datasets:
D1: The complete USTC-TFC2016 dataset [43] containing 20 traffic
categories (10 normal and 10 malicious). This comprehensive collection
includes application-layer network traffic for malware analysis and
intrusion detection, covering common protocols (HTTP, FTP, SMTP)
and malicious activities (Cridex, Geodo, Zeus).
D2: A composite dataset combining 5 selected malware families
from Malicious_TLS [44] with 5 selected application categories from
CrossNet2021 [19]. The malicious component consists of TLS traffic
collected from real networks (2018–2021), while the benign component
includes applications tested under realistic network conditions with
packet loss and latency.
B. Experimental setup.
Our implementation utilizes PyTorch 2.5.1 and Python 3.10.14 on
Ubuntu 22.04, equipped with an NVIDIA V100 (32 GB) GPU and an
Intel Xeon Gold 5218R CPU. We evaluate performance using standard
metrics: Accuracy, Recall, Precision, and F1-score.
Key implementation parameters are shown in Table 3. We use the
Adam optimizer with a learning rate of 10−4 and weight decay of
9

Information Fusion 126 (2026) 103581

X. Wang et al.
Table 4
Comparison results on the D1(%).

Table 5
Comparison results on the D2(%).

Method

Accuracy

Recall

Precision

F1

Method

Accuracy

Recall

Precision

F1

Unimodal

1D CNN [45]
ACID [46]
IIT [21]
RFG-HELAD [47]
FastTraffic [48]

89.76
94.13
97.86
85.18
96.93

90.37
93.92
97.15
84.76
94.97

90.32
94.19
97.55
84.98
96.57

90.25
94.53
97.68
82.68
95.51

Unimodal

1D CNN [45]
ACID [46]
IIT [21]
RFG-HELAD [47]
FastTraffic [48]

87.86
92.87
96.36
88.29
92.16

88.14
92.64
96.12
87.63
91.52

88.09
92.35
96.17
87.94
91.33

87.76
92.79
96.06
88.26
91.83

Multimodal

AppNet [30]
MIMETIC [14]
DISTILLER [15]
AN-Net [31]
ER-CMGI

91.31
93.25
95.23
98.54
99.12

91.54
93.14
95.13
98.57
99.17

91.24
93.42
95.21
98.67
99.23

90.87
93.07
95.24
98.42
99.12

Multimodal

AppNet [30]
MIMETIC [14]
DISTILLER [15]
AN-Net [31]
ER-CMGI

90.32
91.87
94.68
97.19
97.83

90.24
91.74
94.63
97.32
97.75

90.29
91.82
94.57
97.29
97.92

90.31
91.84
94.52
97.31
97.81

Multimodal Models:

When compared with existing multimodal frameworks, ER-CMGI
still exhibits clear advantages. Relative to the closest competitor ANNet, our model achieves 0.58% and 0.64% accuracy improvements on
D1 and D2, respectively. Compared to other multimodal methods such
as DISTILLER and MIMETIC, ER-CMGI demonstrates accuracy improvements of 5.87% and 3.89% on D1, and 5.96% and 3.15% on D2. This
performance gain stems from our entropy-regulated fusion mechanism
and cross-modal semantic alignment, which effectively address the
semantic inconsistency issues that limit other multimodal approaches.
Notably, ER-CMGI demonstrates robust performance across two
datasets with distinct characteristics, validating its capability to handle
diverse traffic patterns. Particularly on dataset D2, which contains
malware families collected from 2018 to 2021, ER-CMGI maintains
strong performance, indicating its effectiveness in addressing evolving
cyber threats - a critical requirement for practical application scenarios.
The normalized confusion matrices on the two datasets are shown in
Fig. 4. The results indicate that our model performs excellently in these
two multi-class classification tasks. From the confusion matrices, it can
be observed that the classification accuracy of most categories reaches
or approaches 1. The diagonal elements generally appear dark blue,
which demonstrates that the model has extremely high classification
accuracy. For example, in the first dataset, applications such as FTP,
WorldOfWarcraft, BitTorrent, and MySQL, as well as platforms like
aiqiyi, shifu, and upatre in the second dataset, all achieve or approach
a recognition accuracy of 1.
It is worth noting that even among applications with similar functions or overlapping features, the model still maintains a strong discriminative ability. In a few cases, there are slight confusion phenomena,
such as between Outlook and Gmail (approximately 2%) and between
Neris and Virut (approximately 11%). These confusions reflect genuine
network behavior similarities rather than dataset annotation issues. The
Outlook-Gmail confusion stems from both applications using identical
IMAP/SMTP protocols and TLS encryption patterns, resulting in nearly
indistinguishable encrypted traffic characteristics. Similarly, the NerisVirut confusion reflects the fact that both botnet families utilize similar
HTTP-based C&C communication patterns with comparable beacon
intervals and payload structures. These patterns represent inherent classification challenges in encrypted traffic analysis, where functionally
similar applications naturally exhibit comparable network behaviors.
Based on comprehensive analysis of the confusion matrices, the
types of attacks most prone to misclassification fall into two main categories: (1) Protocol-similar traffic, where different applications adopt
identical communication protocols, making their encrypted patterns
nearly indistinguishable; and (2) Behavioral-similar malware, where sophisticated attacks intentionally mimic legitimate application behaviors
or exhibit similar communication patterns. The underlying technical
causes include protocol convergence in encrypted environments and
advanced evasion techniques.
The results validate our hypothesis that traditional static fusion
paradigms limit multimodal synergy, while explicit cross-modal generation constraints enhance semantic coherence. ER-CMGI’s informationtheoretic optimization framework successfully bridges the modality
gap between statistical features and raw payloads, establishing new
state-of-the-art performance for encrypted traffic analysis.

• AppNet [30]: An end-to-end hybrid CNN-RNN architecture designed to jointly model sequential flow patterns and applicationspecific signatures from raw TLS traffic for mobile app identification via parallel feature extraction pathways.
• MIMETIC [14]: A multimodal deep learning framework for encrypted mobile traffic classification that captures both intra- and
inter-modality dependencies from heterogeneous data sources,
enabling more effective modeling of complex traffic patterns
through multi-view representation learning.
• DISTILLER [15]: A multitask multimodal deep learning architecture that jointly learns intra- and inter-modality relationships
across diverse traffic features, supporting simultaneous optimization over multiple classification objectives within a unified model.
• AN-Net [31]: An anti-noise deep learning architecture tailored
for anonymous traffic classification, featuring robust short-term
feature extraction and an enhanced multimodal fusion mechanism
to mitigate both packet-level noise and attribute perturbations.
To ensure fair and valid comparisons across all methods, all benchmark models are trained and evaluated under identical conditions:
(1) Consistent Data Preprocessing : All methods apply the same preprocessing pipeline detailed in Section 3.1, including background traffic
removal, flow segmentation, and feature extraction procedures. (2)
Uniform Dataset Partitioning : We use a consistent 70%–10%–20% split
for training, validation, and testing across all experiments, with stratified sampling to maintain class distribution balance. (3) Standardized
Training Environment : All models are trained on the same hardware
configuration with identical computational resources, using PyTorch’s
deterministic settings (fixed random seeds) to ensure reproducible results. (4) Consistent Evaluation Metrics: Performance evaluation employs
the same metrics (Accuracy, Recall, Precision, F1-score) with identical
calculation methods. (5) Hyperparameter Optimization: For each baseline method, we conduct grid search or follow the original paper’s
recommendations to ensure optimal performance, while maintaining
consistency in optimization procedures across all comparisons.
4.2. Comparison with benchmarks
The comparison results of ER-CMGI and benchmark on two datasets
are shown in Tables 4 and 5.
The experimental results demonstrate that our proposed ER-CMGI
model significantly outperforms both unimodal and multimodal baseline methods on two datasets. The performance gap between ER-CMGI
and traditional unimodal approaches is particularly notable. Compared
to the best unimodal method IIT, ER-CMGI improves accuracy by 1.26%
and 1.47% on D1 and D2, respectively. In comparison to FastTraffic, the
accuracy improvements reach 1.81% on D1 and 5.38% on D2, demonstrating the inherent limitations of unimodal methods in capturing
complex patterns in encrypted traffic.
10

Information Fusion 126 (2026) 103581

X. Wang et al.

Fig. 4. Confusion matrices on two datasets.
Table 6
The ablation results on D1(%).
Model

Accuracy

Recall

Precision

F1

w/o Packet length
w/o Raw byte
w/o Entropy-guided fusion
w/o Cross-modal generation
ER-CMGI

93.86
91.17
94.17
94.87
99.12

93.74
91.23
94.22
94.76
99.17

93.56
90.97
94.19
94.92
99.23

93.71
91.14
94.15
94.83
99.12

Model

Accuracy

Recall

Precision

F1

w/o Packet length
w/o Raw byte
w/o Entropy-guided fusion
w/o Cross-modal generation
ER-CMGI

92.85
90.41
93.23
94.27
97.83

92.81
90.49
93.19
94.25
97.75

92.56
90.47
93.08
94.14
97.92

92.79
90.51
93.21
93.89
97.81

network traffic, particularly critical for malware relying on specific
communication rhythms. These results validate the necessity of our
multimodal approach, which simultaneously leverages content and
behavioral features for classification.
After removing the entropy-guided adaptive fusion mechanism (w/o
entropy-guided adaptive fusion), accuracy on D1 and D2 decreased to
94.17% and 93.23%, representing 4.95% and 4.60% drops compared
to the full model. This demonstrates that our entropy-based dynamic
fusion strategy significantly outperforms traditional static fusion methods. The mechanism quantifies information entropy across modalities
to dynamically adjust their decision-making weights, enabling adaptive
focus on discriminative features. This flexibility proves crucial when
handling complex, variable encrypted traffic with differing feature
manifestations across modalities.
Removing the cross-modal generation component (w/o cross-modal
generation) resulted in accuracy reductions to 94.87% and 94.27%
on D1 and D2, representing 4.25% and 3.56% decreases. Though the
smallest decline among the four components, this remains significant.
It confirms that our lightweight diffusion-based cross-modal generation
framework effectively enhances semantic consistency and complementarity between modalities. By generating mappings between modalities,
the framework establishes tighter cross-modal correlations, enriching
feature representations while maintaining coherence. This mechanism
particularly benefits scenarios with modal imbalance, where certain
encryption techniques may disrupt raw byte features but minimally
affect packet length sequences.
Notably, clear synergistic effects exist between components. The
complete ER-CMGI model significantly outperforms any ablated variant, with advantages exceeding simple additive contributions from
individual components. For example, the entropy-guided fusion mechanism better balances contributions from raw bytes and packet length
sequences, while cross-modal generation further strengthens their complementarity. This mutual reinforcement collectively enhances overall
model performance.
In summary, these ablation experiments comprehensively validate
the necessity and effectiveness of ER-CMGI’s core components, particularly demonstrating the value of multimodal fusion, entropy-based
dynamic weighting, and cross-modal semantic alignment in encrypted
traffic classification.

Table 7
The ablation results on D2(%).

4.3. Ablation experiment
In order to verify the effectiveness of each module of ER-CMGI,
we conducted ablation experiments, mainly including four aspects: (1)
removing the packet length sequence modality and only using the
original byte modality; (2) removing the original byte mode and only
use the packet length sequence mode; (3) removing entropy guided
adaptive fusion; (4) removing cross modal generation. In the first two
cases, the model actually degenerates into a uni-modal model. The
experimental results are shown in Tables 6 and 7.
When the raw byte modality was removed (w/o raw byte), model
performance significantly declined, with accuracy dropping to 91.12%
and 90.41% on D1 and D2 datasets respectively, representing decreases
of 7.95% and 7.42% compared to the full model. F1 scores also showed
substantial declines, reaching 91.14% and 90.51%. This indicates that
raw bytes contain critical feature information in encrypted traffic,
capable of capturing fine-grained patterns in packet content and providing rich classification evidence even in encrypted states. Among all
ablated components, removing the raw byte modality caused the most
significant performance drop, confirming its role as the foundational
pillar of the model.
When removing the packet length sequence modality (w/o packet
length), model accuracy on D1 and D2 decreased to 93.86% and
92.85%, representing 5.26% and 4.98% reductions compared to the
full model. Though smaller than the raw byte removal impact, this
decrease remains substantial, demonstrating that packet length sequences provide crucial supplementary information. Packet length sequences reflect temporal dynamics and communication patterns in

4.4. Sensitivity analysis
In this section, we conduct a comprehensive analysis of key hyperparameters that significantly impact model performance and computational efficiency. We focus on two critical aspects: (1) the number
of diffusion time steps (T) in the lightweight diffusion model, which
11

Information Fusion 126 (2026) 103581

X. Wang et al.

(1) fixing the cross-modal generation weight at 𝜆𝑔𝑒𝑛 = 0.1 while varying
the KL divergence weight 𝜆𝐾𝐿 from 0.001 to 0.2, and (2) fixing the
KL divergence weight at 𝜆𝐾𝐿 = 0.05 while varying the cross-modal
generation weight 𝜆𝑔𝑒𝑛 from 0.01 to 0.25. Throughout all experiments,
the classification weight remains fixed at 𝜆𝑐𝑙𝑠 = 1.0 to serve as the
baseline. Fig. 6 shows the results of both experimental phases on
dataset D1.
It can be clearly observed from Fig. 6 that both loss components
exhibit distinct inverted-U shaped performance curves, indicating optimal weight ranges for maximum classification effectiveness. For the KL
divergence weight analysis, the classification accuracy increases from
97.63% when 𝜆𝐾𝐿 = 0.001 to a peak of 99.12% when 𝜆𝐾𝐿 = 0.05, representing an improvement of 1.49 percentage points. However, further
increasing 𝜆𝐾𝐿 to 0.2 causes the accuracy to decline significantly to
97.23%, a drop of 1.89 percentage points from the peak performance.
Similarly, the cross-modal generation weight demonstrates comparable
sensitivity patterns. When 𝜆𝑔𝑒𝑛 increases from 0.01 to 0.1, the accuracy
improves substantially from 97.29% to 99.12%, achieving a 1.83 percentage point gain. Beyond this optimal point, increasing 𝜆𝑔𝑒𝑛 to 0.25
results in performance degradation to 97.59%, representing a 1.53%
decrease from the peak.
The performance curves reveal distinct characteristics of diminishing and then negative returns beyond the optimal points. For KL
divergence weight, the most significant improvement occurs in the
range 𝜆𝐾𝐿 ∈ [0.001, 0.05], where accuracy increases by 1.49 percentage
points. When [0.001, 0.05] increases from 0.05 to 0.1, the performance
shows only a marginal decline of 0.17 percentage points (from 99.12%
to 98.95%), but further increases lead to more substantial degradation.
For cross-modal generation weight, the steepest improvement occurs in
the range 𝜆𝑔𝑒𝑛 ∈ [0.01, 0.1], with an improvement of 1.83 percentage
points, while increases beyond 0.1 result in consistent performance
decline.
Based on the above analysis, we identify the optimal weight configuration as 𝜆𝑐𝑙𝑠 ∶ 𝜆𝐾𝐿 ∶ 𝜆𝑔𝑒𝑛 = 1.0 ∶ 0.05 ∶ 0.1, which achieves the
highest classification accuracy of 99.12% in both experimental phases.
This configuration demonstrates that effective multimodal learning
requires careful balance among the three loss components: sufficient
classification guidance, appropriate latent space regularization, and optimal cross-modal consistency enforcement. Deviating from this balance
either under-utilizes the auxiliary information (when weights are too
small) or introduces excessive noise that interferes with the primary
classification objective (when weights are too large). Therefore, in all
subsequent experiments, we adopt this optimal weight configuration as
the default setting.

Fig. 5. Impact of diffusion timesteps on accuracy and training time.

determines the granularity of the diffusion process and affects both
representational capacity and computational complexity; and (2) the
weight balance among the three loss function components of formula (18), which governs the relative importance of classification,
regularization, and cross-modal consistency objectives.
4.4.1. Diffusion time steps analysis
To systematically evaluate the impact of T, we conduct a series of
controlled experiments, increasing the value of T from 2 to 14, while
measuring the classification accuracy and the normalized training time.
The normalized training time is based on the training time when T = 2
(set as 1.0), and the training time of other configurations is normalized
relative to this benchmark to intuitively show the relative increase in
computational overhead. Fig. 5 shows the results on dataset D1.
It can be observed that as the number of diffusion time steps
increases, the classification accuracy of the model shows a continuous
upward trend, increasing from 96.02% when T = 2 to 99.22% when T =
14. This indicates that a more fine-grained diffusion process can indeed
generate more accurate feature representations, thereby improving the
classification performance.
However, the improvement in classification accuracy is accompanied by a significant increase in the normalized training time. When T
= 2, the normalized training time is 1.0, and when T increases to 14,
the normalized training time rises to approximately 3.53, representing a
253% increase. It is worth noting that the curve of the improvement in
classification accuracy exhibits a distinct characteristic of diminishing
marginal returns. When T increases from 2 to 10, the accuracy improves
by 3.10%, and the normalized training time increases to approximately
2.64. When T further increases from 10 to 14, the accuracy only
improves by an additional 0.10%, while the normalized training time
increases by approximately 33.7%.
Based on the above analysis, we consider that T = 10 is an ideal
choice for balancing classification performance and computational efficiency. Under this configuration, the model achieves a high classification accuracy of 99.12%. Although the computational overhead
increases by 164% compared to the baseline, the performance improvement brought about by further increasing the number of diffusion
time steps is relatively limited and is difficult to offset the significant
increase in computational cost. In contrast, reducing the number of
time steps can lower the computational overhead but will significantly
affect the classification performance. Therefore, in the experiment, we
adopt T = 10 as the default configuration.

4.5. Entropy strategy analysis
This section presents an analysis of the model’s core mechanism,
namely the mixed entropy strategy, and its effectiveness. We perform a
detailed differential entropy analysis of the ER-CMGI model on dataset
D1, revealing important insights into multimodal encrypted traffic
classification, as shown in Fig. 7. Specifically, we observe that the
average entropy of byte sequences (0.0735) is significantly lower than
that of packet length sequences (0.8775). This indicates that byte
sequences in encrypted traffic tend to carry more certain and concentrated information, whereas packet length sequences exhibit higher
uncertainty.
More importantly, by analyzing the entropy distributions between
correctly and incorrectly classified samples, we uncover distinct patterns across modalities. In the byte modality, correctly predicted samples exhibit higher average entropy compared to misclassified ones. In
contrast, in the length modality, the trend is reversed—incorrectly predicted samples show higher entropy on average. These findings suggest
fundamental differences in how each modality contributes to classification performance and imply that traditional fusion strategies – such

4.4.2. Loss weight balance analysis
To systematically evaluate the impact of loss function weight balance, we conduct a series of controlled experiments with two phases:
12

Information Fusion 126 (2026) 103581

X. Wang et al.

Fig. 6. Impact of loss function weights on classification accuracy.

Fig. 7. Differential entropy analysis results.
Fig. 8. Performance comparison: Hybrid vs. traditional entropy strategy.

as ‘‘low entropy, high weight’’ – fail to fully exploit the discriminative
characteristics of individual modalities.
Motivated by the design principles established in Section 3.3.3,
we propose a novel hybrid entropy-based fusion strategy. The core
idea lies in introducing learnable or tunable mixing coefficients that
separately control the balance between two fusion principles: ‘‘high entropy, high weight’’ and ‘‘low entropy, high weight’’ for each modality.
Through systematic experimentation, we determine the optimal mixing
coefficient for the byte modality to be 0.7, favoring a ‘‘high entropy,
high weight’’ approach, while for the length modality, the optimal
value is 0.2, aligning with the conventional ‘‘low entropy, high weight’’
paradigm. This asymmetric weighting mechanism is well-aligned with
the observed entropy characteristics of the two modalities.
The effectiveness of the proposed hybrid entropy strategy is comprehensively validated through experiments, as shown in Fig. 8. Compared
to the traditional entropy-weighting method, our strategy achieves
improvements in accuracy (2.58%), recall (2.80%), F1 score (2.68%),
and precision (2.77%). Notably, the significant improvement in F1
score highlights not only enhanced overall performance but also better
class-level balance, which is crucial in real-world scenarios where class
imbalance is common.
The underlying mechanism of the hybrid entropy strategy can
be interpreted as a dynamically adaptive weight allocation process
that respects the intrinsic statistical properties of each modality. For
byte sequences, greater importance is assigned to samples with higher
entropy—reflecting their potential informativeness. Conversely, for
packet length sequences, higher weights are given to samples with
lower entropy, prioritizing those that are more predictable. This
modality-specific, sample-level adaptation enables the model to flexibly
adjust its reliance on different modalities, thereby maximizing the
benefits of multimodal fusion.

Experimental results demonstrate that the hybrid entropy strategy not only achieves superior performance on our dataset but also
exhibits strong generalization capabilities. As such, it offers a novel
and effective feature fusion approach for encrypted traffic classification and other multimodal learning tasks, opening new directions for
entropy-aware design in deep multimodal modeling.
4.6. Computational complexity and efficiency analysis
To address concerns regarding computational overhead and practical deployability, we present a comprehensive analysis of the model’s
complexity, efficiency, and resource requirements based on the actual architectural implementations. This evaluation directly compares
our lightweight diffusion framework with standard diffusion models,
demonstrating the practical feasibility and deployment advantages of
the proposed approach.
We begin by analyzing the component-wise complexity and parameter distribution, as summarized in Table 8. The analysis is conducted
on the real model structures, with the lightweight version containing
16.63M parameters and the standard diffusion baseline comprising
64.47M parameters.
The results show that the byte encoder is the most parameterheavy component, accounting for 77.3% of the total due to its large
fully connected layer. Meanwhile, cross-modal generators contribute
20.3% of the overall parameters. During inference, only 13.24M parameters are actively engaged (79.6% of the total), as the diffusion
time embedding and noise prediction modules remain operational to
ensure generation consistency verification. This selective activation
13

Information Fusion 126 (2026) 103581

X. Wang et al.
Table 8
Detailed model complexity and parameter analysis.
Component

Time complexity

Space complexity

Params (M)

Percentage

Byte encoder (2D CNN)
Length encoder (1D CNN)
Cross-modal generators
Entropy-guided fusion
Classification head

𝑂(1.6 × 106 )
𝑂(2.0 × 104 )
𝑂(2.0 × 106 )
𝑂(8.2 × 103 )
𝑂(1.3 × 103 )

𝑂(105 )
𝑂(103 )
𝑂(106 )
𝑂(102 )
𝑂(101 )

12.86
0.17
3.37
0.21
0.002

77.3%
1.0%
20.3%
1.3%
0.01%

Total (Training)
Total (Inference)

𝐎(𝟐.𝟎 × 𝟏𝟎𝟔 )
𝐎(𝟏.𝟔 × 𝟏𝟎𝟔 )

𝐎(𝟏𝟎𝟔 )
𝐎(𝟏𝟎𝟓 )

16.63
13.24

100%
79.6%

Table 9
Framework efficiency comparison.
Configuration

Params (M)

Training (h)

FLOPs/Sample

Memory (GB)

Standard diffusion
framework
ER-CMGI framework

64.47

8.5

3.2 × 108

4.8

16.63

1.3

7.1 × 107

1.2

Improvement

−74.2%

−84.7%

−77.8%

−75.0%

paradigms. However, these datasets may not fully encompass the complexity of modern network environments, including emerging protocols
(e.g., QUIC, HTTP/3), diverse geographical sources, and large-scale enterprise deployment scenarios. To address these limitations, we employ
cross-dataset validation and comprehensive preprocessing normalization to reduce dataset-specific biases. Future work will investigate
performance on larger-scale datasets and emerging protocol types to
further validate the practical applicability of our approach.
The framework also exhibits sensitivity to multiple hyperparameters, including diffusion timesteps, entropy mixing coefficients, and
loss weighting factors, requiring careful domain-specific optimization
for different network environments and attack types. Furthermore, the
current implementation is specifically designed for byte sequences and
packet length sequences, and extension to additional modalities would
require architectural modifications. A critical architectural limitation
emerges from the byte encoder design, where the majority of model
parameters are concentrated in a single large fully connected layer that
processes flattened CNN feature maps. This design creates parameter
inefficiency and potential information loss during aggressive dimensionality reduction, while constraining deployment on resource-limited
environments.
In addition, while our approach incorporates basic anonymization mechanisms (removing IP/MAC addresses), it currently lacks formal privacy guarantees such as differential privacy or secure multiparty computation. The flow-level analysis approach, although more
privacy-friendly than deep packet inspection, still processes raw network traffic that may contain implicit behavioral patterns. Future work
could explore integrating differential privacy techniques by adding
calibrated noise to latent representations or adopting federated learning approaches for distributed privacy-preserving intrusion detection,
though such enhancements may require balancing privacy protection
with detection accuracy.
Despite these limitations, the theoretical foundation and experimental results demonstrate the effectiveness of entropy-guided cross-modal
generation for encrypted traffic analysis, providing a solid foundation
for future improvements and practical deployment considerations.

contributes to the model’s efficient runtime behavior while preserving
functional integrity.
To demonstrate the efficiency improvements achieved by our
lightweight design, Table 9 presents a comprehensive comparison
between our full ER-CMGI framework and standard diffusion-based approaches. The results highlight that our framework achieves significant
efficiency gains through the integration of lightweight component design and optimized diffusion mechanisms. These improvements include
reduced parameter overhead, simplified architectural complexity, and
efficient cross-modal generation strategies.
The comparison demonstrates that our ER-CMGI framework
achieves 74.2% parameter reduction (16.63M vs. 64.47M), 84.7%
training time reduction (1.3 h vs. 8.5 h), 77.8% FLOPs reduction, and
75.0% memory reduction (1.2 GB vs. 4.8 GB) compared to standard
diffusion-based frameworks while maintaining classification performance.
The comparative analysis demonstrates the superior efficiency of
our ER-CMGI framework across multiple computational metrics. Compared to standard diffusion-based frameworks, ER-CMGI achieves a
74.2% reduction in model parameters (16.63M vs. 64.47M), an 84.7%
decrease in training time (1.3 h vs. 8.5 h), along with 77.8% fewer
FLOPs and 75.0% lower memory consumption (1.2 GB vs. 4.8 GB),
all while maintaining competitive classification performance. These
improvements translate into significant advantages for practical deployment scenarios. The lightweight design enables highly efficient
training, reducing training time by 84.7%, which facilitates faster
model iteration and deployment.
From an inference perspective, the architecture is optimized to
maintain low computational overhead without sacrificing processing
throughput. The asymmetric design ensures that the cross-modal
generators – comprising only 20.3% of the total parameters – are
primarily active during training. As a result, the deployed model
utilizes only 13.24M active parameters and occupies a compact size
of 33.3 MB under FP16 precision. Moreover, the model converges
stably within 20 training epochs, further enhancing its suitability for
resource-constrained environments.

5.2. Generalizability of the hybrid entropy strategy
The hybrid entropy strategy proposed in this work demonstrates
potential for extension beyond network traffic analysis to other multimodal learning domains. The core principle – dynamically weighting
modalities based on their information-theoretic properties while respecting modality-specific entropy characteristics – can be adapted to
various scenarios where heterogeneous data sources exhibit different
uncertainty patterns.
In audio-visual multimodal analysis, for instance, audio features
often exhibit higher entropy due to temporal variability and noise,
while visual features may show more stable patterns in certain contexts. The hybrid entropy approach could adaptively balance these
modalities by applying different entropy weighting strategies: favoring high-entropy audio features during dynamic scenes (where audio
provides discriminative information) while prioritizing low-entropy visual features during stable scenes (where visual consistency indicates
reliable information). Similarly, in medical multimodal analysis combining imaging and sensor data, different modalities may exhibit varying reliability patterns across patients or conditions, making adaptive
entropy-based fusion particularly valuable.

5. Discussion
5.1. Limitations
While our experimental datasets provide valuable validation for
the proposed approach, we acknowledge several inherent limitations
that may affect real-world applicability. Dataset D1 offers comprehensive coverage of traditional protocols and malware families, while
Dataset D2 incorporates recent TLS-encrypted traffic (2018–2021), enabling assessment across different temporal periods and encryption
14

Information Fusion 126 (2026) 103581

X. Wang et al.

6. Conclusion

References
[1] Matthew Roughan, Subhabrata Sen, Oliver Spatscheck, Nick Duffield, Class-ofservice mapping for QoS: a statistical signature-based approach to IP traffic
classification, in: Proceedings of the 4th ACM SIGCOMM Conference on Internet
Measurement, Association for Computing Machinery, 2004, pp. 135–148.
[2] Michael Finsterbusch, Chris Richter, Eduardo Rocha, Jean-Alexander Muller,
Klaus Hanssgen, A survey of Payload-Based traffic classification approaches, IEEE
Commun. Surv. & Tutorials 16 (2) (2014) 1135–1156.
[3] Iman Akbari, Mohammad A. Salahuddin, Leni Ven, Noura Limam, Stephane
Tuffin, A look behind the curtain: Traffic classification in an increasingly
encrypted web, Proc. ACM Meas. Anal. Comput. Syst. 5 (1) (2021) 1–26.
[4] Shahbaz Rezaei, Xin Liu, Deep learning for encrypted traffic classification: An
overview, IEEE Commun. Mag. 57 (5) (2019) 76–81.
[5] Navid Malekghaini, Elham Akbari, Mohammad Ali Salahuddin, Noura Limam,
Raouf Boutaba, Bertrand Mathieu, Stephanie Moteau, Stéphane Tuffin, Deep
learning for encrypted traffic classification in the face of data drift: An empirical
study, Comput. Netw. 225 (2023) 109648.
[6] Qingjun Yuan, Qianwei Meng, Jing Tao, Guangsong Li, Jinlong Fei, Bin Lu,
Yongjuan Wang, Multi-Agent for network security monitoring and warning: A
generative AI solution, IEEE Netw. (2025) 1–1.
[7] Ola Salman, Imad H. Elhajj, Ayman I. Kayssi, Ali Chehab, Data representation
for CNN based internet traffic classification: a comparative study, Multimedia
Tools Appl. 80 (2020) 16951–16977.
[8] Chen Mo, Wang Xiaojuan, He Mingshu, Jin Lei, Xiaojun Wang, A network traffic
classification model based on metric learning, Comput. Mater. Contin. 64 (2)
(2020) 941–959.
[9] Xinming Ren, Huaxi Gu, Wenting Wei, Tree-RNN: Tree structural recurrent neural
network for network traffic classification, Expert Syst. Appl. 167 (2021) 114363.
[10] Haipeng Yao, Chong Liu, Peiying Zhang, Sheng Wu, Chunxiao Jiang, Shui Yu,
Identification of encrypted traffic through attention mechanism based long short
term memory, IEEE Trans. Big Data 8 (1) (2022) 241–252.
[11] Xinbo Han, Guizhong Xu, Meng Zhang, Zheng Yang, Ziyang Yu, Weiqing
Huang, Chen Meng, DE-GNN: Dual embedding with graph neural network for
fine-grained encrypted traffic classification, Comput. Netw. 245 (2024) 110372.
[12] Guangwu Hu, Xi Xiao, Meng Shen, Bin Zhang, Xia Yan, Yunxia Liu, TCGNN:
Packet-grained network traffic classification via graph neural networks, Eng.
Appl. Artif. Intell. 123 (2023) 106531.
[13] Peng Xu, Xiatian Zhu, David A. Clifton, Multimodal learning with transformers:
A survey, IEEE Trans. Pattern Anal. Mach. Intell. 45 (2022) 12113–12132.
[14] Giuseppe Aceto, Domenico Ciuonzo, Antonio Montieri, Antonio Pescapé,
MIMETIC: Mobile encrypted traffic classification using multimodal deep learning,
Comput. Netw. 165 (2019) 106944.
[15] Giuseppe Aceto, Domenico Ciuonzo, Antonio Montieri, Antonio Pescapé, DISTILLER: Encrypted traffic classification via multimodal multitask deep learning,
J. Netw. Comput. Appl. 183–184 (2021) 102985.
[16] Peng Lin, Kejiang Ye, Yishen Hu, Yanying Lin, Cheng-Zhong Xu, A novel multimodal deep learning framework for encrypted traffic classification, IEEE/ACM
Trans. Netw. 31 (3) (2023) 1369–1384.
[17] Robin Rombach, Andreas Blattmann, Dominik Lorenz, Patrick Esser, Björn
Ommer, High-Resolution image synthesis with latent diffusion models, in: 2022
IEEE/CVF Conference on Computer Vision and Pattern Recognition, CVPR, 2022,
pp. 10674–10685.
[18] Naoto Inoue, Kotaro Kikuchi, Edgar Simo-Serra, Mayu Otani, Kota Yamaguchi,
LayoutDM: Discrete diffusion model for controllable layout generation, in: 2023
IEEE/CVF Conference on Computer Vision and Pattern Recognition, CVPR, 2023,
pp. 10167–10176.
[19] Wenhao Li, Xiao-Yu Zhang, Huaifeng Bao, Haichao Shi, Qiang Wang, ProGraph:
Robust network traffic identification with graph propagation, IEEE/ACM Trans.
Netw. 31 (2023) 1385–1399.
[20] Meng Shen, Kexin Ji, Zhenbo Gao, Qi Li, Liehuang Zhu, Ke Xu, Subverting website fingerprinting defenses with robust traffic representation, in: 32nd USENIX
Security Symposium (USENIX Security 23), USENIX Association, Anaheim, CA,
2023, pp. 607–624.
[21] Qianwei Meng, Qingjun Yuan, Weina Niu, Yongjuan Wang, Siqi Lu, Guangsong
Li, Xiangbin Wang, Wenqi He, IIT: Accurate decentralized application identification through mining intra- and inter-flow relationships, IEEE Trans. Netw. Serv.
Manag. 22 (1) (2025) 394–408.
[22] Akbar Telikani, Amir H. Gandomi, Kim-Kwang Raymond Choo, Jun Shen, A
Cost-Sensitive deep learning-based approach for network traffic classification,
IEEE Trans. Netw. Serv. Manag. 19 (1) (2022) 661–670.
[23] Giampaolo Bovenzi, Alfredo Nascita, Lixuan Yang, Alessandro Finamore,
Giuseppe Aceto, Domenico Ciuonzo, Antonio Pescapé, Dario Rossi, Benchmarking
class incremental learning in deep learning traffic classification, IEEE Trans.
Netw. Serv. Manag. 21 (1) (2024) 51–69.
[24] Zhaolei Shi, Nurbol Luktarhan, Yangyang Song, Gaoqi Tian, BFCN: A novel
classification method of encrypted traffic based on BERT and CNN, Electronics
12 (3) (2023) 516.

To address the challenges of dynamic feature fusion and crossmodal semantic alignment in encrypted traffic analysis, we propose
the ER-CMGI. The framework integrates the probabilistic generation capabilities of diffusion models with information-theoretic optimization,
enabling adaptive learning of multimodal representations. By introducing a lightweight hybrid architecture that combines diffusion models
and variational autoencoders, our approach facilitates more coherent
interaction between byte and length modalities, thereby overcoming
the limitations of static fusion strategies and misaligned latent spaces
commonly found in traditional methods.
We further propose an entropy guided fusion mechanism that dynamically balances the contribution of each modality based on its
intrinsic information content. By adjusting the fusion weights based
on the uncertainty and richness of individual modal representations,
this method achieves better integration of supplementary information while maintaining model interpretability. The performance of
adaptive weighting strategies has been demonstrated in complex classification scenarios, where modalities may exhibit varying degrees of
discriminative ability. While the current framework shows promising
results, future research directions should address computational efficiency through model compression and adaptive inference strategies,
enhance robustness by developing adaptation mechanisms for emerging
protocols such as QUIC and HTTP/3, and conduct large-scale validation
studies in production environments to further demonstrate practical
applicability in real-world deployment scenarios.

CRediT authorship contribution statement
Xiangbin Wang: Writing – original draft, Software, Methodology,
Conceptualization. Qingjun Yuan: Writing – review & editing, Methodology, Data curation. Wentao Yu: Visualization, Validation. Qianwei
Meng: Software, Formal analysis. Siqi Lu: Supervision, Funding acquisition. Wenqi He: Resources, Formal analysis. Chunxiang Gu: Writing
– review & editing, Project administration. Yongjuan Wang: Writing –
review & editing, Project administration, Funding acquisition.

Declaration of competing interest
The authors declare that they have no known competing financial interests or personal relationships that could have appeared to
influence the work reported in this paper.

Acknowledgments
This work is supported by The National Key Research and Development Program of China No. 2023YFB2705000.

Appendix A. Supplementary data
Supplementary material related to this article can be found online
at https://doi.org/10.1016/j.inffus.2025.103581.

Data availability
Data will be made available on request.

15

Information Fusion 126 (2026) 103581

X. Wang et al.
[25] Nguyen Huu Quyen, Phan The Duy, Ngo Thao Nguyen, Nghi Hoang Khoa, VanHau Pham, FedKD-IDS: A robust intrusion detection system using knowledge
distillation-based semi-supervised federated learning and anti-poisoning attack
mechanism, Inf. Fusion 117 (2025) 102807.
[26] Zhiping Jin, Zhibiao Liang, Meirong He, Yao Peng, Hanxiao Xue, Yu Wang, A
federated semi-supervised learning approach for network traffic classification,
Int. J. Netw. Manage. 33 (3) (2023) e2222.
[27] ZiXuan Wang, ZeYi Li, MengYi Fu, YingChun Ye, Pan Wang, Network traffic
classification based on federated semi-supervised learning, J. Syst. Archit. 149
(2024) 103091.
[28] Saadat Izadi, Mahmood Ahmadi, Amir Rajabzadeh, Network traffic classification
using deep learning networks and Bayesian data fusion, J. Netw. Syst. Manage.
30 (2) (2022) 1–21.
[29] Mohammad Lotfollahi, Ramin Shirali Hossein Zade, Mahdi Jafari Siavoshani,
Mohammadsadegh Saberian, Deep Packet: A novel approach for encrypted traffic
classification using deep learning, Soft Comput. 24 (2020) 1999–2012.
[30] Xin Wang, Shuhui Chen, Jinshu Su, App-Net: A hybrid neural network for
encrypted mobile traffic classification, in: IEEE INFOCOM 2020 - IEEE Conference on Computer Communications Workshops, IEEE, Piscataway, NJ, 2020, pp.
424–429.
[31] Xianwen Deng, Yijun Wang, Zhi Xue, AN-Net: an anti-noise network for anonymous traffic classification, in: Proceedings of the ACM Web Conference 2024,
2024, pp. 4417–4428.
[32] Giuseppina Andresini, Annalisa Appice, Luca De Rose, Donato Malerba, GAN
augmentation to deal with imbalance in imaging-based intrusion detection,
Future Gener. Comput. Syst. 123 (2021) 108–127.
[33] Aiyan Qu, Qiuhui Shen, Gholamreza Ahmadi, Towards intrusion detection in fog
environments using generative adversarial network and long short-term memory
network, Comput. Secur. 145 (2024) 104004.
[34] M. Rajkumar, J. Karthika, S.S. Abinayaa, Multi-view consistent generative
adversarial network for enhancing intrusion detection with prevention systems
in mobile ad hoc networks against security attacks, Comput. Secur. 150 (2025)
104242.
[35] Haofan Wang, Farah Kandah, Thilina Mendis, Lalith Medury, Clustering-Based
intrusion detection system meets multicritics generative adversarial networks,
IEEE Internet Things J. 12 (11) (2025) 16112–16128.
[36] Chao Zha, Zhiyu Wang, Yifei Fan, Bing Bai, Yinjie Zhang, Sainan Shi, Ruyun
Zhang, A-NIDS: Adaptive network intrusion detection system based on clustering
and stacked CTGAN, IEEE Trans. Inf. Forensics Secur. 20 (2025) 3204–3219.
[37] Nirhoshan Sivaroopan, Dumindu Bandara, Chamara Madarasingha, Guillaume
Jourjon, Anura P. Jayasumana, Kanchana Thilakarathna, NetDiffus: Network
traffic generation by diffusion models through time-series imaging, Comput.
Netw. 251 (2024) 110616.
[38] Xizheng Wang, Libin Liu, Li Chen, Dan Li, Yukai Miao, Yu Bai, Resolving
packets from counters: Enabling Multi-scale network traffic super resolution via
composable large traffic model, in: 22nd USENIX Symposium on Networked
Systems Design and Implementation (NSDI 25), 2025, pp. 1541–1561.
[39] Jonathan Ho, Ajay Jain, Pieter Abbeel, Denoising diffusion probabilistic models,
in: Advances in Neural Information Processing Systems, Vol. 33, 2020, pp.
6840–6851.
[40] Yang Song, Jascha Sohl-Dickstein, Diederik P Kingma, Abhishek Kumar, Stefano Ermon, Ben Poole, Score-based generative modeling through stochastic
differential equations, 2021, arXiv preprint arXiv:2011.13456.
[41] Alexander Quinn Nichol, Prafulla Dhariwal, Improved denoising diffusion probabilistic models, in: International Conference on Machine Learning, 2021, pp.
8162–8171.
[42] Prafulla Dhariwal, Alexander Nichol, Diffusion models beat GANs on image
synthesis, Adv. Neural Inf. Process. Syst. 34 (2021) 8780–8794.

[43] Wei Wang, Ming Zhu, Xuewen Zeng, Xiaozhou Ye, Yiqiang Sheng, Malware traffic
classification using convolutional neural network for representation learning, in:
2017 International Conference on Information Networking, ICOIN, 2017, pp.
712–717.
[44] Qingjun Yuan, Chang Liu, Wentao Yu, Yuefei Zhu, Gang Xiong, Yongjuan Wang,
Gaopeng Gou, BoAu: Malicious traffic detection with noise labels based on
boundary augmentation, Comput. Secur. 131 (2023) 103300.
[45] Wei Wang, Ming Zhu, Jinlin Wang, Xuewen Zeng, Zhongzhen Yang, End-to-end
encrypted traffic classification with one-dimensional convolution neural networks, in: IEEE International Conference on Intelligence and Security Informatics,
IEEE, Piscataway, NJ, 2017, pp. 43–48.
[46] Alec F. Diallo, Paul Patras, Adaptive Clustering-based malicious traffic classification at the network edge, in: IEEE INFOCOM 2021 - IEEE Conference on
Computer Communications, 2021, pp. 1–10.
[47] Ying Zhong, Zhiliang Wang, Xingang Shi, Jiahai Yang, Keqin Li, RFG-HELAD:
A robust Fine-Grained network traffic anomaly detection model based on
heterogeneous ensemble learning, IEEE Trans. Inf. Forensics Secur. 19 (2024)
5895–5910.
[48] Yuwei Xu, Jie Cao, Kehui Song, Qiao Xiang, Guang Cheng, FastTraffic: A
lightweight method for encrypted traffic fast classification, Comput. Netw. 235
(2023) 109965.

Xiangbin Wang received the M.Eng. degrees from Information Engineering University.
He is currently a graduate student studying for a Ph.D. in Information Engineering
University, China. His research interests include network security and network traffic
analysis.

Qingjun Yuan received the Ph.D. degree from Information Engineering University. He
is currently a lecturer at Information Engineering University. His research interests
include network security and side channel attack.

Wentao Yu received the Ph.D. degree from Information Engineering University. He is
currently a lecturer at Information Engineering University. He is also a postdoctoral
researcher at the Institute of Computing Technology, Chinese Academy of Sciences,
and his research interests include artificial intelligence and knowledge engineering.

Qianwei Meng is currently pursuing the Ph.D. degree at Information Engineering University. His research interests include network security and unknown traffic
detection.

Wenqi He received the M.S. degree in statistics from Zhengzhou University. Her
research interest is network security.

Chunxiang Gu received the Ph.D. degree from Information Engineering University. He
is currently a professor at Information Engineering University. His research interests
include network security and cryptographic analysis.

Yongjuan Wang received the Ph.D. degree from Information Engineering University.
She is currently a researcher at Information Engineering University. Her main research
interests include cryptographic analysis and zero trust security.

16
PAPER_TEXT
