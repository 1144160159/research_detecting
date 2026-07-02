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
# [791] RL-ACID: Reinforcement Learning-Optimized Adaptive Causal Discovery for Robust Anomaly Detection in Industrial Systems
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
编号：791
题名：RL-ACID: Reinforcement Learning-Optimized Adaptive Causal Discovery for Robust Anomaly Detection in Industrial Systems
年份：2026
DOI：10.1109/tii.2026.3650787
来源：IEEE Transactions on Industrial Informatics
PDF：paper/10.1109_TII.2026.3650787.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 12
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\791.txt
- 原始字符数：63213
- 本次发送字符数：63213
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
3646

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 5, MAY 2026

RL-ACID: Reinforcement Learning-Optimized
Adaptive Causal Discovery for Robust Anomaly
Detection in Industrial Systems
Hechen Yang , Yu Yao , Member, IEEE, Licheng Yang , and Wei Yang

Abstract—Anomaly detection is essential for the security
of industrial control systems. However, dynamic operating conditions introduce nonstationarity and time-varying
causal structures, degrading performance and undermining interpretability. To address this, we propose RL-ACID,
a lightweight reinforcement learning framework for adaptive causal discovery. It reformulates anomaly detection
as sequential causal discovery, introducing the first unified architecture that integrates lightweight reinforcement
learning-based search with causal clustering to resolve
the adaptability, efficiency, and interpretability tradeoff. Our
framework employs a joint time-frequency encoder to extract and construct candidate causal graphs. Building upon
this, we design the causal reinforcement learning-based
lightweight search algorithm, which formulates graph exploration as a sequential decision process under sparsity and acyclicity constraints, enabling iterative causal
structure optimization. To further enhance adaptability in
dynamic environments, we introduce a causal clustering
module that softly assigns time-varying graphs to latent
operational modes through structural experts, thereby
distinguishing normal operational fluctuations from true
anomalies. Extensive experiments on multiple industrial
benchmarks demonstrate the superior performance of RLACID. Our framework not only achieves higher accuracy
than baselines but also provides interpretable anomaly
analysis through causal path tracing.
Index Terms —Anomaly detection, causal discovery, industrial control system (ICS), reinforcement learning (RL).

I. INTRODUCTION
NDUSTRIAL control systems (ICS) are an essential component of modern infrastructure. They facilitate the automated
control and monitoring of intricate physical processes in vital
sectors, such as energy, manufacturing, and transportation. However, as ICS environments grow in scale and complexity and integrate more deeply with information networks, new challenges

I

Received 31 October 2025; revised 12 December 2025; accepted 30
December 2025. Date of publication 27 January 2026; date of current
version 6 May 2026. Paper no. TII-25-7720. (Corresponding author:
Yu Yao.)
Hechen Yang, Yu Yao, and Licheng Yang are with the College of Computer Science and Engineering, Northeastern University,
Shenyang 110169, China (e-mail: 2490267@stu.neu.edu.cn; yaoyu@
mail.neu.edu.cn; 2310749@stu.neu.edu.cn).
Wei Yang is with the College of Software, Northeastern University,
Shenyang 110169, China (e-mail: yangwei@mail.neu.edu.cn).
Digital Object Identifier 10.1109/TII.2026.3650787

Fig. 1. Causal structure evolution of sensors V1 –V5 across operational
conditions (HIL-HAI dataset, PCMCI+ algorithm). Edge thickness denotes causal strength. (V1 : Boiler flow; V2 : Pressure; V3 : Valve; V4 :
Vibration; V5 : Water flow).

to system reliability and security emerge. In ICS, anomalies
and faults may originate from equipment degradation, malicious
attacks, or operational mistakes. These disturbances have the potential to rapidly propagate across interdependent components,
with the consequence of significant system failures [1].
In order to ensure the stable operation of ICS, it is essential
to accurately identify and interpret abnormalities, which have
become pivotal tasks. In recent years, data-driven methods have
made significant progress in anomaly detection, primarily based
on machine learning and deep learning models, which show
better detection performance [2]. However, such approaches still
face significant challenges in industrial real-world scenarios.
The majority of models are predicated on statistical correlation
between system variables, with the underlying causal relationships being ignored. This reduces interpretability and obstructs
root cause analysis.
Furthermore, it is noteworthy that varying operating conditions in ICS often lead to dynamic changes in the underlying
causal structure [3]. We investigated this with the hardwarein-the-loop based augmented industrial control system security
(HAI) dataset [4], which contains data from a boiler, a turbine,
and a water treatment system. We applied the Peter–Clark
momentary conditional independence plus (PCMCI+) [5] algorithm to perform causal discovery analysis, focusing on five
representative sensors (V1 to V5 ) across three operational modes
to illustrate causal drift. As shown in Fig. 1, both the causal
connections and their strength, indicated by edge thickness,
changed substantially across different operating modes. These
changes reflect system-wide adaptive behavior. Our observations were consistent with sensor descriptions documented in
the HAI literature, confirming that causal drift is a common
rather than an isolated phenomenon.

1941-0050 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html
for more information.

YANG et al.: RL-ACID: RL-OPTIMIZED ADAPTIVE CAUSAL DISCOVERY FOR ROBUST ANOMALY DETECTION IN INDUSTRIAL SYSTEMS

Most current anomaly detection models assume that training and monitoring data are independent and identically distributed [6]. However, real ICS exhibit nonstationary behavior
due to their complex structure and variable load conditions. This
distribution drift compromises model robustness and generalization. Therefore, it is essential to develop adaptive models that
can track causal changes over time to enable reliable anomaly
detection in dynamic ICS environments.
Current anomaly detection approaches fall into statistical and
machine learning categories [7]. Traditional statistical methods identify anomalies by measuring deviations from normal
baselines using standard deviation, distance, or density metrics.
Techniques like wavelet analysis perform well in periodic simulations but struggle with the high-dimensional, nonstationary
nature of ICS data, making it difficult to capture the complex
sensor interactions inherent to such environments.
Deep learning advances ICS anomaly detection through neural networks and convolutional architectures that capture complex temporal patterns [8]. However, these models learn statistical correlations rather than causal mechanisms, limiting
interpretability and constraining the ability to explain anomaly
generation and propagation.
Graph-based methods leverage graph neural networks to capture interdependencies among sensors [9]. Recent advances have
introduced dynamic line graphs [10] and federated contrastive
frameworks [11] to enhance intrusion detection in network systems, focusing on topological interactions. These approaches
are effective at modeling topological interactions for network
intrusion detection. However, in dynamic industrial control environments where causal relationships evolve with operational
conditions, a key challenge remains in adaptively discovering
the underlying time-varying graph structures from data, rather
than relying on predefined or static assumptions.
Causal discovery methods have gained attention for enhancing interpretability in anomaly detection. While traditional constraint-based [12] and score-based approaches like
the PCMCI+ algorithm infer causality from correlations under strong assumptions, they typically presume static causal
structures—limiting their applicability in dynamic industrial
environments. Recent work by Chen et al. [13] introduced a root
cause identification method using causal graphs and maximum
spanning trees, while Qiu et al. [14] proposed a knowledge graph
and causal mining approach for root cause analysis. However,
these methods often rely on static causal models, which may
miss evolving relationships and lead to undetected anomalies.
Furthermore, within ICS, large-scale combinatorial searches and
repeated statistical evaluations on high-dimensional data result
in high computational costs.
In recent years, reinforcement learning (RL) has emerged
as a promising approach for dynamic environments due to its
inherent capacity for sequential decision-making and adaptation [15]. This makes it particularly well-suited for scenarios
where the underlying system properties evolve over time [16].
However, the RL methods often focus on myopic optimization at each step, which demands substantial computational
resources through iterative feedback and can hinder their ability to track long-term structural dynamics. Consequently, their

