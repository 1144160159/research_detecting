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
# [755] Multimodal Reasoning with LLM for Encrypted Traffic Interpretation: A Benchmark
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
编号：755
题名：Multimodal Reasoning with LLM for Encrypted Traffic Interpretation: A Benchmark
年份：2026
DOI：10.48550/arXiv.2604.08140
来源：arXiv preprint
PDF：paper/10.48550_arXiv.2604.08140.pdf
已有粗分类：加密流量分类与应用识别
二级关联：数据集、基准、综述与开源工具
相关性：强相关，分数 14
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\755.txt
- 原始字符数：88062
- 本次发送字符数：88062
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

1

Multimodal Reasoning with LLM for Encrypted
Traffic Interpretation: A Benchmark

（a）Traditional classification methods

Malicious (Tor)

45 00 3c 00 1c 46
40 06 00 c0 a8 01
c0 a8 01 02 00 50

Traditional
Classifier
"Offsets 42 has a weight of 0.8"
(meaning it has no practical
operational value)

Raw Traffic Bytes
（b）ours
Evidence-Grounded
Forensic Report

45 00 3c 00 1c 46
40 06 00 c0 a8 01
c0 a8 01 02 00 50

Raw Traffic Bytes

Cognitive LLM

Abstract—Network traffic, as a key media format, is crucial
for ensuring security and communications in modern internet
infrastructure. While existing methods offer excellent performance,
they face two key bottlenecks: (1) They fail to capture multidimensional semantics beyond unimodal sequence patterns. (2) Their
“black box” property, i.e., providing only category labels, lacks an
auditable reasoning process. We identify a key factor that existing
network traffic datasets are primarily designed for classification
and inherently lack rich semantic annotations, failing to generate
human-readable evidence report. To address data scarcity, this
paper proposes a Byte-Grounded Traffic Description (BGTD)
benchmark for the first time, combining raw bytes with structured
expert annotations. BGTD provides necessary behavioral features
and verifiable chains of evidence for multimodal reasoning
towards explainable encrypted traffic interpretation. Built upon
BGTD, this paper proposes an end-to-end traffic-language
representation framework (mmTraffic), a multimodal reasoning
architecture bridging physical traffic encoding and semantic
interpretation. In order to alleviate modality interference and
generative hallucinations, mmTraffic adopts a jointly-optimized
perception-cognition architecture. By incorporating a perceptioncentered traffic encoder and a cognition-centered LLM generator,
mmTraffic achieves refined traffic interpretation with guaranteed
category prediction. Extensive experiments demonstrate that
mmTraffic autonomously generates high-fidelity, human-readable,
and evidence-grounded traffic interpretation reports, while maintaining highly competitive classification accuracy comparing to
specialized unimodal model (e.g., NetMamba). The source code
is available at Traffic-Reasoning-Project.

Perception Traffic
Encoder

arXiv:2604.08140v1 [cs.CR] 9 Apr 2026

Longgang Zhang, Xiaowei Fu, Fuxiang Huang, and Lei Zhang, Senior Member, IEEE

"class"
Malicious (Tor)
"traits"
TLS 1.3
"evidence"
high entropy, low ASCII ratio

"description"

"Automated Tor
malware C2 beaconing
with high-entropy, lowthroughput payloads

"notes"

Understandable
classification results and
reasoning details

Persistent and low
throughput

Byte-Grounded
Knowledge

Fig. 1. Comparison of traffic analysis paradigms. (a) Traditional classification
methods that act as a “black box”, providing only a label and low-level feature
weights that lack operational value. (b) Our proposed multimodal reasoning
framework, composed of a Traffic Perception Encoder and a Cognitive LLM,
instructed by Byte-Grounded Knowledge, generating an evidence-grounded
report with human-understandable reasoning and executable insights.

relied on statistical features (e.g., packet size distribution and
arrival time intervals, etc.) and machine learning techniques,
but struggled to adapt to the highly-dimensional and dynamic
Index Terms—Encrypted traffic classification, network traffic adversarial nature of modern network traffic. In contrast,
interpretation, large language model, multimodal learning.
deep learning (DL) models achieved significant performance
improvements by automatically extracting hierarchical representations from raw byte sequences. In recent years, inspired by the
I. I NTRODUCTION
success of self-supervised pre-training in large models, traffic
ETWORK traffic analysis is a core pillar for ensuring analysis models based on Transformers [33] and state space
network security, implementing intrusion detection, and models (SSMs) [13] are emerged. For example, ET-BERT [19]
conducting traffic engineering. With the widespread deployment introduced a masked burst flow model, MPAF [6] proposed
of Transport Layer Security (TLS 1.3), Quick UDP Connections a multi-phase attribute fingerprint, YaTC [38] proposed a
(QUIC), and anonymous routing networks such as Tor [9], end- multi-level flow representation (MFR) matrix, NetMamba [34]
to-end encryption has made payload content extremely opaque. achieved ultra-fast inference using the linear-time complexity of
This evolution has rendered traditional Deep Packet Inspection the Mamba architecture, FlowletFormer [22] further optimized
(DPI) mechanisms, relying on plaintext signature matching, alignment capabilities by introducing behavior-semantic-aware
largely ineffective. Facing this challenge, encrypted traffic Flowlet units, and WF-Transformer [39] further proposed a
classification techniques have emerged. These methods heavily Transformer-based temporal feature extraction method.
Despite the empirical success of deep representation learning
This work was partially supported by National Natural Science Fund of
China under Grants 92570110 and 62271090, Chongqing Natural Science
models, contemporary cryptographic traffic analysis models
Fund under Grant CSTB2024NSCQ-JQX0038, and National Youth Talent
remain constrained by two key bottlenecks: (1) Semantic Void in
Project. (Corresponding author: Lei Zhang)
Unimodal
Representations. Existing models essentially perform
L. Zhang, X. Fu and L. Zhang are with the School of Microelectronics and
Communication Engineering, Chongqing University, Chongqing 400044, China. nonlinear boundary partitioning in a high-dimensional space,
(E-mail: zlg502361@gmail.com, xwfu@cqu.edu.cn, leizhang@cqu.edu.cn,)
directly mapping pure numerical hexadecimal byte sequences
Fuxiang Huang is with the School of Data Science, Lingnan University,
to classification labels. In complex enterprise environments,
Hong Kong, China. (E-mail: fxhuang1995@gmail.com)
Manuscript received April 19, 2015; revised August 16, 2015.
security analysts often encounter the “statistical twin” phe-

N

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

nomenon, i.e., benign traffic and malicious traffic employing
obfuscation techniques exhibit almost identical statistical distributions. Relying solely on unimodal sequence patterns makes
these models inadequate to capture the rich, multidimensional
semantics required to distinguish such threats. (2) Black-box
Property and Limitations of Traditional Explainable Artificial
Intelligence (XAI). Purely statistical classifiers cannot provide
human-readable, auditable, protocol-level forensic evidence to
justify their decisions. While post-hoc interpretation techniques
(e.g., SHAP [25], LIME [30] and Grad-CAM [31]) attempted
to address this, they can only generate importance scores for
features or attention heatmaps. For frontline Security Operations
Center (SOC) analysts, knowing that “the byte with offset 42
has high weight” is of no operational value unless the byte
can be logically mapped to a specific protocol anomaly, such
as a malformed handshake frame or an illegal cipher suite.
To overcome the aforementioned semantic limitations and
black-box constraints, the deep model is expected to learn to
map low-level physical bytes to high-level protocol semantics.
However, existing network traffic datasets are primarily collected for the traditional classification task, providing only
discrete category labels and inherently lacking the rich, multidimensional semantic annotations required, and thus unable
to train generative interpretable models. To bridge this fundamental gap, we innovatively construct a Byte-Grounded Traffic
Description (BGTD) dataset. To the best of our knowledge,
BGTD is the first benchmark that explicitly pairs raw network
traffic bytes with structured, rich expert knowledge. To ensure
strong generalization capabilities, the dataset integrates six
authoritative public repositories covering a broad ecosystem
of applications. Beyond basic classification, BGTD provides
fine-grained semantic annotations such as discriminative behavioral features, verifiable chains of evidence, and natural
language descriptions. These elements are constructed through
an automated expert knowledge generation process powered by
Claude Opus. By linking numerical payloads with the highlevel forensic information, BGTD provides the key foundational
data required for multimodal reasoning.
Building upon this multimodal benchmark, this paper proposes an end-to-end, multi-modal traffic-language representation framework (mmTraffic) to overcome the inherent limitations of semantic void and black-box property in traditional
traffic classifiers. Unlike traditional pipelines that strictly freeze
the traffic encoder to prevent catastrophic forgetting and often
lead to weak semantic alignment, mmTraffic advocates for a
joint optimization for perception and cognition modules. By
introducing an auxiliary classification head in perception and
a semantic-priority guided generation mechanism in cognition,
our framework explicitly constrains the continuous feature
space and forces the large language model (LLM) to perform
accurate classification before reasoning. This intrinsically
empowers LLM to understand non-semantic traffic bytes and
generate human-readable, evidence-grounded reports.
Fig. 1 describes the paradigm difference between mmTraffic
and others. The main contributions are summarized as follows:
• A Byte-grounded traffic description benchmark
(BGTD). We construct the first benchmark to explicitly
pair raw network traffic bytes with structured expert

2

knowledge. By providing discriminative behavioral traits
and verifiable chains of evidence, BGTD bridges the
fundamental data-knowledge gap and enables multimodal
reasoning towards interpretable encrypted traffic analysis.
• A multi-modal traffic reasoning framework (mmTraffic). We reformulate encrypted traffic analysis as a jointly
optimized multimodal alignment pipeline. By unfreezing
the traffic encoder and training it synergistically with the
LLM, we achieve a deep semantic mapping from physical
network bytes to human-readable concepts.
• Auxiliary constraint and semantic-priority generation.
We introduce a classification head to enforce discriminative constraints on the traffic encoder. Furthermore, we
design a semantic-priority generation loss that dynamically
assigns higher weights to the categorical tokens, effectively
mitigating LLM hallucinations in category prediction and
ensuring the quality of generated reports.
• Superior performance of traffic interpretation with
classification. Extensive evaluations across six diverse
traffic benchmarks demonstrate that mmTraffic achieves
high-fidelity, auditable report generation, while maintaining exceptional classification accuracy.
II. R ELATED W ORK
A. Self-supervised Methods for Encrypted Traffic Classification
Large-scale self-supervised representation learning for network traffic is one of the most significant breakthroughs in
cybersecurity in recent years. Early efforts primarily adapted
paradigms from natural language processing and computer
vision. For instance, ET-BERT [19] pioneered the application
of transformer architectures to traffic sequences via binary
segmentation and masked burst flow modeling. Conversely,
YaTC structured raw traffic as a multi-level flow representation
(MFR) matrix, employing a dual-attention masked autoencoder to explicitly capture hierarchical packet interactions. To
address computational bottlenecks and structural limitations,
recent research has shifted towards efficiency and behavioral
semantics. NetMamba [34] innovatively introduced state-space
model (SSM) [13] via a stride-based representation, achieving
faster inference suitable for high-speed networks. Meanwhile,
FlowletFormer [22] moved beyond fixed-length truncation by
encoding explicit multi-layer protocol semantics based on
coherent behavioral interaction units. Beyond masked modeling
paradigms, contrastive learning has also been explored as
a self-supervised pre-training strategy for encrypted traffic
analysis. For instance, SmartDetector [32] proposes a Semantic
Attribute Matrix (SAM) representation and designs a traffic
data augmentation method to improve robustness against
obfuscation strategies such as dummy packet injection, pretraining the detection model via contrastive learning to learn
deep representations from unlabeled traffic data.
Despite the diverse architectures and continuous breakthroughs [10] in accuracy, these models share a fundamental
limitation: they are entirely constrained by the nature of
unimodal black-box classifiers, as shown in Tables I. While they
excel at the classification task, they can only map numerical
sequences to discrete labels, but fail to reasoning and generate
interpretable reports with chains of evidence.

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

