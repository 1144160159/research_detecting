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
# [778] Quantum Machine Learning for Cybersecurity: Toward Smarter Intrusion Detection Systems
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
编号：778
题名：Quantum Machine Learning for Cybersecurity: Toward Smarter Intrusion Detection Systems
年份：2026
DOI：10.1109/tce.2026.3697692
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2026.3697692.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 15
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\778.txt
- 原始字符数：59343
- 本次发送字符数：59343
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3697692

1

Quantum Machine Learning for Cybersecurity: Toward Smarter
Intrusion Detection Systems
Mujeeb Ur Rehman, Senior Member, IEEE

, Kamran Rehan

Abstract—The growing scale and complexity of contemporary
cyber threats require intrusion detection systems (IDS) that
can operate effectively in high-dimensional feature spaces while
maintaining robustness against rare and evolving attack patterns.
Classical machine learning techniques, such as support vector
machine (SVM) can face increasing limitations in modeling
nonlinear decision boundaries under such conditions. This work
presents a systematic and reproducible benchmark comparing
classical support vector machine (SVM) and quantum support
vector machine (QSVM) for nine-class network intrusion detection, covering benign traffic and eight attack categories (DoS
Hulk, DDoS, FTP Brute Force, SSH Brute Force, SQL Injection,
XSS, PortScan, and Infiltration). The evaluation is conducted
on the CICIDS2017 dataset, comprising over 2.8 million labeled
network flows. To ensure compatibility with near-term quantum
hardware, mutual information (MI) based feature selection is
employed to construct a compact yet information-preserving representation, which is encoded into a quantum feature map with
an optimized entanglement structure. Experimental evaluation
is conducted across two complementary settings. In the binary
setting (1,000 balanced samples), classical SVM achieves 99.2%
accuracy and 99.1% F1-score against QSVM’s 96.9% accuracy
and 96.7% F1-score, an accuracy gap of 2.3 percentage points
and an F1-score gap of 2.4 percentage points, reflecting marginal
differences in precision–recall balance across the balanced test
set. In the primary nine-class multiclass setting (1,800 balanced
samples, 200 per class), classical SVM achieves a macro-F1
of 97.3% compared to QSVM’s 95.5%, narrowing the F1 gap
to 1.8 percentage points. Critically, per-class analysis reveals
that the SVM–QSVM gap narrows to only 0.3% for SQL
Injection and Infiltration, the highest-complexity minority classes,
suggesting that quantum kernel geometry provides relatively
stronger representational capacity precisely for the rare, complex attack patterns of greatest operational significance. The
proposed Docker- and Qiskit-based benchmarking framework
provides a reproducible and extensible foundation for systematic
classical–quantum benchmarking in cybersecurity, establishing a
transparent baseline that can guide the design of future hybrid
quantum–classical intrusion detection architectures.
Index Terms—Quantum Machine Learning (QML), Quantum
Support Vector Machines (QSVM), Intrusion Detection Systems
(IDS), Multiclass Classification, One-vs-Rest Decomposition, Cybersecurity, Quantum Computing

I. I NTRODUCTION
The rapid growth of global digital connectivity has made
cyberattacks a critical threat to individuals, organizational
(Corresponding author: Mujeeb Ur Rehman)
Mujeeb Ur Rehman and Muhammad Abrar are with the School of Computer
Science and Informatics, De Montfort University, Leicester, LE1 9BH, UK
(e-mail: mujeeb.rehman@dmu.ac.uk).
Kamran Rehan is with the Department of Physics, The University of
Haripur, Haripur-22620, Pakistan.
Imran Rehan is with the Department of Physics, Islamia College University
Peshawar, Pakistan.
Digital Object Identifier 10.1109/TCE.2025.[Your DOI Number].

, Muhammad Abrar

, and Imran Rehan

assets, and national infrastructure. The global annual cost
of cybercrime is projected to reach $15.63 trillion by 2029,
increasing from $0.86 trillion in 2018 to $10.29 trillion in
2025 [1], as shown in Fig. 1.

Fig. 1. Projected annual cost of cybercrime from 2018 to 2029.

Major network intrusion threats, including Distributed Denial of Service (DDoS), brute-force attacks, and malware
injection, continue to evolve faster than traditional defense
systems can handle [2]. Intrusion Detection Systems (IDS) are
essential security mechanisms that monitor network activity
to detect anomalous behavior. Classical machine learning
approaches, particularly Support Vector Machines (SVMs),
are widely used in IDS due to their strong classification
performance [3]. These models have also been applied to
cyber-physical systems [4]. However, they face limitations in
handling nonlinear, high-dimensional network traffic and the
increasing scale and diversity of modern datasets [5].
Beyond scalability, practical IDS deployments require finegrained attack discrimination, as different attack types trigger
distinct response strategies. A nine-class taxonomy—covering
DoS, DDoS, FTP and SSH Brute Force, PortScan, Web
Attacks (XSS, SQL Injection), and Infiltration—reflects the
diversity of threats in CICIDS2017 and provides a more
realistic and challenging benchmark beyond binary detection.
Quantum Machine Learning (QML) has emerged as a
promising paradigm for exploring computational advantages
beyond classical approaches by leveraging quantum information processing [6]. In particular, Quantum Support Vector
Machines (QSVMs) use quantum feature maps to embed
classical data into high-dimensional Hilbert spaces, potentially
enhancing representational capacity for complex datasets.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3697692

2

Recent studies have explored QSVM applications in cybersecurity. For example, [7] demonstrated QSVM-based detection of DDoS attacks in smart micro-grids using Qiskit and the
HHL algorithm, reporting promising performance compared to
classical methods. However, practical deployment of QSVMs
for large-scale datasets remains challenging due to hardware
limitations and reliance on quantum simulation [8].
In this work, we evaluate QSVM on the CICIDS2017
dataset, which contains approximately 2.8 million labeled
network traffic records representing modern attack scenarios.
To ensure compatibility with near-term quantum resources,
the original 80-dimensional feature space is reduced to 10
informative features using a mutual information–based feature
selection method.
Experimental results show that classical SVM outperforms
QSVM under current simulation conditions, achieving accuracy (99.2% vs. 96.9%), precision (99.0% vs. 96.5%),
recall (99.4% vs. 97.0%), and F1-score (99.1% vs. 96.7%).
Nevertheless, QSVM provides a quantum-enhanced feature
mapping framework that may offer advantages in representing complex data structures as quantum hardware matures.
Therefore, benchmarking QSVM against classical approaches
is essential for assessing its practical potential and guiding
scalable quantum machine learning solutions for cybersecurity.
This study makes five key contributions:
1) Controlled Benchmarking Framework: Fair comparison under identical data regimes, feature spaces, and
evaluation protocols across binary and nine-class settings.
2) NISQ-Constrained Feature Analysis: Investigation of
dimensionality constraints on quantum kernel performance under practical resource limitations.
3) Regime-Dependent Performance Trade-offs: Analysis
of QSVM performance under constrained representations, identifying when quantum and classical kernels
are most effective.
4) Reproducible QML Pipeline: A transparent and extensible benchmarking pipeline for quantum intrusion
detection studies.
5) Per-Class Quantum Kernel Analysis: Evaluation
across nine attack types, highlighting non-uniform
SVM–QSVM gaps, with smaller gaps for complex minority classes.
While performance is competitive in simulation, quantum
advantage remains hardware-dependent. The results highlight
regime-dependent quantum kernel behavior under NISQ constraints in both binary and multiclass settings.
The remainder of this paper is organized as follows: Section
II reviews existing literature; Section III presents the methodology; Section IV discusses experimental results; and Section
V concludes the paper.
II. L ITERATURE R EVIEW