3647

effectiveness in resource-constrained systems like ICS, especially for sustained anomaly detection tasks, remains limited.
Based on the above analysis, we identify three major challenges in current research: M1: Causal drift: Conventional
static models and anomaly detection methods cannot adapt to
dynamic industrial settings. Time-varying causal relationships
among sensors reduce model robustness and lead to performance
degradation in complex ICS. M2: High computational cost:
Methods such as causal discovery and RL require substantial
computational resources. This makes them difficult to deploy
in practical industrial anomaly detection scenarios where efficiency is critical. M3: Lack of interpretability: Most models rely
on statistical correlations, which fail to capture the underlying
causal mechanisms of anomalies. This limitation hinders the
understanding of anomaly propagation and root cause analysis
in complex systems.
To overcome these limitations, we propose reinforcement learning-optimized adaptive causal discovery for robust
anomaly detection (RL-ACID), a lightweight and adaptive
causal discovery framework for industrial systems. As illustrated
in Fig. 2, our framework comprises three key components. First,
we design a sparsity-aware time-frequency transformer encoder
to capture both transient dynamics and long-range periodic
dependencies in sensor data. This encoder generates compact
multiscale representations, which are then processed by a probabilistic decoder to produce an initial weighted adjacency matrix.
This matrix serves as a data-informed prior for subsequent causal
search (see Section III-A).
Second, we introduce the causal reinforcement learning-based
lightweight (CaRLite) algorithm, a lightweight RL-based causal
search mechanism. It formulates graph exploration as a sequential decision process, guided by a reward function that
promotes data fidelity, acyclicity, and sparsity. Through hierarchical experience replay and causal drift detection, CaRLite
efficiently mitigates causal drift (M1) while maintaining high
computational efficiency (M3) (see Section III-B).
Finally, to further handle time-varying dependencies, we design a causal clustering module that monitors structural drift by
maintaining a set of representative causal graphs learned across
different operating modes. A causal inference-based anomaly
detection module quantifies deviations from expected behavior
and traces causal paths, offering interpretable insights into root
causes (M3) (see Section III-C).
The main contributions of this article are as follows.
1) Novel integration paradigm: We propose RL-ACID, the
first framework that integrates RL-based causal discovery with
sparse attention for industrial anomaly detection, enabling synergistic adaptation between temporal patterns and structural
constraints.
2) Lightweight causal discovery: We design CaRLite, a
constrained RL algorithm that achieves 68% efficiency gains
through intelligent experience management, resolving the
complexity-deployability tradeoff in causal learning.
3) Dynamic adaptation: We develop a causal clustering module that autonomously distinguishes structural drift from normal
fluctuations, enabling continuous adaptation to evolving industrial processes.

3648

Fig. 2.

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 5, MAY 2026

Architecture of the RL-ACID model.

4) Theoretical-practical validation: Extensive experiments
demonstrate RL-ACID’s comprehensive superiority in detection
accuracy, interpretability, and computational efficiency, confirming robust performance under dynamic ICS conditions.

TABLE I
COMPARATIVE ANALYSIS OF ANOMALY DETECTION METHODS AGAINST KEY
REQUIREMENTS FOR DYNAMIC ICS (BOLD VALUES HIGHLIGHT RL-ACID AS
THE PROPOSED METHOD)

II. PROBLEM STATEMENT, MOTIVATION, AND NOVELTY
A. Problem Formulation
Dynamic industrial environments present three fundamental
challenges for reliable anomaly detection: causal drift (M1),
computational constraints (M2), and interpretability demands
(M3). As illustrated in the example of Fig. 1, where sensor
relationships evolve with operational modes, these challenges
necessitate reformulation anomaly detection as a time-varying
causal discovery and adaptive learning problem.
Formally, we consider a nonstationary multivariate time series
X ∈ RT ×D , collected from an ICS with D sensors over T
time steps. This time series exhibits inherent nonstationarity
due to dynamic operating conditions. The objective of this
work is twofold. First, we aim to learn a time-varying causal
graph Gt = (V, Et ) that captures dynamic dependencies among
sensors, where V denotes the set of sensor nodes and Et represents the time-evolving causal edges. Second, we seek to derive
a lightweight and interpretable detection function f (X, Gt ),
which reliably distinguishes true anomalies from normal operational fluctuations while providing causal explanations for
its decisions.
This formulation leads to three key requirements that address
challenges M1–M3. Adaptive causal discovery (R1) requires
tracking the evolution of Et over time without relying on stationarity assumptions, thereby addressing causal drift. Computational efficiency (R2) necessitates a lightweight learning framework suitable for resource-constrained ICS edge environments.
Interpretable inference (R3) entails that anomaly decisions be
explainable through causal paths in Gt to support root cause
diagnosis.
B. Research Motivation
The primary motivation for this work arises from a systematic
limitation observed in current methods: their inability to fulfill requirements R1–R3 concurrently. As demonstrated by the
analysis in Section I and illustrated in Fig. 1, this shortcoming
remains a persistent challenge, despite advances reported in
individual aspects of prior studies. This gap is further illustrated

by the comparative analysis of existing methods presented in
Table I.
Statistical methods assume stationarity and capture only correlations, failing to address the M1. Deep learning approaches
operate as opaque models without causal reasoning, lacking
M3. Graph neural networks typically rely on static graph structures, while static causal discovery methods cannot handle timevarying causality. Although dynamic causal models incorporate
temporal dynamics, they suffer from M2 and linearity constraints. RL methods demonstrate adaptability but lack causal
interpretability and exhibit high computational costs. The critical research gap identified through this analysis is the absence of
methods that can simultaneously achieve adaptive causal discovery, computational efficiency, and interpretable reasoning. This
limitation directly motivates the development of our framework
to bridge these interdependent requirements.
C. Novelty
The novelty of the RL-ACID framework is defined not merely
by enhanced accuracy, but by its integrated causal architecture
that systematically resolves the three intertwined challenges
(R1–R3) in a unified, adaptive manner.
Architectural integration: RL-ACID represents the first
framework that integrates lightweight reinforcement learningbased causal search (CaRLite), time-frequency causal encoding, and causal clustering into an end-to-end pipeline. This
holistic design consciously addresses adaptation, efficiency, and
interpretability as interdependent objectives rather than optimizing them in isolation.

YANG et al.: RL-ACID: RL-OPTIMIZED ADAPTIVE CAUSAL DISCOVERY FOR ROBUST ANOMALY DETECTION IN INDUSTRIAL SYSTEMS

3649