3

TABLE I
C OMPARISONS OF DIFFERENT PARADIGMS FOR NETWORK TRAFFIC ANALYSIS . MBM, SBP, MAE, MFM, AND FPT REPRESENT M ASKED B YTE M ODEL ,
S EGMENT B URST P REDICTION , M ASKED AUTOENCODER , M ASKED F LOW M ODEL , AND F LOW P REDICTION TASK , RESPECTIVELY.
Model

Traffic Representation

Core Structure

Pre-training

Limitations

ET-BERT [19]

4-hex Bigram / Burst
Segmentation

Transformer Encoder

MBM / SBP

Ignores protocol hierarchy; uses natural language
subword tokenization

YaTC [38]

Multi-level Flow
Representation (MFR)
Matrix

Dual-Attention
Transformer

MAE (Matrix
Masking)

Fixed matrix dimensions; truncates long-range
session features

NetMamba [34]

Stride-based Byte Sequence

Unidirectional Mamba
(SSM)

Masked Stride
Reconstruction

Purely numerical mapping; lacks interpretability

FlowletFormer [22]

Flowlet Behavioral Unit /
Field Tokenization

Transformer Encoder

MFM / FPT

Black-box classifier; unable to output forensic
reasoning

diverse vision-language tasks. mmTraffic draws the following
Early applications of Large Language Models (LLMs) in insight: rather than relying on disparate training stages with
cybersecurity were primarily limited to plain text tasks, such as a frozen perception module, we align an active traffic encoder
threat intelligence aggregation [2], log parsing, and vulnerability with a language model through a lightweight MLP connector,
description summarization. However, recent study begun to empowering the LLM to perform encrypted traffic interpretation
explore domain-specific LLMs capable of directly interpret- with rigorous multimodal reasoning.
ing underlying telemetry data. TrafficLLM [7] represents a
significant attempt to bridge the modality gap. It employs a D. Explainability in Traffic Analysis
traffic-domain tokenizer to compress protocol fields by reducing
Despite the strong empirical performance of deep traffic
token length to an approximately half. While TrafficLLM [7] classifiers, their black-box nature has motivated a growing
has demonstrated the feasibility of feeding continuous/discrete body of work on explainable AI (XAI) [5]. Post-hoc techniques
telemetry data into an LLM, this one-tower early fusion archi- such as SHAP [25], LIME [30], and Grad-CAM [31] provide
tecture suffers from an inherent structural vulnerability. Forcing feature-level attribution scores, but cannot produce protocolan LLM to simultaneously process discrete natural language level forensic evidence for security analysts. While attentiontokens and high-entropy, non-semantic numerical traffic tokens based mechanisms have been extended to model inter-modal
within the same attention layers frequently induces modality interactions [23] and structured multimodal representations [14],
interference. Consequently, in high-risk intrusion detection, these approaches remain confined to feature-level enhancethis architecture may neglect the authenticity of underlying ment without producing human-readable explanations. DISphysical bytes in order to maintain the fluency of the language, TILLER [1] proposed a multimodal multitask framework that
inevitably generating fictitious security alert logic. In contrast, jointly learns traffic representations and human-readable labels,
the proposed mmTraffic explicitly mitigates this limitation by but still lacks free-form natural language generation. mmTraffic
reformulating the architecture as an end-to-end multimodal addresses this gap by leveraging large language models to
framework, fundamentally bridges the modality gap, prevents produce structured, evidence-grounded forensic reports, moving
generative hallucinations, and forces the LLM to ground its beyond importance scores toward auditable reasoning chains.
reasoning in authentic physical bytes.
B. LLMs for Network Security

III. BGTD B ENCHMARK FOR T RAFFIC R EASONING
C. Multimodal Alignment and Cross-Modal Fusion

A. Overview

The problem of bridging heterogeneous modalities is wellA benchmark that explicitly links raw traffic analysis data
studied in the vision-language domain. Early approaches to with expert-level semantic reasoning is a prerequisite for
cross-modal alignment include graph-based relational mod- training a multimodal traffic reasoning framework, but is
eling [15] and semantic-driven hashing for large-scale re- still unexplored. Therefore, we develop a Byte-Grounded
trieval [4], which established the importance of preserving Traffic Description (BGTD) benchmark, which, to the best
semantic correspondences across modalities. CLIP [27] demon- of our knowledge, bridges the data scarcity and persistent
strated that contrastive alignment between image and text data-knowledge gap in encrypted traffic interpretation for
encoders produces powerful transferable representations. Subse- the first time. To ensure the diversity of data distribution
quent works such as LLaVA [20] and InstructBLIP [8] extended and scenarios, the BGTD dataset integrates six authoritative
this paradigm by using lightweight projection connectors to map public traffic repositories, covering different network behaviors,
frozen visual encoders into the token space of large language application ecosystems, and encryption protocols. Specifically,
models, enabling instruction-following behavior over visual BGTD deeply integrates cross-platform mobile application
inputs. Flamingo [3] further showed that cross-modal fusion via traffic (i.e., CrossPlatform-Android [29] and CrossPlatformgated attention layers enables few-shot generalization across iOS [29]), cutting-edge TLS 1.3 encrypted web communication

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

4

Category Extraction

Class 1
Class 2
Class 3

Class 4

Dataset Generation Pipeline Script

Pcaps Extraction

Split PCAPs

5-Tuple
Session
Splitting

Raw
Traffic
Pcaps

Header

Head: First
2 Packets

Mid 6
Packets

Knowledge
Base Prompt
Template

Tail: Last
2 Packets

Claude
Opus-4.6
Knowledge
Base

Global Stats
Drop: Class < Min Samples

Truncate: Random
Sample to Max Cap

Class 1
Class 3

Class 2

Packets List

category
"class"： Trafficlabel

"traits"：

Global & Local
Features

Payload

Target
Byte-level
features
byte-level

supporting the
"evidence"：
classification

NPY Fixed Length

Entropy &
Payload

64 byte
Class 4

Global
Statistical
features and
Local Byte-level
attributes

Pattern
Match

96 byte

（a）Session Extraction and Class Balancing （b）Fixed-Length Truncation and NPY Array Generation

Natural
language

"description"：summary of

traffic type and
behavior

"notes"：

Related
suggestions

（c）Automated Expert-Knowledge Generation Pipeline

Fig. 2. Pipeline of developing BGTD dataset: (a) session extraction and class balancing from raw PCAP files, (b) fixed-length 10 × 160 NPY array generation
via priority-based packet sampling, and (c) LLM-assisted ground-truth synthesis using Claude Opus-4.6 prompted as a senior network security expert.

B. Session Extraction and Class Balancing
As shown in Figure 2 (a), the raw PCAP files from various
datasets undergo a multi-stage preprocessing. First, each PCAP
file is partitioned into the standard five-tuple format (i.e., source
IP address, destination IP address, source port, destination port,
protocol). To mitigate the impact of the long-tail distribution,
the original dataset is filtered by category, with lower and
upper sample thresholds applied. Categories below the lower
threshold are removed, while categories above the upper
threshold are sampled according to the threshold. Specific
processing methods for each dataset are provided in Sec. V-A1.
The statistics of the BGTD dataset are shown in Figure 3.
C. Fixed-Length Truncation and NPY Array Generation

 ' D W D V H W  & R P S R V L W L R Q   6 D P S O H  & R X Q W V  D Q G  & O D V V  ' L V W U L E X W L R Q
      

 1 X P E H U  R I  6 D P S O H V

(i.e., CSTNet-TLS1.3) [19], complex encrypted VPN tunnels
and anonymous routing networks (i.e., ISCXVPN2016 [11] and
ISCX-Tor-2016) [17], and hybrid malware traffics containing
multiple attack families (i.e., USTC-TFC-2016 [35]). The
pipeline for the BGTD dataset is shown in Figure 2.

 7 U D L Q
 7 H V W

      
      

      
      

      

      

     F O V

 

      
     F O V

 & U R V V 3 O D W I R U P  & U R V V 3 O D W I R U P
 $ Q G U R L G
 L 2 6

      

      
   F O V

 , 6 & ; 9 3 1
    

    F O V
     F O V

   F O V

 , 6 & ;  7 R U
    

 & 6 7 1 H W
 7 / 6    

 8 6 7 &  7 ) &
    

Fig. 3. Statistical overview of the BGTD dataset.

larger payloads typically carry richer application-layer
protocol fingerprints.
• Dimension Alignment and Consistency Guarantee: To
ensure every sample has exactly K packets, the algorithm
applies two strategies depending on the flow length n. If
n ≥ K, the first two and last two packets are retained
as structural anchors, and the remaining K−4 slots are
filled by selecting packets from the middle region in
descending order of payload size, prioritizing informationrich packets. If the quota is still unmet, equidistant
indices are computed via linspace(0, n−1, deficit) and
the corresponding packets are appended. If n < K, all
packets are kept and the sequence is extended by cyclic
repetition, i.e., position j maps to packet j mod n, until
exactly K packets are obtained.

Each segmented flow from above step is treated as an
independent sample. To extract informative byte-level features
from the original traffic data, we implement a heuristic prioritybased sampling algorithm, aiming to transform variable-length
network flows into fixed-dimensional tensor features. This
algorithm does not employ simple sequential truncation or
random sampling, but rather comprehensively considers the
temporal structure and payload information of the flow. Its
specific execution logic is as follows:
Simultaneously, to ensure the consistency of the input
• Temporal Keyframe Preservation: The algorithm
dimensions for subsequent processing and focus on the critical
forcibly preserves the first two packets and the last two protocol negotiation phase, each packet obtained by the packet
packets in the flow sequence. Preserving the header sampling algorithm is truncated or padded to a fixed length of
packets is to capture key metadata such as protocol 160 bytes. As shown in Figure 2 (b), the 160 bytes consists
handshakes and control negotiations. Preserving the tail of a 64-byte header area (i.e., L3/L4 header used to capture
packets helps record the state characteristics.
protocol metadata) and a 96-byte payload area. Ultimately,
• Payload Information Filtering: For packets in the middle
each network stream is transformed into a fixed-dimensional
of the stream, the algorithm sorts them in descending tensor X ∈ R10×160 containing a custom protocol ID byte,
order based on the transport layer (L4) payload length a 63-byte processed header, and a 96-byte payload, which is
and prioritizes packets with larger payloads to fill the then flattened into a 1600-dimensional continuous byte matrix.
preset sampling number K (K = 10 in this paper). This Furthermore, to protect privacy and prevent the model from
strategy is based on the assumption that packets with overfitting specific network identifiers, the system forcibly

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