representation of real-world attack scenarios, including DDoS,
botnets, and web intrusions [10], [11]. Statistical-based IDS
methods employ entropy, correntropy, and distance metrics
for anomaly detection. While effective for known attacks, they
suffer from poor generalization to novel threats and high falsepositive rates [12].
Machine learning-based IDS significantly improve detection
by learning complex decision boundaries. SVMs remain a
standard classifier, achieving strong performance in both binary and multi-class settings when combined with effective
feature selection [13]. However, their performance degrades
in high-dimensional spaces and large-scale traffic, motivating ensemble approaches that integrate SVMs with decision
trees and neural networks to improve accuracy, reduce false
alarms, and enhance robustness to imbalanced and adversarial
data [14], [15], [16]. Recent advances highlight the growing
role of deep learning models, including convolutional, recurrent, and transformer-based architectures, which effectively
capture temporal and spatial traffic patterns for real-time IDS
applications [17], [18]. Despite their success, these models
require substantial computational resources and large labeled
datasets, limiting their applicability in resource-constrained
environments.
QML has therefore emerged as a promising alternative,
leveraging quantum superposition and entanglement to process high-dimensional data and capture complex nonlinear
relationships [19], [20]. Beyond kernel-based methods, more
advanced quantum-enhanced frameworks are being explored.
For example, a hybrid approach combining quantum entropy
and reinforcement learning for DDoS detection in smart grids
was proposed in [21], demonstrating improved adaptability
and resilience compared to traditional methods. QSVMs have
shown strong potential in intrusion detection, offering enhanced kernel expressivity and improved generalization for
complex decision boundaries [22]. Effective deployment requires careful feature selection to map classical data into
quantum-compatible representations. Prior studies report that
QSVMs can achieve comparable or superior accuracy with
lower false positive rates than classical SVMs using reduced
feature sets [23], [24], as summarized in Table VIII.
As IDS research shifts toward hybrid, deep learning, and
quantum-enhanced approaches, evaluating QSVMs against
classical SVMs on CICIDS2017 is essential for assessing
their practical readiness and operational feasibility in nextgeneration IDS systems [25], [26].
Recent work on a 4-qubit QSVM-based IDS for IoT networks [27] achieved an F1-score of 86.4% using PCA-based
feature transformation. However, reproducible, NISQ-aware
benchmarking on large-scale datasets such as CICIDS2017
remains limited. This work addresses this gap through a
statistically validated framework. Unlike PCA, which projects
data into a latent space, we employ MI-based feature selection
to retain the most informative original features, enabling direct
mapping to quantum circuits under NISQ constraints.

Modern IDS increasingly rely on machine learning as
network environments grow in complexity and cyber threats
become more sophisticated [9]. The CICIDS2017 dataset
is widely used as a benchmark due to its comprehensive

III. M ETHODOLOGY
This study presents a complete framework for developing
and evaluating intrusion detection using classical SVM and

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3697692

3

TABLE I
CHARACTERISTICS OF NETWORK ATTACK CATEGORIES AND
BENIGN TRAFFIC IN CICIDS2017 WITH CLASS DISTRIBUTION
AND STRATIFIED SAMPLING FOR MULTI-CLASS EVALUATION
Class

Attack Name

Attack Type

0
1
2
3
4
5
6
7
8
TOTAL

Benign
DoS Hulk
DDoS
FTP Brute Force
SSH Brute Force
SQL Injection
XSS
PortScan
Infiltration
—

Normal
Denial of Service
Denial of Service
Brute Force
Brute Force
Web Attack
Web Attack
Reconnaissance
Infiltration
—

Original Dataset
Samples
2,273,097
231,073
128,027
7,938
5,897
21
652
158,930
36
2,805,671

Selected Samples
per Class
200
200
200
200
200
200
200
200
200
1,800

Description
Legitimate background traffic
High-volume TCP flooding
Distributed denial of service
Password guessing via FTP
Password guessing via SSH
Database manipulation
Cross-site scripting
Probing open ports
Unauthorized access
Nine-class balanced subset

QSVM on the CICIDS2017 dataset, with preprocessing and
feature selection adapted to quantum hardware constraints. The
overall workflow is illustrated in Fig. 2.
A. Dataset Description
The CICIDS2017 dataset from the Canadian Institute for
Cybersecurity is used in this study. It contains approximately
2.8 million network traffic records collected over several days,
described by 80 flow-based features, including duration, packet
counts, byte rates, inter-arrival times, and TCP flags. The
dataset consists of nine classes: one benign class and eight
attack types (DoS Hulk, DDoS, FTP Brute Force, SSH Brute
Force, SQL Injection, XSS, PortScan, and Infiltration).
As shown in Table I, the dataset is highly imbalanced,
with benign traffic dominating and critical attack categories
underrepresented [28]. Rare classes such as SQL Injection and
Infiltration account for less than 0.5% of total records.
To enable controlled evaluation, two regimes are defined. In
Regime A (binary), a balanced subset of 1,000 samples (500
benign, 500 attack) is used, consistent with NISQ-constrained
benchmarking. In Regime B (nine-class), a balanced subset of
1,800 samples (200 per class) is constructed. This sampling
mitigates class imbalance (benign ≈ 71%) while preserving
dataset characteristics. Stratified sampling is applied within
each fold to prevent data leakage. This approach follows
established CICIDS2017 benchmarking practices [10].
B. Data Preprocessing
To prevent data leakage, all preprocessing is performed
exclusively on the training set, with learned parameters applied to the test set without re-estimation. The preprocessing
pipeline includes missing value handling, label encoding, and
normalization.
Missing Values: Missing entries are handled via mean
imputation or record removal depending on their proportion.
Label Encoding: Categorical features (e.g., protocol
type) are converted into numerical values: xencoded
=
j
LabelEncode(xj ).
Normalization: Continuous features are normalized using
z-score normalization:
xj − µ j
x′j =
(1)
σj
where µj and σj denote the mean and standard deviation of
feature j computed on the training set.
The complete preprocessing procedure is summarized in
Algorithm 1, ensuring a leakage-free and unbiased evaluation
pipeline.

Algorithm 1 Data Preprocessing
1: Load dataset D with features X and labels Y
2: Perform stratified split: (Xtrain , Xtest , Ytrain , Ytest )
Missing Value Handling (training only)
3: for each feature do
4:
if missing ≤ 5% then
5:
Compute imputation mean on Xtrain only
6:
Apply mean imputation to both Xtrain and Xtest
7:
else
8:
Remove affected records from Xtrain and Ytrain only
9:
end if
10: end for
Label Encoding (training only)
11: for each categorical feature do
12:
Fit mapping on Xtrain only
13:
Apply mapping to both Xtrain and Xtest
14: end for
Z-score Normalization (training only)
15: for each continuous feature do
16:
Compute µj , σj on Xtrain only
17:
Normalize Xtrain and Xtest using same µj , σj
18: end for
19: Output: Preprocessed Xtrain , Xtest , Ytrain , Ytest