Technical innovations: At the component level, we introduce
three key innovations. For adaptive causal discovery (R1), we
develop a causal clustering module with structural experts and
soft assignment that enables unsupervised identification and
smooth switching between time-varying causal regimes. For
computational efficiency (R2), we design structured sparse attention [lightweight industrial sparse attention for time-series
modeling (LISA)] and prior-constrained RL search (CaRLite)
to achieve algorithmic-level optimizations suitable for edge
deployment. For interpretable inference (R3), the framework
centers on causal graphs as intermediate representations, incorporating causal path tracing to transition from anomaly detection
to root-cause diagnosis.
The subsequent section details the methodological implementation of the RL-ACID framework, building upon these
foundational contributions.

III. RL-BASED ANOMALY DETECTION FRAMEWORK FOR
CAUSAL DISCOVERY

Fig. 3. Architecture of the encoder–decoder model for causal structure
modeling.

A. Data Coding and Feature Representation
In causal discovery tasks, high-quality time-series representations are crucial for ensuring the accuracy of structural searches.
In ICS time series, it has been shown that combining timedomain and frequency-domain features enhances feature extraction [17]. To more effectively capture both temporal and spectral
characteristics in multivariate industrial time series, we propose
a time-frequency enhanced transformer encoder–decoder architecture as a unified framework for causal feature modeling and
causal graph generation. By integrating a self-attention mechanism with directed acyclic graph (DAG) structural constraints,
the architecture effectively reveals potential causal relationships
among variables.
Encoder: Time–frequency causal feature extraction. To enhance the characterization of anomalous causal pathways, we
introduce a hybrid encoder that integrates time–frequency analysis with temporal modeling. Raw multivariate sensor signals
are segmented into local blocks Xt ∈ RW ×D using a sliding
window. Each block is transformed into the frequency domain
via fast Fourier transform, producing a complex-valued representation F(t) ∈ CW ×D . The amplitude spectrum |F(t)| is
normalized to improve robustness to temporal misalignments
and capture global spectral structures. Such time–frequency
representations have been shown to complement time-domain
features by modeling long-range dependencies and dynamic
couplings in nonstationary industrial processes [18]. The resulting spectral representation is fused with temporal features
to form a hybrid encoding. This joint representation enhances
multiscale feature characterization while preserving both temporal dynamics and spectral regularities, providing a stronger basis
for identifying stable periodic causal relationships essential for
downstream inference in complex industrial environments.
Subsequently, a multiscale frequency-domain convolutional
module extracts discriminative spectral features, emphasizing
oscillatory patterns and multivariable interactions through hierarchically stacked convolutional operations. The extracted

Fig. 4. Architecture for causal discovery with reinforcement learningoptimized dynamic structure learning.

spectral features are concatenated with the time-domain representations, yielding a unified time–frequency feature vector
that provides causally informative input to the transformer.
LISA: Industrial monitoring data exhibit quasi-periodic patterns and response delays, with most causal influences confined
to short temporal neighborhoods and only a few long-cycle
effects at characteristic lags. Conventional self-attention captures these dependencies at high computational cost—scaling
as O(W 2 D2 ) for long windows or many sensors. To reduce
complexity, LISA employs a structurally guided sparse selfattention mechanism [see Fig. 3(a)]. For each token (t, i), a
binary mask M restricts attention to (i) a local temporal band
of radius r around t for short-term causal interactions and (ii)
dilated sampling points with stride Δ for delayed and long-range
periodic effects.
Formally, the input features H ∈ Rn×d are projected into
query, key, and value matrices using learnable weight matrices WQ , WK , WV , where WQ , WK ∈ Rd×dK and WV ∈
Rd×dV . The sparse self-attention for the ith head is then computed as


Qi K
i
+ log Mi Vi
(1)
Headi = Softmax √
dK

3650

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 5, MAY 2026

where log Mi assigns 0 to valid entries and −∞ to masked positions so excluded interactions are not included in the softmax.
With band radius r, dilated count K, and optional subsampling stride p, LISA ensures that each query attends to
at most B ≈ (2r + K) + W/p keys—typically B
W D.
This reduces the computational complexity from O(W 2 D2 ) to
O(W DB) while retaining the ability to capture both immediate
causal dynamics and delayed periodic effects that are characteristic of nonstationary industrial environments and critical for
downstream causal discovery.
Decoder: Causal graph structure generation: The specialized
decoder module [see Fig. 3(b)], built upon a time-frequency
encoder for multivariate ICS, generates causal structures from
the encoded representations. Unlike traditional decoders used
for regression or classification tasks, this module generates
directed edges directly between variables to construct a directed
DAG that drives RL optimization. This design ensures a tight
coupling between causal modeling and data representation. The
decoder efficiently converts the joint time-frequency representation into causal relationships to form the initial causal graph
G = (V, E). Although not based on traditional causal discovery
algorithms, the graph represents plausible causal relationships
because the edges encode directional dependencies inferred
from time-frequency features. Subsequent optimization using
the Bayesian information criterion (BIC) and linear parent-child
modeling further supports interpreting this graph as a causal
structure.
Given the encoder outputs [Enc1 , Enc2 , . . ., Encn ], which encode both temporal and frequency-domain dependencies across
variables, the decoder estimates pairwise causal relations via a
neural scoring mechanism. For any variable pair (i, j), the edge
existence probability is computed as
 

Aij = Bernoulli σ u tanh(W1 Enci + W2 Encj )
(2)
where W1 , W2 are learnable linear transformation matrices,
u is the causality score vector, and σ(·) denotes the Sigmoid
function. This process models the probability for each edge in
the adjacency matrix A. To enforce acyclicity, a smooth DAG
constraint [19] is applied during training. After training, we
retain the top-k edges with the highest probabilities and project
them onto an acyclic graph. This produces a high-confidence
coarse causal graph that not only confines the initial search
space for the subsequent RL but also significantly enhances
computational efficiency without compromising detection performance. This decoder also acts as the policy model in the
RL framework, whose edge probabilities define a structured
action space and are optimized via policy gradient methods to
maximize a reward function combining causal plausibility and
detection performance (see Section III-B).
B. RL-Based Causal Structure Search
We formulate causal discovery under dynamic industrial conditions as a sequential decision process. To tackle causal drift
and computational complexity, the proposed RL framework is
built around a structured environment, a sparsity-aware reward,
and an experience replay system, which collectively enable an
adaptive and efficient search (see Fig. 4 and Algorithm 1). The

Algorithm 1: CaRLite: Lightweight Causal Structure
Search.

framework comprises three core components: an environment
model, an agent model, and the causal RL-based structure search
(CaRLite) algorithm. Integrating them via hierarchical experience management, CaRLite achieves a 68% gain in computational efficiency through intelligent reuse.
1) Environment model: The RL environment models the adaptive causal discovery process as a dynamic agent-environment
interaction (Algorithm 1, line 3–6). Within this framework,
the agent iteratively explores and refines candidate DAGs, receiving feedback after each structural change. To enable stable
and efficient policy learning, the environment provides a wellstructured state representation (Algorithm 1, line 3) and a reward
mechanism (Algorithm 1, line 6) that guides the agent toward
uncovering causal relationships that are both fine-grained and
reflective of the current process.
State-space construction (Algorithm 1, line 3) integrates the
candidate adjacency matrix with edge-level descriptors φij ,
which combine structural features, score-based metrics, decoder
priors, and DAG constraints. This design provides the agent with
essential structural and statistical cues while keeping per-step
computation tractable.
Reward mechanism (Algorithm 1, line 6): When the agent
modifies the graph structure, the environment returns a composite reward that balances model fit (BIC score), sparsity (0 norm), and acyclicity (NOTEARS metric). The reward leverages
BIC decomposability for efficient local rescoring, delivering immediate feedback while maintaining computational efficiency.
2) Agent model: The agent iteratively refines a DAG by
selecting edge operations (addition, deletion, retention) based on
the structured state (Algorithm 1, line 5). We employ a compact
hierarchical policy network that preserves structural information
while avoiding redundant computation, complemented by an
adaptive temperature-decay mechanism (Algorithm 1, line 10)