5

Multi-field Semantic “Label” Generation. Thirdly, upon
the above features and expert knowledge base, the dataset
generation pipeline conducts a structured process to generate
fine-grained semantic labels (i.e., “Target” in Figure 2 (c)),
comprising 5 structured fields. The class field provides the
ground-truth traffic category label, directly derived from the
directory structure of the original dataset after session splitting
and class balancing. The traits field encodes five deterministic
byte-level attributes extracted from the NPY array: a boolean
indicating the presence of TLS record header patterns, a boolean
D. Automated Expert-Knowledge Generation Pipeline
indicating the presence of plaintext HTTP tokens, and three
To construct relationships between traffic data and reliable discretized bucket indicators for ASCII ratio, Shannon entropy,
analysis reports, we resort to large-scale language models to and zero-padding ratio, each categorized as low, mid, high based
conduct a structured process from low-level data to high-level on the 33rd and 66th percentiles of the full data distribution.
The evidence field contains 2 to 4 natural language statements
semantics [21], as shown in Figure 2 (c).
Global and Local Feature Extraction. Firstly, to capture constructed by combining the above byte-level traits and
interpretable reasoning evidence, we deploy a Dataset Gener- global features. Each statement describes a concrete, verifiable
ation Pipeline Script to extract global statistical features and observation grounded in the raw byte data (e.g., “High Shannon
entropy in non-zero payload regions indicates that the data
local byte-level attributes from traffic analysis data X:
is highly likely to have been encrypted or compressed”).
• Global Statistical Features: This data includes the duration
The description field provides a 2 to 3 sentence behavioral
of traffic, average packet size, throughput (Bps), and summary that integrates byte-level observations with the expert
the proportion of dominant protocols. These features knowledge base, depicting the protocol attribution, applicationare transformed into semantic descriptions by script. For layer characteristics, and typical communication behavior of
example, an average packet length exceeding 800 bytes is the traffic. The notes field supplies a single security-relevant
mapped to “large-volume data transmission sentence drawn from the knowledge base’s security context,
characteristics”.
highlighting potential misuse risks, recommended monitoring
• Encryption and Payload Distribution Evaluation: For
strategies, or distinguished indicators for anomaly detection.
encrypted traffic, such as TLS 1.3 environments, the
Ultimately, all five fields are serialized together as a strucShannon entropy of non-zero payload regions and the tured JSON object and stored in JSONL format, forming the
proportion of printable ASCII characters are calculated. complete training target for the proposed mmTrafficframework.
Based on the statistical distribution of the entire dataset,
these continuous indicators are discretized into three levels:
IV. T HE P ROPOSED MM T RAFFIC
low, mid, and high, at the 33rd and 66th percentiles. For
example, “low ASCII rate” combined with “high Shannon A. Overview of the Framework
entropy” will serve as a strong signal of encrypted or
The pipeline of mmTraffic is illustrated in Figure 4. It
compressed data characteristics.
comprises three highly-collaborative and jointly-optimized mod• Deterministic Pattern Matching: Detect if the payload conules: Perception module, Alignment module, and Cognition
tains obvious plaintext HTTP methods (e.g., GET, POST, module. First, the Perception module acts as the foundational
etc.) or TLS record layer header features (e.g., 0x14-0x17 feature extractor. Unlike previous paradigms that freeze the
with version number 0x03) via feature matching, providing traffic encoder, our encoder actively participates in the multihard logic support for classification.
modal training phase, updating its parameters to learn languagemasks the source and destination IP addresses at the network
layer and uses a bucketing mechanism to map transport layer
ports into three categories: privileged ports, registered ports, and
dynamically private ports. This de-identification strategy forces
the model to focus on protocol semantics and payload sequence
patterns, thereby improving the model’s generalization ability.
Ultimately, for ease of development, the pre-processed traffic
data is stored as NPY array.

Expert Knowledge Base Construction. Secondly, to address aligned representations directly from raw traffic bytes. Second,
the lack of rich semantic descriptions in traditional traffic the Alignment module bridges the dedicated traffic latent space
datasets, this study introduces a large language model (Claude and the natural language lexical space. To force this projected
Opus-4.6) to help construct a structured domain expert space to capture highly discriminative semantics autonomously,
knowledge base. For each traffic category in the dataset, we introduce an auxiliary classification head with a dedicated
according to preset Knowledge Base Prompt Template, LLM constraint loss. This ensures the continuous features possess
automatically generates an expert description containing three clear, linear-separable categorical boundaries before entering
dimensions: (1) a protocol hint that concisely defines the the language model. Finally, the Cognition module leverages
application or protocol to which the traffic belongs; (2) the aligned multimodal embeddings to perform autoregressive
behavioral characteristics describing 3 to 5 typical patterns reasoning. To ensure the generated traffic analysis report
of the traffic at the network level; (3) a security context remains logically rigorous, we propose a Semantic-Priority
that provides supplementary explanations from a network Guided Generation mechanism. This mechanism dynamically
security and traffic monitoring perspective, identifying the assigns higher optimization weights to the categorical tokens
key distinguishable features among easily confused categories. generated at the beginning of the sequence, compelling the
This knowledge base provides powerful domain knowledge for large language model (LLM) to perform accurate classification
subsequently constructing rich, multi-perspective training texts. before reasoning about verifiable chains of evidence. By

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

Analysis Report

Traffic
Analysis
Report and
Category
Information

Payload

Header

Payload

Header

Payload

Header

Payload

Traffic Data

（a）Perception Module

Projection
Connector

(b) Alignment Module with Auxiliary Classification

Large Language Models (LLMs)

Payload

Header

Auxiliary
Cls
Head

Class label

[traffic token] + The traffic has been classified
as: VoIP + Prompt

Header

Class：VoIP
Behavioral Traits

Prompt

Payload

Analysis report

Traffic Encoder

Header

6

Entropy
(Low)

ASCII Ratio
(High)

True

True

False

False

TLS
Record

Zero Pad
(Mid)

HTTP
Method

Evidence Chain
Synthesized as
Plaintext

Excluded Web-

Transmission (No
Encryption
detected).

Anchored by DNS

based traf f ic;
(100.0% ) as Audio
Carrier.

Unlike Chat
(Irregular) or
Streaming
(Unidirectional).

Description
Final
Prediction：

VoIP

"Confirmed bi-directional real-time
audio stream. Dominant protocol
identified as DNS (100.0% of bytes).
Payload exhibits persistent plaintext
accessibility."

⚠️ Risk: Unencrypted Plaintext (Eavesdropping)

（c）Cognitive Module

Fig. 4. Overview of the mmTraffic framework. (a) The frozen traffic encoder Tθ extracts high-dimensional features from raw traffic data. (b) The linear
connector Cω projects traffic features into the LLM token space, with the CGHF mechanism injecting a class-aware anchor token into the input sequence.
(c) The LLM Gϕ autoregressively generates a structured forensic report containing behavioral traits, evidence chain, and diagnostic description.

transitioning to an end-to-end joint optimization strategy,
mmTraffic empowers the LLM to intrinsically understand and
classify non-semantic traffic sequences, successfully achieving
accurate classification and evidence-grounded interpretation
within a unified framework.

activation. Given the continuous traffic embedding Ttraffic from
the Perception module, the non-linear transformation of Cω is
formally defined as:
Halign = Cω (Ttraffic ) = W2 σ(W1 Ttraffic + b1 ) + b2 (2)

where σ(·) denotes the GELU activation function, and ω =
{W1 , b1 , W2 , b2 } represents the learnable weight matrices
B. Perception Module
and bias vectors of the connector. The resulting Halign bridges
This module receives the raw byte sequence X preprothe dimensional gap, projecting the traffic features into the
cessed according to the BGTD protocol and performs a highLLM’s lexical space.
dimensional non-linear mapping via the traffic encoder Tθ .
Auxiliary Classification. During alignment, simply mapping
High-dimensional Continuous Feature Embedding: The the dimensions is insufficient to guarantee that the projected
encoder Tθ processes X to automatically extract complex tokens carry explicit categorical semantics. To force the continspatial dependencies and structural patterns of protocol fields, uous feature space to capture highly discriminative information,
generating a dense feature tensor:
we introduce an Auxiliary Classification Head, denoted as Aκ ,
Ttraf f ic = Tθ (X)
(1) atop the projection connector. Specifically, we first apply Global
Average Pooling (GAP) across the sequence dimension L of the
where Ttraf f ic ∈ RL×dtraf f ic , L denotes the sequence length, aligned features Halign to obtain a condensed sequence-level
and dtraf f ic represents the feature dimension of the traffic semantic representation Hpool ∈ Rdh :
encoder.
L
End-to-End Optimization: In contrast to previous multi1 X (i)
H
=
GAP(H
)
=
H
(3)
pool
align
stage paradigms where the perception module is trained
L i=1 align
independently and then strictly frozen to prevent catastrophic
forgetting, our framework treats Tθ as an active component where H(i)
align represents the i-th token embedding in the
within a unified multimodal architecture. The parameters of sequence, and dh is the hidden dimension of the LLM.
the traffic encoder are unfrozen and updated during the joint This pooled representation is then processed by the auxiliary
training phase. By receiving gradient feedback backpropagated classification head Aκ to predict the discrete probability
from both the downstream auxiliary classification head Aκ and distribution pcls ∈ RC over C predefined traffic classes:
the cognitive language model, the encoder is explicitly guided
pcls = Aκ (Hpool ) = Softmax(Wcls Hpool + bcls ) (4)
to map non-semantic raw bytes into a representation space that
is naturally aligned with language-based reasoning.
where κ = {Wcls , bcls } are the learnable parameters of Aκ ,
mapping the hidden dimension dh to the category space C.
Then we compute the auxiliary classification loss using the
C. Alignment Module with Auxiliary Classification
standard cross-entropy objective:
To achieve implicit alignment between the dedicated traffic
C
X
latent space and the natural language lexical space, mmTraffic
L
=
−
yc log(pcls,c )
(5)
aux
deploys a lightweight projection connector Cω . For computac=1
tional efficiency, we employ a two-layer Multi-Layer Perceptron
(MLP) equipped with a Gaussian Error Linear Unit (GELU) where yc ∈ {0, 1} is the binary indicator of the ground-truth

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

7

