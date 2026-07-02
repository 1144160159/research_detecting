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
# [787] Reverse Engineering of Industrial Protocols From Network Traffic
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
编号：787
题名：Reverse Engineering of Industrial Protocols From Network Traffic
年份：2026
DOI：10.1109/tii.2026.3681937
来源：IEEE Transactions on Industrial Informatics
PDF：paper/10.1109_TII.2026.3681937.pdf
已有粗分类：基础理论、密码协议与安全机制
二级关联：无
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\787.txt
- 原始字符数：89961
- 本次发送字符数：89961
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS

1

Reverse Engineering of Industrial Protocols
From Network Traffic
Chuan Sheng , Member, IEEE, Shan Jiang , Qing-Long Han , Fellow, IEEE, Wei Zhou ,
Wanlun Ma , Member, IEEE, Xiaogang Zhu , Member, IEEE, Sheng Wen , Senior Member, IEEE,
and Yang Xiang , Fellow, IEEE

Abstract—Reliable protocol knowledge is often difficult
to obtain in industrial networks, as industrial communications come with limited documentation, vendor-specific
encodings, and opaque payloads. This lack of transparency
hinders message interpretation and protocol analysis. To
recover this missing protocol knowledge, network-tracebased protocol reverse engineering (PRE) infers message
structure, field roles, and interaction logic directly from
recorded traces. This enables protocol-aware intrusion
detection, process monitoring, and protocol testing and
fuzzing without access to device internals. Although PRE
has advanced rapidly, existing techniques are developed
under diverse objectives and assumptions. As a result,
it is often unclear how isolated results relate to an endto-end reverse-engineering workflow, and how evaluation
outcomes should be compared across tasks and protocols.
In this article, we cast reverse engineering of industrial
protocols from network traces as a task-driven pipeline
and articulate a unified task decomposition spanning message type identification, protocol syntax and semantic inference, payload pattern recognition and semantic inference, and protocol state machine reconstruction. For each
task, we describe key methodological themes, common
evaluation practices, and practical limitations that affect
robustness and deployability in industrial settings. We further discuss security, privacy, and ethical risks that accompany increasingly capable PRE, and identify promising
research directions toward more systematic, dependable,
and deployment-oriented PRE methodologies.
Index Terms —Industrial communication protocols, industrial control systems (ICSs), network traffic analysis,
protocol reverse engineering (PRE).

I. INTRODUCTION
NDUSTRIAL communication protocols constitute the backbone of modern industrial control systems (ICSs), enabling
data acquisition, supervisory control, and coordinated operation

I

Received 13 February 2026; revised 11 March 2026; accepted 3 April
2026. Paper no. TII-26-1533. (Chuan Sheng and Shan Jiang contributed
equally to this work.) (Corresponding author: Qing-Long Han.)
Chuan Sheng, Shan Jiang, Qing-Long Han, Wei Zhou, Wanlun Ma,
Sheng Wen, and Yang Xiang are with the Swinburne University of
Technology, Hawthorn, VIC 3122, Australia (e-mail: chuansheng@swin.
edu.au; shanjiang@swin.edu.au; qhan@swin.edu.au; weizhou@swin.
edu.au; wma@swin.edu.au; swen@swin.edu.au; yxiang@swin.edu.au).
Xiaogang Zhu is with the School of Computer Science and Information
Technology, Adelaide University, Adelaide, SA 5005, Australia (e-mail:
xiaogang.zhu@adelaide.edu.au).
Digital Object Identifier 10.1109/TII.2026.3681937

among heterogeneous industrial devices [1]. Despite their ubiquity in operational technology networks, many industrial deployments rely on proprietary, undocumented, or poorly specified
protocols, which significantly hinders the reliable identification
of message types, interpretation of communication content, and
modeling of device interaction behaviors [2]. In particular, industrial message payloads encapsulate critical information, such
as device states, measurement values, and control commands,
yet their internal formats are often opaque due to proprietary
implementations and vendor-specific design choices [3], [4].
This lack of protocol visibility fundamentally limits a principled understanding of system behavior, thereby constraining the effectiveness of essential ICS tasks, including system
monitoring, security analysis, and fault diagnosis in real-world
deployments [5], [6], [7].
Against this background, protocol reverse engineering (PRE)
has emerged as a primary methodological paradigm for recovering protocol structure and communication semantics from
observable artifacts. The existing PRE research can be broadly
divided into network-trace-based and program-analysis-based
approaches [8], [9]. Network-trace-based PRE focuses on inferring protocol structure and communication semantics solely
from message exchanges observed on the network [10], [11],
[12]. In contrast, program-analysis-based methods analyze internal artifacts, such as firmware images, binaries, or source
code, to understand protocol implementations [13], [14], [15].
While powerful in controlled settings, program-analysis-based
techniques are often impractical in industrial environments,
where device internals are inaccessible, modifications are infeasible, and proprietary implementations provide limited structural
transparency [16], [17]. Consequently, this article concentrates
on network-trace-based PRE techniques, which better align with
the operational constraints and closed-box nature of real-world
ICS deployments.
By reconstructing protocol knowledge, PRE enables a wide
range of downstream ICS applications. Recovered protocol
structures facilitate automated testing and conformance verification through the generation of valid and invalid message sequences [18]. Building on reconstructed protocol state machines,
PRE further enables stateful and semantic-aware fuzzing, significantly improving the effectiveness of vulnerability discovery [19], [20], [21]. In the security domain, PRE-derived semantics enhance intrusion detection by exposing protocol-violating
behaviors, such as illegal function codes or parameter values,
that statistic-based IDS cannot capture [22]. At the operational
level, PRE supports system monitoring and process anomaly detection by revealing device states and control intentions directly
from network traffic [23].

1941-0050 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html
for more information.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

2

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS

Fig. 2.

Overview of the article organization.

TABLE I
KEY DIFFERENCES BETWEEN GENERAL-PURPOSE AND INDUSTRIAL
COMMUNICATION PROTOCOLS FROM A PRE PERSPECTIVE
Fig. 1. Temporal distribution of PRE papers, illustrating the rapid
growth of network-trace-based PRE in recent years and the limited
coverage of this trend in existing surveys. Bars show the number of PRE
papers reviewed across time periods by different survey works.

The existing surveys provide valuable foundations, yet they
do not fully capture the rapid methodological advances made
over the past decade. As shown in Fig. 1, network-trace-based
PRE techniques for industrial protocols have expanded rapidly
in recent years. Most of this progress has occurred in the past five
years, yet it remains insufficiently reflected in prior surveys [8],
[24], [25], [26]. More recent studies also exhibit limited scope.
For example, work on controller area network (CAN) reverse
engineering [27] offers detailed analysis but is confined to a
single bus protocol and does not generalize to broader ICS
settings. Research on industrial control PRE [28] primarily
emphasizes earlier methods and provides only partial coverage
of recent advances. Other efforts focus on automation aspects
of PRE, such as interaction and information requirements [9],
rather than on the technical foundations of PRE itself.
In contrast to prior work, this survey provides a contemporary and comprehensive view of PRE for industrial communication protocols. We base our study on papers published
between 2016 and 2025 in leading security venues (S&P, CCS,
USENIX Security, NDSS, TDSC, and TIFS) and major networking venues (SIGCOMM, MobiCom, INFOCOM, NSDI,
JSAC, TMC, and TON), ensuring that our analysis captures
the significant methodological progress made in recent years.
Building on these recent advances, this article offers four major
contributions. First, we present the first task-oriented taxonomy
of PRE techniques, aligning algorithmic developments with
practical reverse-engineering workflows and clarifying their
roles in specific PRE tasks. Unlike prior surveys that organize
techniques primarily by methodological categories, our taxonomy is structured around the PRE workflow and its constituent
tasks. Second, we systematically describe techniques and evaluation practices across different PRE tasks and identify key open
challenges. Third, we provide the first structured discussion of
security, privacy, and ethical considerations of PRE in industrial
settings. Finally, we outline concrete future research directions
to support the continued development of PRE for ICSs.
The rest of this article is organized as shown in Fig. 2.
Section II provides background on industrial protocols and
introduces the PRE taxonomy used in this work. Section III reviews existing PRE techniques from a task-oriented perspective.
Section IV reviews datasets used in prior industrial PRE research. Section V discusses security, privacy, and ethical considerations related to PRE in ICS settings. Section VI explores
promising and emerging future research directions. Finally,
Section VII concludes this article.

II. BACKGROUND AND TAXONOMY
Although industrial communication protocols are routinely
observed through network traces, the information required to
understand their structure, semantics, and behavior is rarely
explicit in the traffic itself. This mismatch between observability
and inference underlies the challenges of PRE in industrial
settings. This section examines the sources of this mismatch
and introduces a task-oriented PRE taxonomy to organize the
existing techniques.
A. Industrial Communication Protocols
Industrial communication protocols enable interactions
among controllers, sensors, actuators, and supervisory systems
in automated environments, such as production lines and process
plants [29]. They span multiple layers of the communication
stack. At the lower layers, fieldbuses and real-time industrial
Ethernet systems, such as PROFIBUS, EtherCAT, and CAN,
primarily carry cyclic I/O exchanges and time-critical process
variables [27]. At the upper layers, industrial application protocols, including Modbus, OPC UA, DNP3, and S7comm, provide device semantics, configuration access, and supervisory
information [28]. Together, these protocols constitute a heterogeneous industrial communication landscape shaped by control requirements, device diversity, and long-standing industrial
technology stacks.
These characteristics fundamentally distinguish industrial
protocols from general-purpose IT protocols. As summarized
in Table I, these distinctions manifest at multiple levels. At the
representation level, industrial protocols commonly rely on proprietary specifications and compact, nonself-describing binary

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

SHENG et al.: REVERSE ENGINEERING OF INDUSTRIAL PROTOCOLS FROM NETWORK TRAFFIC

3

Fig. 3. Task-oriented taxonomy of industrial PRE, illustrating the major inference tasks in the PRE pipeline for recovering protocol structure,
semantics, and behavior. Each task is characterized by representative technique families; the dashed connections indicate cross-task integration.