C. Feature Selection
Due to qubit limitations in current quantum simulators, the
top 10 most informative features are selected from the original
80 using MI ranking:
X X
p(xj , y)
I(Xj ; Y ) =
p(xj , y) log
,
(2)
p(xj )p(y)
xj ∈Xj y∈Y

where I(Xj ; Y ) measures the dependence between feature Xj
and label Y . The selected features include flow duration, forward/backward packet counts, packet lengths, flow byte/packet
rates, and inter-arrival times.
Consistent with the leakage-free protocol, MI-based ranking
is computed exclusively on training data, and the selected features are applied unchanged to the test set. Under CV, feature
selection is recomputed independently within each training
fold. The complete procedure is summarized in Algorithm 2.
Algorithm 2 Feature Selection using MI
1: Input: Xtrain , Ytrain
2: Initialize score vector S, bins B = 10
3: for each feature Xj do
4:
if Xj is continuous then
5:
Discretize into B bins (training data only)
6:
end if
7:
Estimate p(xj ), p(y), and joint p(xj , y)
8:
Compute I(Xj ; Y ) and store in S[j]
9: end for
10: Select top-10 features Ftop
red
11: Xtrain
← Xtrain [Ftop ]
red
12: Xtest
← Xtest [Ftop ]
13: Output: Reduced datasets

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3697692

4

Fig. 2. Hybrid quantum-classical intrusion detection framework using classical SVM and QSVM on CICIDS2017 (2.8M flows, 80 features). Data is split
80/20 with stratification, followed by preprocessing (missing value handling, label encoding, z-score normalization) and MI-based top-10 feature selection
applied within training folds to avoid leakage. Two regimes are evaluated: binary (1,000 samples: 500 benign, 500 attack) and nine-class (1,800 samples, 200
per class). Models include SVM (RBF), Random Forest, XGBoost, and QSVM with a 10-qubit ZZFeatureMap. Performance is estimated via nested 5-fold
cross-validation (CV), with final evaluation on a held-out test set. Classification covers nine attack types using One-vs-Rest under NISQ constraints.

TABLE II
TOP 10 FEATURES VIA MI
Feature Name

MI

Description

Flow Duration
Total Fwd Packets
Total Bwd Packets
Fwd Packet Length Max
Bwd Packet Length Max
Flow Bytes/s
Flow Packets/s
Flow IAT Mean
Fwd IAT Total
Bwd IAT Total

0.85
0.82
0.79
0.76
0.74
0.72
0.69
0.67
0.65
0.63

Total duration of the flow
Packets from source to target
Packets from target to source
Max forward packet size
Max backward packet size
Byte rate per second
Packet rate per second
Mean inter-arrival time
Total forward IAT
Total backward IAT

Table II summarizes the selected features. Reducing dimensionality from 80 to 10 mitigates overfitting and enables direct
one-to-one mapping between features and qubits in QSVM,
which is essential for NISQ compatibility.

1) Classical Support Vector Machine (SVM): SVM is a
supervised learning model that performs classification by
identifying an optimal hyperplane that maximizes the margin
between classes. The primal optimization problem is given by:
min

w,b,ξ

subject to

M
X
1
∥w∥2 + C
ξi
2
i=1

yi w⊤ ϕ(xi ) + b ≥ 1 − ξi ,

(3)
(4)

ξi ≥ 0, i = 1, . . . , M.
Here, w defines the hyperplane orientation, b is the bias,
ξi are slack variables for soft-margin classification, and ϕ(·)
denotes the feature mapping into a higher-dimensional space.
SVMs employ kernel functions to implicitly perform this
mapping. Common kernels include linear, polynomial, sigmoid, and Radial Basis Function (RBF). In this study, the
RBF kernel is used due to its effectiveness in modeling localized nonlinear patterns and its robustness in high-dimensional
spaces. A comparison of commonly used kernels is provided
in Table III.

D. Selection of Comparative Baselines
To strengthen empirical evaluation, classical ensemble
baselines—Random Forest (RF) and XGBoost—are included
alongside SVM. These models are well-suited for tabular
intrusion detection due to their ability to capture nonlinear
feature interactions and provide robust generalization. Their
inclusion enables a comprehensive comparison with QSVM
under the constrained 10-feature setting.
E. Model Design
This section presents the design of two classification models, classical SVM and QSVM, operating on the reduced
feature set obtained via MI-based selection.

TABLE III
C OMPARISON OF K ERNEL F UNCTIONS U SED IN SVM C LASSIFICATION
Kernel Type
Linear
Polynomial
Sigmoid
RBF

Kernel
Function
K(xi , xj ) =
x⊤
i xj
K(xi , xj ) =
d
(αx⊤
i xj + r)
K(xi , xj ) =
⊤
tanh(αxi xj + r)
K(xi , xj ) =
exp(−γ∥xi − xj ∥2 )

Parameters
None
α, r, d
α, r
γ

Advantages

Limitations

Fast, interpretable,
low complexity
Captures curved
decision boundaries
Neural-network
inspired
Captures localized
nonlinearity; robust

Limited for
nonlinear data
Sensitive to
degree, may overfit
May violate Mercer’s
condition; unstable
Requires tuning of γ

2) Quantum Support Vector Machine (QSVM): The QSVM
is a hybrid quantum–classical supervised learning model that
embeds classical data into the Hilbert space of a quantum system and defines a kernel based on quantum state fidelity [29],

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3697692

5

[30], [31], [32], [33]. This maps data into a high-dimensional
Hilbert space representation that may capture feature interactions differently than classical kernels.
For an n-qubit system, the Hilbert space is
n

H = (C2 )⊗n ∼
= C2 ,

(5)

with normalized pure states |ψ⟩ ∈ H satisfying
⟨ψ|ψ⟩ = 1.

(6)

Classical data x ∈ Rd is encoded into quantum states via a
parameterized feature map
⊗n

|ψ(x)⟩ = Uϕ(x) |0⟩

,

(7)

Fig. 3. Quantum feature mapping and QSVM classification pipeline. Classical
inputs are encoded into quantum states, and the kernel K(xm , xn ) =
|⟨ψ(xm )|ψ(xn )⟩|2 enables linear separation in Hilbert space.

where Uϕ(x) is a data-dependent unitary transformation. In
practice, input features are embedded through single-qubit
rotations and entangling operations, generating nonlinear correlations in Hilbert space.
In general, each classical feature contributes to the quantum
state encoding as
xi 7→ |ψ(xi )⟩ ∈ H2 ,

(8)

and multi-dimensional inputs are embedded into H2n .
A layered feature map used in this work is


L
n
Y
Y
(ℓ)
Uent
Uϕ (x) =
Rz (αℓ xj ) H ⊗n ,