Algorithm 1 The Training Pipeline of mmTraffic
Require: Traffic tensor X ∈ R10×160 , ground-truth label y,
chain of evidence annotation R = {r1 , . . . , rT } of BGTD,
unfrozen encoder Tθ , connector Cω , auxiliary classification
head Aκ , LLM Gϕ , task prompt P, auxiliary loss weight
λ, semantic boost weight γ, and threshold M .
D. Cognition Module
Ensure: Predicted traffic class ŷ and forensic report Rpred .
With the auxiliary classification constraint enforcing
// Step 1: Perception Module
category-aware features in the alignment stage, the Cognition
1: Ttraffic ← Tθ (X)
▷ Extract embeddings via unfrozen
module calls the large language model Gϕ to perform autoreencoder
gressive inference directly from the aligned traffic features,
// Step 2: Alignment Module & Auxiliary Constraint
without relying on hard-coded discrete labels. The full input
2: Halign ← Cω (Ttraffic )
▷ Project to LLM lexical space
sequence Ein of Gϕ is constructed by concatenating the aligned
3: Hpool ← GAP(Halign ) ▷ Sequence-level global average
traffic tokens Halign and the task instruction prompt P:
pooling
Ein = [Halign ; P]
(6)
4: pcls ← Aκ (Hpool ) ▷ Predict auxiliary class distribution
5: ŷ ← arg max(pcls )
▷ Traffic classification prediction
The LLM then autoregressively generates the diagnostic report
// Step 3: Multimodal Construction
Rpred conditioned on this sequence:
6: Ein ← [Halign ; P]
▷ Directly concatenate features and
prompt
Rpred = Gϕ (Ein )
(7)
// Step 4: Cognition Module & Joint Optimization
In the multi-modal report generation task, the correct
7: if training then
identification of the traffic category acts as the foundational
8:
Laux ← − log(pcls,y )
▷ Compute auxiliary
premise for all subsequent behavioral descriptions and evidence
cross-entropy loss
chains. Standard negative log-likelihood (NLL) loss treats
Compute dynamic
9:
PT weights wt : 1 + γ if t ≤ M , else 1
all generated tokens equally, which may lead to the LLM 10:
Lgen ← − T1 t=1 wt log Pϕ,ω,θ (rt | Ein , r<t )
▷
generating fluent but factually incorrect hallucinated reports
Semantic-priority guided loss
if the core category is misidentified. To address this, we 11:
Ltotal ← Lgen + λLaux ▷ End-to-end joint objective
propose a Semantic-Priority Guided Generation Loss. We 12:
Update {θ, ω, κ, ϕ} via AdamW ▷ Jointly optimize all
assign an amplification weight to the prefix tokens of the
modules
target sequence (which correspond to the primary categorical 13: else
decision in the JSON structure) to explicitly force the LLM to 14:
Rpred ← Gϕ (Ein ) ▷ Autoregressive report generation
prioritize classification accuracy during the generative process. 15:
Parse
Rpred
into
JSON
format:
The weighted generation loss over the expert evidence chains
{class, traits, evidence, description, notes}
R = {r1 , r2 , . . . , rT } is formulated as:
16: end if
T
17: return ŷ, Rpred
1X
Lgen = −
wt log Pϕ,ω,θ (rt | Ein , r<t )
(8)
T t=1
class label, and pcls,c is the predicted probability for class
c. During the joint training phase, Laux actively propagates
gradient back through Cω and Tθ , strictly anchoring the
representation space to the identity of a traffic sample.

where r<t = {r1 , . . . , rt−1 } denotes all ground-truth tokens
preceding position t, and wt is the dynamic positional weight
defined as:
(
1 + γ, if t ≤ M
wt =
(9)
1,
otherwise
where M defines the boundary of the critical categorical tokens
at the beginning of the sequence, and γ is the boost weight
factor applied to strictly penalize misclassifications in the
generated text.
Unlike previous paradigms that freeze the traffic encoder,
our mmTraffic framework enables end-to-end multimodal
alignment. The overall objective function integrates both the
token-level generative comprehension and the sequence-level
auxiliary classification constraint:

In summary, the proposed mmTraffic constructs a closed-loop
analysis system from the underlying bit stream to the high-level
forensic report through a perception module (feature extraction),
an alignment module (cross-space mapping with auxiliary
constraint), and a cognition module (logical reconstruction with
semantic-priority guidance). This joint optimization empowers
the LLM to intrinsically understand non-semantic traffic
sequences, ensuring the reliability of the analysis report. To
clearly demonstrate the logical pipeline of the above procedure,
we summarize mmTraffic in Algorithm 1.
V. E XPERIMENTS
A. Experimental Settings

1) Data Preparation: We evaluate the proposed framework
on six publicly available network traffic datasets, covering
Ltotal = Lgen + λLaux
(10)
a wide range of traffic types, application ecosystems, and
where λ is a hyperparameter balancing the auxiliary classifica- encryption protocols. To reduce the impact of class imbalance,
tion task. During training, the parameters of the traffic encoder we apply a category filtering strategy to each dataset: classes
(Tθ ), projection connector (Cω ), auxiliary classification head with fewer than Nmin samples are removed, and classes
(Aκ ), and language model (Gϕ ) are jointly optimized.
exceeding Nmax samples are randomly downsampled to Nmax .

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

8

TABLE II
S TATISTICS OF THE SIX BENCHMARK DATASETS AFTER PREPROCESSING .

Dataset
CrossPlatform-Android
CrossPlatform-iOS
ISCXVPN2016
ISCX-Tor-2016
CSTNet-TLS1.3
USTC-TFC-2016

Classes

Nmin

Nmax

Train

Test

212
196
7
8
120
12

50
50
200
3,000
0
3,000

2,000
3,000
6,000
10,000
6,000
6,000

31,029
29,302
33,600
64,000
37,148
53,112

7,644
7,233
8,400
16,000
9,224
13,276

All datasets are split into training and test sets at an 8:2 ratio.
Statistics of the six datasets after the above preprocessing are
shown in Tables II. Details of each dataset are as follows:
• CrossPlatform-Android and CrossPlatform-iOS [29]:
These two datasets contain mobile application traffic
collected from Android and iOS devices across multiple
countries and network environments, covering 212 and
196 application categories respectively. We set Nmin = 50,
Nmax = 2,000 for Android and Nmax = 3,000 for iOS,
resulting in 38,673 and 36,535 samples after filtering.
• ISCXVPN2016 [11]: This dataset contains application traffic tunneled through VPN connections, covering 7 categories: Browsing, Chat, Email, FTP,
P2P, Streaming, and VoIP. VPN encapsulation adds
an additional encryption layer that obscures applicationlayer signatures. We set Nmin = 200 and Nmax = 6,000,
yielding 42,000 samples.
• ISCX-Tor-2016 [17]: This dataset contains traffic routed
through the Tor anonymous network, covering 8 traffic categories. Tor’s multi-hop encryption substantially reduces
the discriminability of byte-level features, making it one
of the most challenging benchmarks in encrypted traffic
analysis. We set Nmin = 3,000 and Nmax = 10,000,
resulting in 80,000 samples.
• CSTNet-TLS1.3 [19]: This dataset contains web traffic
encrypted exclusively with TLS 1.3, covering 120 website
categories. Since TLS 1.3 removes observable handshake
metadata, certificate-based identification is not applicable.
The class distribution is relatively balanced, so Nmin = 0
and Nmax = 6, 000, yielding 46,372 samples.
• USTC-TFC-2016 [35]: This dataset contains both benign
application traffic and traffic from 12 malware families,
making it the only dataset in our benchmark that includes
adversarial network behavior. We set Nmin = 3,000 and
Nmax = 6,000, resulting in 66,388 samples.
2) Implementation Details: The traffic encoder Tθ is instantiated with NetMamba [34]. Unlike previous decoupled
methods, Tθ is completely unfrozen and fully fine-tuned to
actively capture language-aligned semantic representations.
The alignment connector Cω is implemented as a two-layer
MLP with GELU activation (mlp2x_gelu) and is also
fully fine-tuned, alongside the newly introduced auxiliary
classification head Aκ . The cognitive module Gϕ is instantiated
with Qwen3-1.7B [36] and adapted via Low-Rank Adaptation
(LoRA) [16]. LoRA is applied to all attention and feed-forward
projection modules (specifically <q_proj>, <k_proj>,
<v_proj>, <o_proj>, <gate_proj>, <up_proj>, and

<down_proj>), with an increased rank r = 32, scaling factor
α = 64, and a dropout rate of 0.1. Thus, the parameters of
Tθ , Cω , Aκ , and the LoRA modules of Gϕ are jointly updated
during the end-to-end training.
For the multi-task optimization objectives, the balancing
weight for the auxiliary classification loss is set to λ = 0.3.
For the semantic-priority guided generation loss, we set the
categorical boundary threshold to M = 15 and the boost weight
factor to γ = 5.0, firmly anchoring the text generation to the
physical traffic identity.
All models are trained for 10 epochs using the AdamW [24]
optimizer with a peak learning rate of η = 5 × 10−5 , a weight
decay of 0.01, a linear warmup [12] over the first 10% of
training steps, and a gradient clipping threshold of 1.0. We
utilize BFloat16 [26] mixed-precision and distributed training
via DeepSpeed ZeRO-2 [28]. The per-device batch size is set
to 3 with a gradient accumulation of 8 steps, yielding a global
batch size of 3 × 8 × 5 = 120 across 5 NVIDIA A800 GPUs.
3) Evaluation Metrics: We evaluate mmTraffic from two
complementary perspectives: traffic classification and forensic
report generation. The evaluation metrics include:
• Classification Metrics. We report Accuracy to assess the
traffic identification performance of the perception module,
measured as the proportion of correctly classified samples
over the full test set. We additionally report JSON Validity
Rate (JSON Valid%), the proportion of model outputs
that can be successfully parsed as a valid JSON object
containing all required fields, which reflects whether the
model has learned the structured output format.
• Text Generation Metrics. To assess the quality of the
generated evidence and description fields, we adopt two
complementary metrics: ROUGE-L [18] measures the F1
score of the longest common subsequence (LCS) between
the generated and reference texts, capturing lexical overlap and word-order consistency. BERTScore [37] computes token-level semantic similarity between generated
and reference texts using contextual embeddings from
roberta-large (num_layers=17), loaded from a
local checkpoint to ensure reproducibility. We report
the macro-averaged BERTScore F1 , computed as the
arithmetic mean of per-sample F1 scores (harmonic mean
of token-level precision and recall) over the full test set.
Compared to ROUGE-L, BERTScore is more robust to
lexical paraphrasing and stylistic variation between the
ground-truth anchor (Claude Opus) and the prediction
model (Qwen3-1.7B) [36], and thus a reliable indicator
of semantic fidelity when surface-level wording differs.
• Structural Consistency Metrics. Beyond lexical and
semantic similarity, we evaluate the internal quality of
generated reports using three reference-free metrics, which
are visualized in the radar charts, computed solely over
the model’s generated output, requiring no ground-truth
text for evaluation. Let N denote the number of samples
with valid JSON predictions, and let ei , di denote the
predicted evidence and description fields of the i-th
report, with ci = [ei ; di ] denoting their concatenation.
Evidence-Trait Consistency (ETC) measures whether the
generated evidence text is semantically coherent with

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

9