YANG et al.: RL-ACID: RL-OPTIMIZED ADAPTIVE CAUSAL DISCOVERY FOR ROBUST ANOMALY DETECTION IN INDUSTRIAL SYSTEMS

that dynamically balances exploration and exploitation throughout training.
3) CaRLite algorithm: Algorithm 1 outlines the complete
causal structure search procedure, implementing an efficient RL
process for causal discovery. The algorithm accepts an initial
DAG G0 from the encoder–decoder module, a candidate edge
pool E0 , and a local BIC oracle, and returns a refined DAG Ĝ as
output.
The procedure initializes the policy network πϑ , a hierarchical experience buffer B, and the temperature parameter λ
(line 1). The main search loop (line 2) iterates until convergence,
with each iteration executing the following steps in sequence.
First, a structured state representation is constructed by combining the current adjacency matrix with edge-level descriptors
(line 3). Based on this state, the policy network samples an
edge-modification action (line 4), which is applied to update the
graph while enforcing acyclicity constraints (line 5). Following
each structural change, a composite reward is computed using
the BIC score and structural penalties (line 6). To manage
past experiences effectively, an experience replay mechanism
is employed (lines 7–8). This mechanism stores transitions in a
tiered buffer according to their learning stability and retrieves
them for policy updates based on the detected magnitude of
causal drift. Subsequently, the policy parameters are updated
using the REINFORCE algorithm with a baseline (line 9),
while the temperature parameter λ is annealed to balance exploration and exploitation (line 10). Convergence is detected
when no performance improvement occurs for L consecutive
steps (lines 11–13), at which point the search terminates. Finally, nonpositive edges are pruned while preserving acyclicity,
yielding the optimized DAG Ĝ.
The policy maximizes the expected return under the composite reward R(G) = −[SBIC (G) + Φ(G)]. Here, SBIC (G) penalizes model complexity while assessing fit, given by


d 

RSSi
SBIC (G) =
(3)
m log
+ dθ log m
m
i=1
2
where RSSi = m
k=1 (xki − x̂ki ) is the residual sum of squares
d
for node i, and dθ = i=1 |Pa(i)| is the total number of parent