N
Fig. 4. Layered quantum feature map U (x; θ) = Uent j Rz (xj )H ⊗n
implementing nonlinear embedding for kernel-based QML.

(9)

F. One-vs-Rest Decomposition for Nine-Class Intrusion Detection

based on entangling gates and phase encoding [32]. The kernel
is defined as the state fidelity

Since quantum kernel SVM is inherently binary, the nineclass problem is addressed using a One-vs-Rest (OvR) strategy
with K = 9 binary QSVM classifiers. Each classifier distinguishes one class from all others and uses the same 10-qubit
ZZFeatureMap kernel with hyperparameters selected via
nested CV. OvR is preferred over One-vs-One (OvO), which
would require K(K − 1)/2 = 36 quantum kernel evaluations,
leading to significantly higher computational overhead under
NISQ constraints. The final prediction is obtained via

ℓ=1

j=1

2

K(x, x′ ) = |⟨ψ(x)|ψ(x′ )⟩| ,

(10)

which replaces classical kernels used in conventional SVMs.
The resulting kernel matrix is evaluated via quantum state
overlaps and subsequently used within a classical SVM framework for training and classification.
Features are encoded using a 10-qubit phase-encoding circuit (Fig. 4). The initial state
X
1
⊗n
|ψ0 ⟩ = |0⟩ , |ψH ⟩ = H ⊗n |ψ0 ⟩ = √
|z⟩ ,
n
2 z∈{0,1}n
(11)
is followed by single-qubit phase rotations,


X
1 X
i
|ψ1 ⟩ = √
xj zj  |z⟩ .
(12)
exp −
2 j
2n z
Nearest-neighbor entangling operations are then applied,
Uent =

n−1
Y

CNOT i,i+1 Rz (θi,i+1 ) CNOTi,i+1 ,

i=1

ŷ = arg

max
k∈{1,...,K}

fk (x),

(15)

where fk (x) is the decision function of the k-th classifier.
For comparison, classical SVM, Random Forest, and XGBoost
models are trained directly in multiclass mode using their
native scikit-learn implementations. Random Forest and
XGBoost natively support multiclass classification without decomposition, whereas QSVM requires OvR decomposition due
to the binary nature of the quantum kernel. This architectural
difference is an inherent constraint of current quantum kernel
methods rather than an experimental choice.

θi,i+1 = ηxi xi+1 ,
(13)

yielding the entangled feature state
n−1
h iX
i
X
1 X
|ψ2 ⟩ = √
exp −
xj zj +i
θj,j+1 zj zj+1 |z⟩ .
2 j
2n z
j=1
(14)
The resulting feature states |ψ2 ⟩ are used to compute the
quantum kernel (Eq. (10)), which forms the kernel matrix for
SVM classification between normal and attack traffic.

G. Quantum Kernel Analysis
QSVMs aim to improve non-linear separability by mapping
data into high-dimensional Hilbert spaces via quantum kernels.
For multiclass classification, a 10-qubit ZZFeatureMap with
depth 10 (reps=10) is used [34]. CICIDS2017 features are
encoded using Rz rotations and entangling layers, and kernels
are computed via state overlaps (Eq. (10)). The resulting kernel
matrix is used in a classical SVM with OvR decomposition.
Alternative feature maps are evaluated in Table IV.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3697692

6

TABLE IV
P ERFORMANCE C OMPARISON OF Q UANTUM F EATURE M APS ON
CICIDS2017 (1,000 RECORDS , 10 FEATURES , 5- FOLD CV)
Feature Map
ZFeatureMap
PauliFeatureMap
ZZFeatureMap

Accuracy %
94.6 ± 0.3
95.8 ± 0.2
96.9 ± 0.1

Precision %
94.2 ± 0.4
95.4 ± 0.3
96.5 ± 0.2

Recall%
94.9 ± 0.3
96.1 ± 0.2
97.0 ± 0.1

F1-score%
94.5 ± 0.3
95.7 ± 0.2
96.7 ± 0.1

The ZZFeatureMap consistently outperforms alternatives
and achieves the highest performance (96.7% binary F1-score
and 95.5% multiclass F1-score), and is therefore used for
both Regime A and Regime B. Its higher accuracy comes at
slightly increased simulation cost due to entangling operations
but remains computationally tractable under simulator-based
NISQ-inspired settings.
TABLE V
AVERAGE CLASSIFICATION TIME OF QUANTUM FEATURE MAPS
Feature Map
ZFeatureMap
PauliFeatureMap
ZZFeatureMap

Time/sample (s)
0.0032
0.0046
0.0050

Depth
Low
Medium
Adjustable

Remark
Fast but limited expressivity
Higher expressivity, increased cost
Best accuracy, slightly slower

TABLE VI
C OMPARISON OF KERNEL PROPERTIES
Property
Feature space
Entanglement
Representation
Evaluation cost (sim.)
Robustness

Classical RBF
Rd
None
Implicit RKHS map via kernel trick
∼O(d)
Moderate

Quantum Kernel
n
C2
Present (pairwise)
n
Explicit unitary map into C2
Simulator-dependent
Potentially enhanced

Unlike classical SVMs in Euclidean space, QSVMs exploit exponentially large Hilbert spaces, enabling improved
representation of complex intrusion patterns. The observed
robustness arises from the geometry of quantum feature
spaces, where small perturbations in input can map to nearly
orthogonal quantum states, stabilizing decision boundaries
[32], [35], [36]. This provides a theoretical basis for improved
adversarial robustness. As shown in Table VI, quantum kernels
differ fundamentally from classical kernels, suggesting that
future hardware improvements may further enhance QSVM
performance on complex or quantum-native datasets.
H. Training and Evaluation
This section describes the unified training and evaluation
pipeline for classical and quantum-enhanced models, ensuring
fair comparison between SVM and QSVM using identical
reduced feature sets under controlled conditions.
1) Dataset Splitting and Preprocessing: The dataset is
reduced to 10 features and split into 80% training and 20%
testing using stratified sampling. All preprocessing steps (normalization, encoding, and missing value handling) are fitted
only on the training set and applied to the test set using the
same parameters.
For model selection, 5-fold CV is performed on the training
set. Within each fold, preprocessing and feature selection are
refitted on the training split and applied to the validation split,
ensuring a leakage-free evaluation protocol.

2) Classical SVM Training: The classical SVM uses an
RBF kernel with hyperparameter optimization via grid search:
C ∈ {0.1, 1, 10, 100},

γ ∈ {0.01, 0.1, 1},

(16)

evaluated using 5-fold cross-validation on the training set.
As a baseline study, Linear, Polynomial, Sigmoid, and RBF
kernels were compared on a stratified subset of 1,000 samples
under identical validation settings. As shown in Table VII, the
RBF kernel achieves the best performance across all metrics
and is selected for the final SVM model.
TABLE VII
P ERFORMANCE COMPARISON OF SVM KERNELS ON CICIDS2017 (1,000
SAMPLES , 10 FEATURES , 5- FOLD CV)
Kernel
Linear
Polynomial
Sigmoid
RBF

Accuracy %
97.4 ± 0.4
98.5 ± 0.3
96.1 ± 0.5
99.2 ± 0.2