encodings that mix byte- and bit-level fields [6], [7]. At the
structural level, message formats are often context-dependent,
varying with protocol functions and service states, and support
heterogeneous command sets and data layouts [30]. At the traffic
level, industrial communications are dominated by cyclic control
exchanges, resulting in high-volume but low-diversity patterns,
while process variable exchange and diagnostic operations may
involve larger or segmented payloads [31]. Beyond protocol
design, implementations further vary across vendors, device
types, and deployment configurations [16], [19].
These properties make industrial communication protocols
difficult to interpret directly from network traces. Understanding
protocol operation in practice therefore cannot rely on explicit
specifications or self-describing message formats. Instead, it
requires inference-based methods that reconstruct message formats, functional roles, and communication patterns from limited
observational evidence. Under these conditions, PRE becomes
essential for obtaining reliable insight into ICSs.
B. Taxonomy of Industrial PRE
In this article, PRE refers to network-trace-based PRE, which
aims to recover the structure and semantics of industrial communication protocols directly from observed network traffic,
without relying on official specifications or source code [25].
In industrial settings, PRE operates on raw packet streams
collected from operational networks and seeks to infer how
messages are differentiated, how protocol fields are organized,
and how exchanged data corresponds to device behavior or
underlying process operation. Due to the limited observability
inherent in network traces, such inference should be performed
under incomplete and implicit protocol information, motivating
a systematic decomposition of PRE into well-defined inference
tasks.
To structure such inference, we organize industrial PRE into
a task-oriented taxonomy, as illustrated in Fig. 3. The taxonomy follows the logical progression of a typical PRE pipeline,
in which protocol knowledge is incrementally recovered from
network traces [10], [25], [32]. It starts with message type
identification to separate heterogeneous traffic, providing a
coarse-grained organization of observed messages. Building on
this separation, protocol syntax and semantic inference focus

on recovering message layouts and associating protocol fields
with their functional roles. The analysis then moves to the
payload level, where payload structure and semantic inference
extract finer-grained data representations and interpret payload
contents in relation to device states or process variables. Finally, protocol state machine reconstruction captures temporal
and logical dependencies across message sequences, modeling
the overall protocol behavior. This task-oriented organization
clarifies dependencies among different inference problems and
provides a systematic framework for reviewing existing PRE
techniques in the following section.
III. TASK-ORIENTED PRE TECHNIQUES
This section reviews industrial PRE techniques from a taskoriented perspective. Rather than attempting to recover complete protocol specifications in a single step, existing PRE systems typically address concrete reverse-engineering objectives
through a sequence of interdependent tasks [6], [33], [34]. Accordingly, we organize prior work by the specific PRE tasks they
target. For each task, we summarize representative techniques,
commonly used evaluation metrics, typical performance analysis practices, and key open challenges. We do not present finegrained quantitative comparisons across methods, as existing
studies are evaluated on diverse protocols and datasets whose
scale and traffic quality are difficult to normalize. Moreover,
there is currently no widely accepted framework for assessing
PRE data quality [27], [35].
A. Message Type Identification
Message type identification aims to partition protocol messages into homogeneous groups, where each group corresponds
to a distinct message type with a consistent structural or functional role. This task serves as the entry point of most networktrace-based PRE pipelines, which assume messages of different
types have been separated.
1) Techniques: In practice, message type identification is
commonly formulated as an unsupervised clustering problem
under the constraint that no protocol specification is available.
Existing approaches mainly differ in how message similarity is
constructed and which aspects of the message are emphasized

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

4

to mitigate payload-induced variability. Based on these design
choices, prior work can be broadly categorized into alignmentbased, pattern-based, and representation-based approaches.
Alignment-based methods: Alignment-based methods identify message types by comparing messages positionally using
sequence alignment or format comparison, under the assumption that messages of the same type share similar byte values
at corresponding offsets [36]. Message similarity is typically
computed via global byte-wise alignment, and clustering is
then performed based on the resulting pairwise similarity matrix, most commonly using hierarchical clustering [37]. Several
studies refine raw byte-wise alignment by introducing segmentaware comparison [38] or improved alignment spaces to better accommodate binary and industrial protocols [39]. While
these methods can capture fine-grained structural similarities,
they incur high computational overhead due to exhaustive pairwise comparisons [37]. They are also particularly sensitive to
payload-induced distortion when variable-length or data-heavy
fields dominate message contents [38].
Pattern-based methods: Pattern-based methods relax strict
positional alignment by constructing message similarity from
statistical or structural patterns [40]. A representative line of
work focuses on probabilistic keyword inference. It models
messages using discriminative byte patterns whose occurrence
statistics distinguish different message types, and derives similarity from shared keyword distributions [34]. In industrial
protocol settings, some approaches exploit coarse-grained structural regularities, such as message length distributions or stable
control regions, to reduce payload-induced interference [41].
More recent work automates this process by identifying entropystable header regions via change-point detection and performing
clustering on the extracted headers, improving robustness under
highly dynamic payloads [42], [43]. By relying on stable patterns
rather than global positional consistency, pattern-based methods exhibit improved resilience to payload variability, while
implicitly assuming that such patterns are sufficiently discriminative [34], [43].
Representation-based methods: Representation-based methods adopt a data-driven perspective by learning latent representations of protocol messages through neural models, rather
than relying on manually designed similarity measures [44].
Autoencoders and shared-learning frameworks are employed
to embed messages into latent spaces that capture structural
regularities across message instances [45]. Subsequent studies
leverage transformer-based architectures to learn contextualized
message embeddings, and perform message type identification
via clustering in the learned representation space [46]. Dynamic
and hierarchical inference frameworks further integrate learned
representations with iterative refinement mechanisms to improve type separation under complex protocol behaviors [5],
[47]. Although learned representations can capture complex
and nonlinear similarities, their effectiveness depends on the
availability of sufficient training data, and their interpretability
remains limited [44], [46].
2) Evaluation Metrics and Performance: Message type identification is commonly evaluated as a clustering task by measuring the consistency between inferred clusters and ground-truth
message types. When ground-truth labels are available, studies
typically report metrics, such as homogeneity, completeness,
and their harmonic mean (V-measure) [43], as well as precision,
recall, or F1-score [45]. In the settings without labels, adjusted
Rand index or intrinsic clustering metrics such as silhouette
score are often adopted [46]. Overall, the existing methods

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS

achieve strong performance on well-structured protocols, particularly when message headers are stable and payload variability
is limited. However, performance tends to degrade for protocols
with highly dynamic payloads, weakly defined headers, or large
numbers of message types, indicating that message type identification remains challenging in complex industrial and proprietary
environments.
3) Challenges: Despite steady progress, message type identification remains challenged by constructing robust similarity
measures in the presence of highly dynamic payloads, scalability
issues arising from pairwise similarity computation or model
training, and limited generalization across diverse protocol families. Addressing these challenges is essential for reliable PRE
in realistic industrial environments.
B. Protocol Syntax Inference
Protocol syntax inference aims to recover the internal structural organization of protocol messages by identifying how each
message type is partitioned into individual fields and how these
fields are interpreted. It operates at the intra-message level,
focusing on field layouts and decoding rules, and provides the
foundation for subsequent semantic inference.
1) Techniques: Protocol syntax inference typically involves
two aspects: field boundary inference and field syntax inference.
Field boundary inference identifies where fields begin and end
in a message, including each field’s position, length, and granularity. Field syntax inference then determines how the extracted
fields should be interpreted, such as their data type, encoding,
and byte order. Prior studies differ in which aspects they address
and what evidence they exploit for structural reconstruction.
Field boundary inference: The early field boundary inference approaches are largely driven by cross-message alignment.
Multiple messages of the same type are aligned, and conserved
regions are interpreted as fields, with boundaries inferred from
alignment gaps or divergence points [48]. Bit-oriented extensions subsequently adapt alignment-based inference to finer
granularities by redefining matching and backtracking rules to
support subbyte fields [49]. This alignment-based paradigm is
further extended to wireless and physical-layer traces by aligning messages via inferred preamble or synchronization patterns,
enabling boundary recovery beyond byte-aligned settings [50].
To reduce reliance on cross-message alignment, a substantial
body of work infers field boundaries by analyzing statistical
regularities within individual messages. NEMESYS identifies
candidate boundaries by exploiting intrinsic value-change patterns and repetition structures [51], while later refinements employ variance correlation and principal component analysis to
iteratively adjust coarse segmentations [52]. Other approaches
formulate boundary detection as a probabilistic inference problem, using entropy, mutual information, or expert voting mechanisms to identify likely boundary positions [53], [54], [55].
Domain-specific adaptations further exploit structural characteristics of industrial protocols, such as compact headers and short
control fields, to guide iterative merging or splitting of candidate
segments [56]. More recent work frames boundary inference as
a sequence labeling or segmentation problem and applies deep
learning models to identify byte- or bit-level boundaries [12],
[57]. These models can improve accuracy on complex binary
protocols, but typically require more data and supervision.
Field syntax inference: Compared to field boundary inference, fewer studies explicitly target field syntax inference.
Early efforts incorporate semantic information and contextual

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

SHENG et al.: REVERSE ENGINEERING OF INDUSTRIAL PROTOCOLS FROM NETWORK TRAFFIC

5

propagate to syntax inference, making it difficult to reliably
infer data types, encodings, and byte order when boundaries
are imperfect. Moreover, the limited availability of field-level
evaluation signals further complicates the validation of inferred
syntax, hindering systematic progress beyond boundary-centric
solutions.
C. Protocol Semantic Inference

Fig. 4. Boundary-level and field-level evaluation in protocol syntax
inference. Boundary-level evaluation treats each candidate position as
a binary decision, while field-level evaluation matches inferred fields to
ground-truth fields.