TABLE III
R ESULTS ON ISCX-T OR -2016, ISCXVPN2016, AND CSTN ET-TLS1.3. N ET M AMBA IS THE UNIMODAL CLASSIFIER (“–” MEANS NO GENERATION );
Z ERO - SHOT LLM FEEDS FEATURES DIRECTLY TO LLM WITHOUT TUNING ; VANILLA FREEZES THE ENCODER WITHOUT AUXILIARY CONSTRAINTS . B OLD
INDICATES THE BEST PER COLUMN WITHIN EACH DATASET GROUP.

Classification

Generation

Acc / JClsAcc%

JSON Valid%

ROUGE-L

BERTScore

ROUGE-L

BERTScore

0.9961
0.0003
0.7092
0.9331

–
100.00%
100.00%
100.00%

–
0.1247
0.6002
0.8192

–
0.8322
0.9217
0.9641

–
0.1164
0.5831
0.7751

–
0.8469
0.9266
0.9481

ISCXVPN2016

NetMamba
Zero-shot LLM
Vanilla
mmTraffic (Ours)

0.9917
0.0004
0.2987
0.9902

–
100.00%
100.00%
100.00%

–
0.1121
0.3597
0.8436

–
0.8290
0.8881
0.9686

–
0.1252
0.2020
0.6975

–
0.8545
0.8679
0.9419

CSTNet-TLS1.3

NetMamba
Zero-shot LLM
Vanilla
mmTraffic (Ours)

0.8474
0.0000
0.0148
0.6448

–
100.00%
100.00%
100.00%

–
0.2675
0.5224
0.7188

–
0.8780
0.9242
0.9538

–
0.1399
0.4346
0.8007

–
0.8492
0.9041
0.9710

Dataset

Method

ISCX-Tor-2016

NetMamba
Zero-shot LLM
Vanilla
mmTraffic (Ours)

the predicted byte-level trait values, verifying that the
model’s reasoning is grounded in the actual traffic features
rather than generating plausible-sounding but ungrounded
observations. It is computed as:

Evidence

Description

correctness in fine-grained settings, as the ground-truth
descriptions across categories share substantial protocollevel vocabulary. This motivates the introduction of
reference-free structural consistency metrics.

N

1 X
ETC =
1[KW(Ti ) ∩ ei ̸= ∅]
N i=1

(11)

B. Main Results

Tables III and IV present the comparison results with
baselines. We report the linear head Accuracy (Acc) for NetMamba, while the JSON Classification Accuracy (JClsAcc%)
extracted directly from the generated natural language reports
for generative models (Zero-shot LLM, Vanilla, and ours).
Evaluation of Classification Performance. NetMamba sets
the upper-bound baseline for specialized unimodal classification.
As observed, the Zero-shot LLM and Vanilla paradigms
suffer a catastrophic drop in classification capability, failing
almost entirely on datasets like CSTNet-TLS1.3 (0.0148) and
CrossPlatform-iOS (0.0058). This collapse demonstrates that
without
joint optimization, the semantic gap between physical
N
1 X
bytes
and
the lexical space is insurmountable. In contrast,
QCR =
1[HasQuant(ci )]
(12)
N i=1
our proposed mmTraffic successfully bridges this gap. By
unfreezing the encoder and applying the auxiliary classification
where HasQuant(·) is true if ci contains any percentage,
head, mmTraffic recovers robust JSON classification perforbyte quantity, multi-digit number, or ordinal descriptor
mance (e.g., reaching 0.9902 on ISCXVPN2016 and 0.8865 on
(high/mid/low), or the keyword ratio.
CrossPlatform-iOS). While there is a slight inherent alignment
Protocol Mention Rate (PMR) measures the proportion
tax compared to the pure linear classifier (e.g., 0.9887 for
of reports that explicitly reference at least one network
NetMamba vs. 0.8624 for mmTraffic on USTC-TFC-2016) due
protocol by name or identifier (e.g., TCP, TLS, HTTP,
to the complexity of autoregressive text generation, it remains
QUIC). Protocol attribution is a fundamental requirement
highly competitive and overwhelmingly surpasses standard
for reports, and a high PMR confirms the model reliably
multimodal baselines (i.e., zero-shot LLM and Vanilla).
grounds its analysis in appropriate protocol context.
Evaluation of Generation Quality. Generating humanN
X
readable
and evidence-grounded reports is the core objective.
1
PMR =
1[P ∩ ci ̸= ∅]
(13) Unimodal classifiers like NetMamba are fundamentally incaN i=1
pable of generating text. The Vanilla manages to produce
where P is a predefined set of protocol keywords (e.g., fluent text but generates severe hallucinations due to its
TCP, TLS, HTTP).
inability to accurately identify the underlying traffic. Conversely,
We note that reference-based metrics such as ROUGE- mmTraffic achieves a JSON validity rate of 100% across
L and BERTScore exhibit insensitivity to classification all datasets, confirming that the LLM has fully mastered
where 1[·] is the indicator function that equals 1 if the
condition holds and 0 otherwise, KW(Ti ) denotes the
union of keyword sets of all predicted traits, and ei denotes
the tokens of the predicted evidence text.
Quantitative Claim Rate (QCR) measures the proportion
of reports containing at least one concrete numerical
observation, such as byte counts, entropy values, or explicit
ordinal descriptors. A high QCR indicates that the model
produces specific, verifiable reports rather than vague
qualitative descriptions. It is computed as:

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

10

TABLE IV
R ESULTS ON C ROSS P LATFORM - I OS, C ROSS P LATFORM -A NDROID , AND USTC-TFC-2016. N ET M AMBA IS THE UNIMODAL CLASSIFIER (“–” MEANS NO
GENERATION ); Z ERO - SHOT LLM FEEDS FEATURES DIRECTLY TO LLM WITHOUT TUNING ; VANILLA FREEZES THE ENCODER WITHOUT AUXILIARY
CONSTRAINTS . B OLD INDICATES THE BEST PER COLUMN WITHIN EACH DATASET GROUP.

Classification

Generation

Acc / JClsAcc%

JSON Valid%

ROUGE-L

BERTScore

ROUGE-L

BERTScore

CrossPlatform-iOS

NetMamba
Zero-shot LLM
Vanilla
mmTraffic (Ours)

0.9060
0.0000
0.0058
0.8865

–
100.00%
100.00%
100.00%

–
0.1962
0.2218
0.6880

–
0.8509
0.8591
0.9387

–
0.1268
0.1255
0.5972

–
0.8503
0.8535
0.9283

CrossPlatform-Android

NetMamba
Zero-shot LLM
Vanilla
mmTraffic (Ours)

0.9104
0.0000
0.0027
0.8654

–
100.00%
100.00%
100.00%

–
0.0000
0.2107
0.5482

–
0.0000
0.8661
0.9060

–
0.0000
0.1283
0.5605

–
0.8405
0.8542
0.9299

USTC-TFC-2016

NetMamba
Zero-shot LLM
Vanilla
mmTraffic (Ours)

0.9887
0.0000
0.7002
0.8624

–
100.00%
100.00%
100.00%

–
0.1386
0.6383
0.8853

–
0.8377
0.9272
0.9769

–
0.1365
0.5447
0.7714

–
0.8536
0.9163
0.9527

Dataset

Method

Evidence

Description

Classification Accuracy (JClsAcc)

 5 D G D U  & K D U W  $ Q D O \ V L V  R Q  . H \  0 H W U L F V
the structured output format. On evidence and description
 , 6 & ;  7 R U     
 , 6 & ; 9 3 1    
 & 3  $ Q G U R L G
generation, mmTraffic demonstrates overwhelming superiority.
 $ F F
 $ F F
 $ F F