Precision %
97.1 ± 0.5
98.1 ± 0.4
95.8 ± 0.6
99.0 ± 0.3

Recall %
97.7 ± 0.3
98.8 ± 0.3
96.6 ± 0.4
99.4 ± 0.2

F1-score %
97.2 ± 0.4
98.4 ± 0.3
96.2 ± 0.5
99.1 ± 0.3

3) Quantum SVM (QSVM) Training: The QSVM employs
a quantum kernel constructed from a parameterized quantum
feature map (Section E), embedding a 10-dimensional input
into a 10-qubit Hilbert space via unitary operations. The kernel
is integrated into an SVM following [32], and all computations
are performed using the Qiskit Aer simulator [37]. Quantum
kernel estimation introduces sampling noise due to measurement statistics [38], which affects training stability and computational complexity. Feature map selection is performed under
identical data splits and validation protocols (Table IV) to
ensure a fair comparison across configurations. This controlled
setup isolates the expressive power of the quantum kernel
from hardware-induced noise, providing a near-term quantum
machine learning benchmark. However, deployment on real
NISQ hardware possibly .introduce additional imperfections
that can impact performance.
4) Evaluation Metrics: Model performance is evaluated
under two regimes. In Regime A (binary classification), accuracy, precision, recall, and F1-score are reported. In Regime
B (nine-class classification), macro-averaged precision, recall,
and F1-score are used to ensure equal weighting across
all classes, along with per-class F1-scores to analyze classspecific behavior.
Statistical significance is assessed using McNemar’s test,
while inter-model consistency is quantified using the Prediction Agreement Rate (PAR), defined as the fraction of
test samples with identical predictions from two classifiers.
McNemar’s test was computed on paired prediction disagreements over the held-out test set using the continuity-corrected
formulation. The complete training and evaluation workflow
is summarized in Algorithm 3.
IV. R ESULTS AND D ISCUSSIONS
Experimental results for both regimes are summarized in
Table IX and Figs. 5–7. Overall, classical models outperform
QSVM across both binary (Regime A) and multiclass (Regime
B) settings, though the performance gap narrows as task
complexity increases.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3697692

7

Algorithm 3 Model Training and Evaluation Pipeline
1: Input: Dataset D
2: Stratified split: (Xtrain , Xtest , Ytrain , Ytest )
5-Fold Cross-Validation:
3: for k = 1 to 5 do
(k)
(k)
(k)
(k)
4:
Split into (Xtrain , Xval , Ytrain , Yval )
(k)
5:
Apply Algorithm 1 and Algorithm 2 on Xtrain only;
(k)
apply learned parameters to Xval
6:
for each (C, γ) do
(k)
7:
Train SVM (RBF) and QSVM (OvR) on Xtrain
(k)
8:
Evaluate on Xval
9:
end for
10: end for
11: Select best (C, γ) from CV results
Final Training:
12: Apply Algorithm 1 and Algorithm 2 on full Xtrain
13: Train final SVM (RBF) and QSVM (OvR) on Xtrain
Testing:
14: Apply learned parameters from Algorithm 1 and Algorithm 2 to Xtest
15: Evaluate on (Xtest , Ytest ); compute Accuracy, Precision,
Recall,
F1-score, McNemar’s test, PAR
16: Output: Performance metrics for SVM and QSVM

In Regime A, SVM achieves an F1-score of 99.1%, compared to 96.7% for QSVM. In Regime B, SVM attains a
macro-F1 of 97.3%, while QSVM reaches 95.5%. Random
Forest (98.5%, 96.7%) and XGBoost (98.2%, 96.4%) also
outperform QSVM in both regimes. The SVM–QSVM gap
reduces from 2.4% (binary) to 1.8% (multiclass), indicating improved relative competitiveness of quantum kernels in
higher-dimensional decision boundaries. These results suggest
that the performance limitation of QSVM is primarily due
to NISQ-era constraints rather than the underlying kernel
formulation. Fig. 5 illustrates the overall comparison across
both regimes, while Fig. 6 shows macro-averaged metrics for
Regime B.
TABLE VIII
C OMPARISON OF RELATED Q UANTUM ML- BASED INTRUSION DETECTION
STUDIES
Study
[39]
[40]
[41]
[42]
[43]

Dataset
CIC-IDS-2017
IoT stream
UGRansome
IoT environment
(BoT-IoT, ACI
IoT, KDD)
Custom network
traffic dataset

Method
QSVM vs SVM
QSVM vs SVM
QSVM vs SVM

Reported Outcome
+0.62% F1
Improved perf.
+1.89% acc.

Remarks
Noise reduces hardware gains
Streaming/parallel focus
3–4 qubits, simulator

HQNN

90.70%, 92.80%,
94.90% acc.

Variable gains

QIDS-OA vs
AMM-CNN

99.8%, 98.7% acc.

High performance
on DDoS attack detection

Table IX reports detailed performance across both regimes.
SVM (RBF) achieves the best overall results, followed by
Random Forest, XGBoost, and QSVM.
Per-class analysis in Table X shows that the SVM–QSVM
performance gap varies with attack complexity. Lowcomplexity classes (Benign, DoS Hulk, DDoS, PortScan)
exhibit gaps of 1.2–1.5%, while high-complexity minority
classes (SQL Injection, Infiltration) show gaps of only 0.3%,
indicating that quantum kernel geometry provides relatively

Fig. 5. Performance comparison of classical and quantum classifiers across
binary (Regime A, 1,000 samples) and nine-class (Regime B, 1,800 samples)
CICIDS2017 evaluation using 10 features and 5-fold CV. The SVM–QSVM
gap decreases from 2.4% to 1.8%, indicating improved relative quantum kernel
performance in more complex settings.
TABLE IX
B INARY (R EGIME A) VS MULTICLASS (R EGIME B) PERFORMANCE ON
CICIDS2017 (10 FEATURES , 5- FOLD CV)
Model
SVM (RBF)
Random Forest
XGBoost
QSVM

Type
Classical
Classical
Classical
Quantum

Bin Acc
99.2
98.6
98.3
96.9

Bin F1
99.1
98.5
98.2
96.7

MC Acc
97.4
96.8
96.5
95.6

MC Prec
97.1
96.5
96.2
95.3

MC Rec
97.6
97.0
96.7
95.8

MC F1
97.3
96.7
96.4
95.5

stronger representational capacity in structurally harder decision regions.
TABLE X
P ER - CLASS TEST- SET F1- SCORE COMPARISON (40 TEST SAMPLES PER
CLASS UNDER 80/20 SPLIT )

Class
Benign
DoS Hulk
DDoS
PortScan
FTP Brute Force
SSH Brute Force
XSS
SQL Injection
Infiltration

N
40
40
40
40
40
40
40
40
40

SVM
99.1
98.9
98.7
98.6
97.4
97.1
95.8
93.4
91.8

QSVM
97.9
97.4
97.3
97.1
96.2
96.0
95.1
93.1
91.5

Gap
1.2
1.5
1.4
1.5
1.2
1.1
0.7
0.3
0.3

Complexity
Low
Low
Low
Low
Medium
Medium
Medium
High
High