constraints to infer field interpretation rules alongside boundary detection, enabling limited recovery of data types and
field roles [58]. Subsequent work explores model-based and
knowledge-driven techniques for inferring field grammar, leveraging protocol templates, expert knowledge, or probabilistic
constraints to guide interpretation [11], [59]. More recently,
graph-based and relational reasoning methods represent inferred
fields and their relationships as structured graphs, enabling
syntax inference via representation learning over field dependencies [30], [60]. Overall, these approaches demonstrate that
PRE can move beyond boundary recovery toward richer syntax
reconstruction, but they often depend on auxiliary knowledge or
domain-specific assumptions.
2) Evaluation Metrics and Performance: Protocol syntax inference is evaluated at different granularities, which leads to
distinct evaluation formulations, as illustrated in Fig. 4. At
the boundary level, each candidate position between adjacent
bytes (or bits) is treated as a binary decision (boundary versus
nonboundary). True positives, false positives, true negatives, and
false negatives are therefore defined over boundary positions,
and metrics, such as accuracy, precision, recall, and F1-score,
are computed accordingly [12]. At the field level, evaluation is
instead based on matching inferred fields to ground-truth fields.
NetPlier [34] defines an inferred field as correct if it is part of
a single true field or merges several consecutive true fields, and
as accurate if it perfectly matches a true field. Based on these
notions, it reports correctness as the fraction of correct fields
and perfection as the fraction of accurate fields among all true
fields.
These two evaluation views capture different failure characteristics: boundary-level metrics primarily reflect local delimiter
errors, whereas field-level metrics reflect end-to-end format
quality. Accordingly, reported performance depends strongly
on both the targeted inference granularity and the complexity
of the evaluated protocols. Boundary inference methods often
achieve high accuracy on protocols with stable formats, whereas
methods that aim to recover complete field structures or syntax
face substantially greater challenges on complex and variable
binary protocols. As a result, performance figures vary considerably across studies, owing to differences in datasets, evaluation
protocols, and the scope of syntax inference considered.
3) Challenges: A fundamental technical challenge in protocol syntax inference is the strong dependence of syntax recovery
on boundary accuracy. Errors in field segmentation directly

Protocol semantic inference aims to determine the operational
roles played by recovered fields in protocol execution, rather
than only their structural boundaries or encodings. Typical targets include message type indicators, function codes, lengthrelated fields, and transaction-related identifiers. For example,
a 1-byte field that takes values, such as 0x01, 0x03, and 0x05
across different messages may be recognized structurally as a
compact numeric field during syntax inference, but semantic
inference further asks whether these values denote message
categories, protocol operations, or transaction states.
1) Techniques: The existing protocol semantic inference approaches mainly differ in how protocol-level semantic roles are
inferred from observed traffic. Accordingly, prior work can be
broadly categorized by the type of evidence exploited for semantic inference, including statistic-based, dependency-based,
and learning-based approaches.
Statistic-based semantic inference: Statistic-based approaches infer protocol semantics through explicit statistical
associations between field values and observable communication properties. FieldHunter [33] is a representative example that
assigns semantic roles by correlating candidate fields with message length, endpoint identity, and request–response structure.
Based on measures of variability and correlation, it identifies
roles, such as message type indicators, length fields, identifiers,
transaction-related fields, and accumulators. Follow-up work
shows that similar statistic-based reasoning can still support
coarse-grained semantic inference even when protocol visibility
is limited, such as in partially encrypted or obscured traffic [61].
Dependency-based semantic inference: Dependency-based
approaches infer protocol semantics by analyzing how fields
function within interactions. Early work shows that semantic
roles can be associated with fields by examining their involvement in request–response relations and conditional message
structures [62]. The two-pathway model [63] further generalize
this idea by jointly considering field stability and interfield
dependencies. More recent work emphasizes control or discriminator fields and shows that a small subset of fields governs
protocol behavior. Specifically, control-field-driven inference
exploits interaction dependencies to associate fields with roles,
such as function codes or operation selectors [6]. Learningbased semantic inference: As illustrated in Fig. 5, learning-based
approaches infer protocol semantics by learning mappings between data patterns and semantic roles from existing protocols
and transferring this knowledge to previously unseen protocols.
Prior work shows that protocol-level field roles can be inferred
by grouping fields with similar learned representations [64].
FSIBP [65] and PREIUD [66] further extend this direction
by leveraging feature learning and representation learning to
automate field-role inference for binary and industrial protocols. Complementary approaches exploit recurring patterns and
temporal regularities to learn semantic signatures of fields and
associate them with protocol roles in an inductive manner [7],
[67]. Empirical studies on real-world protocols further confirm

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

6

Fig. 5. Learning-based protocol semantic inference via cross-protocol
knowledge transfer, where semantic mappings learned from existing
protocols are transferred to infer semantic roles in unseen protocols.

that such learning-based semantic inference can generalize to
protocols without available specifications [68].
2) Evaluation Metrics and Performance: Protocol semantic
inference lacks standardized evaluation methodologies. Existing
studies typically adopt problem-specific evaluation criteria, including agreement with known protocol specifications, or qualitative validation through manual analysis. When ground-truth
semantic annotations are unavailable, inferred semantics are often evaluated indirectly by assessing their utility in downstream
tasks, such as protocol-aware intrusion detection, fuzzing, or
traffic parsing [21], [69], [70]. Consequently, reported performance varies widely across studies and is difficult to compare
in a unified manner, as results are strongly influenced by protocol complexity, traffic diversity, and the semantic granularity
considered. Existing approaches are generally more stable for
recurring semantic roles, such as length fields, sequence numbers, or control codes. Protocol-specific semantics, such as the
ROSCTR and Function Group fields in S7comm, are harder to
infer reliably because reference instances are limited.
3) Challenges: A key challenge in protocol semantic inference lies in the absence of a unified semantic taxonomy for
protocol fields. Without commonly accepted semantic categories
and reference definitions, inferred field semantics lack stable
anchors, making it difficult to establish transferable semantic
models from traffic. For example, message type indicators,
operation selectors, and transaction identifiers may all fall under
control-related semantics, yet their semantic distinctions are
often defined inconsistently across studies. This limitation is
particularly severe for protocol-specific semantics, where scarce
and nonreusable evidence in observed traces further constrains
reliable semantic assignment.
D. Payload Structure Recognition
Payload structure recognition recovers recurring structural
patterns within message payloads. It typically outputs bit/bytelevel offset-length segments. For long or composite payloads,
it can further recover repeated submessages and nested blocks
under explicit length constraints. Compared with protocol-level
syntax inference, it focuses on semantics-heavy payload regions
that carry application data and complex parameters but expose
few explicit delimiters. The recovered structure provides a basis
for payload semantic inference.
1) Techniques: Existing payload structure recognition approaches aim to recover field boundaries by analyzing repeated

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS

payload observations and enforcing consistent layouts across
messages. While they share this common objective, existing
methods differ primarily in the type of structural evidence used
to infer boundaries and in how segmentation hypotheses are regularized. Based on these differences, prior work can be broadly
grouped into three paradigms: variability-based segmentation, feature-driven recognition, and constraint-regularized
recognition.
Variability-based segmentation: A common strategy infers
payload boundaries from variability observed across repeated
payload samples. It computes per-bit or per-byte variability
statistics, such as flip rates, transition counts, and distributional
stability, and then locates field boundaries by detecting abrupt
changes of these statistics along the payload [71], [72]. Robust
variants move beyond a single global profile and model each
position as a short sequence across observations. They use interposition similarity and correlation to decide whether adjacent
bits or bytes belong to the same field [73], [74]. These methods
work well when traffic contains abundant repetitions, but their
effectiveness can degrade when signal changes are rare in the
capture window or layouts vary across contexts.
Feature-driven recognition: Recent approaches increasingly
treat segmentation as a data-driven grouping problem. They
encode each bit position, byte position, or small position block
as a feature vector that captures multiple behavioral aspects,
including variability, value distribution, and simple temporal
descriptors [75]. Boundaries are then derived from transitions
between learned groups or directly predicted from these representations [76], [77], [78]. Related ideas also appear in interactive closed-box settings, where response-driven signals provide weak supervision to localize influential payload snippets
and approximate their boundaries across queries [69], [70],
[79]. Compared with fixed heuristics, feature-driven methods
better handle heterogeneous field types and unknown numbers
of fields, but they shift sensitivity to feature design and data
representativeness.
Constraint-regularized recognition: For long or composite
payloads, structure is better revealed by explicit format constraints and cross-sample repetition than by variability-based
cues alone. Constraint-driven methods identify control fields
that govern block extents and validate inferred boundaries
against observed payload spans. Along the same line, templatecentric recognition aligns repeated records or submessages to
expose stable anchors and variable regions, and iteratively refines boundaries across samples [80], [81]. Multiple-sequence
alignment extends this idea by revealing conserved cores and
insertions and deletions, enabling boundary discovery when
explicit delimiters are absent [82].
2) Evaluation Metrics and Performance: When ground-truth
boundaries are available, segmentation quality is commonly
measured by boundary precision, recall, and F1-score at bit
or byte granularity, often using a small tolerance window to
account for minor alignment ambiguity [71], [72], [73]. For
methods that output position groupings, consistency can be
evaluated by the agreement between predicted and reference
group labels [76]. For composite payloads, evaluation further
checks whether inferred length-controlled extents match observed payload spans and whether recovered templates remain
stable across samples [80], [81].
Practical performance is mainly shaped by sample efficiency,
scalability with payload length, and robustness under mixed
layouts. Variability-based methods typically require abundant

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

SHENG et al.: REVERSE ENGINEERING OF INDUSTRIAL PROTOCOLS FROM NETWORK TRAFFIC

Fig. 6. Example of payload semantic inference. Raw payload data
are analyzed to recover internal representations and to infer process
semantics, where decoding functions associate payload content with
interpretable values and domain meanings.