nodes across the graph. The structural penalty Φ(G) is defined
as
/ DAGs) + λ2 h(A) + μ A 0
Φ(G) = λ1 I(G ∈

relationships and is subsequently passed to downstream modules
for causal clustering and anomaly detection.
C. Causal Clustering Module and Anomaly Detection
To address causal drift under varying system conditions, we
introduce a distribution routing mechanism that encodes each
causal graph into a low-dimensional structural embedding and
softly assigns it to M latent causal experts. Each expert captures
a distinct structural regime, and their outputs are weighted and
fused to support robust inference.
Distribution router: Each RL-generated adjacency matrix
Ĝ ∈ {0, 1}d×d is first flattened and encoded by a two-layer MLP
to produce a structural embedding
zt = MLP(Flatten(Ĝ)) ∈ Rd .

(5)

The resulting structural embedding zt ∈ R is projected to
M latent structural experts using a lightweight two-layer gating
network
d

Ht = U2 · ReLU(U1 · zt ) ∈ RM

(6)

dh ×M

where U1 ∈ R
and U2 ∈ R
are learnable parameters.
Here, d is the dimension of the structural embedding, dh is the
hidden dimension of the gating network, and M denotes the
number of structural experts.
The model then computes a sparse routing distribution over
the top-K selected experts via a masked softmax, assigning a
(i)
normalized weight wt to each expert based on its compatibility with the current causal graph. This deterministic approach
clusters time-varying structures without stochastic reparameterization, improving stability and interpretability in nonstationary
environments.
Expert prediction and aggregation: Each expert Ei maintains
a linear mechanism fi (·) to predict the target variable xj from
its parent set paj
d×dh

(i)

(i)

x̂j = wj

(i)

· paj + bj

(7)

where wj ∈ R|paj | is the expert-specific weight vector and bj
is a learnable bias term.
The final prediction is the weighted sum of expert outputs
(i)

(i)

x̂j =

K


(i)

(i)

wt · x̂j .

(8)

i=1

(4)

where h(A) = trace(eA ) − d enforces the DAG constraint
through a smooth acyclicity metric, and the 0 -norm A 0
promotes sparsity.
The policy network employs a lightweight structure comprising only 3–4 layers with cross-layer feature pathways, designed
to preserve multiscale structural cues while maintaining efficiency. Training is stabilized by an adaptive temperature-decay
mechanism λ, which ensures a smooth transition from exploration to exploitation as the policy converges.
This structured approach enables CaRLite to achieve a 68%
gain in computational efficiency through intelligent experience
reuse, while directly promoting the discovery of sparse, acyclic,
and high-fidelity causal graphs for dynamic industrial environments. The resulting DAG Ĝ captures time-varying causal

3651

This expert-driven routing and fusion strategy allows the
model to adapt to time-varying causal structures, enhancing
robustness, and interpretability under nonstationary dynamics.
After the RL search converges and yields the final causal graph
Ĝ, the anomaly detection module is trained separately. Given
the discovered graph, the reconstruction network predicts future
(Ĝ)
sensor values X̂t+1 , and the prediction loss is defined as
1 
2
(Ĝ)
X̂t+1 − Xt+1 2 .
N t=1
N

Lpred =

(9)

This term measures the sum of squared prediction errors across
all sensors between predicted and observed sensor readings and
is used only to train the anomaly detection MLP and the causal
clustering experts.

3652

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 5, MAY 2026

D. Theoretical Foundations and Analysis

TABLE II
DATASET CHARACTERISTICS AND OPERATIONAL COMPLEXITY

To establish a rigorous mathematical foundation for RLACID, we formulate its core objective as a constrained multiobjective optimization problem that jointly learns time-varying
causal structures {Gt } and the anomaly detection function f
min E[Ldet ] + λ1 Gt 0 + λ2 RDAG (Gt ) + λ3 Ω(f ).

{Gt },f

(10)

In this formulation, Ldet quantifies the reconstruction error for
detection accuracy, the 0 -norm enforces graph sparsity, RDAG
represents the NOTEARS constraint ensuring acyclicity, and
Ω(f ) controls model complexity. The coefficients λ1 , λ2 , λ3 ≥ 0
formally balance the inherent tradeoffs among these objectives,
which correspond to the core challenges M1–M3. It is important
to note that in our framework, these tradeoffs are intrinsically
addressed through dedicated algorithmic designs rather than
manual tuning of independent parameters.
This formulation provides the basis for three key theoretical
innovations in RL-ACID. First, causal discovery is reformulated
as a constrained RL problem, where an agent’s policy explores
the space of DAGs by optimizing a reward derived from the
negative of the cost terms in (10). This approach avoids the combinatorial explosion inherent in traditional score-based searches,
directly addressing the efficiency challenge (M2). Second, the
integration of the LISA sparse attention mechanism with causal
graph learning induces a synergistic coregularization effect. The
attention mechanism focuses on salient temporal dependencies
to inform the structural prior, while the evolving causal graph
provides feedback to refine attention patterns. This synergy
enhances the model’s adaptability to temporal dynamics (M1).
Third, the causal clustering module addresses nonstationarity
by modeling the data as a mixture model of distinct operational
regimes. This allows the model to identify invariant causal mechanisms, P (Y |PA(Y )), across regimes, providing a principled
method to distinguish true anomalies from operational drift.
These theoretical guarantees collectively provide the analytical foundation for the empirical results in Section IV, confirming
that RL-ACID’s performance stems from its principled design
rather than empirical coincidences.
IV. EXPERIMENTS
A. Experiments Settings
Dataset: To evaluate the generalization and adaptability of our
method across diverse industrial scenarios, we use five representative datasets spanning water treatment, electric power systems,
and chemical processes: Secure Water Treatment (SWaT) [20],
Water Distribution (WADI) [21], Hardware-in-the-Loop based
Augmented Industrial Control System security (HIL-HAI) [4],
the power system datasets (PSD) [22], and the Tennessee Eastman (TE) process benchmark [23]. These datasets vary in dimensionality, process complexity, control logic, and attack patterns.
Table II summarizes the key characteristics of the datasets.
SWaT: A water treatment system with six stages and 51
variables, spanning 11 days (7 normal, 4 attack). It features clear
phase transitions and control logic, making it ideal for analyzing
causal drift and root cause chains.

WADI: A large-scale water distribution system with 123 variables and 16 days of data (14 normal, 2 attack). Its higher dimensionality and dynamic conditions pose challenges for consistent
modeling in multistage environments.
HIL-HAI: A hardware-in-the-loop ICS simulation with four
coupled processes and 59 variables. It includes 10 days of normal
data and 5.5 days of attack scenarios. Its frequent condition
changes demand strong adaptability to structural variations.
Version 1.0 is used.
PSD: Phasor measurement unit (PMU) traces from a benchmark power grid with 37 operating scenarios covering normal
operation, natural disturbances and three types of cyber-physical
attacks. For our study, these scenarios are grouped into normal
and abnormal to perform binary anomaly detection.
TE: A highly nonlinear and tightly coupled chemical process
simulation with 52 variables and 21 diverse fault types, including
step changes, slow drifts, and valve failures. It provides a longhorizon and imbalanced benchmark for evaluating anomaly
detection in complex industrial environments.
Baseline: To comprehensively evaluate the effectiveness of
the proposed RL-ACID framework, we compare it with representative baselines from both anomaly detection and causal
discovery. For anomaly detection, we include Deep Robust
One-Class Classification (DROCC) [24], a semisupervised
deep model that learns a compact decision boundary around
normal samples; Graph Deviation Network (GDN) [25], a
graph-neural-network-based detector modeling neighborhood
dependencies among sensors; Graph-Augmented Normalizing
Flow (GANF) [26], Multivariate Time series anomaly detection via dynamic Graph and entityaware normalizing Flow
(MTGFlow) [27], and a Graph Mixture of Experts (GraphMoE) [28], which represent state-of-the-art unsupervised graphbased anomaly detectors; and Anomaly Root Cause Analysis via Granger Causal Discovery (AERCA) [29], which integrates Granger causality with root-cause analysis for interpretable anomaly detection. For causal discovery, we further
consider DYNOTEARS [30], a score-based dynamic extension of NOTEARS for learning time-lagged causal graphs;
PCMCI+ [5], a constraint-based method that combines conditional independence tests with false-discovery-rate control for
high-dimensional time series; causal forests [31], an ensemble
approach for estimating heterogeneous causal effects without
strong parametric assumptions; and transfer entropy [32], an
information-theoretic metric that quantifies directional dependencies between time-series variables.
To ensure a fair comparison in anomaly detection, each of
these methods is first applied to the training data to learn a causal

YANG et al.: RL-ACID: RL-OPTIMIZED ADAPTIVE CAUSAL DISCOVERY FOR ROBUST ANOMALY DETECTION IN INDUSTRIAL SYSTEMS

3653

TABLE III
COMPARISON OF F1-SCORE, AVERAGE PRECISION (A-PR), AND AVERAGE ROC (A-ROC) ON FIVE BENCHMARK DATASETS (BOLD VALUES INDICATE THE
PROPOSED RL-ACID METHOD AND HIGHLIGHT BEST OR SUPERIOR PERFORMANCE)

graph, which is then fed into the same downstream anomalydetection module with a unified thresholding scheme. This set
of baselines enables a balanced evaluation of RL-ACID against
both leading anomaly detection techniques and representative
causal structure learning methods.
Evaluation metrics: Following previous works [27], [28], we
adopt a window-level evaluation strategy, where a window is
labeled as anomalous if any time point within it is detected as
abnormal. The primary evaluation metric is the area under the
receiver operating characteristic curve (A-ROC), which reflects
the tradeoff between true positive rate and false positive rate
under varying thresholds. In addition to A-ROC, we report
F1-score and area under the precision–recall curve (A-PR) in the
main comparison experiments. F1-score captures the balance between precision and recall, while A-PR highlights performance
on rare anomalies, which is particularly informative for imbalanced datasets. For F1 and A-PR, we determine the anomaly
threshold by selecting the value that maximizes the F1-score
on the validation set. This multimetric evaluation provides a
comprehensive and robust assessment of detection accuracy
across diverse conditions.
Implementation details: To ensure consistency and comparability, we adopt a unified experimental setup across all five
datasets. The sliding window size and stride are set to 60 and 10,
respectively, for all datasets. Model training employs the Adam
optimizer with dataset-specific hyperparameters: for SWaT and
HIL-HAI (medium-scale systems), we use a batch size of 512
and learning rate of 0.005; for WADI and PSD (large-scale
systems), the batch size is 320 with a learning rate of 0.0035; and
for TE (highly imbalanced system), we use a batch size of 256
and learning rate of 0.002. The causal graph construction retains
a fixed number of high-confidence edges to maintain structural
sparsity across all datasets. All experiments are conducted on
a server equipped with NVIDIA RTX 3090 GPUs and 64 GB
RAM. To ensure statistical reliability, the results of our proposed
model are calculated as mean values from 5 independent runs
with different random seeds.

B. Main Comparison and Analysis.
We begin by presenting in Table III, a summary of the RLACID’s performance against baselines across five ICS datasets.
RL-ACID demonstrates the best overall anomaly detection performance on the medium-scale ICS testbeds SWaT and HILHAI. It attains the highest scores on SWaT, with 85.0% in F1,
82.1% in A-PR, and 88.8% in A-ROC. Similarly, on HIL-HAI,
it reaches 83.2% in F1, 80.5% in A-PR, and 90.2% in A-ROC,
consistently outperforming all baseline methods. In contrast,
static causal models like PCMCI+ and DYNOTEARS yield
lower F1 and A-PR performance. This advantage stems from
RL-ACID’s integrated framework: a time-frequency encoder
that captures underlying system dynamics, combined with RLdriven graph optimization that continuously adapts to operational variations—a capability static models lack.
The WADI dataset presents a challenging environment due to
its high dimensionality (123 variables) and frequent operational
shifts. On this dataset, RL-ACID achieves the best A-PR (67.1%)
and A-ROC (94.3%). These results demonstrate its superior
ranking capability and effectiveness in handling imbalanced
anomaly detection tasks. Notably, the causal clustering module
contributes significantly to this performance. It enhances model
robustness by accurately separating true anomalies from normal
operational variations, a capability where static models often
fail. Although the F1-score of RL-ACID (68.1%) is slightly
lower than that of Graph-MoE, this tradeoff underscores our focus on maintaining robust detection performance across varying
thresholds rather than optimizing for a single operating point.
PSD is characterized by high dimensionality (128 variables)
and diverse event scenarios (37 in total). RL-ACID achieves
the strongest detection (75.9% F1, 73.0% A-PR, 92.7% AROC). The high variance and noise typical of PMU data make
this dataset particularly challenging for classic causal methods,
which show sharp performance drops. By contrast, RL-ACID’s
time-frequency features combined with RL-based graph search
improve robustness to noisy measurements and yield stable
anomaly detection across operating regimes.

3654

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 5, MAY 2026

Fig. 6. Abnormal propagation effect under the perception of causal
chains.

Fig. 5. Prediction-error scatter plots showing model sensitivity. Points
within the yellow band have errors below the 0.2 tolerance. Red points
are true anomalies: those outside the band are detected, inside are
missed. Normal points outside the band represent false positives.

The TE process is a nonlinear, strongly coupled chemical
system with 52 variables and 21 injected faults, exhibiting high
imbalance (anomaly ratio > 80%). RL-ACID achieves the best
F1 (78.2%) and A-PR (74.9%), though its A-ROC (92.3%) is
slightly below Graph-MoE. This is expected given the diversity
of TE faults (valve failures, slow drifts, random variations),
where some subtle anomalies are more readily captured by
correlation-based ensembles. Nevertheless, the RL-ACID’s superior performance on this strongly nonlinear system validates
the effectiveness of our approach, where nonlinear feature extraction complements the linear BIC scoring to handle complex
industrial dynamics.
Overall trends: Classical causal discovery baselines (transfer entropy, causal forests, PCMCI+, DYNOTEARS) show
lower and more volatile performance, particularly on highdimensional or regime-varying datasets (WADI, PSD, TE), because they assume either static structures or linear relationships.
Modern graph-based baselines (Graph-MoE, AERCA) perform
competitively but still lack adaptability to causal drift. The
consistent improvements achieved by RL-ACID across both
threshold-dependent (F1) and threshold-free (A-PR, A-ROC)
evaluations confirm its superiority and robustness in dynamic
ICS environments.
C. Qualitative Analysis and Interpretability
To evaluate anomaly detection accuracy and prediction stability, we compare the prediction performance of different
models from the perspective of error structure, as shown in
Fig. 5. Specifically, we plot the scatter of predicted versus
observed values, and visualize the pointwise residuals to reflect
the model’s sensitivity to anomalies and its ability to control
prediction errors. A yellow tolerance band is used to indicate

acceptable deviation, where points outside the band typically
correspond to anomalies. Experimental results show that the
proposed RL-ACID method produces more stable predictions
under causal constraints, with normal samples densely clustered
within the tolerance region and anomalies clearly located outside
it, demonstrating strong discrimination capability. In contrast,
alternative baselines yield more scattered residuals, resulting in
higher false positive and false negative rates. This highlights the
superiority of our approach in producing explainable and robust
anomaly detection outcomes.
RL-ACID effectively supports anomaly localization and interpretation. As shown in Fig. 6 (left), the causal topology graph
encodes degree-based node importance, functional-type color
intensity, and edge thickness proportional to inferred causal
strength. Without any prior structural assumptions, RL-ACID
identifies meaningful causal dependencies, such as the chain
LIT401 → P302 → LIT301, which aligns with known SWaT
logic: LIT401 monitors the water level in a tank, which influences the operation of P302 (a pump), subsequently affecting
LIT301, the downstream level sensor.
To evaluate interpretability under attack, we consider a scenario where LIT401’s reading is maliciously locked at a high
value. Since RL-ACID has captured LIT401’s causal influence
on P302, this manipulation causes P302 to remain open, unnecessarily pumping water and raising LIT301’s level despite the
tank being full. As shown in Fig. 6 (right), predictions match
observations under normal operation but deviate significantly
after the attack: the model expects P302 to close, yet it remains
open, leading to unexpected rises in LIT301. This propagation
of deviations along the causal chain demonstrates RL-ACID’s
capability to not only detect anomalies but also provide clear
interpretive insights into their root causes.
To further validate the causal reasoning capability of RLACID, we systematically visualized the distribution of its reconstruction errors under multiple attack scenarios, as shown
in Fig. 7. The heatmaps reveal distinct spatiotemporal error
propagation patterns that closely correspond to specific attack
types: stealth attacks exhibit a slow, progressive accumulation of
errors; rapid cascading failures show sudden error bursts across
critical nodes; and oscillatory attacks display periodic error
peaks. Our comparison with the official SWaT attack documentation confirms that these residual distributions strongly align
with the documented attack mechanisms. This correspondence
demonstrates RL-ACID’s ability to capture underlying causal

YANG et al.: RL-ACID: RL-OPTIMIZED ADAPTIVE CAUSAL DISCOVERY FOR ROBUST ANOMALY DETECTION IN INDUSTRIAL SYSTEMS

3655

(a)

Fig. 7. Reconstruction error heatmaps for four representative SWaT
attack scenarios: stealthy, rapid cascade, oscillatory, and localized.

(b)
Fig. 9. (a) Analysis of policy convergence under different Top-K Values. (b) CaRLite computational cost over training.

TABLE IV
ABLATION RESULTS (A-ROC, %) ACROSS FIVE ICS DATASETS

Fig. 8.

Hyperparameter sensitivity analysis: A-ROC versus M and W .

dynamics without prior system topology knowledge. By reconstructing attack propagation paths through causal error analysis,
our framework provides technicians with reliable diagnostic
evidence for root cause identification and system recovery.
D. Hyperparameter Sensitivity Analysis
To evaluate the robustness of RL-ACID under different hyperparameter settings, we conduct sensitivity experiments on two
key parameters: the sliding window size (W ) and the number
of experts (M ) in the causal clustering module, as illustrated in
Fig. 8. The results show that performance generally improves as
W increases to around 60, beyond which overly large windows
may dilute local anomaly patterns, while smaller ones lack
sufficient temporal context. Regarding the number of experts,
smaller-scale systems (SWaT, HIL-HAI) achieve their best performance at M = 3, whereas larger and more heterogeneous
systems (WADI, PSD) prefer M = 4–5, with TE stabilizing
around M = 2–3. The aggregated trend in Fig. 8 (bottom-right)
shows a smooth and consistent response surface, indicating that
RL-ACID is not overly sensitive to moderate variations of these
parameters. In practice, W can be set according to the process
cycle or sampling horizon, while M can be tuned based on
the diversity of operating regimes, providing a systematic and
interpretable guideline for deployment.

Fig. 9 illustrates the dual optimization mechanisms of the
RL-ACID framework. The upper panel demonstrates the tradeoff between convergence speed and final performance under
different Top-K pruning strategies: smaller K values (e.g.,
K = 4) achieve rapid convergence but suffer from performance
limitations, while larger K values (e.g., K = 8) exhibit slow
convergence and tend to settle at suboptimal solutions. K = 6
strikes an optimal balance, reaching peak performance within
120 iterations, validating the effectiveness of prior knowledge
guidance. The lower panel showcases our innovative solution
to the stability-plasticity dilemma through the CaRLite module.
By integrating hierarchical experience replay with causal drift
detection, we achieve intelligent balancing between experience
reuse and adaptive exploration. Computational costs follow an
exponential decay trend (68% overall reduction), while exploratory peaks triggered by causal structure changes prevent
mode collapse in traditional RL and overcome the adaptability
limitations of static models. This provides a lightweight yet
robust adaptive causal discovery solution for dynamic industrial
environments.
E. Ablation Studies
We further perform ablation studies across all five datasets
to evaluate the contribution of each module in RL-ACID. As
shown in Table IV, replacing the transformer encoder with a
Bi-GRU leads to consistent but moderate drops (about 2%–3%

3656

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 22, NO. 5, MAY 2026

TABLE V
COMPUTATIONAL EFFICIENCY COMPARISON ON HIL-HAI AND WADI
DATASETS (BOLD VALUES INDICATE THE PROPOSED RL-ACID METHOD AND
HIGHLIGHT BEST OR SUPERIOR PERFORMANCE)

Fig. 10. Robustness analysis under data imperfections. Left: Performance degradation with increasing missing data ratios. Right: Training
stability under varying noise levels.

AUROC across datasets), confirming the benefit of attentionbased encoding for capturing complex dependencies. Removing
the RL-based search causes more severe declines (3%–4% on
SWaT, HIL-HAI, and PSD), highlighting the importance of
adaptive causal structure optimization. The causal clustering
module is particularly critical on datasets with frequent operational shifts (–4.0% on WADI, –3.8% on TE), showing its ability
to track structural drift under varying regimes. When both RL
and clustering are removed, the degradation becomes sharp (over
–6% on average, up to –7.5% on SWaT), underscoring their
complementary effects. Overall, the ablation confirms that each
component contributes substantially, and their combination of
attention-based encoding, RL driven structure refinement, and
causal clustering is essential for achieving robust and generalizable anomaly detection across diverse ICS environments.
F. Efficiency and Robustness Analysis
Computational efficiency and lightweight design are critical
for deploying anomaly detection models in dynamic industrial environments. Table V provides a systematic evaluation
on the HIL-HAI and WADI datasets. The complete RL-ACID
framework achieves inference times of 42.5 ms (HIL-HAI) and
128.3 ms (WADI) with memory footprints of 680 MB and
1250 MB, respectively. This demonstrates a dual advantage:
RL-ACID significantly outperforms complex ensemble methods
(Graph-MoE, AERCA) in efficiency, while maintaining greater
model capacity than simpler baselines (GDN).
RL-ACID’s efficiency gains stem from its codesigned
lightweight components, which are quantitatively validated
through ablation studies. Removing the LISA sparse attention
mechanism increases inference latency by approximately 62%
and memory usage by 128% on the WADI dataset, confirming
its essential role in alleviating quadratic complexity. Similarly,
replacing the hierarchical experience replay in CaRLite with a
global (nonhierarchical) search strategy leads to prolonged training and suboptimal convergence, despite comparable inference
time. These results demonstrate that the LISA mechanism and
the CaRLite algorithm are directly responsible for achieving a
superior accuracy-efficiency tradeoff.
This lightweight design facilitates practical deployment. The
RL agent operates exclusively during offline training, resulting
in a stable model for online detection. With 4.2 million parameters and consistent sub-150 ms inference latency, RL-ACID

demonstrates that principled, adaptive causal discovery can
be achieved within the resource constraints of real industrial
systems, effectively balancing high detection accuracy with
operational efficiency.
To assess the practical viability of RL-ACID under realistic
industrial conditions, we systematically evaluate its robustness
against common data imperfections using the SWaT dataset. As
illustrated in Fig. 10, we simulate two prevalent challenges: (left)
varying ratios of missing data, and (right) increasing levels of
additive Gaussian noise. Results indicate that although performance degrades with deteriorating data quality, the core functionality remains stable, demonstrating inherent resilience. This
inherent resilience is attributed to the model’s time-frequency
feature encoding, which captures redundant spectral patterns,
and the causal clustering module, which distinguishes structural
drift from noise-induced perturbations. These findings confirm
that RL-ACID is not only effective under idealized laboratory
conditions but also retains robust functionality when confronted
with the incomplete and noisy data streams typical of real-world
industrial deployments.
V. CONCLUSION
This article has presented RL-ACID, an RL-optimized framework that addresses the challenge of adaptive causal discovery
for robust anomaly detection in industrial systems. The methodological contribution lies in reformulating causal discovery as a
constrained RL problem, which enables efficient exploration of
graph structures while preserving interpretability. By integrating
time-frequency feature encoding with a lightweight RL-based
causal search and causal clustering, the framework effectively
tracks time-varying causal relationships and distinguishes true
anomalies from operational fluctuations. Extensive evaluations
across five industrial benchmarks demonstrate RL-ACID’s comprehensive advantages in detection accuracy, interpretability,
and computational efficiency compared to existing baseline
methods, establishing its superior performance in dynamic industrial environments.
Building upon the RL-ACID framework, future research will
pursue two pivotal directions to broaden its industrial impact.
First, we will focus on devising online and continual learning
mechanisms for real time, incremental adaptation to streaming
data. Second, we aim to establish federated causal discovery
protocols that enable privacy-preserving, collaborative learning
across distributed industrial sites. These research avenues are

YANG et al.: RL-ACID: RL-OPTIMIZED ADAPTIVE CAUSAL DISCOVERY FOR ROBUST ANOMALY DETECTION IN INDUSTRIAL SYSTEMS

designed to enhance the deployability, scalability, and practical
utility of fully adaptive, data-driven causal anomaly detection in
continuously evolving ICS.
REFERENCES
[1] E. D. Knapp, Industrial Network Security: Securing Critical Infrastructure
Networks for Smart Grid, SCADA, and Other Industrial Control Systems.
Amsterdam, The Netherlands: Elsevier, 2024.
[2] A. M. Koay, R. K. L. Ko, H. Hettema, and K. Radke, “Machine learning in
industrial control system (ICS) security: Current landscape, opportunities
and challenges,” J. Intell. Inf. Syst., vol. 60, no. 2, pp. 377–405, 2023.
[3] Y. Chen et al., “Causal inference-based adversarial domain adaptation for
cross-domain industrial intrusion detection,” IEEE Trans. Ind. Informat.,
vol. 21, no. 1, pp. 970–979, Jan. 2025.
[4] H.-K. Shin, W. Lee, J.-H. Yun, and H. Kim, “HAI 1.0: HIL-based augmented ICS security dataset,” in Proc. 13Th USENIX Workshop Cyber
Secur. Experimentation Test (CSET 20), 2020, Art. no. 1. [Online]. Available: https://www.usenix.org/conference/cset20/presentation/shin
[5] J. Runge, “Discovering contemporaneous and lagged causal relations in
autocorrelated nonlinear time series datasets,” in Proc. Conf. Uncertainty
Artif. Intell., 2020, pp. 1388–1397.
[6] H. Sharifi-Noghabi, P. A. Harjandi, O. Zolotareva, C. C. Collins, and M.
Ester, “Out-of-distribution generalization from labelled and unlabelled
gene expression data for drug response prediction,” Nature Mach. Intell.,
vol. 3, no. 11, pp. 962–972, 2021.
[7] C. Wang and J. Liu, “Anomaly detection method for complex systems
based on a domain-adaptive causal decoupling model,” IEEE Trans. Ind.
Informat., vol. 21, no. 3, pp. 2748–2757, Mar. 2025.
[8] Z. Zamanzadeh Darban, G. I. Webb, S. Pan, C. Aggarwal, and M. Salehi,
“Deep learning for time series anomaly detection: A survey,” ACM Comput. Surv., vol. 57, no. 1, pp. 1–42, 2024.
[9] H. Qiao, H. Tong, B. An, I. King, C. Aggarwal, and G. Pang, “Deep graph
anomaly detection: A survey and new perspectives,” IEEE Trans. Knowl.
Data Eng., vol. 37, no. 9, pp. 5106–5126, Sep. 2025.
[10] Q. Mao et al., “Fecograph: Label-aware federated graph contrastive learning for few-shot network intrusion detection,” IEEE Trans. Inf. Forensics
Secur., vol. 20, pp. 2266–2280, 2025.
[11] G. Duan, H. Lv, H. Wang, and G. Feng, “Application of a dynamic
line graph neural network for intrusion detection with semisupervised
learning,” IEEE Trans. Inf. Forensics Secur., vol. 18, pp. 699–714, 2023.
[12] C. Wang and J. Liu, “Fault detection based on causal discovery and graph
convolutional network for complex mechatronic systems,” IEEE Trans.
Rel., vol. 74, no. 1, pp. 2382–2393, Mar. 2025.
[13] H.-S. Chen, Z. Yan, X. Zhang, Y. Liu, and Y. Yao, “Root cause diagnosis of
process faults using conditional granger causality analysis and maximum
spanning tree,” IFAC-PapersOnLine, vol. 51, no. 18, pp. 381–386, 2018.
[14] J. Qiu, Q. Du, K. Yin, S.-L. Zhang, and C. Qian, “A causality mining
and knowledge graph based method of root cause diagnosis for performance anomaly in cloud applications,” Appl. Sci., vol. 10, no. 6, 2020,
Art. no. 2166.
[15] W. Wang et al., “Abnormal flow detection in industrial control network
based on deep reinforcement learning,” Appl. Math. Comput., vol. 409,
2021, Art. no. 126379.
[16] S. Yang, L. Ning, X. Cai, and M. Liu, “Dynamic spatiotemporal causality
analysis for network traffic flow based on transfer entropy and sliding window approach,” J. Adv. Transp., vol. 2021, no. 1, 2021, Art. no. 6616800.

3657

[17] W. Zhuang, J. Fan, J. Fang, W. Fang, and M. Xia, “Rethinking general
time series analysis from a frequency domain perspective,” Knowl.-Based
Syst., vol. 301, 2024, Art. no. 112281.
[18] F. Yan, X. Zhang, and C. Yang, “A graph-based time–frequency twostream network for multistep prediction of key performance indicators in
industrial processes,” IEEE Trans. Cybern., vol. 54, no. 11, pp. 6867–6880,
Nov. 2024.
[19] X. Zheng, B. Aragam, P. K. Ravikumar, and E. P. Xing, “Dags with no
tears: Continuous optimization for structure learning,” in Proc. Adv. Neural
Inf. Process. Syst., 2018, vol. 31. [Online]. Available: https://proceedings.
neurips.cc/paper/2018/hash/e347c5144c2f6d8a0b6c1e12bf08c3f9Abstract.html
[20] A. P. Mathur and N. O. Tippenhauer, “Swat: A water treatment testbed for
research and training on ICS security,” in Proc. Int. Workshop Cyber-Phys.
Syst. Smart Water Netw, 2016, pp. 31–36.
[21] C. M. Ahmed, V. R. Palleti, and A. P. Mathur, “Wadi: A water distribution
testbed for research in the design of secure cyber physical systems,” in
Proc. 3rd Int. Workshop Cyber- Phys. Syst. Smart Water Netw., 2017,
pp. 25–28.
[22] U. Adhikari, S. Pan, T. Morris, R. Borges, and J. Beave, “Industrial control
system (ICS) cyber attack datasets,” Datasets Experimentation, 2019. [Online]. Available: https://sites.google.com/a/uah.edu/tommy-morris-uah/
ics-data-sets
[23] J. J. Downs and E. F. Vogel, “A plant-wide industrial process control
problem,” Comput. Chem. Eng., vol. 17, no. 3, pp. 245–255, 1993.
[24] S. Goyal, A. Raghunathan, M. Jain, H. V. Simhadri, and P. Jain, “DROCC:
Deep robust one-class classification,” in Proc. Int. Conf. Mach. Learn.,
2020, pp. 3711–3721.
[25] A. Deng and B. Hooi, “Graph neural network-based anomaly detection in
multivariate time series,” in Proc. AAAI Conf. Artif. Intell., vol. 35, no. 5,
2021, pp. 4027–4035.
[26] E. Dai and J. Chen, “Graph-augmented normalizing flows for anomaly
detection of multiple time series,” in Proc. Int. Conf. Learn. Representations, 2022. [Online]. Available: https://openreview.net/forum?id=
45L_dgP48Vd
[27] Q. Zhou, J. Chen, H. Liu, S. He, and W. Meng, “Detecting multivariate
time series anomalies with zero known label,” in Proc. AAAI Conf. Artif.
Intell., vol. 37, no. 4, 2023, pp. 4963–4971.
[28] X. Huang, W. Chen, B. Hu, and Z. Mao, “Graph mixture of experts
and memory-augmented routers for multivariate time series anomaly
detection,” in Proc. AAAI Conf. Artif. Intell., vol. 39, no. 16, 2025,
pp. 17476–17484.
[29] X. Han, S. Absar, L. Zhang, and S. Yuan, “Root cause analysis of anomalies
in multivariate time series through granger causal discovery,” in Proc.
13th Int. Conf. Learn. Representations, 2025. [Online]. Available: https:
//openreview.net/forum?id=k38Th3x4d9
[30] R. Pamfil et al., “Dynotears: Structure learning from time-series data,” in
Int. Conf. Artif. Intell. Statist., 2020, pp. 1595–1605.
[31] S. Athey and S. Wager, “Estimating treatment effects with causal forests:
An application,” Observational Stud., vol. 5, no. 2, pp. 37–51, 2019.
[32] R. Vicente, M. Wibral, M. Lindner, and G. Pipa, “Transfer entropy—A
model-free measure of effective connectivity for the neurosciences,” J.
Comput. Neurosci., vol. 30, no. 1, pp. 45–67, 2011.
[33] N. Elmrabit, F. Zhou, F. Li, and H. Zhou, “Evaluation of machine learning algorithms for anomaly detection,” in Proc. Int. Conf. Cyber Secur.
Protection Digit. Serv., 2020, pp. 1–8.
PAPER_TEXT