Fig. 6 summarizes macro-averaged performance, confirming
consistent ranking: SVM > Random Forest > XGBoost >
QSVM. Fig. 7 further highlights that QSVM performance
degradation is reduced for structurally complex attack classes,
suggesting improved quantum kernel sensitivity in challenging
decision boundaries.
1) Statistical Validation and Discussion: McNemar’s test
confirms statistically significant differences in both regimes
(binary: χ2 = 4.21, p = 0.040; nine-class: χ2 = 6.12,
p = 0.013), supported by non-overlapping 95% confidence
intervals (Table XI).

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3697692

8

structure and phase encoding yield a more expressive decision
boundary in Hilbert space, consistent with the possibility that
quantum feature embeddings may encode certain nonlinear
feature interactions differently from classical Euclidean kernels [32], [33].
This behavior is operationally significant, as these highcomplexity classes are among the most critical for intrusion
response, where QSVM shows its strongest relative advantage.
TABLE XI
S TATISTICAL COMPARISON OF SVM AND QSVM UNDER BINARY
(R EGIME A) AND NINE - CLASS (R EGIME B).
Fig. 6. Macro-averaged performance comparison on Regime B (1,800
samples). SVM achieves the highest macro-F1 (97.3%), followed by Random
Forest (96.7%), XGBoost (96.4%), and QSVM (95.5%).

Fig. 7. Per-class F1-score comparison between SVM and QSVM. The performance gap ranges from 1.2–1.5% for low-complexity attack classes to 0.3%
for high-complexity minority classes (SQL Injection, Infiltration), indicating
improved QSVM relative performance in structurally harder decision regions.

The Prediction Agreement Rate (PAR) of 91.8% in Regime
B, indicates that both models agree on the majority of test
samples. The remaining 8.2% disagreement is concentrated
in SQL Injection, Infiltration, and FTP–SSH boundary cases,
suggesting that performance differences arise from localized
representational limits of the 10-feature quantum encoding
rather than a structural limitation of the quantum kernel.
2) Per-class Analysis: Table X and Fig. 7 show a clear
complexity-dependent trend. For low-complexity, high-volume
classes (DoS Hulk, DDoS, PortScan, Benign), both models exceed 97% F1, with SVM outperforming QSVM by 1.4–1.5%,
reflecting the strong suitability of the RBF kernel for wellseparated Euclidean structures.
For medium-complexity classes (FTP/SSH Brute Force,
XSS), the gap reduces to 0.7–1.2%, consistent with increased
feature overlap between authentication- and web-layer attacks.
For high-complexity minority classes (SQL Injection, Infiltration), the gap narrows further to 0.3% (93.4% vs. 93.1% and
91.8% vs. 91.5% F1). Here, the ZZFeatureMap’s entangling

Metric / Test
Mean F1 (± SD)
Mean Macro-F1 (± SD)
95% CI
95% CI
McNemar χ2
McNemar χ2
PAR
Hard-class F1

Regime
A – Binary
B – Nine-class
A – Binary
B – Nine-class
A – Binary
B – Nine-class
B – Nine-class
B– Nine-class

SVM (RBF)
99.1% ± 0.20
97.3% ± 0.25
[98.85, 99.35]
[96.99, 97.61]
—
—
—
92.6% avg

QSVM (ZZ)
96.7% ± 0.10
95.5% ± 0.15
[96.58, 96.82]
[95.31, 95.69]
4.21 (p=0.040)
6.12 (p=0.013)
91.8%
92.3% avg

Interpretation
Experimental result
—
Non-overlapping
Non-overlapping
Significant
Lower p-value
Strong agreement
Minimal difference

3) Sensitivity Analysis and External Validation: Sensitivity
results across dataset scales are summarized in Table XII.
The performance gap between SVM and QSVM decreases
from 2.4% (N=1,000) to 1.0% (N=450), indicating improved
relative QSVM competitiveness in low-data regimes, which
are representative of rare intrusion classes in cybersecurity
settings.
As sample size increases in the nine-class CICIDS2017
setting, the gap stabilizes at 1.1–1.8%, with larger datasets
favoring classical SVM performance due to stronger statistical
learning stability. Overall, this trend highlights a trade-off between data efficiency and asymptotic performance in quantum
kernel models.
Cross-dataset evaluation on NSL-KDD (five-class,
N=1,800) yields a 1.6% performance gap, lying between
constrained and full CICIDS2017 regimes. This indicates
consistent generalization behavior across intrusion detection
benchmarks under independent feature selection over
41-dimensional input space.
TABLE XII
S ENSITIVITY ANALYSIS : ROBUSTNESS ACROSS DATASET SCALES AND
EVALUATION SETTINGS

Setting
Binary
Nine-class
Nine-class
Nine-class
Cross-dataset

Dataset
CICIDS2017
CICIDS2017
CICIDS2017
CICIDS2017
NSL-KDD

N
1,000
450
900
1,800
1,800

Classes
2
9
9
9
5

SVM(%)
99.1± 0.2
91.8± 0.3
94.9± 0.3
97.3± 0.5
96.1± 0.3

QSVM(%)
96.7± 0.3
90.8± 0.5
93.8± 0.5
95.5± 0.3
94.5± 0.6

Gap(%)
2.4
1.0
1.1
1.8
1.6

V. C ONCLUSION
This work presents a systematic benchmarking study of
classical SVM and QSVM for multi-class intrusion detection on the CICIDS2017 dataset under NISQ-compatible
constraints. Using identical data regimes (binary Regime A
and nine-class Regime B), a 10-feature MI–selected feature
space, and 5-fold cross-validation with One-vs-Rest (OvR)
decomposition, we provide a fair and reproducible comparison
of classical and quantum kernel methods at realistic detection granularity. Our results confirm a statistically significant

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3697692

9

classical advantage under current NISQ constraints and lowdimensional feature representations; classical methods maintain an overall advantage across the full attack taxonomy.
Importantly, the observed gap is not interpreted as a fundamental limitation of quantum machine learning but as a consequence of resource-constrained quantum representations. The
SVM–QSVM performance gap is non-uniform across classes.
For low-complexity classes (Benign, DoS Hulk, DDoS, and
PortScan), the gap ranges from 1.2–1.5%, reflecting the strong
advantage of the RBF kernel for high-volume, volumetrically
distinct attack patterns. This gap reduces to 0.3% for highcomplexity minority classes (SQL Injection and Infiltration),
indicating relatively stronger QSVM representational capacity
in more challenging regimes where application-layer attacks
produce flow statistics near-indistinguishable from benign traffic. Rather than demonstrating immediate performance gains,
the primary contribution of this work is a standardized benchmarking framework for consistent classical–quantum comparison under identical constraints. These findings suggest that
any potential quantum advantage is conditional on richer feature embeddings and reduced information compression under
NISQ limitations. Although this study considers eight attack
categories, the proposed framework can be readily extended
to additional attack types. Future work will focus on: (i)
evaluating QSVM on near-term quantum hardware with error
mitigation techniques to determine whether the observed narrowing gap persists under realistic noise conditions, with faulttolerant hardware as a longer-term goal; (ii) developing hybrid
quantum–classical architectures for selective classification of
rare or ambiguous samples; and (iii) extending evaluation to
streaming IoT environments to assess the generalization of
regime-dependent quantum kernel behavior.