repeated observations to obtain reliable position-wise statistics [71], [72], and can degrade when traffic diversity is limited
or layouts vary across contexts [74]. Feature-driven methods reduce the need for abundant repeated observations, but they incur
additional costs for feature representation learning. Their performance is also sensitive to the choice and quality of features [76],
[77], [78]. Constraint-regularized methods can stabilize long
or repeated structures but introduce additional validation and
alignment overhead [81], [82]. ReCAN supports reproducible
comparisons of metrics and scalability across traces and setups [83].
3) Challenges: Mixed layouts created by optional fields and
context dependent multiplexing blur structural cues. At a fixed
offset, the same bits or bytes can correspond to different fields
across messages. As a result, variability statistics and feature
representations mix multiple structures. The resulting change
signals are blurred rather than localized [74], [77]. This ambiguity also destabilizes cross message regularization. Alignment, template induction, and length controlled block validation
must reconcile hypotheses that fit only subsets of samples. As
a result, inferred boundaries become unstable and recovered
blocks become inconsistent across observations [80], [81], [82].
Bit-level packing and endianness further weaken usable anchors
and reduce contrast in variability profiles, which compounds the
difficulty of locating reliable boundaries [71], [73].
E. Payload Semantic Inference
As illustrated in Fig. 6, payload semantic inference aims to
assign domain meanings to recovered payload fields and to
derive their decoding rules. Unlike protocol semantic inference
that mainly targets control-oriented header fields, it focuses on
semantics-heavy data regions grounded in physical processes
and device behaviors.
1) Techniques: Existing payload semantic inference approaches aim to assign domain meanings to recovered payload
fields and infer their decoding rules. They differ mainly in the
type of evidence used to ground semantic interpretations. In
practice, three main lines of work have emerged: anchor-based
semantic alignment, correlation-guided semantic mining, and
reference-guided semantic transfer.
Anchor-based semantic alignment: A practical way to obtain semantics is to use standardized diagnostic services or
professional tooling as semantic anchors. The key idea is to
trigger or observe queries whose returned values have known
meanings, and then align these reference values with candidate

7

payload fields to infer both field roles and decoding rules.
For in-vehicle diagnostics, DP-Reverser leverages professional
diagnostic tools and automated physical triggering to recover
message semantics and proprietary formulas for interpreting
responses at scale [31]. ACTT and CAN-D similarly exploit
diagnostic knowledge to attach physical meanings to a subset
of extracted signals and to refine encoding details that are hard
to infer from traffic alone [32], [84]. This family provides highconfidence semantic grounding, but its coverage is constrained
by what standards expose and what tooling can exercise in the
captured operational context.
Correlation-guided semantic mining: When explicit semantic
anchors are unavailable, another line of work infers semantics by correlating payload fields with side information that
reflects the underlying physical system. LibreCAN combines
raw CAN traces with smartphone inertial measurements and
OBD-II readings to match candidate signals to known physical
quantities [85]. AutoCAN further exploits laws of physics by
searching for correlation and functional relationships among
time series, enabling label propagation once a small set of
signals are identified [86]. For industrial control protocols, SeMiner uses image-based process observations to extract semantic
channels and match them to payload fields, enabling domain
semantics inference without protocol specifications [87]. Recent
work also moves beyond correlation to directional reasoning.
PicaCAN models physically induced causality and uses timeprecedence structure to infer physical semantics of signals from
passive traces [4]. In wireless cyber-physical control, similar
correlation-based reasoning can be used to associate captured
command payloads with control actions [88]. These approaches
generalize across proprietary encodings, but they depend on the
availability, synchronization quality, and state coverage of side
information.
Reference-guided semantic transfer: It aligns unknown traffic
with reference patterns in the form of previously decoded or
annotated message templates from related systems. This establishes cross-system correspondences and enables the transfer
of semantic labels and decoding rules. CANMatch exploits
frame reuse and similarity across vehicles [89]. It infers signal
meanings and scaling factors through automated frame matching
and redundancy resolution. Translation-oriented systems, such
as LibreCAN, can also benefit from this paradigm once a small
set of semantically grounded signals is available [85]. This
enables broader interpretation of raw traces via label propagation. While reference-guided transfer reduces the need for direct
semantic anchors, it remains sensitive to deployment variability,
partial reuse, and mismatches introduced by vendor-specific
multiplexing.
2) Evaluation Metrics and Performance: Semantic inference
is typically evaluated along three axes: correctness of semantic
assignment, fidelity of decoded values, and coverage. When
reference semantics are available through diagnostics, tooling,
or instrumented observations, studies measure whether each
inferred field matches the intended quantity using top-1 or top-k
accuracy [32], [84]. They also compare decoded time series
against references using MAE, RMSE, and correlation after applying inferred signedness, endianness, scaling, and units [85],
[87]. Coverage is reported as the fraction of fields or signals
that can be assigned semantics and decoded reliably under the
available evidence [32], [86].
Anchor-based alignment tends to achieve higher correctness
and value fidelity when anchors can be exercised, while coverage

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

8

is bounded by what standards or tools expose and what operational states can be triggered or observed during capture [32],
[84]. Correlation-guided mining is more broadly applicable
but is sensitive to synchronization quality, delays, noise, and
limited state coverage, which can reduce fidelity or introduce
false matches [85], [88]. Physics- and causality-guided designs
can improve robustness over correlation alone when sufficient
data support stable relationship or precedence estimation [4],
[86]. Reference-guided semantic transfer can be accurate once
cross-trace matches exist, yet its effective coverage and mapping
stability depend on cross-system reuse and resilience to mode
shifts [89].
3) Challenges: Payload semantic inference is fundamentally
underconstrained because multiple fields can exhibit similar
temporal patterns while encoding different quantities, and decoding rules such as scaling, offset, and signedness may be
indistinguishable without semantic anchors [90]. Since passive
traces reveal only value evolution rather than physical meaning [31], temporally similar fields may remain observationally
equivalent, allowing multiple decoding hypotheses to explain the
same trace data equally well. As a result, semantic assignment
and decoding rule inference cannot be uniquely determined from
network traffic alone without reliable anchors.
F. Protocol State Machine Reconstruction
Protocol state machine reconstruction aims to infer a compact
behavioral model of a protocol from network traces, typically
as a finite-state machine (FSM), or as an extended finite-state
machine (EFSM), with variables and guards. An FSM captures
control-state evolution and ordering constraints over abstracted
message symbols, while an EFSM additionally models valuedependent branching through guarded transitions and variable
updates.
1) Techniques: Most approaches first abstract raw messages
into a finite symbol set and then learn a state machine over
the resulting sequences. Prior work mainly falls into controlstate reconstruction (FSM) and data-aware reconstruction
(EFSM).
Control-state reconstruction: Control-state reconstruction
learns an FSM that encodes which message classes can follow
one another and how requests pair with responses. A typical
workflow consists of message abstraction, state construction
from symbol sequences, and state merging or splitting to obtain a compact model that generalizes beyond the observed
network traces [91], [92], [93]. Network traces are often noisy
and underconstrained because of partial state coverage, payload
variability, and session interleaving. To cope with this, many
systems embed robustness directly into the reconstruction loop.
They adopt probabilistic formulations to tolerate noisy observations [94] or analyze how abstraction granularity and merging
criteria affect model quality, helping suppress spurious states and
transitions [95]. In addition, inferred control-state machines are
validated and refined through downstream tasks, such as stateful
testing or fuzzing, where the learned model guides sequence
generation and exploration of deeper behaviors [16], [96].
Data-aware reconstruction: Data-aware approaches first
learn a control-state skeleton from abstracted message sequences. They then lift this skeleton to an EFSM by selecting payload fields as variables and inferring transition guards
and update rules that explain value-dependent branches across
traces [97]. Because guard and update inference from passive
traces is highly underconstrained, EFSM reconstruction often

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS

Fig. 7. Cross-task patterns observed in prior PRE research. Tx/y denotes the combination of tasks x and y.

relies on constraint-based refinement or guided correction to
revise candidate predicates and state distinctions [98].
2) Evaluation Metrics and Performance: When a reference
FSM or EFSM is available, studies typically evaluate inferred
models using state precision and recall, transition precision and
recall, completeness, F1-score, and model conciseness under a
consistent abstraction [97]. In the absence of a reference model,
evaluation commonly relies on held-out traces. Typical metrics
include trace or session acceptance rate, next-symbol prediction
accuracy or likelihood, and model size [92], [94].
Across both settings, performance is largely determined by
the chosen abstraction and by how states are merged or split, reflecting a fundamental tradeoff between state explosion and state
aliasing [95]. Probabilistic formulations can improve robustness
to noise and unseen variations, but they may overgeneralize
when trace diversity is limited [94]. EFSM reconstruction, by
contrast, can better capture value-dependent behavior, yet it
remains sensitive to ambiguity in guard and update inference
from passive traces [97], [98].
3) Challenges: The core challenge in protocol state-machine
reconstruction lies in the nonidentifiability of latent control
structure from finite execution traces. Because traces expose
only observable message sequences, distinct state machines can
exhibit identical external behavior, making reconstruction sensitive to abstraction choices, such as state merging or splitting.
This challenge is further amplified in data-aware reconstruction, where lifting an FSM skeleton to an EFSM introduces
additional degrees of freedom. Different selections of variables
and guard or update predicates can fit the same traces, yielding
structurally different yet observationally equivalent models [97],
[98]. Consequently, reconstruction outcomes are difficult to
compare across studies [95].
G. Cross-Task Integration and Dependencies
To complement the per-task review above, Fig. 7 summarizes
cross-task patterns in prior PRE studies. Among studies that
span multiple tasks, T1/T2 is the most common combination,
followed by T2/3, while other pairings, such as T1/3, T2/4,
and T4/5, appear only sporadically. This pattern reflects the
PRE pipeline’s dependency structure: cross-task coupling arises
when upstream tasks produce stable intermediate outputs for
downstream analysis, such as message partitions, field boundaries, and structural hypotheses. By contrast, payload semantic
inference and state machine reconstruction rely on heterogeneous evidence, including application-specific semantics, side
information, and longer -range temporal context, for which
no equally stable intermediate abstraction is available. Consequently, these later-stage tasks are often only partially grounded
in upstream outputs and, in many cases, require additional

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

SHENG et al.: REVERSE ENGINEERING OF INDUSTRIAL PROTOCOLS FROM NETWORK TRAFFIC

TABLE II
DATASETS USED IN INDUSTRIAL PRE RESEARCH