For example, it achieves an Evidence ROUGE-L of 0.8436
   
   
   
   
   
   
 ( Y  % 6
 3 0 5
 ( Y  % 6
 3 0 5
 ( Y  % 6
on ISCXVPN2016 and a Description BERTScore of 0.9710  3 0 5
   
   
   
   
   
   
   
   
   
on CSTNet-TLS1.3. Across all six datasets, the BERTScore
consistently remains above 0.90, proving that the generated ev ' H V F  % 6
 4 & 5
 ' H V F  % 6
 4 & 5
 ' H V F  % 6
idence and behavioral descriptions maintain rigorous semantic  4 & 5
alignment with the ground-truth expert annotations.
 ( 7 &
 ( 7 &
 ( 7 &
 2 X U V
 9 D Q L O O D  0 / 0
Evaluation of Structural Consistency. A critical observation in multimodal traffic analysis is the ”fluency trap”: models
Fig. 5. Analysis on Structural Consistency Metrics. The semantic-priority
like Vanilla MLM might achieve moderate text generation constraints in mmTraffic ensure high logical rigor.
metrics (e.g., Ev-BS and Desc-BS) by memorizing common
vocabulary, even when their classification accuracy (Acc)
Ablation Trajectory (ISCX-Tor-2016)
Ablation Trajectory (ISCXVPN2016)
Ours
V3
V3
Average ROUGE-L
Average ROUGE-L
1.00
1.0
completely collapses—as starkly visible in the ISCXVPN2016
Ours
Average BERTScore
Average BERTScore
V2
V2
V3
V3 Ours 0.9
0.95
and CP-Android radar charts. This reveals a fundamental
Ours
0.90
0.8
V2
limitation of reference-based metrics in forensics—lexical
0.85
0.7
V2
overlap does not guarantee factual correctness. The radar
0.80
0.6
0.75
0.5
charts in Figure 5 provide a comprehensive picture of logical
V1
0.70
0.4
V1
rigorousness across six key dimensions. While Vanilla MLM
V1
0.65
0.3
V1
exhibits severely distorted performance profiles , our proposed
0.60
0.2
0.5
0.6
0.7
0.8
0.9
0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
Average Generation Quality Score (ROUGE-L / BERTScore) Average Generation Quality Score (ROUGE-L / BERTScore)
mmTraffic maintains a robust, near-symmetrical shape that
pushes towards the outer boundaries (1.0) across all evaluated
datasets. Driven by our semantic-priority guided generation Fig. 6. Ablation analysis on ISCX-Tor-2016 and ISCXVPN2016, with respect
to the classification and generation metrics for four variants from V1 to V4.
mechanism, mmTraffic ensures that its high structural consistency (ETC, QCR, PMR) is strictly anchored in correct
traffic identification, effectively eliminating the multimodal (4) V4 (mmTraffic Full): incorporating the semantic-priority
hallucinations prevalent in unconstrained architectures.
guided generation mechanism (Lgen ).
Breaking the Modality Barrier via Joint Optimization.
C. Ablation Study
The initial transition from V1 to V2 in Figure 6 reveals
To isolate the contribution of each proposed component in the fundamental bottleneck of cross-modal traffic analysis.
mmTraffic, we conduct an ablation study across two distinct In the Vanilla MLLM (V1) setting, the framework suffers a
domains: ISCX-Tor-2016 and ISCXVPN2016. As illustrated in catastrophic failure on ISCXVPN2016 (accuracy at 0.2987)
Figure 6, we systematically evaluate four configurations: (1) V1 and struggles at 0.7092 on ISCX-Tor-2016. Because raw cryp(Vanilla MLLM): freezing the NetMamba encoder and relying tographic traffic sequences lack the natural lexical alignments
solely on the standard Negative Log-Likelihood (NLL) loss; (2) found in visual-text data, a frozen encoder fundamentally fails
V2 (+ Unfrozen): unfreezing the traffic encoder for end-to-end to project these non-semantic bytes into the LLM’s sophistijoint optimization; (3) V3 (+ Auxiliary Head): introducing cated cognitive space. Unfreezing the encoder (+ Unfrozen)
the auxiliary classification head (Laux ) to the latent space; and opens the gradient bottleneck, allowing the perceptual backbone

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

11

TABLE V
ISCX-T OR -2016 FOR SAMPLE #6227: MM T RAFFIC CORRECTLY IDENTIFIES
THE CLASS . E VIDENCE AND DESCRIPTION FIELDS ARE ABBREVIATED .
G REEN MEANS CORRECTLY INTERPRETED KEY CONTENT.

TABLE VII
USTC-TFC-2016 FOR SAMPLE #11786: MM T RAFFIC CORRECTLY
IDENTIFIES THE CLASS . E VIDENCE AND DESCRIPTION FIELDS ARE
ABBREVIATED . G REEN MEANS CORRECTLY INTERPRETED KEY CONTENT.

Field

mmTraffic (Ours)

Ground Truth

Field

mmTraffic(Ours)

Ground Truth

Class

CHAT ✓

CHAT

Class

Outlook ✓

Outlook

Traits

has tls: true
has http: false
ascii: low
entropy: mid
zero pad: mid

has tls: true
has http: false
ascii: mid
entropy: mid
zero pad: mid

Traits

has tls: true
has http: false
ascii: low
entropy: mid
zero pad: mid

has tls: true
has http: false
ascii: low
entropy: high
zero pad: low

Evidence

(1) TLS record header detected, in- (1) TLS record header detected, indidicating an encrypted TLS session.
cating an encrypted TLS session.
(2) TCP dominant (100%), consistent (2) TLS dominant (100%), consistent
with Tor CHAT profile.
with Tor CHAT profile.
(3) Unlike Tor VOIP (codec-driven tim- (3) Unlike Tor VOIP (codec-driven timing), Tor CHAT has irregular human- ing), Tor CHAT has irregular humanconversation-driven timing. . . .
conversation-driven timing. . . .

Evidence

(1) TLS record header detected, indicating an encrypted TLS session.
(2) TLS dominant (100%), consistent
with Outlook profile.
(3) Unlike Gmail (HTTP/2 and QUIC),
Outlook uses MAPI protocol. . . .

(1) TLS record header detected, indicating an encrypted TLS session.
(2) Low ASCII with high entropy:
encrypted payload.
(3) Low zero-padding: sustained bulk
data transfer.
(4) TLS dominant (100%). . . .

Description

TLS record headers present, indicating
encrypted transport. Instant messaging
and chat protocols (AIM, ICQ, Facebook Chat, Hangouts, Skype Chat)
tunneled through Tor onion routing.
Dominant protocol: TCP (100%). . . .

TLS record headers present, indicating
encrypted transport. Instant messaging
and chat protocols (AIM, ICQ, Facebook Chat, Hangouts, Skype Chat)
tunneled through Tor onion routing.
Dominant protocol: TLS (100%).

Description

TLS record headers present, indicating encrypted transport. Microsoft
Outlook email client using HTTPS
and MAPI. Dominant protocol: TLS
(100%). . . .

TLS record headers alongside highentropy payload confirm encrypted
communication. Microsoft Outlook
email client using HTTPS and MAPI.
Dominant protocol: TLS (100%).

Notes

Notes

Chat over Tor hides who is communicating with whom; message content
may still be visible at exit nodes if not
end-to-end encrypted.

Chat over Tor provides metadata
anonymity; message content may still
be visible at exit nodes if not end-toend encrypted.

Generally benign; verify connections
go to Microsoft ASN; anomalous sync
volumes may indicate data exfiltration.

Generally benign; verify connections
go to Microsoft ASN; anomalous sync
volumes or off-hours activity may indicate data exfiltration via email.

TABLE VI
CSTN ET-TLS1.3 FOR SAMPLE #350: MM T RAFFIC CORRECTLY IDENTIFIES
THE CLASS . E VIDENCE AND DESCRIPTION FIELDS ARE ABBREVIATED .
G REEN MEANS CORRECTLY INTERPRETED KEY CONTENT.
Field

mmTraffic (Ours)

Ground Truth

Class

Steam ✓

Steam

Traits

has tls: true
has http: false
ascii: mid
entropy: high
zero pad: low

has tls: true
has http: false
ascii: low
entropy: high
zero pad: low

Evidence

(1) TLS record header detected, indicating an encrypted TLS session.
(2) High Shannon entropy: encrypted
or compressed payload.
(3) Low zero-padding: sustained bulk
data transfer. . . .

(1) TLS record header detected, indicating an encrypted TLS session.
(2) Low ASCII with high entropy:
encrypted payload.
(3) Low zero-padding: sustained bulk
data transfer.
(4) TCP dominant (84.2%). . . .

Description

TLS record headers alongside high- TLS record headers alongside highentropy payload confirm encrypted entropy payload confirm encrypted
communication. Valve Steam gaming communication. Valve Steam gaming
platform for game downloads, updates, platform for game downloads, updates,
and multiplayer services over TLS 1.3. and multiplayer services over TLS 1.3.
Large avg. packet (858 bytes). . . .
TCP dominant (84.2%). . . .

Notes

Game distribution platform; monitor
for Steam account phishing; Workshop
mods can contain malicious code.

Game distribution platform; game
downloads are very large; monitor for
Steam account phishing.

hard, discriminative boundaries before the features ever reach
the LLM. This explicit concept anchoring effectively resolves
perceptual ambiguity, propelling the classification accuracy
to 0.9312 on ISCX-Tor-2016 and 0.9819 on ISCXVPN2016,
while maintaining strong generative performance.
Synergistic Grounding via Semantic-Priority Generation.
The final transition to mmTraffic (Full) demonstrates that
our semantic-priority generation loss (Lgen ) is not merely a
linguistic constraint, but a mechanism for cognitive synergy. In
standard unconstrained generation (V3), all tokens are treated
equally, leaving the model susceptible to generating fluent but
ungrounded priors. By dynamically assigning a heavy penalty
weight to the categorical prefix tokens, mmTraffic forces the
LLM to commit strictly to a physical traffic identity first.
Remarkably, rather than acting as a restrictive trade-off, this
strong semantic grounding mechanism stabilizes the reasoning
chain, pushing the final classification accuracy to its peak
across both domains (0.9331 on Tor and 0.9902 on VPN) and
maximizing the structural alignment of the generated evidence
(Average BERTScore reaches 0.9561 on Tor and 0.9552 on
VPN). This confirms that forcing logical rigorousness inherently
enhances the overall multimodal reasoning reliability.

to dynamically adapt its feature extraction guided by the LLM’s
generation objective. This mechanistic bridge yields a massive
concurrent leap in both text fidelity (e.g., Average ROUGE-L D. Qualitative Evaluation on Traffic Reasoning
Despite the quantitative evaluations, this section presents
on Tor rises from 0.59 to 0.78) and classification accuracy
qualitative analysis of traffic reasoning on three datasets: ISCX(0.8674 on Tor and 0.9751 on VPN).
Shaping the Latent Space with Auxiliary Constraints. Tor-2016, CSTNet-TLS1.3, and USTC-TFC-2016.
While unfreezing the encoder bridges the modality gap, relying
Qualitative Evaluation. Tables V, VI, and VII present
exclusively on the LLM’s autoregressive text-generation loss high-quality correct classifications across three datasets: ISCXprovides weak and implicit supervision, which is insufficient to Tor-2016, CSTNet-TLS1.3, and USTC-TFC-2016. Despite the
disentangle highly overlapping encrypted traffic patterns. The diversity of encryption contexts, mmTraffic consistently procritical inflection point occurs in V3 with the introduction of duces forensically grounded reports that accurately characterize
the auxiliary classification head. By directly penalizing misclas- the underlying traffic behavior. The CHAT case from ISCXsifications at the feature bottleneck, Laux explicitly reshapes Tor-2016 (sample #6227) is particularly illustrative. Although
the continuous latent space. It forces the encoder to establish the predicted ascii bucket diverges slightly from the ground

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

12

TABLE VIII
ISCX-T OR -2016 FOR SAMPLE #15750: MM T RAFFIC CORRECTLY IDENTIFIES THE VIDEO CLASS WHILE Vanilla VLM MISCLASSIFIES IT AS BROWSING.
E VIDENCE AND DESCRIPTION FIELDS ARE ABBREVIATED . G REEN AND R ED MEAN CORRECT AND WRONG INTERPRETATIONS .
Field

mmTraffic (Ours)

Vanilla VLM

Ground Truth

Class

VIDEO ✓

BROWSING %

VIDEO

Evidence

(1) Video streaming services (YouTube, Vimeo) tunneled via Tor
onion routing.
(2) High throughput (49.8 MB/s) indicates active data exchange.
(3) Sustained download dominant over upload, consistent with video
consumption. . . .

(1) TLS record header detected, indicating encrypted session.
(2) High zero-padding: short flow with small payload.
(3) TCP dominant (100%), consistent with HTTPS browsing profile.
...

(1) TCP dominant (100%), consistent with VIDEO profile.
(2) Unlike Tor AUDIO (moderate throughput), VIDEO requires
significantly higher bandwidth.
(3) Unlike Tor BROWSING (bursty), VIDEO maintains sustained highthroughput download. . . .

Description

Mixed entropy and ASCII across packet slices. Video streaming
services (youtube.com, vimeo.com) tunneled via Tor onion routing.
TCP dominant. High throughput (498 KB/s). . . .

TLS record headers indicate encrypted transport. HTTPS/SSL web
browsing tunneled through Tor hides both location and activities.
High zero-padding suggests background activity. . . .

Mixed entropy and ASCII across packet slices. Video streaming
services (YouTube HTML5, YouTube Flash, Vimeo) tunneled through
Tor. Dominant protocol: TCP (100%).

TABLE IX
CSTN ET-TLS1.3 FOR SAMPLE #4728: MM T RAFFIC CORRECTLY IDENTIFIES THE A D O B E WHILE Vanilla VLM MISCLASSIFIES IT AS B A I D U . C O M . U NDER
TLS 1.3, BYTE - LEVEL FEATURES ARE NEARLY IDENTICAL ACROSS ALL WEBSITES . G REEN AND R ED MEAN CORRECT AND WRONG INTERPRETATIONS .
Field

mmTraffic (Ours)

Vanilla VLM

Ground Truth

Class

Adobe ✓

baidu.com %

Adobe

Evidence

(1) TLS record header detected.
(2) High Shannon entropy: encrypted or binary payload.
(3) Low zero-padding: sustained bulk data transfer. . . .

(1) TLS record header detected.
(2) High zero-padding: short flow with small payload.
(3) TCP dominant (68.5%), consistent with Baidu’s search and CDN
infrastructure. . . .

(1) TLS record header detected.
(2) Low ASCII with high entropy: encrypted payload.
(3) TLS dominant (55.6%), consistent with Adobe profile. . . .

Description

TLS record headers alongside high-entropy payload confirm encrypted
communication. Adobe creative software, cloud services, and
document management platform over TLS 1.3. . . .

TLS record headers indicate active encrypted communication. Large
volume of bulk control-plane packets over TCP. Baidu search and
CDN infrastructure. . . .

TLS record headers alongside high-entropy payload confirm encrypted
communication. Adobe creative software, cloud services, and
document management platform over TLS 1.3. . . .

TABLE X
USTC-TFC-2016 FOR SAMPLE #10195: MM T RAFFIC CORRECTLY IDENTIFIES THE G EODO MALWARE FLOW WHILE Vanilla VLM MISCLASSIFIES IT AS
H TBOT. B OTH ARE HTTP- BASED BOTNETS WITH SIMILAR BYTE SIGNATURES . G REEN AND R ED MEAN CORRECT AND WRONG INTERPRETATIONS .
Field

mmTraffic (Ours)

Vanilla VLM

Ground Truth

Class

Geodo ✓

Htbot %

Geodo

Evidence

(1) High Shannon entropy: encrypted or binary payload.
(2) Low zero-padding: sustained bulk data transfer.
(3) TCP dominant (100%).
(4) Unlike Zeus (banking only), Geodo also performs spam relay.

(1) HTTP tokens (GET/POST) indicate plaintext HTTP requests.
(2) High ASCII: plaintext application-layer content.
(3) Low zero-padding: sustained bulk data transfer. . . .

(1) High zero-padding: short flow, small payload.
(2) TCP dominant (100%).
(3) Unlike Zeus (banking only), Geodo also performs spam relay. . . .

Description

Mixed entropy and ASCII characteristics. Geodo/Emotet banking
trojan and email spam botnet. Dominant protocol: TCP (100%). . . .

HTTP method tokens and readable ASCII confirm plaintext botnetdriven web scraping or C&C command execution (Htbot). Low
throughput suggests sparse traffic. . . .

Mixed entropy and ASCII characteristics. Geodo/Emotet banking
trojan and email spam botnet. Dominant protocol: TCP (100%).

truth, the generated description correctly identifies the traffic
Qualitative Effect of Joint Optimization. Tables VIII, IX,
as instant messaging protocols tunneled through Tor onion and X present cases where mmTraffic correctly identifies the
routing, accurately attributing it to AIM, ICQ, Facebook Chat, traffic category while the Vanilla VLM produces an erroneous
Hangouts, and Skype Chat services. This suggests that the classification, revealing how joint optimization resolves the
joint optimization between the traffic encoder and the LLM semantic gap that a frozen encoder cannot bridge. Crucially, the
effectively compensates for trait-level uncertainty by grounding misclassifications are not random: the predicted category shares
generation in a semantically aligned feature space. A similar substantial byte-level similarity with the ground truth. On ISCXpattern is observed in the Outlook case from USTC-TFC- Tor-2016, VIDEO is confused with BROWSING because both
2016 (sample#11786). While the predicted entropy and zero- exhibit similar Tor-tunneled TCP flows and differ primarily
padding buckets differ from the ground truth, the generated in sustained throughput consistency rather than observable
description correctly identifies the traffic as Microsoft Outlook byte patterns. On CSTNet-TLS1.3, Adobe is misidentified
using HTTPS and MAPI, and accurately distinguishes it as baidu.com because TLS 1.3 eliminates all certificate
from Gmail by referencing Outlook’s exclusive connection metadata, leaving both flows with nearly identical TLS record
to Microsoft infrastructure. This decoupling between trait headers and entropy profiles that are indistinguishable at
accuracy and description quality demonstrates that the auxiliary the byte level with a frozen encoder. On USTC-TFC-2016,
classification head enforces categorical boundaries in the latent Geodo is confused with Htbot because both are HTTP-based
space, anchoring the LLM’s generation to the correct traffic botnets relying on similar C&C communication patterns. This
identity even when individual byte-level features are imprecise. systematic pattern demonstrates that a frozen encoder fails
The Steam case from CSTNet-TLS1.3 (sample #350) further to project fine-grained categorical boundaries into the LLM’s
reinforces this observation: under TLS 1.3 where all flows lexical space. By contrast, mmTraffic allows gradient feedback
share identical encryption overhead, mmTraffic produces a from the auxiliary classification head to actively reshape the
platform-specific description referencing Valve Steam’s game encoder’s feature space, forcing it to learn language-aligned
downloads and multiplayer services, going beyond what raw representations that carry explicit categorical semantics. The
byte features alone could support.
downstream effect is consistent: without joint optimization, the

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

13

TABLE XI
ISCX-T OR -2016 FOR SAMPLE #6622: MM T RAFFIC FAILS TO CLASSIFY.
R ED MEANS WRONG INTERPRETATIONS IN KEY SEMANTICS .

TABLE XIII
USTC-TFC-2016 FOR SAMPLE #4090: MM T RAFFIC FAILS TO CLASSIFY.
R ED MEANS WRONG INTERPRETATIONS IN KEY SEMANTICS .

Field

mmTraffic (Ours)

Ground Truth

Field

mmTraffic (Ours)

Ground Truth

Class

BROWSING %

FILE-TRANSFER

Class

Geodo %

Htbot

Traits

has tls: false
has http: false
ascii: low
entropy: mid
zero pad: mid

has tls: false
has http: false
ascii: mid
entropy: low
zero pad: mid

Traits

has tls: false
has http: false
ascii: high
entropy: low
zero pad: mid

has tls: false
has http: false
ascii: high
entropy: low
zero pad: mid

Evidence

(1) TCP dominant (100%), consistent
with profile.
(2) Unlike direct HTTPS browsing,
Tor browsing shows only Tor relay
IPs.
(3) More bursty than Tor AUDIO or
VOIP. . . .

(1) TCP dominant (100%), consistent
with FILE-TRANSFER profile.
(2) Unlike Tor P2P (bidirectional),
FILE-TRANSFER is predominantly
unidirectional.
(3) FILE-TRANSFER shows sustained
throughput vs Tor BROWSING (bursty
with idle gaps). . . .

Evidence

(1) High ASCII with low entropy:
repetitive plaintext content.
(2) DNS dominant (100%), consistent
with profile.
(3) Unlike Zeus (banking only), Geodo
also performs spam relay. . . .

(1) High ASCII with low entropy:
repetitive plaintext content.
(2) DNS dominant (100%), consistent
with Htbot profile.
(3) Unlike Miuref (click fraud), Htbot
focuses on C&C command execution.

Description

HTTPS/SSL web browsing tunneled
through Tor onion routing, including
both direct Tor Browser usage and
gateway-proxied SSL browsing. Dominant protocol: TCP. . . .

Mixed entropy and ASCII characteristics. File transfer protocols (FTP,
SFTP, Skype file transfer) tunneled
through Tor onion routing. Dominant
protocol: TCP (100%).

Substantial readable ASCII content Substantial readable ASCII content
present. Geodo/Emotet banking tro- present. HTTP-based botnet using
jan and email spam botnet. Dominant web proxies for C&C (Htbot). Domiprotocol: DNS (89.1%). Uses HTTP- nant protocol: DNS (100%).
based C&C more frequently than Zeus.

Notes

Tor browsing provides strong
anonymity; exit node traffic is
unencrypted unless HTTPS is used
end-to-end.

File transfer over Tor hides source and
destination; commonly used to transfer
sensitive documents.

High-risk banking trojan; block known
Geodo C&C IPs; inspect SMTP traffic
for spam relay.

Description

Notes

Monitor for HTTP requests with unusual headers; correlate with known
Htbot infrastructure.

TFC-2016, Htbot is misclassified as Geodo because both
are DNS-based botnets with nearly identical ASCII ratios,
TABLE XII
CSTN ET-TLS1.3 FOR SAMPLE #6404: MM T RAFFIC FAILS TO CLASSIFY.
entropy profiles, and protocol distributions. In all three cases,
R ED MEANS WRONG INTERPRETATIONS IN KEY SEMANTICS .
the misclassification originates at the perceptual stage: even
with
end-to-end joint optimization, the encoder fails to establish
Field
mmTraffic (Ours)
Ground Truth
sufficiently
discriminative boundaries between classes that share
Class
arXiv %
Semantic Scholar
highly
similar
byte-level signatures. The erroneous categorical
Traits
has tls: true
has tls: true
has http: false
has http: false
prediction
then
propagates into the cognitive module, producing
ascii: low
ascii: mid
reports that are internally consistent with the predicted class
entropy: high
entropy: high
zero pad: mid
zero pad: mid
rather than the ground truth. Despite the prediction errors, this
Evidence
(1) TLS record header detected.
(1) TLS record header detected.
transparency remains an operational advantage: the cognitive
(2) Low ASCII with high entropy: (2) High Shannon entropy: encrypted
encrypted payload.
payload.
module faithfully reflects the perceptual judgment, making
(3) TCP dominant (96.8%), consistent (3) TCP dominant (97.9%), consistent
the error visible and traceable in the generated report rather
with arXiv profile.
with Semantic Scholar profile.
(4) Similar PDF download pattern to (4) More API-driven than traditional
than silently absorbed into an opaque label. For a network
ACM and IEEE. . . .
academic publishers. . . .
analyst, the evidence chain in the generated report can be
Description TLS record headers alongside high- TLS record headers alongside highentropy payload confirm encrypted entropy payload confirm encrypted
independently verified against the raw traffic, and discrepancies
communication. arXiv open-access communication. Semantic Scholar AIbetween the reported behavior and observed network activity
academic preprint repository for powered academic paper search and
physics, math, and CS over TLS 1.3. knowledge graph over TLS 1.3. Large
serve as a natural signal that the classification may warrant
Large avg. packet (925 bytes). . . .
avg. packet (964 bytes). . . .
further investigation. In security-sensitive applications such as
Notes
Open academic repository; monitor for Allen Institute AI-operated academic
automated bulk downloading indicating search; open access focus means fewer
malware triage, encrypted traffic auditing, and network incident
research scraping bots.
paywall authentication flows.
response, both high-fidelity generation under correct perception
and transparent failure under incorrect perception represent a
practical step toward interpretable traffic analysis.
generated reports describe the wrong traffic identity, producing
Paradigm, Benchmark and Evaluation. While mmTraffic
forensically plausible but factually incorrect outputs.
demonstrates strong performance across diverse encrypted
traffic benchmarks, several aspects of the current design require
E. Limitation Analysis
further investigation. The tight coupling between the perceptual
Failure Cases. Tables XI, XII, and XIII present failure and cognitive layers also means that the traffic reasoning
cases where mmTraffic produces an incorrect classification. quality is inherently linked to the reliability of the traffic
On ISCX-Tor-2016, FILE-TRANSFER is misclassified as encoder. Exploring mechanisms that allow the cognitive layer
BROWSING because both categories produce similar TCP to express uncertainty or partially recover from perceptual errors
flows under Tor multi-hop encryption, without an observable represents a promising direction for future work. Additionally,
protocol marker to distinguish sustained file transfer from bursty the current benchmark construction pipeline relies on Claude
web browsing. On CSTNet-TLS1.3, Semantic Scholar Opus to generate reference reports from structured traffic
is misclassified as arXiv because both are open-access features. Although this pipeline can produce high-quality
academic platforms that share nearly identical TLS 1.3 byte annotations, its scalability to open-world applications with
signatures, making them fundamentally indistinguishable at new datasets or emerging traffic categories may be limited.
the byte level without application-layer metadata. On USTC- Finally, a more comprehensive traffic reasoning evaluation

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2015

protocol is still a worthwhile avenue.
VI. C ONCLUSION AND F UTURE W ORK
This paper addresses multi-modal traffic reasoning for
the first time, successfully bridging the gap between highprecision encrypted traffic classification and human-readable
forensic report generation. By developing the foundational
Byte-Grounded Traffic Description benchmark, i.e., BGTD and
proposing a jointly optimized multi-modal traffic reasoning
architecture with large language model (LLM), i.e., mmTraffic,
we transform encrypted traffic analysis from a black-box
classification paradigm to an auditable generative paradigm
towards explainable traffic interpretations. Unlike previous
decoupled pipelines that freeze the traffic encoder, mmTraffic
actively unfreezes the encoder and trains it synergistically with
the LLM. Extensive evaluations across six diverse benchmarks
demonstrate that mmTraffic achieves high-fidelity, evidencegrounded traffic report generation, while maintaining highly
competitive classification accuracy, confirming its success in
resolving the semantic gap between physical network bytes
and human-understandable concepts.
In future work, one key direction is to optimize inference
latency to support real-time flow analytics and introduce
uncertainty quantification to allow the cognitive layer to
explicitly handle low-confidence perceptual predictions in
adversarial scenarios. Furthermore, a more scalable automated
annotation process to efficiently extend the framework to emerging cryptographic protocols and open-world traffic categories
remains a worthwhile direction.
R EFERENCES
[1] G. Aceto, D. Ciuonzo, A. Montieri, and A. Pescapé, “Distiller: Encrypted
traffic classification via multimodal multitask deep learning,” Journal of
Network and Computer Applications, vol. 183, p. 102985, 2021.
[2] E. Aghaei, X. Niu, W. Shadid, and E. Al-Shaer, “Securebert: A domainspecific language model for cybersecurity,” in international conference
on security and privacy in communication systems, 2022, pp. 39–56.
[3] J.-B. Alayrac, J. Donahue, P. Luc, A. Miech, I. Barr, Y. Hasson, K. Lenc,
A. Mensch, K. Millican, M. Reynolds et al., “Flamingo: a visual language
model for few-shot learning,” NeurIPS, pp. 23 716–23 736, 2022.
[4] Anonymous, “Semantic-driven interpretable deep multi-modal hashing
for large-scale multimedia retrieval,” IEEE Transactions on Multimedia,
vol. 23, 2021.
[5] A. B. Arrieta, N. Dı́az-Rodrı́guez, J. Del Ser, A. Bennetot, S. Tabik,
A. Barbado, S. Garcı́a, S. Gil-López, D. Molina, R. Benjamins et al.,
“Explainable artificial intelligence (xai): Concepts, taxonomies, opportunities and challenges toward responsible ai,” Information fusion, vol. 58,
pp. 82–115, 2020.
[6] Y. Chen and Y. Wang, “Mpaf: Encrypted traffic classification with multiphase attribute fingerprint,” IEEE Transactions on Information Forensics
and Security, vol. 19, pp. 7091–7105, 2024.
[7] T. Cui, X. Lin, S. Li, M. Chen, Q. Yin, Q. Li, and K. Xu, “Trafficllm:
Enhancing large language models for network traffic analysis with generic
traffic representation,” arXiv preprint arXiv:2504.04222, 2025.
[8] W. Dai, J. Li, D. Li, A. Tiong, J. Zhao, W. Wang, B. Li, P. N. Fung, and
S. Hoi, “Instructblip: Towards general-purpose vision-language models
with instruction tuning,” NeurIPS, pp. 49 250–49 267, 2023.
[9] R. Dingledine, N. Mathewson, and P. Syverson, “Tor: The secondgeneration onion router,” 2004.
[10] W. Dong, J. Yu, X. Lin, G. Gou, and G. Xiong, “Deep learning and pretraining technology for encrypted traffic classification: A comprehensive
review,” Neurocomputing, vol. 617, p. 128444, 2025.
[11] G. Draper-Gil, A. H. Lashkari, M. S. I. Mamun, and A. A. Ghorbani,
“Characterization of encrypted and vpn traffic using time-related,” in
ICISSP, 2016, pp. 407–414.

14

[12] P. Goyal, P. Dollár, R. Girshick, P. Noordhuis, L. Wesolowski, A. Kyrola,
A. Tulloch, Y. Jia, and K. He, “Accurate, large minibatch sgd: Training
imagenet in 1 hour,” arXiv preprint arXiv:1706.02677, 2017.
[13] A. Gu and T. Dao, “Mamba: Linear-time sequence modeling with
selective state spaces,” in First conference on language modeling, 2024.
[14] W. Guo, Y. Zhang, X. Cai, L. Meng, J. Yang, and X. Yuan, “Ld-man:
Layout-driven multimodal attention network for online news sentiment
recognition,” IEEE Transactions on Multimedia, 2020.
[15] G. Han, M. Lin, Z. Li, H. Zhao, and S. Kwong, “Text-to-image person reidentification based on multimodal graph convolutional network,” IEEE
Transactions on Multimedia, vol. 26, 2024.
[16] E. J. Hu, Y. Shen, P. Wallis, Z. Allen-Zhu, Y. Li, S. Wang, L. Wang,
W. Chen et al., “Lora: Low-rank adaptation of large language models.”
Iclr, 2022.
[17] A. H. Lashkari, G. D. Gil, M. S. I. Mamun, and A. A. Ghorbani,
“Characterization of tor traffic using time based features,” in ISSP, vol. 2,
2017, pp. 253–262.
[18] C.-Y. Lin, “Rouge: A package for automatic evaluation of summaries,”
in Text summarization branches out, 2004, pp. 74–81.
[19] X. Lin, G. Xiong, G. Gou, Z. Li, J. Shi, and J. Yu, “Et-bert: A
contextualized datagram representation with pre-training transformers
for encrypted traffic classification,” in Proceedings of the ACM Web
Conference 2022, 2022.
[20] H. Liu, C. Li, Q. Wu, and Y. J. Lee, “Visual instruction tuning,” NeurIPS,
vol. 36, pp. 34 892–34 916, 2023.
[21] J. Liu, C. Liu, P. Zhou, R. Lv, K. Zhou, and Y. Zhang, “Is chatgpt a
good recommender? a preliminary study,” arXiv, 2023.
[22] L. Liu, R. Li, Q. Li, M. Hou, Y. Jiang, and M. Xu, “Flowletformer:
Network behavioral semantic aware pre-training model for traffic
classification,” arXiv preprint arXiv:2508.19924, 2025.
[23] Y. Liu, W. Wei, D. Peng, X.-L. Mao, Z. He, and P. Zhou, “Depth-aware
and semantic guided relational attention network for visual question
answering,” IEEE Transactions on Multimedia, 2022.
[24] I. Loshchilov and F. Hutter, “Decoupled weight decay regularization,”
arXiv preprint arXiv:1711.05101, 2017.
[25] S. M. Lundberg and S.-I. Lee, “A unified approach to interpreting model
predictions,” NeurIPS, vol. 30, 2017.
[26] P. Micikevicius, S. Narang, J. Alben, G. Diamos, E. Elsen, D. Garcia,
B. Ginsburg, M. Houston, O. Kuchaiev, G. Venkatesh et al., “Mixed
precision training,” arXiv preprint arXiv:1710.03740, 2017.
[27] A. Radford, J. W. Kim, C. Hallacy, A. Ramesh, G. Goh, S. Agarwal,
G. Sastry, A. Askell, P. Mishkin, J. Clark et al., “Learning transferable
visual models from natural language supervision,” in ICML, 2021.
[28] S. Rajbhandari, J. Rasley, O. Ruwase, and Y. He, “Zero: Memory
optimizations toward training trillion parameter models,” in SC20:
international conference for high performance computing, networking,
storage and analysis. IEEE, 2020, pp. 1–16.
[29] J. Ren, D. Dubois, and D. Choffnes, “An international view of privacy
risks for mobile apps,” Tech. Rep, 2019.
[30] M. T. Ribeiro, S. Singh, and C. Guestrin, “Why should i trust you?”
explaining the predictions of any classifier,” in ACM SIGKDD, 2016.
[31] R. R. Selvaraju, M. Cogswell, A. Das, R. Vedantam, D. Parikh, and
D. Batra, “Grad-cam: Visual explanations from deep networks via
gradient-based localization,” in ICCV, Oct 2017.
[32] M. Shen, J. Wu, K. Ye, K. Xu, G. Xiong, and L. Zhu, “Robust detection of
malicious encrypted traffic via contrastive learning,” IEEE Transactions
on Information Forensics and Security, vol. 20, pp. 4228–4242, 2025.
[33] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez,
Ł. Kaiser, and I. Polosukhin, “Attention is all you need,” Advances in
neural information processing systems, vol. 30, 2017.
[34] T. Wang, X. Xie, W. Wang, C. Wang, Y. Zhao, and Y. Cui, “Netmamba:
Efficient network traffic classification via pre-training unidirectional
mamba,” arXiv preprint arXiv:2405.11449, 2024.
[35] W. Wang, M. Zhu, X. Zeng, X. Ye, and Y. Sheng, “Malware traffic
classification using convolutional neural network for representation
learning,” in ICOIN, 2017, pp. 712–717.
[36] A. Yang, A. Li, B. Yang, B. Zhang, B. Hui, B. Zheng, B. Yu, C. Gao,
C. Huang, C. Lv et al., “Qwen3 technical report,” arXiv, 2025.
[37] T. Zhang, V. Kishore, F. Wu, K. Q. Weinberger, and Y. Artzi, “Bertscore:
Evaluating text generation with bert,” arXiv, 2019.
[38] R. Zhao, M. Zhan, X. Deng, Y. Wang, Y. Wang, G. Gui, and Z. Xue, “Yet
another traffic classifier: A masked autoencoder based traffic transformer
with multi-level flow representation,” in AAAI, vol. 37, 2023.
[39] Q. Zhou, L. Wang, H. Zhu, T. Lu, and V. S. Sheng, “Wf-transformer:
Learning temporal features for accurate anonymous traffic identification
by using transformer networks,” IEEE Transactions on Information
Forensics and Security, 2024.
PAPER_TEXT