R EFERENCES
[1] Statista. (n.d.) Cost of cybercrime worldwide. [Online]. Available:
https://www.statista.com/forecasts/1280009/cost-cybercrime-worldwide
[2] Q. Li, H. Huang, R. Li, J. Lv, Z. Yuan, L. Ma, Y. Han, and Y. Jiang,
“A comprehensive survey on ddos defense systems: New trends and
challenges,” Computer Networks, vol. 233, p. 109895, 2023.
[3] M. Mohammadi, T. A. Rashid, S. H. T. Karim, A. H. M. Aldalwie,
Q. T. Tho, M. Bidaki, A. M. Rahmani, and M. Hosseinzadeh, “A comprehensive survey and taxonomy of the svm-based intrusion detection
systems,” Journal of Network and Computer Applications, vol. 178, p.
102983, 2021.
[4] D. Said and M. Elloumi, “A new false data injection detection protocol
based machine learning for p2p energy transaction between cevs,” in
2022 IEEE international conference on electrical sciences and technologies in maghreb (CISTEM), vol. 4. IEEE, 2022, pp. 1–5.
[5] A. Al-Bakaa and B. Al-Musawi, “A new intrusion detection system
based on using non-linear statistical analysis and features selection
techniques,” Computers & Security, vol. 122, p. 102906, 2022.
[6] K. Taghandiki, “Quantum machine learning unveiled: A comprehensive
review,” Journal of Engineering and Applied Research, vol. 1, no. 2, pp.
29–48, 2024.
[7] D. Said, “Quantum computing and machine learning for cybersecurity:
Distributed denial of service (ddos) attack detection on smart microgrid,” Energies, vol. 16, no. 8, p. 3572, 2023.
[8] M. S. Akter, H. Shahriar, S. I. Ahamed, K. D. Gupta, M. Rahman,
A. Mohamed, M. Rahman, A. Rahman, and F. Wu, “Case study-based
approach of quantum machine learning in cybersecurity: Quantum support vector machine for malware classification and protection,” in 2023
IEEE 47th Annual Computers, Software, and Applications Conference
(COMPSAC). IEEE, 2023, pp. 1057–1063.

[9] Z. Ahmad, A. Shahid Khan, C. Wai Shiang, J. Abdullah, and F. Ahmad,
“Network intrusion detection system: A systematic study of machine
learning and deep learning approaches,” Transactions on Emerging
Telecommunications Technologies, vol. 32, no. 1, p. e4150, 2021.
[10] Z. K. Maseer, R. Yusof, N. Bahaman, S. A. Mostafa, and C. F. M.
Foozy, “Benchmarking of machine learning for anomaly based intrusion
detection systems in the cicids2017 dataset,” IEEE access, vol. 9, pp.
22 351–22 370, 2021.
[11] J. Kumar Samriya, S. Kumar, M. Kumar, H. Wu, and S. Singh Gill, “Machine learning-based network intrusion detection optimization for cloud
computing environments,” IEEE Transactions on Consumer Electronics,
vol. 70, no. 4, pp. 7449–7460, 2024.
[12] R. Kumar, M. Swarnkar, and M. Muskan, “Lnnids: A hybrid liquid
neural network based ids for known and unknown iot attacks,” ACM
Transactions on Internet Technology, vol. 25, no. 4, pp. 1–31, 2025.
[13] I. S. Thaseen and C. A. Kumar, “Intrusion detection model using fusion
of chi-square feature selection and multi class svm,” Journal of King
Saud University-Computer and Information Sciences, vol. 29, no. 4, pp.
462–472, 2017.
[14] F. Sharif, “The role of ensemble learning in strengthening intrusion
detection systems: A machine learning perspective,” 2024.
[15] H. Kamal and M. Mashaly, “Advanced hybrid transformer-cnn deep
learning model for effective intrusion detection systems with class
imbalance mitigation using resampling techniques,” Future Internet,
vol. 16, no. 12, p. 481, 2024.
[16] B. Majid, S. A. Sofi, and Z. Jabeen, “Quantum machine learning: a
systematic categorization based on learning paradigms, nisq suitability,
and fault tolerance,” Quantum Machine Intelligence, vol. 7, no. 1, pp.
1–55, 2025.
[17] F. Ullah, S. Ullah, G. Srivastava, and J. C.-W. Lin, “Ids-int: Intrusion detection system using transformer-based transfer learning for imbalanced
network traffic,” Digital Communications and Networks, vol. 10, no. 1,
pp. 190–204, 2024.
[18] C. Nalayini, T. Soumya, S. Lalitha, and R. Tamijetchelvy, “A novel
adaptive transformer based quantum intrusion detection system for
software defined networks,” Scientific Reports, vol. 15, no. 1, p. 36505,
2025.
[19] P. Lamichhane and D. B. Rawat, “Quantum machine learning: Recent
advances, challenges and perspectives,” IEEE Access, 2025.
[20] Y.-Y. Hong and D. J. D. Lopez, “A review on quantum machine learning
in applied systems and engineering,” IEEE Access, 2025.
[21] D. Said, M. Bagaa, A. Oukaira, and A. Lakhssassi, “Quantum entropy
and reinforcement learning for distributed denial of service attack
detection in smart grid,” IEEE Access, vol. 12, pp. 129 858–129 869,
2024.
[22] R. A. Kerkatou, H. Belhadef, A. Eutamene, and S. P. Stefanova, “Hybrid
quantum machine learning for intrusion detection: A comparative study
of qnn and qsvm models,” IEEE Access, 2026.
[23] G. Abdulsalam and I. Ahmad, “Comparative investigation of quantum
and classical kernel functions applied in support vector machine algorithms,” Quantum Information Processing, vol. 24, no. 4, p. 109, 2025.
[24] A. A. Shaji, S. Sadhwani, R. Muthalagu, P. M. Pawar, and T. Mathew,
“Qml-ids: Quantum machine learning approaches for intrusion detection
systems in iot devices,” in 2025 3rd International Conference on
Computational Intelligence and Network Systems (CINS). IEEE, 2025,
pp. 1–7.
[25] P. Dinsha and R. Santhosh, “Quantum-inspired intrusion detection system using dual metaheuristic optimization and deep neural analysis,” in
2026 4th International Conference on Intelligent Data Communication
Technologies and Internet of Things (IDCIoT). IEEE, 2026, pp. 1481–
1486.
[26] R. Kumar, V. Varghese, S. Vidhya, P. Vigneshkumar, S. Santhoshkumar,
and D. Vikram, “Quantum machine learning-based anomaly detection
for cybersecurity systems,” in 2025 International Conference on Next
Generation Computing Systems (ICNGCS). IEEE, 2025, pp. 1–6.
[27] R. Kumar and M. Swarnkar, “QuIDS: A quantum support vector
machine-based intrusion detection system for IoT networks,” Journal
of Network and Computer Applications, vol. 234, p. 104072, 2025.
[28] A. B. M. Alzririg and A. K. Türkben, “Optimized intrusion detection
using bees algorithm enhanced deep neural networks with perfect roc
separability,” Journal of King Saud University Computer and Information Sciences, 2026.
[29] M. A. Nielsen and I. L. Chuang, Quantum computation and quantum
information. Cambridge university press, 2010.
[30] S. L. Wu, S. Sun, W. Guan, C. Zhou, J. Chan, C. L. Cheng, T. Pham
et al., “Application of quantum machine learning using the quantum

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3697692