evidence rather than continuing earlier-stage inference. Later
reasoning stages therefore inherit intermediate assumptions that
are often difficult to verify or revise, which may affect downstream robustness.
IV. DATASETS FOR INDUSTRIAL PRE
Table II summarizes datasets used in prior industrial PRE
studies. Viewed through the task-driven PRE pipeline, these
datasets support different stages of protocol knowledge recovery.
For message- and field-level tasks, datasets are often built from
protocol traces whose annotations are obtained with the aid
of protocol analyzers, such as Wireshark and manual verification. Such resources support message typing, syntax recovery,
and field-level semantic analysis. By contrast, datasets, such
as SWaT [100] and WADI [101], provide process-aware evidence, including network traffic, sensor/actuator readings, and
operational logs collected over sustained plant execution, and
are therefore more relevant to payload semantic inference and
behavior-oriented analysis.
Public dataset support remains uneven across PRE tasks.
Dataset resources are much more common for T1–T3, and to a
lesser extent for T4, whereas datasets that naturally support T5
and state-related analysis are fewer and are more often derived
from CPS testbeds than from protocol-format benchmarks. PRE
evaluation is therefore still most mature at the message and field
levels, while process-aware semantic understanding and behavior reconstruction depend on a smaller body of domain-specific
datasets.
V. SECURITY, PRIVACY, AND ETHICAL CONSIDERATIONS
As PRE becomes increasingly effective at uncovering the
structure and semantics of industrial communication protocols,
it also raises important security, privacy, and ethical concerns.
In industrial settings, PRE-derived knowledge can facilitate
protocol-conformant attacks, enable the inference of sensitive
operational information from network traffic, and expose proprietary protocol designs. This section examines these risks and
their implications for ICSs.
A. Security Issues
PRE fundamentally lowers the barrier for conducting
protocol-conformant attacks against ICSs. By recovering message formats, field semantics, and interaction logic from network
traces, PRE enables attackers to move beyond malformed or
random traffic and instead generate well-formed messages that
closely resemble legitimate control communications [29]. Such
capabilities directly undermine defenses that rely on syntactic

9

deviations or simple traffic anomalies as primary detection signals [22].
As PRE techniques advance toward semantic inference and
protocol state machine reconstruction, attackers gain increasingly fine-grained understanding of device behaviors and command sequences. This knowledge facilitates precise manipulation of device states and control workflows, enabling attacks that
are both semantically valid and operationally effective [16]. As
a result, attacks evolve from protocol-conformant interactions to
more sophisticated manipulations that exploit device logic and
control dependencies, weakening detection approaches based on
control invariants [23].
Furthermore, some PRE approaches rely on active interaction
or probing to validate inferred hypotheses [5]. While effective for
analysis, these techniques also demonstrate that even protocolcompliant traffic can alter device states or disrupt time-sensitive
control logic [76]. In adversarial settings, similar interaction patterns may be exploited to induce unsafe states or degrade system
availability, particularly in industrial environments where safety
margins are narrow and timing assumptions are critical.
B. Privacy Issues
PRE also raises significant privacy concerns by enabling the
extraction of sensitive operational and process-level information
from industrial network traffic [87]. Unlike traditional traffic
analysis, which often treats payloads as opaque, PRE aims to
recover the semantics encoded within protocol fields, including
process variables, control parameters, and device states [3].
Such information may reveal detailed insights into industrial
processes, production logic, and operational conditions that are
not intended to be externally observable.
Through large-scale or long-term traffic analysis, PRE can
further expose temporal patterns, control cycles, and correlations
among devices, allowing inference of production schedules,
process dependencies, and system bottlenecks. In industrial
settings, these inferred semantics may constitute proprietary
process knowledge or sensitive operational intelligence, the
disclosure of which could harm competitiveness or system
security [15]. Such privacy risks are amplified when PRE is
applied to traffic collected from shared networks, monitoring
infrastructures, or Internet-facing industrial services. Even in the
absence of explicit identifiers, reconstructed protocol semantics
and behavior patterns may enable fine-grained fingerprinting of
industrial deployments [1], raising concerns about data ownership, consent, and the unintended secondary use of inferred
process information [102].
C. Ethical Issues
The analysis and disclosure of proprietary industrial protocols through PRE introduce distinct ethical considerations.
Many industrial communication protocols are custom-designed
by vendors and intentionally undocumented, forming part of a
manufacturer’s intellectual property and competitive advantage [66]. PRE techniques that recover protocol specifications,
message semantics, or interaction logic can expose proprietary
protocol knowledge without vendor consent.
Beyond intellectual property concerns, public disclosure of
private protocol details may increase the exposure of deployed
systems to security risks, particularly for legacy devices that
cannot be easily patched or upgraded [28]. In practice, such
disclosures may reveal previously unknown attack surfaces or

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

10

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS

protocol behaviors, while corresponding mitigations remain
unavailable. In such cases, PRE research may unintentionally
shift risk onto operators who lack the resources or authority to
mitigate newly revealed vulnerabilities.
Moreover, the publication of detailed protocol artifacts and
semantics raises questions about responsible disclosure and
research boundaries. While PRE is often conducted for benign or
defensive purposes, the same outputs may be readily repurposed
for large-scale reconnaissance, exploitation, or unauthorized
system manipulation [27]. Balancing scientific transparency
with the potential for misuse remains an open ethical challenge
for the PRE research community.
VI. FUTURE RESEARCH DIRECTIONS
Building on the challenges identified across PRE tasks, as
well as the associated security, privacy, and ethical issues, we
highlight several future research directions that are critical for
advancing the robustness, generality, and responsible deployment of PRE techniques in industrial settings.
Data-centric benchmarking and evaluation: Many challenges
in PRE arise from the characteristics of traffic traces, including
limited diversity, insufficient coverage of protocol behaviors,
and varying data volume across studies. These factors substantially affect inference outcomes, yet are rarely modeled or evaluated explicitly. A problem is how to define PRE dataset quality in
a task-aware manner, since different tasks may depend on different properties of the underlying traces, such as message diversity,
field variability, behavior coverage, or temporal context. Future
work should focus on constructing benchmark datasets with
controlled characteristics and standardized evaluation protocols,
together with metrics that describe dataset properties in addition
to algorithmic performance. This would provide a stronger basis
for interpreting results and comparing methods.
Dependency-aware joint PRE across tasks: The most existing
PRE systems adopt loosely coupled pipelines in which message
typing, syntax inference, semantic inference, and state machine
reconstruction are treated as independent stages, allowing errors
from early stages to propagate to downstream inference. A key
future direction is the development of dependency-aware joint
PRE frameworks that explicitly model cross-task dependencies
and perform unified inference. Rather than committing to a single intermediate result, such frameworks should preserve uncertainty and exploit cross-task consistency signals, including semantic coherence and state-transition constraints, to iteratively
refine hypotheses. Moving beyond pipeline-style architectures
is essential for robustness under complex and heterogeneous
industrial protocols.
Large language model (LLM)-enabled semantic representation and reasoning for PRE: Recent advances in LLMs create
new opportunities for PRE by making it possible to reuse semantic knowledge across protocols at a much larger scale [59],
[103]. A key challenge is how to use LLMs to support semantic
inference without divorcing PRE from trace-based evidence.
Future work should investigate trace-conditioned semantic modeling, where recovered fields, value distributions, and interaction
contexts are aligned with LLM-generated semantic hypotheses
under explicit evidence constraints. This includes retrieval over
protocol specifications, documentation, or prior PRE artifacts,
with mechanisms for determining whether a semantic interpretation is supported by observed traces rather than merely plausible
in language space. Addressing this problem could improve

field-role inference and cross-protocol semantic transfer while
reducing hallucinated interpretations in industrial PRE.
Security-aware and ethically grounded PRE methodologies:
Increasingly capable and automated PRE techniques raise the
risk of misuse in industrial settings where protocol semantics are
tightly coupled with physical processes. Future research should
embed security, privacy, and ethical considerations directly into
the design of PRE methodologies, rather than treating them as
external constraints. This includes developing disclosure-aware
evaluation practices, limiting the exposure of sensitive operational semantics in released artifacts, and exploring abstractions
that preserve analytical value while reducing exploitability. Establishing community norms for responsible dataset sharing and
artifact release will be critical to ensuring that PRE advances
defensive understanding without disproportionately increasing
real-world risks. In addition, future work should explore practical applications of PRE in industrial environments, such as
protocol-aware intrusion detection and asset discovery, to ensure
that methodological advances translate into deployable defensive capabilities.
VII. CONCLUSION
This article presented a task-oriented review of network-tracebased PRE for industrial protocols. Despite recent advances that
have significantly expanded the scope and capability of PRE
techniques, fundamental challenges remain in data dependency,
inference reliability, and evaluation practice. Moreover, the
growing effectiveness of PRE raises important security, privacy,
and ethical considerations in industrial contexts. Addressing
these issues is essential for advancing PRE from isolated case
studies toward more systematic and deployable methodologies.
The insights from this paper provide a structured basis for future
PRE research and support the effective and responsible use of
PRE techniques for ICSs.
REFERENCES
[1] C. Sheng et al., “Network traffic fingerprinting for IIoT device identification: A survey,” IEEE Trans. Ind. Informat., vol. 21, no. 5, pp. 3541–3554,
May 2025.
[2] G. Han, Z. Xu, H. Zhu, Y. Ge, and J. Peng, “A two-stage model based on a
complex-valued separate residual network for cross-domain IIoT devices
identification,” IEEE Trans. Ind. Informat., vol. 20, no. 2, pp. 2589–2599,
Feb. 2024.
[3] Z. Yang, L. He, Y. Ruan, P. Cheng, and J. Chen, “Unveiling physical
semantics of PLC variables using control invariants,” IEEE Trans. Dependable Secur. Comput., vol. 22, no. 2, pp. 1400–1417, Mar.-Apr. 2025.
[4] Y. Ruan, C. Zhao, Z. Yang, Y. Shu, P. Cheng, and J. Chen, “PicaCAN:
Reverse engineering physical semantics of signals in CAN messages using physically-induced causalities,” IEEE Trans. Mob. Comput., vol. 24,
no. 7, pp. 5871–5887, Jul. 2025.
[5] Z. Luo et al., “DynPRE: Protocol reverse engineering via dynamic
inference,” in Proc. 31st Annu. Netw. Distrib. System Secur. Symp., NDSS,
2024, pp. 1–18.
[6] Z. Qin et al., “Reverse engineering industrial protocols driven by control
fields,” in Proc. IEEE INFOCOM 2024-IEEE Conf Comput Commun,
2024, pp. 2408–2417.
[7] D. Yang et al., “Patty: Pattern series-based semantics analysis for agnostic
industrial control protocols,” IEEE Trans. Inf. Forensics Secur., vol. 20,
pp. 5478–5491, 2025.
[8] Y. Huang, H. Shu, F. Kang, and Y. Guang, “Protocol reverse-engineering
methods and tools: A survey,” Comput. Commun., vol. 182, pp. 238–254,
2022.
[9] S. Katcher, J. Mattei, J. Chandler, and D. Votipka, “An investigation
of interaction and information needs for protocol reverse engineering
automation,” in Proc. CHI Conf. Hum. Factors Comput. Syst., 2025,
pp. 1–21.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

SHENG et al.: REVERSE ENGINEERING OF INDUSTRIAL PROTOCOLS FROM NETWORK TRAFFIC

[10] J. Chandler, A. Wick, and K. Fisher, “BinaryInferno: A semantic-driven
approach to field inference for binary message formats,” in Proc. 30th
Annu. Netw. Distrib. System Secur. Symp., NDSS, 2023, pp. 1–18.
[11] S. Zhao, S. Yang, Z. Wang, Y. Liu, H. Zhu, and L. Sun, “Crafting
binary protocol reversing via deep learning with knowledge-driven augmentation,” IEEE/ACM Trans. Netw., vol. 32, no. 6, pp. 5399–5414,
Dec. 2024.
[12] T. Huang, Y. Gao, Y. Zheng, Z. Wang, C. Hu, and A. Fu, “FineBID: Finegrained protocol reverse engineering for bit-level field identification,”
IEEE Trans. Dependable Secur. Comput., vol. 22, no. 3, pp. 2670–2686,
May-Jun. 2025.
[13] Q. Shi, X. Xu, and X. Zhang, “Extracting protocol format as state machine
via controlled static loop analysis,” in Proc. 32nd USENIX Secur. Symp.
(USENIX Secur. 23), 2023, pp. 7019–7036.
[14] J. Jiang, X. Zhang, C. Wan, H. Chen, H. Sun, and T. Su, “BinPRE:
Enhancing field inference in binary analysis based protocol reverse
engineering,” in Proc. ACM SIGSAC Conf. Comput. Commun. Secur.,
2024, pp. 3689–3703.
[15] Y. Qu et al., “ICEPRE: ICS protocol reverse engineering via data-driven
concolic execution,” in Proc. 35th ACM SIGSOFT Int. Symp. Softw.
testing Anal. (ISSTA ’25). ACM, 2025, pp. 2384–2406.
[16] Z. Luo et al., “Bleem: Packet sequence oriented fuzzing for protocol
implementations,” in Proc. 32nd USENIX Secur. Symp. (USENIX Security 23), 2023, pp. 4481–4498.
[17] J. Hu, D. Sun, W. Lu, J. Dong, and H. Wu, “Blockchain-enabled distributed authentication mechanism for industrial device access,” IEEE
Trans. Ind. Inform., vol. 21, no. 4, pp. 2819–2828, Apr. 2025.
[18] M. Zheng, D. Xie, Q. Shi, C. Wang, and X. Zhang, “Validating network protocol parsers with traceable RFC document interpretation,” in
Proc. 35th ACM SIGSOFT Int. Symp. Softw. testing Anal. ACM, 2025,
pp. 1772–1794.
[19] P. Fiterau-Brostean, B. Jonsson, R. Merget, J. De Ruiter, K. Sagonas, and
J. Somorovsky, “Analysis of DTLS implementations using protocol state
fuzzing,” in Proc. 29th USENIX Secur. Symp. (USENIX Secur. 20), 2020,
pp. 2523–2540.
[20] X. Feng, X. Zhu, Q.-L. Han, W. Zhou, S. Wen, and Y. Xiang, “Detecting
vulnerability on IoT device firmware: A survey,” IEEE/CAA J. Automatica Sinica, vol. 10, no. 1, pp. 25–41, Jan. 2023.
[21] M. Ammann, L. Hirschi, and S. Kremer, “DY fuzzing: Formal Dolev-Yao
models meet cryptographic protocol fuzz testing,” in Proc. IEEE Symp.
Secur. Privacy (SP)., 2024, pp. 1481–1499.
[22] A. A. Bhutta and A. N. Mian, “Robust defense against data reconstruction
attack in federated industrial intrusion detection systems,” IEEE Trans.
Ind. Informat., vol. 21, no. 10, pp. 7795–7804, Oct. 2025.
[23] S. G. Abbas, M. O. Ozmen, A. Alsaheel, A. Khan, Z. B. Celik, and
D. Xu, “SAIN: Improving ICS attack detection sensitivity via state-aware
invariants,” in Proc. 33rd USENIX Secur. Symp. (USENIX Security), 2024,
pp. 6597–6613.
[24] B. D. Sija, Y.-H. Goo, K.-S. Shim, H. Hasanova, and M.-S. Kim, “A
survey of automatic protocol reverse engineering approaches, methods,
and tools on the inputs and outputs view,” Sec. Comm. Netw., vol. 2018,
no. 1, 2018, Art. no. 8370341.
[25] S. Kleber, L. Maile, and F. Kargl, “Survey of protocol reverse engineering algorithms: Decomposition of tools for static traffic analysis,” IEEE Commun. Surv. Tutor., vol. 21, no. 1, pp. 526–561,
Firstquarter 2019.
[26] J. Duchêne, C. Le Guernic, E. Alata, V. Nicomette, and M. Kaâniche,
“State of the art of network protocol reverse engineering tools,”
J. Comput. Virol. Hack. Tech., vol. 14, no. 1, pp. 53–68, 2018.
[27] A. Buscemi, I. Turcanu, G. Castignani, A. Panchenko, T. Engel, and
K. G. Shin, “A survey on controller area network reverse engineering,”
IEEE Commun. Surv. Tutor., vol. 25, no. 3, pp. 1445–1481, thirdquarter
2023.
[28] Y. Wu, Z. Zhang, Z. Hetu, X. Cheng, and P. Cheng, “Reverse engineering of industrial control protocol: A survey,” Secur. Saf., vol. 4, 2025,
Art. no. 2025012.
[29] J. Cai, Z. Wei, and J. Luo, “ICS anomaly detection based on sensor
patterns and actuator rules in spatiotemporal dependency,” IEEE Trans.
Ind. Informat., vol. 20, no. 8, pp. 10647–10656, Aug. 2024.
[30] D. Yang et al., “InSyfer: Industrial control protocols syntax inference via
graph representation learning,” IEEE Trans. Dependable Secur. Comput.,
vol. 22, no. 6, pp. 7495–7507, Nov.-Dec. 2025.
[31] L. Yu et al., “Towards automatically reverse engineering vehicle diagnostic protocols,” in Proc. 31st USENIX Secur. Symp. (USENIX Security 22),
2022, pp. 1939–1956.

11

[32] M. E. Verma, R. A. Bridges, J. J. Sosnowski, S. C. Hollifield, and M. D.
Iannacone, “CAN-D: A modular four-step pipeline for comprehensively
decoding controller area network data,” IEEE Trans. Veh. Technol.,
vol. 70, no. 10, pp. 9685–9700, Oct. 2021.
[33] I. Bermudez, A. Tongaonkar, M. Iliofotou, M. Mellia, and M. M.
Munafo, “Automatic protocol field inference for deeper protocol understanding,” in Proc. IFIP Netw. Conf. (IFIP Networking), 2015,
pp. 1–9.
[34] Y. Ye, Z. Zhang, F. Wang, X. Zhang, and D. Xu, “NetPlier: Probabilistic
network protocol reverse engineering from message traces,” in Proc. 28th
Annu. Netw. Distrib. System Secur. Symp., NDSS, 2021, pp. 1–18.
[35] A. Rohl, M. Roughan, M. White, and A. Chambers, “Poster: Packet field
tree: A hybrid approach, open database and evaluation methodology for
automated protocol reverse-engineering,” in Proc. ACM SIGCOMM 2024
Conf.: Posters Demos, 2024, pp. 13–15.
[36] X. Yun, Y. Wang, Y. Zhang, and Y. Zhou, “A semantics-aware approach to
the automated network protocol identification,” IEEE/ACM Trans. Netw.,
vol. 24, no. 1, pp. 583–595, Feb. 2016.
[37] F. Sun, S. Wang, C. Zhang, and H. Zhang, “Clustering of unknown protocol messages based on format comparison,” Comput. Netw., vol. 179,
2020, Art. no. 107296.
[38] S. Kleber, R. W. van der Heijden, and F. Kargl, “Message type identification of binary network protocols using continuous segment similarity,”
in Proc. IEEE INFOCOM 2020-IEEE Conf. Comput. Commun., 2020,
pp. 2243–2252.
[39] Y. Ji, T. Huang, C. Ma, C. Hu, Z. Wang, and A. Fu, “IMCSA: Providing better sequence alignment space for industrial control protocol reverse engineering,” Sec. Comm. Netw., vol. 2022, no. 1, 2022,
Art. no. 8026280.
[40] M. Guo, Y. Zhu, and J. Fei, “ProInfer: Inference of binary protocol
keywords based on probabilistic statistics,” Comput. J., vol. 68, no. 2,
pp. 109–125, 2025.
[41] K.-S. Shim, Y.-H. Goo, M.-S. Lee, and M.-S. Kim, “Clustering method
in protocol reverse engineering for industrial protocols,” Int. J. Netw.
Manag., vol. 30, no. 6, 2020, Art. no. e2126.
[42] X. Sun, H. Li, Y. Chen, J. Cui, and H. Zhong, “Variable-length field
extraction for unknown binary network protocols,” in Proc. IEEE 49th
Conf. Local Comput. Netw., 2024, pp. 1–7.
[43] M. Zhu et al., “Adaptive header identification and unsupervised clustering
strategy for enhanced protocol reverse engineering,” Expert Syst. Appl.,
vol. 291, 2025, Art. no. 128467.
[44] H. Yan, X. Li, R. Dai, H. Li, X. Zhao, and F. Li, “MARS: Automated
protocol analysis framework for Internet of Things,” IEEE Internet
Things J., vol. 9, no. 19, pp. 18333–18345, Oct. 2022.
[45] W. Zhang, X. Meng, and Y. Zhang, “Dual-track protocol reverse analysis
based on share learning,” in Proc. IEEE INFOCOM 2022-IEEE Conf.
Comput. Commun., 2022, pp. 51–60.
[46] Y. Liu, Y. Ding, J. Jiang, B. Xiao, and S.-H. Yang, “Industrial control
protocol type inference using transformer and rule-based re-clustering,”
in Proc. IEEE INFOCOM 2024-IEEE Conf. Computer Commun., 2024,
pp. 1011–1020.
[47] K. Liang et al., “MDIplier: Protocol format recovery via hierarchical
inference,” in Proc. IEEE 35th Int. Symp. Softw. Rel. Eng. IEEE, 2024,
pp. 547–557.
[48] W. Cui, J. Kannan, and H. J. Wang, “Discoverer: Automatic protocol
reverse engineering from network traces,” in Proc. USENIX Secur. Symp.
Boston, MA, USA, 2007, pp. 1–14.
[49] S. Tao, H. Yu, and Q. Li, “Bit-oriented format extraction approach for
automatic binary protocol reverse engineering,” IET Commun., vol. 10,
no. 6, pp. 709–716, 2016.
[50] J. Pohl and A. Noack, “Automatic wireless protocol reverse engineering,”
in Proc. 13th USENIX Workshop Offensive Technol., 2019, pp. 1–13.
[51] S. Kleber, H. Kopp, and F. Kargl, “NEMESYS: Network message syntax
reverse engineering by analysis of the intrinsic structure of individual
messages,” in Proc. 12th USENIX Workshop Offensive Technol., 2018,
pp. 1–13.
[52] S. Kleber and F. Kargl, “Refining network message segmentation with
principal component analysis,” in Proc. IEEE Conf. Commun. Netw.
Secur., 2022, pp. 281–289.
[53] F. Sun, S. Wang, C. Zhang, and H. Zhang, “Unsupervised field segmentation of unknown protocol messages,” Comput. Commun., vol. 146,
pp. 121–130, 2019.
[54] Y. He et al., “A sparse protocol parsing method for IIoT based on
BPSO-vote-HMM hybrid model,” IEEE/ACM Trans. Netw., vol. 31, no. 2,
pp. 485–496, Apr. 2023.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