10

kernel algorithm on high energy physics analysis at the lhc,” Physical
Review Research, vol. 3, no. 3, p. 033221, 2021.
[31] M. Schuld and N. Killoran, “Quantum machine learning in feature
hilbert spaces,” Physical Review Letters, vol. 122, no. 4, p. 040504,
2019.
[32] V. Havlı́ček, A. D. Córcoles, K. Temme, A. W. Harrow, A. Kandala,
J. M. Chow, and J. M. Gambetta, “Supervised learning with quantumenhanced feature spaces,” Nature, vol. 567, no. 7747, pp. 209–212, 2019.
[33] Z. Li, X. Liu, N. Xu, and J. Du, “Experimental realization of a quantum
support vector machine,” Physical review letters, vol. 114, no. 14, p.
140504, 2015.
[34] E. Krátká and A. G. Gábris, “Quantum computing methods for malware
detection,” in Machine Learning, Deep Learning and AI for Cybersecurity. Springer, 2025, pp. 207–228.
[35] M. Schuld and N. Killoran, “Quantum machine learning in feature
hilbert spaces,” Physical review letters, vol. 122, no. 4, p. 040504, 2019.
[36] G. Montalbano and L. Banchi, “Quantum adversarial learning for kernel
methods,” Quantum Machine Intelligence, vol. 7, no. 1, p. 15, 2025.
[37] Qiskit contributors, “Qiskit: An open-source framework for quantum
computing,” 2021, available at: https://qiskit.org. [Online]. Available:
https://qiskit.org
[38] D. A. Kreplin and M. Roth, “Reduction of finite sampling noise in
quantum neural networks, 2024. doi: https://doi.org/10.22331/q-202406-25-1385,” Quantum, vol. 8, no. 14, p. 1385, 2024.
[39] D. Abreu, C. E. Rothenberg, and A. Abelém, “Qml-ids: Quantum
machine learning intrusion detection system,” in 2024 IEEE Symposium
on Computers and communications (ISCC). IEEE, 2024, pp. 1–6.
[40] M. Kalinin and V. Krundyshev, “Security intrusion detection using
quantum machine learning techniques,” Journal of Computer Virology
and Hacking Techniques, vol. 19, no. 1, pp. 125–136, 2023.
[41] S. J. Nhlapo, E. N. Mutombo, and M. N. W. Nkongolo, “Parameterised
quantum svm with data-driven entanglement for zero-day exploit detection,” Computers, vol. 14, no. 8, p. 331, 2025.
[42] I. Bharathi, V. Sonai et al., “Quantum-driven enhanced machine learning
algorithm for intrusion detection in internet of things environment,” EPJ
Quantum Technology, vol. 13, no. 1, p. 20, 2026.
[43] T. H. Kim and S. Madhavi, “Quantum intrusion detection system using
outlier analysis,” Scientific Reports, vol. 14, no. 1, p. 27114, 2024.

Mujeeb Ur Rehman (Senior Member, IEEE; ORCID: 0000-0002-4228-385X) received the Ph.D. degree in Engineering, with a focus on artificial intelligence and cybersecurity, in 2022. He has more
than 10 years of teaching and research experience at
institutions including De Montfort University, University of Glasgow, and York St John University. He
was recognised among the Stanford/Elsevier World’s
Top 2% Scientists in 2025. He is a Senior Fellow of
the Higher Education Academy (SFHEA), a Senior
Member of IEEE, and a Professional Member of
the BCS. He has supervised numerous Ph.D. and master’s students and
has published over 60 research papers in leading journals and conferences,
including IEEE Transactions, IET journals, and Elsevier journals. In 2022, he
was endorsed as a Global Talent in Artificial Intelligence and Cyber Security
by the Royal Academy of Engineering. He has also received several Best Paper
Awards at international conferences. Dr. Rehman is a member of the Talent
Peer Review College at UK Research and Innovation and the National Institute
for Health and Care Research. He has contributed to multiple internationally
funded research projects, securing over £1.8 million in competitive research
funding. He was awarded a Gold Medal in his M.S. degree and graduated
with Distinction in his B.S. degree.

Kamran Rehan (ORCID: 0000-0002-3456-7890)
received the Ph.D. degree in atomic and molecular
physics from the University of Chinese Academy
of Sciences, China, in 2020, with a focus on quantum computing, quantum information processing,
precision measurement, and quantum simulations.
He subsequently held research positions at leading
institutions, including the University of Science and
Technology of China (USTC), the Beijing Academy
of Quantum Information Sciences, and Tsinghua
University. During his tenure at USTC, he led the development and establishment of a 40 Ca+ trapped-ions experimental platform
as a joint USTC and CAS-PIFI Fellow. He is currently an Assistant Professor
and an approved Ph.D. supervisor with the Department of Physics, The
University of Haripur, Pakistan. During his academic career, he has received
several national and international awards, including CAS-TWAS and CASPIFI fellowships, Excellent International Student and Excellent International
Graduate awards, and an Outstanding International Student award. He was also
awarded a Gold Medal for his bachelor’s degree. His research interests include
quantum computing, quantum information science, precision measurements,
and quantum simulations, with emerging applications in machine learning and
cybersecurity.

Muhammad Abrar (ORCID: 0009-0001-5494-7529)
received the B.S. degree in electrical engineering
from Riphah International University, Islamabad,
Pakistan, in 2020. He subsequently served as a
research associate, collaborating on projects in areas
including signal processing and machine learning.
He is currently pursuing the Ph.D. degree in the
School of Computer Science and Informatics, De
Montfort University, Leicester, U.K. He has coauthored several conference papers and journal articles in IEEE and other reputable venues. His research interests include deep learning, condition monitoring, signal processing,
computer vision, machine learning, data science, and their applications in
cybersecurity and intrusion detection.

Imran Rehan (ORCID: 0000-0004-5678-9012) received the Ph.D. degree in physics (biophotonics) in
Pakistan and completed a postdoctoral fellowship in
the United Kingdom in 2024. He has over 14 years
of experience in teaching and research and has supervised numerous undergraduate and postgraduate
students. He is an active member of the editorial
boards of several international scientific journals. His
research interests include AI-enhanced optical spectroscopy for biomedical diagnostics, environmental
monitoring, and materials science, with a focus on
label-free diagnostic techniques for diseases such as diabetes, chronic kidney
disease, and cancer. Dr. Rehan has authored or co-authored over 60 research
articles in international journals and a book chapter on CF-LIBS and its
applications. He is the recipient of the International Outstanding Scientist
Award (2021) and the Best Researcher of the Year Award (2017–2018).

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.
PAPER_TEXT