12

[55] G. Maohua, Z. Yuefei, and F. Jinlong, “SegInfer: Binary network protocol
segmentation based on probabilistic inference,” China Commun., vol. 22,
no. 6, pp. 334–354, 2025.
[56] O. Liu et al., “A data-driven approach for reverse engineering electric
power protocols,” J. Signal Process. Syst., vol. 93, no. 7, pp. 769–777,
2021.
[57] S. Zhao et al., “ProsegDL: Binary protocol format extraction by deep
learning-based field boundary identification,” in Proc. IEEE 30th Int.
Conf. Netw. Protoc. IEEE, 2022, pp. 1–12.
[58] G. Bossert, F. Guihéry, and G. Hiet, “Towards automated protocol reverse
engineering using semantic information,” in Proc. 9th ACM Symp. Inf.,
Comput. Commun. Secur., 2014, pp. 51–62.
[59] Y. Zhao et al., “Protocol syntax recovery via knowledge transfer,” Comput. Netw., vol. 258, 2025, Art. no. 111022.
[60] T. Tang, Y. Lai, and Y. Wang, “Relational reasoning-based approach for
network protocol reverse engineering,” Comput. Netw., vol. 230, 2023,
Art. no. 109797.
[61] L. De Carli, R. Torres, G. Modelo-Howard, A. Tongaonkar, and S. Jha,
“BotNet protocol inference in the presence of encrypted traffic,” in Proc.
IEEE INFOCOM 2017-IEEE Conf. Comput. Commun., 2017, pp. 1–9.
[62] G. Ládi, L. Buttyán, and T. Holczer, “Message format and field semantics
inference for binary protocols using recorded network traffic,” in Proc.
2018 26th Int. Conf. Softw., Telecommun. Comput. Networks, 2018,
pp. 1–6.
[63] Y.-H. Goo, K.-S. Shim, U.-J. Baek, and M.-S. Kim, “Two-pathway model
for enhancement of protocol reverse engineering,” KSII Trans. Internet
Inf. Syst., vol. 14, no. 11, pp. 4310–4330, 2020.
[64] S. Kleber, F. Kargl, M. State, and M. Hollick, “Network message field type
clustering for reverse engineering of unknown binary protocols,” in Proc.
52nd Annu. IEEE/IFIP Int. Conf. Dependable Syst. Netw. Workshops,
2022, pp. 80–87.
[65] M. Zhan, Y. Li, B. Li, J. Zhang, C. Li, and W. Wang, “Toward automated
field semantics inference for binary protocol reverse engineering,” IEEE
Trans. Inf. Forensics Secur., vol. 19, pp. 764–776, 2024.
[66] B. Ning, X. Zong, K. He, and L. Lian, “PREIUD: An industrial control protocols reverse engineering tool based on unsupervised learning
and deep neural network methods,” Symmetry, vol. 15, no. 3, 2023,
Art. no. 706.
[67] S. A. Qasim, W. Jo, and I. Ahmed, “PREE: Heuristic builder for reverse
engineering of network protocols in industrial control systems,” Forensic
Sci. International: Digit. Investigation, vol. 45, 2023, Art. no. 301565.
[68] G. Visky, A. Rohl, R. Vaarandi, S. Katsikas, and O. M. Maennel,
“Hacking on the high seas: How automated reverse-engineering can
assist vulnerability discovery of a proprietary communication protocol,”
in Proc. IEEE 49th Conf. Local Comput. Netw., 2024, pp. 1–7.
[69] X. Feng et al., “Snipuzz: Black-box fuzzing of IoT firmware via message
snippet inference,” in Proc. ACM SIGSAC Conf. Comput. Commun.
Secur., 2021, pp. 337–350.
[70] M. J. Varghese, F. Jiang, A. Rakib, R. Doss, and A. Anwar, “Reverse
engineering-guided fuzzing for CAN bus vulnerability detection,” in
Proc. Int. Conf. Inf. Secur. Appl., 2024, pp. 219–230.
[71] M. Marchetti and D. Stabili, “Read: Reverse engineering of automotive data frames,” IEEE Trans. Inf. Forensics Secur., vol. 14, no. 4,
pp. 1083–1097, Apr. 2019.
[72] B. C. Nolan, S. Graham, B. Mullins, and C. S. Kabban, “Unsupervised
time series extraction from controller area network payloads,” in Proc.
2018 IEEE 88th Veh. Technol. Conf., 2018, pp. 1–5.
[73] W. Choi, S. Lee, K. Joo, H. J. Jo, and D. H. Lee, “An enhanced method
for reverse engineering CAN data payload,” IEEE Trans. Veh. Technol.,
vol. 70, no. 4, pp. 3371–3381, Apr. 2021.
[74] M. A. Mokhadder, S. Bayan, and U. Mohammad, “An intelligent approach to reverse engineer CAN messages in automotive systems,” in
Proc. IEEE Int. Conf. Electro Inf. Technol., 2021, pp. 1–7.
[75] H. Zhang et al., “Payload state prediction based on real-time IoT network
traffic using hierarchical clustering with iterative optimization,” Sensors,
vol. 25, no. 1, 2024, Art. no. 73.
[76] X. Lin et al., “ByCAN: Reverse engineering controller area network
(CAN) messages from bit to byte level,” IEEE Internet Things J., vol. 11,
no. 21, pp. 35477–35491, Nov. 2024.
[77] R. Loh, Z. Dai, K. W. Fok, and V. L. Thing, “Automated protocol reverse
engineering with message format inference,” in Proc. IEEE Int. Conf.
Mach. Learn. Appl. Netw. Technol. IEEE, 2024, pp. 96–101.
[78] R. Ji, J. Wang, C. Tang, and R. Li, “Automatic reverse engineering of
private flight control protocols of UAVs,” Sec. Comm. Netw., vol. 2017,
no. 1, 2017, Art. no. 1308045.

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS

[79] B. Blumbergs and R. Vaarandi, “BBuzz: A bit-aware fuzzing framework
for network protocol systematic reverse engineering and analysis,” in
Proc. MILCOM 2017-2017 IEEE Mil. Commun. Conf. IEEE, 2017,
pp. 707–712.
[80] Z. Huang, K. Wu, S. Huang, Y. Zhou, and R. S. Giagone, “Automatic field
extraction of extended TLV for binary protocol reverse engineering,” in
Proc. Int. Conf. Comput. Commun. Netw. IEEE, 2022, pp. 1–10.
[81] Y. Liu, F. Zhang, Y. Ding, J. Jiang, and S.-H. Yang, “Sub-messages
extraction for industrial control protocol reverse engineering,” Comput.
Commun., vol. 194, pp. 1–14, 2022.
[82] H. Kim, S. Kim, W. Jo, K.-H. Kim, and T. Shon, “Unknown payload
anomaly detection based on format and field semantics inference in cyberphysical infrastructure systems,” IEEE Access, vol. 9, pp. 75542–75552,
2021.
[83] M. Zago et al., “ReCAN–dataset for reverse engineering of controller
area networks,” Data Brief, vol. 29, 2020, Art. no. 105149.
[84] M. Verma, R. Bridges, and S. Hollifield, “ACTT: Automotive CAN
tokenization and translation,” in Proc. Int. Conf. Comput. Sci. Comput.
Intell., 2018, pp. 278–283.
[85] M. D. Pesé et al., “LibreCAN: Automated CAN message translator,” in Proc. ACM SIGSAC Conf. Comput. Commun. Secur., 2019,
pp. 2283–2300.
[86] D. Frassinelli, S. Park, and S. Nürnberger, “I know where you parked last
summer: Automated reverse engineering and privacy analysis of modern
cars,” in Proc. IEEE Symp. Secur. Privacy, 2020, pp. 1401–1415.
[87] J. Cai, W. Zhong, and J. Luo, “SeMiner: Side-information-based semantics miner for proprietary industrial control protocols,” IEEE Internet
Things J., vol. 9, no. 22, pp. 22796–22810, Nov. 2022.
[88] D. Pratama et al., “Behind the wings: The case of reverse engineering
and drone hijacking in DJI enhanced Wi-Fi protocol,” in Proc. 2024 Int.
Conf. Platform Technol. Service. IEEE, 2024, pp. 127–132.
[89] A. Buscemi, I. Turcanu, G. Castignani, R. Crunelle, and T. Engel,
“CANMatch: A fully automated tool for CAN bus reverse engineering
based on frame matching,” IEEE Trans. Veh. Technol., vol. 70, no. 12,
pp. 12358–12373, Dec. 2021.
[90] M. A. Telfor, B. R. Payne, and T. T. Abegaz, “Reverse engineering the can
bus: Vulnerability analysis in the tesla model 3,” in Proc. World Congr.
Comput. Sci., Comput. Eng. Appl. Comput., 2024, pp. 478–489.
[91] C. Lee, J. Bae, and H. Lee, “PRETT: Protocol reverse engineering using
binary tokens and network traces,” in Proc. IFIP Int. Conf. ICT Syst.
Secur. Privacy Protection, 2018, pp. 141–155.
[92] J. Yang, F. Li, Y. Zhang, J. Zhang, L. Fang, and Y. Guo, “Automatic
state machine inference for binary protocol reverse engineering,” in
Proc. GLOBECOM 2025-2025 IEEE Global Commun. Conf., 2025,
pp. 2922–2927.
[93] Y. Yang, Y. Geng, Q. Wei, R. Ma, and Z. Wei, “IPSMInfer: Industrial
proprietary protocol state machine inference from network traces,” Int.
J. Crit. Infrastruct. Prot., vol. 49, 2025, Art. no. 100765.
[94] Y. Wang, Z. Zhang, D. Yao, B. Qu, and L. Guo, “Inferring protocol state
machine from network traces: A probabilistic approach,” in Proc. Int.
Conf. Appl. Cryptogr. Netw. Secur., 2011, pp. 1–18.
[95] G. Ládi and T. Holczer, “On the performance evaluation of protocol state
machine reverse engineering methods,” J. commun. softw. syst., vol. 20,
no. 1, pp. 76–87, 2024.
[96] C. Lee, I. Jafarov, S. Dietrich, and H. Lee, “PRETT 2: Discovering
http/2 DOS vulnerabilities via protocol reverse engineering,” in Proc.
Eur. Symp. Res. Comput. Secur., 2024, pp. 3–23.
[97] Y.-D. Lin, Y.-K. Lai, Q. T. Bui, and Y.-C. Lai, “ReFSM: Reverse
engineering from protocol packet traces to test generation by extended finite state machines,” J. Netw. Comput. Appl., vol. 171, 2020,
Art. no. 102819.
[98] G. Székely, G. Ládi, T. Holczer, and L. Buttyán, “Protocol state machine
reverse engineering with a teaching-learning approach,” Acta Cybernetica, vol. 25, no. 2, pp. 517–535, 2021.
[99] A. Rohl, M. Roughan, M. White, and A. Chambers, “Packet field tree:
A hybrid approach for automated protocol reverse-engineering,” in Proc.
9th Int. Conf. Commun., Image Signal Process. IEEE, 2024, pp. 160–169.
[100] J. Goh, S. Adepu, K. N. Junejo, and A. Mathur, “A dataset to
support research in the design of secure water treatment systems,”
in Proc. Int. Conf. Crit. Inf. Infrastructures Secur. Springer, 2016,
pp. 88–99.
[101] C. M. Ahmed, V. R. Palleti, and A. P. Mathur, “WADI: A water distribution testbed for research in the design of secure cyber physical systems,”
in Proc. 3rd Int. workshop cyber- Phys. Syst. Smart Water Netw., 2017,
pp. 25–28.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

SHENG et al.: REVERSE ENGINEERING OF INDUSTRIAL PROTOCOLS FROM NETWORK TRAFFIC

[102] K. Jin and D. Ye, “Actuator and sensor attacks against multisensor state
estimation with round-robin protocol,” IEEE Trans. Ind. Inform., vol. 21,
no. 5, pp. 3636–3644, May 2025.
[103] X. Zhu, W. Zhou, Q.-L. Han, W. Ma, S. Wen, and Y. Xiang, “When
software security meets large language models: A survey,” IEEE/CAA J.
Autom. Sinica, vol. 12, no. 2, pp. 317–334, 2025.

Chuan Sheng (Member, IEEE) received the
Ph.D. degree in computer science from Northeastern University, Shenyang, China.
He joined the Shenyang Institute of Automation, Chinese Academy of Sciences, Shenyang,
China, in 2022, and is also a Visiting Postdoc
with the Swinburne University of Technology,
Hawthorn, VIC, Australia. His research interests
include industrial cybersecurity, network traffic
analysis, and ICS device identification.

Shan Jiang received the M.S. degree from the
School of Artificial Intelligence, Guangzhou University, Guangzhou, China, in 2025. He is currently working toward the Ph.D. degree with the
School of Science, Computing and Engineering
Technologies, Swinburne University of Technology, Melbourne, VIC, Australia.
His research focuses on network security.

Qing-Long Han (Fellow, IEEE) received the
B.Sc. degree in mathematics from Shandong
Normal University, Jinan, China, in 1983, and
the M.Sc. and Ph.D. degrees in control engineering from the East China University of Science and Technology, Shanghai, China, in 1992
and 1997, respectively.
He is Pro Vice-Chancellor (Research Quality)
and a Distinguished Professor with the Swinburne University of Technology, Melbourne, VIC,
Australia. He held various academic and management positions with Griffith University, Nathan QLD, Australia, and
Central Queensland University, Melbourne VIC, Australia. His research
interests include networked control systems, multiagent systems, timedelay systems, smart grids, unmanned surface vehicles, and neural
networks.
Professor Han was the recipient of the 2024 IEEE Dr.-Ing. Eugene
Mittelmann Achievement Award, the 2024 Chinese Association of Automation Science and Technology Achievement Award, the 2021 Norbert Wiener Award, the 2021 M. A. Sargent Medal, the IEEE Systems,
Man, and Cybernetics Society Andrew P. Sage Best Transactions Paper
Award in 2019, 2020, and 2022, the IEEE/CAA Journal of Automatica
Sinica Norbert Wiener Review Award in 2020, and the IEEE Transactions on Industrial Informatics Outstanding Paper Award in 2020. He is
a Member of the Academia Europaea and a Fellow of the International
Federation of Automatic Control, the Asian Control Association, and
the Chinese Association of Automation. He is also an Honorary Fellow
of the Institution of Engineers Australia and a Clarivate Highly Cited
Researcher in both Engineering and Computer Science. He was an
AdCom Member of IEEE Industrial Electronics Society (IES), a Member
of the IEEE IES Fellows Committee and Publications Committee, Chair
of the IEEE IES Technical Committee on Network-Based Control Systems and Applications, and Co-Editor-in-Chief of IEEE TRANSACTIONS
ON INDUSTRIAL INFORMATICS. He is currently President-Elect, an Executive Board Member, and a Steering Committee Member of the Asian
Control Association, Vice-President of the Chinese Association of Automation, Editor-in-Chief of IEEE/CAA Journal of Automatica Sinica, and
Co-Editor of Australian Journal of Electrical and Electronic Engineering.

13

Wei Zhou received the B.Eng. and M.Eng.
degrees in CS from Central South University,
Changsha, China, in 2005 and 2008, respectively, and the Ph.D. degree in computer science
from the School of Engineering and IT, University of New South Wales, Canberra, NSW, Australia, in 2016.
Her research interests include computer networks, network security, and fingerprint biometric.

Wanlun Ma (Member, IEEE) received the bachelor’s and master’s degrees in information and
communication engineering from the University
of Electronic Science and Technology of China,
China, in 2017 and 2020, respectively, and the
Ph.D. degree in computer science from the
Swinburne University of Technology, Hawthorn,
VIC, Australia, in 2024.
He is currently a Research Fellow with the
Swinburne University of Technology. His research interests focus on responsible AI, adversarial machine learning, and network security and privacy.
Xiaogang Zhu (Member, IEEE) received the
Ph.D. degree in computer science and engineering from the Swinburne University of Technology Hawthorn, VIC, Australia.
He is currently a Lecturer with Adelaide University, Adelaide, SA, Australia, and focuses
on searching vulnerabilities in programs. He
has published papers on top journals, such as
TDSC, and conferences, such as CCS, USENIX
Security, and ICSE. His research interests include detecting techniques such as fuzzing, machine learning, and symbolic execution.
Dr. Zhu was a Reviewer for many top journals, such as TDSC, IoTJ,
and CSUR.
Sheng Wen (Senior Member, IEEE) received
the Ph.D. degree from Deakin University, Melbourne, VIC, Australia, in October 2014.
He is currently working as an Associate Professor with the Swinburne University of Technology, Melbourne. He is now the Director of
Blockchain Innovation Lab and the Deputy Director of Swinburne Cybersecurity Lab in Swinburne University. He is also leading a mediumsized research team with co-/supervised Ph.D.
students in the system security area. In addition, he has authored or coauthord more than 100 high-quality papers,
including top conference papers such as papers in IEEE S&P, ACM
CCS, NDSS, ICSE and FSE, as well as many papers in IEEE/ACM
transactions series journals.
Yang Xiang (Fellow, IEEE) received the Ph.D.
degree in computer science from Deakin University, Melbourne, VIC, Australia.
He is currently a Full Professor and the Dean
of Digital Research, Swinburne University of
Technology, Melbourne. In the past 20 years,
he has authored or coauthored more than 300
research papers in many international journals
and conferences. His research interests include
cyber security, which covers network and system security, data analytics, distributed systems,
and networking.
Dr. Xiang is the Editor-in-Chief of the SpringerBriefs on Cyber Security
Systems and Networks. He was the Associate Editor for IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, IEEE INTERNET OF
THINGS JOURNAL, and ACM Computing Surveys. He is the Coordinator,
Asia for IEEE Computer Society Technical Committee on Distributed
Processing, and the Chair of the Australia and New Zealand, and IEEE
Blockchain Technical Community.
PAPER_TEXT
