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
# [587] A Physics-Informed Hybrid Approach for Cyberattack Detection in the Power Grid
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
编号：587
题名：A Physics-Informed Hybrid Approach for Cyberattack Detection in the Power Grid
年份：2026
DOI：10.1109/tia.2026.3676008
来源：IEEE Transactions on Industry Applications
PDF：paper/10.1109_TIA.2026.3676008.pdf
已有粗分类：恶意流量、暗网与攻击检测
二级关联：无
相关性：强相关，分数 13
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\587.txt
- 原始字符数：60781
- 本次发送字符数：60781
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3676008

1

A Physics-Informed Hybrid Approach for
Cyberattack Detection in the Power Grid
Fatemeh Sharifi, Graduate Student Member, IEEE, and Ali Mehrizi-Sani, Senior Member, IEEE

Abstract—Cyberattacks targeting critical infrastructure such
as the power grid pose significant risks to the reliability and
security of energy networks. Among the cyberattacks, false data
injection (FDI) attacks, which manipulate power grid data, is
a serious concern due to their potential to cause widespread
disruptions and damage. The 2015 Ukraine power grid cyberattack demonstrated its destructive potential and revealed the
real-world impact of such threats. It is especially challenging to
detect AC FDI attacks since they are based on the AC power flow.
Traditional cyberattack detection methods are primarily based
on rule-based or statistical anomaly detection. They often fall
short in detecting these cyber threats due to their design based on
static thresholds. Recent advances in deep learning show promise
in improving detection accuracy and adaptability. Building on
these advances, this paper proposes a novel physics-informed
approach for detecting AC FDI attacks in the power grid,
integrating graph attention convolutional networks (GACN), long
short-term memory (LSTM) networks, and unscented Kalman
filters (UKF). GACN uses the physical topology of the power
grid to capture spatial dependencies and correlations between
grid components, while LSTM models temporal dynamics. In
addition, UKF enhances the detection capabilities of the proposed
method as a second layer of protection. Extensive simulation
studies using PSCAD/EMTDC datasets demonstrate that the proposed method outperforms several baseline models in detecting
sophisticated cyber threats in the power grid. These baseline
models encompass a range of simpler machine learning and deep
learning architectures.
Index Terms—AC false data injection, cyberattack, graph
attention convolutional neural network, long short-term memory,
physics-informed detection, unscented Kalman filter.

I. I NTRODUCTION
In recent years, cyberattacks targeting critical infrastructure
systems, such as the power grid, pose significant threats to the
reliability and security of energy networks [1]–[3]. Among the
spectrum of cyber threats, false data injection (FDI) attacks
represent a critical vulnerability, wherein adversaries alter
power grid data. FDI attacks can lead to erroneous decisions
and potentially catastrophic consequences [4], [5]. A particular
variant, AC FDI attacks, is especially challenging to detect due
to its design based on the AC power flow [6]–[8]. Detecting
and mitigating AC FDI attacks in the power grid is important
to ensure its integrity and resilience.
Traditional approaches to FDI attack detection often rely on
rule-based methods or statistical anomaly detection techniques,
which may struggle to adapt to the evolving nature of cyber
F. Sharifi and A. Mehrizi-Sani are with the Bradley Department of Electrical
and Computer Engineering, Virginia Tech, Blacksburg, VA, 24061, USA (emails: {fatima94,mehrizi}@vt.edu).
This work is supported in part by the National Science Foundation
(NSF) under award ECCS-1953213 and in part by the State of Virginia’s
Commonwealth Cyber Initiative (www.cyberinitiative.org).

threats and the complex dynamics of the power grid [12], [13].
To address these challenges, recent research has explored the
application of advanced machine learning and deep learning
techniques for FDI attack detection, aiming to enhance the
accuracy and efficiency of detection algorithms [14]–[16]. The
use of deep neural networks (DNN) is increasing due to their
enhanced capacity for extracting information [17], [18].
In recent studies, various approaches are proposed to tackle
FDI detection by DNN. [19] addresses the growing risk of
cyber intrusions in power grid digitalization using an intrusion detection and mitigation system (IDMS) employing
DNNs. The proposed scheme in [20] employs a conditional
deep belief network (CDBN) to effectively identify the highdimensional temporal behavior features of FDI attacks. An
FDI attack detection is achieved through the integration of
discrete wavelet transform (DWT) and DNN techniques to
construct an intelligent detection system in [21]. In [22], the
authors propose a deep learning-based remedial action scheme
(RAS) utilizing long short-term memory (LSTM) networks
to mitigate the effects of FDI cyberattacks on the power
grid. A deep reinforcement learning-based method is proposed
in [23] to identify vulnerabilities in load frequency control
of the electric grid, synthesizing FDI and load switching
attacks. In [11], a two-step approach is proposed, combining
convolutional neural network with long short-term memory
(CNN-LSTM) models and an unscented Kalman filter (UKF)
to detect DC FDI attacks on the IEEE 39-bus system.
However, as highlighted in [1], [24], [25], the utilization of
graph neural networks (GNN) holds great promise for modeling complex relationships and dependencies in networked
systems, making them well-suited for physics-informed FDI
attack detection. In [26], the authors propose an unsupervised
approach combining dual graph-convolutional autoencoder
(DAE) and generative adversarial network (GAN) techniques.
The fault diagnosis method in [27] integrates graph convolutional networks (GCN) with prior system knowledge and
measurement data, offering improved diagnosis performance
by combining structural analysis and GCN techniques. The
approach in [9] employs short-time Fourier transform (STFT)
and a two-channel convolutional neural network (2C-CNN) for
spectral-temporal correlation modeling, followed by GCN for
spectral-spatial relationship modeling using nodal admittance
matrix and physical properties of the power grid to localize
FDI attacks. However, this method lacks the ability to fully
exploit the temporal dynamics of the system and may struggle
with real-time adaptability.
Moreover, current deep learning-based methods for FDI
attacks encounter challenges in interpretability, often characterized as “black box” approaches because of the inherent

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3676008

2

TABLE I
R ECENT S TUDIES ON FDI DETECTION BY DNN S
Paper

Detection Method

Physics-Based
Graph

Spatial Pattern
Recognition

Temporal Pattern
Recognition

Attention
Mechanism

Second Layer
of Protection

AC FDI

[9]

2C-CNN + GCN

✓

✓

[10]

DAMGAT

✓

✓

✓

✗

✗

✓

✗

✓

✗

✗

[11]

CNN-LSTM + UKF

✗

✓

✓

✗

✓

✗

This paper

GACN-LSTM + UKF

✓

✓

✓

✓

✓

✓

complexity of the models [10]. Therefore, using the attention mechanism which attains model interpretability by the
quantification of attention weights throughout the learning
process can address this concern. By incorporating a dualattention mechanism into a multi-head graph attention network
(DAMGAT), [10] captures spatial correlations between attack
characteristics and measurement data. However, using GCN
instead of GNN has benefits for processing graph-structured
data, efficient propagation of information through the graph,
and scalability for handling large-scale power grid networks.
Recent work on the power grid increasingly emphasizes
physics-informed learning, where data-driven methods are
constrained by the underlying physical laws and network
structure. For example, [28] introduces a physics-aware neural
network for distribution system state estimation, [29] develops
a physics-informed graphical learning approach for threephase line parameter estimation, and [30] provides a comprehensive review of physics-informed neural networks for power
system applications.
This paper proposes a novel physics-informed approach that
explicitly incorporates the topology of the power grid. This
method leverages the synergistic combination of graph attention convolutional networks (GACN), long short-term memory
(LSTM) networks, and UKF. Our approach integrates physicsinformed modeling at two levels: first, by embedding the grid
topology and electrical variables into GACN, and second,
by enforcing consistency with the AC measurement model
through UKF. Therefore, by utilizing a graph-based model
grounded in the system structure, the proposed framework
captures both spatial and temporal correlations within the grid.
As a second layer of detection, UKF has the advantage of
effectively estimating the true state of a system based on noisy
measurements and its dynamics. Moreover, UKF can adapt to
changes in system dynamics over time, making it suitable for
detecting attacks with less than 20% falsification.
The main contributions of this paper are
Applying GACN for handling large-scale data and providing interpretability of the measurements in the power
grid;
• Using LSTM networks to capture and analyze temporal
patterns in the power grid;
• Implementing UKF as a complementary layer of security
for improved detection capabilities; and
• Detecting and localizing multiple AC FDI attacks on
random number of buses or specific area of the power
grid.
•

The remainder of this paper is an overview of the proposed
framework. Section II explains the architecture and methodology. Section III describes the training dataset and AC FDI
attack preparation. Simulation details and results are presented
in Section IV. Finally, Section V summarizes the findings and
their significance.
II. M ETHODOLOGY
This section presents the methodology developed for detecting FDI attacks in the power grid. The proposed framework
integrates three core components: GACN, LSTM networks,
and UKF. The following subsections detail the function and
integration of each component within the proposed framework.
A. Graph Attention Convolutional Network
GACN is employed to model the complex spatial dependencies and relationships in the power grid. It uses graph-based
representations to capture the correlations between different
nodes. This physics-informed model employs an attention
mechanism to focus on the most relevant parts of the graph,
improving both detection accuracy and model interpretability.
Let G = (V, E) represent the power grid, where V denotes the set of nodes (buses), and E represents the edges
(transmission lines). The feature matrix X ∈ RN ×F describes
the node features, where N is the number of buses, and F
is the number of features per bus. In other words, this matrix
encapsulates features such as voltage, phase angle, real power,
reactive power, and other relevant properties linked to each bus
within the graph.
GACN computes the node embeddings H ∈ RN ×F by
aggregating information from neighboring buses using an
attention mechanism. Here, the embedding matrix H represents the updated bus features and captures the transformed
representations of each bus after aggregation.


X
Hi = σ 
αij W Xj  ,
(1)
j∈N (i)

where Hi represents the embedding of bus i, N (i) denotes
the neighborhood of bus i, W is the learnable weight matrix,
σ is a nonlinear activation function (ReLU), and αij is the
attention coefficient between bus i and j which determines
the importance of neighboring buses. The attention coefficients
αij are computed as

exp LeakyReLU(aT [W Xi ∥W Xj ])
P
, (2)
αij =
T
k∈N (i) exp (LeakyReLU(a [W Xi ∥W Xk ]))

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3676008

3

Attention Layers

Dense Layer

Mean

UT Covariance
Control
Center

Covariance
PMU
Measurements
GCN Layers

LSTM Layer
GACN-LSTM Network
(1st Level of Protection)

UT Mean
Unscented Kalman Filter
(2nd Level of Protection)

Discard
Attacked Data!

Discard
Attacked Data!

Physics-informed
Graph

Fig. 1. Schematic diagram of the proposed method, illustrating the two layers of protection and the detailed components within each layer.

where a is a learnable vector, and ∥ denotes concatenation. The
attention mechanism allows the model to dynamically focus
on the most informative connections in the graph.
B. Long Short-Term Memory Networks
To capture the temporal dependencies in power grid data,
LSTM is integrated into the framework. LSTM is well-suited
for sequential data analysis and can effectively model longterm dependencies, which are critical for detecting temporal
patterns indicative of FDI attacks. Given a sequence of node
embeddings {Ht }Tt=1 obtained from GACN over time T ,
LSTM processes this sequence to learn temporal patterns.
LSTM maintains a hidden state ht and a cell state ct at each
time step t, updated according to
it = σ(Wi Ht + Ui ht−1 + bi ),
ft = σ(Wf Ht + Uf ht−1 + bf ),
ot = σ(Wo Ht + Uo ht−1 + bo ),

(3)

ct = ft ⊙ ct−1 + it ⊙ tanh(Wc Ht + Uc ht−1 + bc ),
ht = ot ⊙ tanh(ct ),
where it , ft , ot are the input, forget, and output gates, respectively; W , U , and b are learnable parameters; σ denotes the
sigmoid activation function; and ⊙ represents element-wise
multiplication. By processing the sequence of node embeddings, LSTM captures the temporal dynamics and correlations
in power grid data, enhancing the detection of temporal
patterns associated with FDI attacks.
C. Unscented Kalman Filter
UKF extends the conventional Kalman filter to effectively
handle nonlinear systems. Unlike the extended Kalman filter
(EKF), which relies on linear approximations via first-order
Taylor expansions, UKF maintains a more accurate representation of the probability distribution utilizing a specific set of
“sigma points” to characterize the distribution of the system
states. These sigma points are passed through the nonlinear
system dynamics, enabling UKF to preserve the statistical
properties of the original distribution more accurately compared to the linearization technique of the EKF. By calculating

the mean and covariance from the propagated sigma points,
UKF captures nonlinearities in the system more effectively.
This deterministic sampling approach makes UKF particularly
advantageous for systems with significant nonlinear behaviors
or where precise linearization is difficult [31]. In addition,
unlike deep Kalman filter (DKF), which requires learning
complex latent dynamics and incurs substantial computational
and training costs, UKF directly incorporates the measurement
models of the power grid. Due to this feature of UKF, our
hybrid method is able to combine the advantages of both
data-driven and measurement-based approaches. For further
exploration of transient power grid state estimation using UKF,
see [32], [33].
To identify anomalies in the data, the chi-squared (χ2 ) test
is employed [34]. χ2 is calculated by summing the squared
differences between observed and expected values, normalized
by the expected measurement. A lower χ2 value indicates a
less substantial gap between observed and expected measurements, signaling a stronger correlation between variables or a
reduced likelihood of abnormal data.
A threshold value γ is defined to determine the probability
that a measurement lies within the uncompromised region.
This probability-based threshold is calculated as
Vγ (k) = {yk : (yk − ŷk )T S(k)−1 (yk − ŷk ) ≤ γ},

(4)

where yk denotes the measurement, and S(k) represents the
innovation covariance matrix at time step k.
The optimal selection of the threshold and innovation covariance matrix requires careful tuning to balance sensitivity
and false alarm rate. Achieving this balance is important
for designing an effective algorithm to detect abnormal data
patterns. The anomaly detection threshold γ is optimized
through a two-step process. First, an initial value is set based
on the inverse χ2 distribution at a 95% confidence level,
with the degrees of freedom equal to the dimension of the
innovation vector. This statistical choice corresponds to a
nominal false-alarm rate under the assumed Gaussian noise
model. Second, a grid search is performed on the validation
dataset, sweeping γ across a range from the 95% to the 99.9%
quantiles. For each candidate value, the detection performance

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3676008

4

is evaluated in terms of the F1-score and recall, while ensuring
the false-positive rate remains within operational limits. The
value of γ that provides the best trade-off between high
detection accuracy and low false-alarm rate is selected for the
final model. This procedure ensures that the UKF’s statistical
decision boundary is both theoretically grounded and tuned
for practical effectiveness. The UKF algorithm with anomaly
detector is explained in Algorithm 1.
“Physics-informed” means that the model structure and its
computations are constrained by the power grid physics: (i)
the graph and neighborhood system used by GACN are built
from the bus-branch topology, so message passing occurs
only along physically connected elements; (ii) node features
contain electrical variables (voltage magnitude/angle, line real
and reactive power), so attention is learned over physically
meaningful quantities; and (iii) the second layer (UKF) embeds the AC measurement model and uses the chi-squared
residual test consistent with state estimation practice. Together,
these design choices carry the power grid’s physical constraints
rather than purely data-driven correlations.
Algorithm 1 UKF Algorithm with Anomaly Detector
Initialize: Initial state m0 = m, covariance P0 = P , tuning
parameters α, β, κ, anomaly threshold γ
Output: Updated state mk , covariance Pk , anomaly detection
status
Compute λ = α2 (n + κ) − n
for k = 1, 2, . . . , T do
Prediction:
(i)
Generate sigma points Xk−1 from mk−1 and Pk−1
Propagate sigma points through the dynamics:
(i)
(i)
X̂k = f (Xk−1 )
−
Compute predicted state m−
k and covariance Pk
Update:
Transform sigma points for measurement:
(i)
−(i)
Ŷk = h(Xk )
Compute predicted measurement µk and innovation covariance Sk
Calculate cross-covariance Ck
Compute Kalman gain: Kk = Ck S−1
k
Update state estimate: mk = m−
k + Kk (yk − µk )
⊤
Update covariance estimate: Pk = P−
k − Kk Sk Kk
Anomaly Detection:
Calculate the residual yk = yk − µk
Compute the chi-squared test statistic: χ2 = ykT S−1
k yk
if χ2 > γ then
Anomaly detected at time step k
else
No anomaly detected
end if
end for

These systems are chosen due to their complexity and ability
to model real-world power grid scenarios.
The dataset is constructed by simulating a variety of operational conditions using PSCAD/EMTDC soft tool. The
dataset includes measurements of bus voltage magnitudes,
bus phase angles, line real power, and line reactive power.
Data collection is automated using a Python script that
runs PSCAD/EMTDC simulations across a range of predefined scenarios. In each scenario, a disturbance i for i ∈
{fault, load change, generator disconnection} is introduced at
bus j for j ∈ {1, 2, · · · , N } at time step k for k ∈
{1, 2, · · · , T }. N denotes the total number of buses, and T
represents the total number of simulation time steps. Fault
scenarios include three types: ABC-to-ground, A-to-B, and Ato-ground. By randomly varying the disturbance type, location,
and occurrence time, a comprehensive dataset is generated.
This dataset captures a broad range of potential system states
and conditions to ensure generalizability in model evaluation.
To determine the number of samples needed for effective
model training, a learning-curve analysis is performed by
incrementally increasing the size of the training set and
monitoring the F1-score and recall on a fixed validation set.
The performance improves significantly as the training set increases from 20% to about 80% of the full dataset, after which
the gains become marginal (less than 1% change in F1-score).
Based on this observation, the full dataset—consisting of 1,200
samples for the IEEE 118-bus system and a proportionally
similar number for the IEEE 39-bus system is considered. This
dataset ensures the model has adequate exposure to diverse
operational scenarios, disturbance types, and attack patterns
to generalize effectively.
The final dataset for the IEEE 118-bus system consists of
1,200 samples, each containing measurements from 118 buses
across 4 different parameters. Each sample is recorded over
1,500 time steps, capturing the dynamic behavior of the power
grid during each scenario with a time resolution of 0.001
seconds per step. The phase angles are measured in radians,
while the voltage magnitudes, real power, and reactive power
are in per unit (pu). The base apparent power is 100 MVA,
and the base voltage levels are 138 or 345 kV, depending on
the area of the grid being analyzed. The same procedure is
done to collect data for the IEEE 39-bus system.
To ensure effective training of deep learning models, minmax normalization is applied to standardize the raw data. This
normalization process scales all features to a uniform range,
typically [0, 1], enhancing the convergence of learning algorithms and improving model generalization across different
scenarios. In other words, this preprocessing step is needed to
mitigate the effects of varying data scales and ensure that the
model learns effectively from the input data.
B. False Data Injection Attack with AC Power Flow

III. DATA P REPARATION IN FALSE DATA I NJECTION
A. Dataset Collection Using PSCAD/EMTDC Software
To evaluate the effectiveness of the proposed approach, the
IEEE 118-bus and 39-bus systems are used as the testbed.

FDI attacks pose a significant threat to power grid security by intentionally altering sensor measurements to mislead
control systems, potentially leading to erroneous operational
decisions and disruptions. These attacks exploit vulnerabilities
in measurement data, making it challenging to distinguish

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3676008

5

between legitimate and manipulated data. For instance, an
FDI attack could involve altering voltage measurements of
certain buses to falsely indicate a stable grid condition, causing
the control system to delay necessary corrective actions and
potentially leading to grid instability or outages.
The AC power flow is governed by nonlinear equations
representing the steady-state operation of the power grid.
Therefore, AC FDI attacks are particularly challenging to
detect by bad data detection algorithms due to their alignment
with AC power flow. The AC power flow equations show the
relationship between bus voltages and the real and reactive
power flows in the network. For a given bus i, the real power
Pi and reactive power Qi are defined by
Pi =

n
X

Vi Vj (Gij cos θij + Bij sin θij ),

(5)

Vi Vj (Gij sin θij − Bij cos θij ),

(6)

a whose residual ra stays below the operator’s threshold τ .
The goal of the proposed methodology is to detect the presence
of the attack vector a to maintain the integrity and security
of the power grid. Effective detection requires distinguishing
between natural measurement variations and those caused by
malicious activities.
IV. P ERFORMANCE E VALUATION
This section presents the performance evaluation of the
proposed approach for detecting AC FDI attacks in the power
grid. The main objectives of this evaluation are to evaluate
detection accuracy, computational efficiency, and robustness
under various attack scenarios. Additionally, the proposed
method is compared against several baseline models to demonstrate its superiority in terms of different performance metrics.

j=1

Qi =

n
X
j=1

where Pi and Qi represent the real and reactive power injections at bus i, respectively. Vi is the voltage magnitude at bus
i. θij = θi − θj is the voltage angle difference between buses
i and j. Gij and Bij are the conductance and susceptance
between bus i and bus j, respectively.
The nonlinearity in these equations stems from the trigonometric terms, which complicates accurate state estimation. In
an AC FDI attack, an attacker manipulates the sensor measurements that feed into these equations, introducing errors that
lead to incorrect state estimations and compromised system
control.
AC FDI attacks can be modeled as additive perturbations to
the original measurements. If z represents the vector of true
measurements, an AC FDI attack modifies these measurements
to produce a compromised measurement vector za
za = z + a,

(7)

where za denotes the compromised measurement vector, z
is the true measurement vector, and a is the attack vector
that represents the malicious modifications introduced by
the attacker. The weighted least squares method is used to
calculate the system state estimate:
x = min[z − h(x)]T R−1 [z − h(x)],
x

(8)

where the system state is denoted by x, while the estimated
system state that best aligns with the measurement data z is
denoted by x̂. The nonlinear relationship between measurements and states is described by function h.
To conduct AC FDI attacks, a must be selected so that the
residual ra is below a threshold τ , usually set by an operator.
ra = ||za − h(xa )||22 .

(9)

Therefore, a successful FDI attack can manipulate power
grid measurements in a way that the AC state estimator fails
to identify the bad data, effectively disguising the attack as
accurate measurements. In other words, an assumption is
made that the attacker knows the network model and AC
measurement function h(·) sufficiently to craft an attack vector

A. Attacks Generation
AC FDI attacks are randomly conducted on the buses, where
the number of affected buses is uniformly distributed within
the interval [1, N/6], with N is the total number of buses.
The process for generating AC FDI attacks is described in
Section III. Since AC FDI attack detection is treated as a multilabel classification problem, data scaling attacks are added to
the dataset to create a more evenly distributed attack dataset.
For data scaling attacks, both the number of targeted buses
and the scale factor are uniformly distributed. The number
of targeted buses falls within the range [1, N/2], while the
scale factor is chosen from the interval [0.9, 0.95] ∪ [1.05, 1.1].
Attack types are gathered in a compact table with parameter
ranges.
In practice, AC FDI attacks do not always occur uniformly
across all buses, which can lead to an imbalanced dataset
where some buses have very few attack samples. To address
this, data-scaling attacks are introduced as an additional class
of disturbances. In these attacks, both the number of targeted
buses and the scaling factor are randomly varied, which
increases the diversity of attack patterns. Therefore, the dataset
becomes more balanced across different buses and scenarios,
ensuring that the model does not become biased toward
buses with more frequent attack samples. This balancing step
improves the robustness by giving the algorithm adequate
exposure to a wider range of possible attack conditions. The
complete distribution of disturbances and attack scenarios used
in this study is summarized in Table IV.
B. Evaluation Metrics
The evaluation of the proposed model is conducted using
several key performance metrics, which are elaborated in detail
below [10].
• Accuracy: The ratio of correctly identified instances (both
positive and negative) to the total number of instances.
This metric provides a general measure of the model’s
correctness.
• Precision: The proportion of correctly identified positive
instances to the total instances predicted as positive.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3676008

6

TABLE II
P ERFORMANCE COMPARISON OF THE PROPOSED MODEL AND BASELINE MODELS IN THE FIRST ATTACK SCENARIO
IEEE 39-Bus System

Model
SVM
CNN
CNN-LSTM [11]
CNN-LSTM + UKF [11]
GACN
GACN-LSTM
Proposed Model

IEEE 118-Bus System

Accuracy

Precision

Recall

F1-Score

Accuracy

Precision

Recall

F1-Score

0.610
0.694
0.716
0.786
0.864
0.876
0.912

0.595
0.714
0.735
0.865
0.902
0.925
0.931

0.496
0.581
0.680
0.810
0.878
0.915
0.920

0.526
0.602
0.664
0.844
0.887
0.904
0.918

0.584
0.642
0.684
0.764
0.849
0.863
0.909

0.471
0.614
0.721
0.821
0.899
0.918
0.924

0.356
0.494
0.677
0.777
0.849
0.910
0.916

0.395
0.526
0.619
0.819
0.834
0.898
0.904

TABLE III
P ERFORMANCE COMPARISON OF THE PROPOSED MODEL AND BASELINE MODELS IN THE SECOND ATTACK SCENARIO
IEEE 39-Bus System

Model
SVM
CNN
CNN-LSTM [11]
CNN-LSTM + UKF [11]
GACN
GACN-LSTM
Proposed Model

IEEE 118-Bus System

Accuracy

Precision

Recall

F1-Score

Accuracy

Precision

Recall

F1-Score

0.608
0.687
0.712
0.778
0.864
0.872
0.906

0.590
0.706
0.727
0.861
0.901
0.924
0.924

0.491
0.575
0.671
0.806
0.875
0.912
0.910

0.523
0.593
0.664
0.843
0.884
0.895
0.915

0.580
0.634
0.680
0.759
0.847
0.853
0.902

0.467
0.613
0.720
0.815
0.896
0.917
0.915

0.348
0.490
0.670
0.773
0.839
0.903
0.910

0.393
0.517
0.610
0.818
0.831
0.895
0.898

TABLE IV
S AMPLE DISTRIBUTION ACROSS DISTURBANCE TYPES AND ATTACK SCENARIOS
IEEE 39-Bus
Count

IEEE 118-Bus
Count

Random bus, random time
Random bus, random time
Random bus, random time
±10% to ±15% change in load
Random generator outage

120
120
120
120
120

360
360
360
360
360

Mag.: [−0.15, −0.1] ∪ [0.1, 0.15] pu; buses: [1, N/6]
Mag.: [−0.15, −0.1] ∪ [0.1, 0.15] pu; buses: [1, N/6]
Mag.: [−0.15, −0.1] ∪ [0.1, 0.15] pu; buses: [1, N/6]
Scale: [0.9, 0.95] ∪ [1.05, 1.1]; buses: [1, N/2]

120
120
120
120

360
360
360
360

Scenario Category

Scenario Type

Parameter Range

Disturbances

Three-phase fault (ABC-G)
Line-to-line fault (A-B)
Single-phase fault (A-G)
Load change
Generator disconnection

AC FDI Attacks

Load-bus attack
Generator-bus attack
Combined attack
Data scaling attack

Precision is crucial for understanding the model’s ability to correctly identify actual AC FDI attacks without
generating excessive false positives.
• Recall (Sensitivity): The proportion of correctly identified
positive instances to the total actual positive instances.
This metric reflects the model’s ability to detect attacks
and is vital for evaluating its effectiveness in preventing
undetected attacks.
• F1-Score: The harmonic mean of precision and recall,
providing a single measure that balances both concerns.
This metric is especially useful when dealing with class
imbalance or when both false positives and false negatives
need to be minimized.

These metrics provide a comprehensive view of the model’s
performance, allowing the evaluation to assess not only the
model’s accuracy but also its reliability, efficiency, and suitability for real-world applications.

C. Baseline Comparisons
To validate the effectiveness of the proposed approach,
comparisons are made against several baseline models for AC
FDI attack detection in the power grid. These baseline models
are selected to provide a comprehensive comparison across
different machine learning paradigms. These baseline models
include: support vector machine (SVM), convolutional neural
network (CNN), convolutional neural network with long short
term memory (CNN-LSTM), CNN-LSTM with UKF proposed
in [11], graph attention convolutional network (GACN), and
GACN-LSTM.
To ensure a fair and informative comparison, the baseline models are selected to represent a range of complexity
and capability in handling spatial, temporal, and physicsbased dependencies in the power grid. Simpler methods such
as support vector machines (SVM) and convolutional neural networks (CNN) capture static or spatial features but
lack explicit temporal modeling. The CNN-LSTM baseline
extends this by incorporating temporal dependencies, while
CNN-LSTM+UKF in [11] further integrates an estimator.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3676008

7

Graph attention convolutional networks (GACN) capture the
grid’s physical topology, and GACN-LSTM combines spatial
and temporal modeling. Including these baselines allows a
stepwise comparison, showing the effect of adding temporal modeling, graph-based spatial modeling, and estimation.
Other classical machine learning algorithms such as k-nearest
neighbors (KNN) and naive Bayes (NB) are excluded from
the reported results because they cannot effectively represent
graph-structured or temporal dependencies, and initial screening experiments showed substantially lower performance than
the selected baselines.
D. Setup and Model Architecture
All simulation studies are conducted using Python 3.8.10,
along with the Pypower 5.1.17, Tensorflow 2.13.0, and Sklearn
1.3.2 libraries, on a system equipped with an Intel i7-10700
CPU and 16GB of RAM. The dataset is split into training,
validation, and testing sets with a ratio of 6:2:2. Model
hyperparameters are tuned using a random search strategy, and
the model that achieves the highest recall on the validation set
is selected.
To assess real-time feasibility, the inference latency and
computational requirements of the proposed method are measured. The forward pass of the GACN-LSTM is profiled on the
experimental setup with batch size one to emulate streaming
operation. On the IEEE 118-bus dataset, the neural network
forward pass requires approximately 2.1 ms per time step,
dominated by graph attention convolutional layers and LSTM
recurrence. The UKF update, which involves state prediction,
covariance update, and residual calculation, adds 0.7 ms per
time step, with complexity scaling as O(n3x ) where nx is
the state dimension (for IEEE-118, nx = 472). The overall
end-to-end latency is therefore around 2.8 ms per sample,
which is well below the 16.7 ms budget required for real-time
monitoring at a 60 Hz PMU reporting rate.
Memory requirements also remain modest. The trained
GACN-LSTM model has about 1.3M parameters (∼5.2 MB),
and the UKF state and covariance matrices require less than
2 MB for the IEEE-118 system. These measurements indicate
that the hybrid model can be deployed on commodity multicore CPUs in control centers without dedicated GPUs, while
still meeting real-time requirements for wide-area monitoring.
For the CNN-LSTM model, the architecture consists of
three convolutional layers, each with a kernel size of 3 × 3.
A single LSTM layer follows the convolutional layers, before
a dense layer whose dimension corresponds to the number
of buses in the test case. For the GACN-LSTM model, the
structure includes three graph convolutional layers with the
same 3 × 3 kernel size, but each graph convolutional layer is
followed by an attention mechanism. Similarly, a single LSTM
layer is used before a dense layer, where the dimension is the
number of buses in the test case.
Different combinations of these models were systematically
evaluated to find the most effective approach for detecting AC
FDI attacks. The optimal architecture was selected based on its
ability to balance detection accuracy, computational efficiency,
and resilience to different attack patterns. The chosen design

uses a layered approach where GACN first processes locationbased grid features, allowing LSTM to then analyze how these
features change over time. By analyzing both location-based
and time-based patterns, this combination performs better
than other model arrangements in tracking power grid state
changes.
Both models are trained using the Adam optimizer with
an initial learning rate of 0.001 and a batch size of 64. The
training process continues for up to 100 epochs, with early
stopping implemented if the validation performance shows no
improvement for 5 consecutive epochs. The learning rate is
dynamically adjusted throughout training. Both models use
binary cross-entropy as their loss function.
E. Results and Analysis
All models are evaluated using online measurements obtained from the test cases simulated in PSCAD/EMTDC,
with the testing and analysis carried out through Python. The
Python code interfaces with PSCAD/EMTDC to process realtime measurements, which are then input into the models to
detect potential cyber intrusions within each time window.
1) Detection of Attack on Load Buses: In this case study,
the targeted buses are load buses, and both the real and reactive
power of those buses are manipulated. The magnitude of
manipulation applied to the targeted buses is randomly selected
from the interval [−0.15, −0.1] ∪ [0.1, 0.15]. Table II presents
a comparison of the performance of the proposed model
against baseline models in this attack scenario. The proposed
model consistently outperforms the baseline models across all
evaluation metrics. This indicates a higher capability of the
proposed model to detect AC FDI attacks accurately while
effectively minimizing false positives and false negatives. The
CNN-LSTM with UKF model shows moderate improvement
over CNN-LSTM, CNN, and SVM but falls short of the
graph-based models (GACN and GACN-LSTM), highlighting the importance of incorporating physics-informed spatial
correlations in the detection process. Ultimately, the superior
performance of the proposed model highlights the capabilities
of this combined approach in detecting and localizing AC FDI
attacks.
2) Attack Detection of Generator Buses: In this case study,
the targeted buses are generator buses, and the real power
and voltage of these buses are manipulated, with the intensity
of manipulation being identical to that in the first case study.
Table III presents the performance comparison of the proposed
approach and baseline models in the second attack scenario.
Consistent with the results from the first scenario, the proposed
model outperforms all baseline models across all evaluation
metrics. While slight reductions are observed in some metrics
compared to the first attack scenario, the proposed method
maintains a high level of performance, demonstrating its robustness even under varied attack patterns. The slight decrease
in performance across all models suggests that this attack
scenario presents a greater challenge for detection. Among
the baseline models, the GACN-LSTM and GACN models
perform relatively well, with GACN-LSTM showing slightly
better results than GACN in most metrics. However, both

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3676008

    

    

    

    

    
    
    
    
    
    
    

 , ( ( (   

 , ( ( (   

 , ( ( (    

     
     

    
    

     

    

     

    

 , ( ( (    

     

    
    

 & 1 1  / 6 7 0    8 . )
 * $ & 1

     

    
    

 , ( ( (    

 $ F F X U D F \

 )   V F R U H

    

 , ( ( (   

     

 )   6 F R U H

 3 U H F L V L R Q

 5 H F D O O

8

 , ( ( (   

 , ( ( (    

 * $ & 1  / 6 7 0
 3 U R S R V H G  0 R G H O

 , ( ( (     E X V  V \ V W H P

 & 1 1  / 6 7 0    8 . )
 * $ & 1

 , ( ( (      E X V  V \ V W H P

 * $ & 1  / 6 7 0
 3 U R S R V H G  0 R G H O

Fig. 2. Comparison of CNN-LSTM + UKF [11], GACN, GACN-LSTM and
the proposed method across various metrics including recall, precision, F1score, and accuracy.

Fig. 3. Comparison of CNN-LSTM + UKF [11], GACN, GACN-LSTM and
proposed method F1-score for the two test cases.

models still lag behind the proposed method, particularly
in precision and F1-score, highlighting the effectiveness of
the integrated approach. On the other hand, simpler models
like SVM and CNN exhibit significantly lower performance,
with notable reductions in recall and F1-score, emphasizing
their limitations in accurately identifying AC FDI attacks in
complex scenarios.
3) Combined Attack Detection: The targets of this case
study are both load and generator buses, and either the real and
reactive power for load buses or the real power and voltage
for generator buses are manipulated, with the intensity of
manipulation consistent with previous case studies. Table V
and Fig. 2 outline the performance comparison of the proposed
model and the baseline models in the third attack scenario. As
observed in previous scenarios, the model exhibits superior
precision and recall, further confirming its ability to accurately
detect AC FDI attacks. Compared to the first and second
attack scenarios, the proposed method exhibits slightly weaker
performance in the third scenario, particularly in precision and
F1-score. However, the proposed model performs better than
baseline models on every metric. This suggests that the model
is highly robust, even in scenarios that combine both load and
generator bus attacks, which typically present more complex
and dynamic challenges. Despite varying attack patterns, the
model precision remains high, indicating it can maintain low
false positive rates.
4) Combined Attack Detection with Higher Intensity Attack:
To further evaluate the contributions of the proposed framework, another case study was conducted using the third case
study scenario with a modification. In this study, the magnitude
of the manipulation applied to the targeted buses was randomly
selected from a wider range, specifically from the interval
[−0.2, −0.05] ∪ [0.05, 0.2]. This modification introduced more
variability in the severity of the attacks, testing the robustness
of the detection models under more diverse conditions. As
shown in Table VI and Fig. 3, even in the presence of this

broader range of cyber intrusions, the proposed method has a
better performance compared with the baseline models across
all metrics. This is particularly evident in the precision and F1score, highlighting the model’s ability to consistently detect
attacks, even with varying conditions and attack patterns.
The results of the performance evaluation clearly indicate
that the proposed approach offers significant improvements
over base methods, particularly in terms of precision, recall,
and interpretability. A key advantage of this approach lies in
its use of the attention mechanism, which prioritizes the most
relevant connections or nodes based on the current state of
the system and the patterns learned from historical data. This
significantly enhances interpretability, as the model does not
treat the power grid as a black box but instead provides insights
into the real-world interactions and dependencies within the
grid. By leveraging the physical topology of the power grid,
the graph attention mechanism helps localize attacks with
high accuracy, enabling operators to visualize which parts
of the grid are most at risk. This not only facilitates early
detection of attacks but also supports preemptive actions to
mitigate potential disruptions. In contrast to previous deep
learning approaches, which often lack transparency, the proposed method offers interpretable results that align with the
physical structure of the grid, providing a more actionable and
intuitive framework for cyberattack detection and localization.
The integration of graph-based learning, temporal sequence
analysis, and state estimation through the UKF enhances the
model’s robustness in detecting and mitigating AC FDI attacks.
The model’s ability to achieve high F1-score demonstrates
its effectiveness in distinguishing between normal and compromised states within power grid environments. However,
despite these promising results, some limitations were observed, particularly regarding the increased computational time
required for training due to the model’s complexity. Future
work could focus on optimizing the training process to reduce

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3676008

9

TABLE V
P ERFORMANCE COMPARISON OF THE PROPOSED MODEL AND BASELINE MODELS IN THE THIRD ATTACK SCENARIO
IEEE 39-Bus System

Model
SVM
CNN
CNN-LSTM [11]
CNN-LSTM + UKF [11]
GACN
GACN-LSTM
Proposed Model

IEEE 118-Bus System

Accuracy

Precision

Recall

F1-Score

Accuracy

Precision

Recall

F1-Score

0.611
0.697
0.721
0.786
0.864
0.881
0.910

0.591
0.715
0.729
0.870
0.904
0.928
0.932

0.497
0.577
0.671
0.813
0.879
0.917
0.913

0.527
0.603
0.667
0.848
0.891
0.899
0.918

0.590
0.641
0.689
0.764
0.848
0.854
0.903

0.469
0.620
0.726
0.817
0.906
0.925
0.916

0.355
0.491
0.676
0.777
0.841
0.908
0.917

0.402
0.526
0.612
0.823
0.836
0.900
0.906

TABLE VI
P ERFORMANCE COMPARISON OF THE PROPOSED MODEL AND BASELINE MODELS IN THE ABLATION STUDY
IEEE 39-Bus System

SVM
CNN
CNN-LSTM [11]
CNN-LSTM + UKF [11]
GACN
GACN-LSTM
Proposed Model

IEEE 118-Bus System

Accuracy

Precision

Recall

F1-Score

Accuracy

Precision

Recall

F1-Score

0.627
0.713
0.738
0.800
0.880
0.895
0.924

0.605
0.729
0.743
0.886
0.920
0.944
0.946

0.503
0.593
0.685
0.827
0.895
0.931
0.929

0.540
0.619
0.681
0.864
0.905
0.915
0.932

0.604
0.654
0.705
0.778
0.862
0.870
0.917

0.486
0.636
0.740
0.833
0.922
0.941
0.932

0.368
0.507
0.693
0.793
0.857
0.924
0.931

0.419
0.539
0.629
0.839
0.850
0.914
0.922

1.0

computational overhead and improve the model’s scalability
for larger the power grid.

28 29
26

F. Attention Interpretability
The attention mechanism is not only used internally for
feature weighting, but also provides an interpretable signal for
operators. In practice, the normalized attention coefficients can
be aggregated over a detection window and ranked to identify
the most affected buses. This yields a simple “top-k suspect
list,” which can be overlaid on the grid topology to highlight
the regions most likely under attack. As illustrated in Fig. 4,
the attention weights concentrate on the attacked buses and
their immediate neighbors.
G. Practical Considerations for Real-World Deployment
In this paper, the dataset is derived from PSCAD/EMTDC
simulations. In real-world applications, PMU measurements
may include higher noise levels, missing samples, or unexpected disturbances not captured in the simulation. Our
framework partially addresses these challenges through the
UKF, which down-weights inconsistent measurements via the
innovation covariance and thus provides robustness against
measurement noise. Missing data can also be mitigated with
standard interpolation or imputation methods before being
input to the GACN-LSTM. A thorough validation with field
PMU data remains an important next step, and forms a
direction for future work to ensure reliable deployment.
Another key practical challenge is grid adaptability. In
practice, grid topologies change due to switching operations,
reconfiguration, and variations in generation dispatch. The
proposed framework mitigates this challenge by embedding
the physical topology into the GACN layer, so re-training on
a modified grid does not require fundamental changes to the

34

20
33

19
18

27
30
17 2

25

16

24
21

1

4

7

23
22

0.6

36
35

0.4

14
13

5

8

0.8

37

15

3
39
9

38

Attention Score

Model

6

31

12 10
11

0.2

32

Fig. 4. Visualization of attention weights during a representative AC-FDI
attack on the IEEE 39-bus system.

architecture. Because GACN takes the grid adjacency matrix
as an explicit input, topology changes can be incorporated by
updating the edge admittances and re-running inference. For
small or localized changes, GACN parameters remain useful,
and only minimal fine-tuning of the final layers is typically
required. Similarly, for the UKF layer, topology or dispatch
updates imply adjustments to the measurement function and
measurement noise covariances, which can be updated without
retraining.
To further enhance adaptability, several practical online and
transfer learning techniques can be considered in future work.
These include fine-tuning the classifier on a small buffer

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3676008

10

of recent measurements after a topology change, continual
learning with replay to avoid catastrophic forgetting, and
periodic retraining during low-load windows using logged
measurements combined with simulated events for the new
topology. These strategies will help ensure that the framework
remains robust and effective under dynamic and evolving grid
conditions.
V. C ONCLUSION
This paper proposed a novel approach for detecting AC
FDI attacks in the power grid, combining GACN, LSTM
networks, and UKF. By integrating graph-based modeling,
temporal sequence analysis, and dynamic state estimation, the
framework enhances accuracy, scalability, and interpretability
in detecting and localizing AC FDI attacks. Simulation results
on the IEEE 39-bus and 118-bus systems demonstrate the
method’s robustness. GACN effectively captures spatial correlations, LSTM models temporal patterns, and UKF increases
resilience by accurately estimating the grid’s true state under
noisy conditions. The attention mechanism in GACN further improves interpretability, highlighting critical nodes and
connections vulnerable to attacks. This work emphasizes the
importance of combining deep learning with traditional state
estimation for securing the power grid. Future research could
focus on optimizing computational efficiency and extending
the framework to larger grids and other types of cyberattacks.
R EFERENCES
[1] M. J. Zideh, P. Chatterjee, and A. K. Srivastava, “Physics-informed
machine learning for data anomaly detection, classification, localization,
and mitigation: A review, challenges, and path forward,” IEEE Access,
vol. 12, pp. 4597–4617, Dec. 2023.
[2] H. Zhang, B. Liu, and H. Wu, “Smart grid cyber-physical attack and
defense: A review,” IEEE Access, vol. 9, pp. 29 641–29 659, Feb. 2021.
[3] M. Beikbabaei, A. Mehrizi-Sani, and C.-C. Liu, “State-of-the-art of
cybersecurity in the power system: Simulation, detection, mitigation, and
research gaps,” IET Gener. Transm. Distrib., vol. 19, no. 1, p. e70006,
Jan. 2025.
[4] G. Liang, J. Zhao, F. Luo, S. R. Weller, and Z. Y. Dong, “A review of
false data injection attacks against modern power systems,” IEEE Trans.
Smart Grid, vol. 8, no. 4, pp. 1630–1638, Mar. 2016.
[5] M. Rahman, J. Yan, and E. T. Fapi, “Adversarial artificial intelligence in
blind false data injection in smart grid ac state estimation,” IEEE Trans.
Ind. Inform., vol. 20, no. 6, pp. 8873–8883, Apr. 2024.
[6] R. Jiao, G. Xun, X. Liu, and G. Yan, “A new AC false data injection
attack method without network information,” IEEE Trans. Smart Grid,
vol. 12, no. 6, pp. 5280–5289, Aug. 2021.
[7] G. Hug and J. A. Giampapa, “Vulnerability assessment of ac state
estimation with respect to false data injection cyber-attacks,” IEEE
Trans. Smart Grid, vol. 3, no. 3, pp. 1362–1370, Aug. 2012.
[8] M. Jin, J. Lavaei, and K. H. Johansson, “Power grid ac-based state
estimation: Vulnerability analysis against cyber attacks,” IEEE Trans.
Autom. Control., vol. 64, no. 5, pp. 1784–1799, Jul. 2018.
[9] S. Peng, Z. Zhang, R. Deng, and P. Cheng, “Localizing false data injection attacks in smart grid: A spectrum-based neural network approach,”
IEEE Trans. Smart Grid, vol. 14, no. 6, pp. 4827–4838, Mar. 2023.
[10] X. Su, C. Deng, J. Yang, F. Li, C. Li, Y. Fu, and Z. Y. Dong, “DAMGAT
based interpretable detection of false data injection attacks in smart
grids,” IEEE Trans. Smart Grid, vol. 15, no. 4, pp. 4182–4195, Feb.
2024.
[11] F. Sharifi and A. Mehrizi-Sani, “False data injection cyberattack detection in transmission system based on deep learning and unscented
Kalman filter,” in IEEE Energy Conversion Congress and Exposition
(ECCE), Phoneix, AZ, Oct. 2024.
[12] J. Zhao, L. Mili, and M. Wang, “A generalized false data injection attacks
against power system nonlinear state estimator and countermeasures,”
IEEE Trans. Power Syst., vol. 33, no. 5, pp. 4868–4877, Jan. 2018.

[13] W. Xu, M. Higgins, J. Wang, I. M. Jaimoukha, and F. Teng, “Blending
data and physics against false data injection attack: An event-triggered
moving target defence approach,” IEEE Trans. Smart Grid, vol. 14, no. 4,
pp. 3176–3188, Dec. 2022.
[14] M. Beikbabaei, A. Mehrizi-Sani, and C.-C. Liu, “Cyberattack detection
and mitigation on central volt-VAr using circuit law and machine
learning,” IET J. Eng., Mar. 2025, accepted for publication (JOE-202404-0132).
[15] M. Beikbabaei, C. Larsen, and A. Mehrizi-Sani, “Model-free cyberresilient coordinated inverter control in a microgrid,” IEEE Access,
vol. 12, pp. 137 790–137 804, Sep. 2024.
[16] M. Beikbabaei, B. M. Kwiatkowski, and A. Mehrizi-Sani, “Modelfree resilient grid-forming and grid-following inverter control against
cyberattacks using reinforcement learning,” Electron., vol. 14, no. 2,
Jan. 2025.
[17] G. Zhang, J. Li, O. Bamisile, D. Cai, W. Hu, and Q. Huang, “Spatiotemporal correlation-based false data injection attack detection using
deep convolutional neural network,” IEEE Trans. Smart Grid, vol. 13,
no. 1, pp. 750–761, Sep. 2021.
[18] H. Wang, J. Ruan, G. Wang, B. Zhou, Y. Liu, X. Fu, and J. Peng, “Deep
learning-based interval state estimation of ac smart grids against sparse
cyber attacks,” IEEE Trans. Ind. Inform., vol. 14, no. 11, pp. 4766–4778,
Feb. 2018.
[19] A. Aljohani, M. AlMuhaini, H. V. Poor, and H. Binqadhi, “A deep
learning-based cyber intrusion detection and mitigation system for smart
grids,” IEEE Trans. Artif. Intell., vol. 5, no. 8, pp. 3902–3914, Jan. 2024.
[20] Y. He, G. J. Mendis, and J. Wei, “Real-time detection of false data injection attacks in smart grid: A deep learning-based intelligent mechanism,”
IEEE Trans. Smart Grid, vol. 8, no. 5, pp. 2505–2516, May 2017.
[21] J. James, Y. Hou, and V. O. Li, “Online false data injection attack
detection with wavelet transform and deep neural networks,” IEEE
Trans. Ind. Inform., vol. 14, no. 7, pp. 3271–3280, Apr. 2018.
[22] E. Naderi and A. Asrari, “A deep learning framework to identify remedial action schemes against false data injection cyberattacks targeting
smart power systems,” IEEE Trans. Ind. Inform., vol. 20, no. 2, pp.
1208–1219, May 2023.
[23] A. S. Mohamed and D. Kundur, “On the use of reinforcement learning
for attacking and defending load frequency control,” IEEE Trans. Smart
Grid, vol. 15, no. 3, pp. 3262–3277, Dec. 2023.
[24] T. Bilot, N. El Madhoun, K. Al Agha, and A. Zouaoui, “Graph neural
networks for intrusion detection: A survey,” IEEE Access, vol. 11, pp.
49 114–49 139, May 2023.
[25] O. Boyaci, M. R. Narimani, K. R. Davis, M. Ismail, T. J. Overbye,
and E. Serpedin, “Joint detection and localization of stealth false data
injection attacks in smart grids using graph neural networks,” IEEE
Trans. Smart Grid, vol. 13, no. 1, pp. 807–819, Oct. 2021.
[26] H. Feng, Y. Han, F. Si, and Q. Zhao, “Detection of false data injection
attacks in cyber-physical power systems: An adaptive adversarial dual
autoencoder with graph representation learning approach,” IEEE Trans.
Instrum. Meas., vol. 73, pp. 1–11, Nov. 2023.
[27] Z. Chen, J. Xu, T. Peng, and C. Yang, “Graph convolutional networkbased method for fault diagnosis using a hybrid of measurement and
prior knowledge,” IEEE Trans. Cybern., vol. 52, no. 9, pp. 9157–9169,
Mar. 2021.
[28] A. S. Zamzam and N. D. Sidiropoulos, “Physics-aware neural networks
for distribution system state estimation,” IEEE Trans. Power Syst.,
vol. 35, no. 6, pp. 4347–4356, Nov. 2020.
[29] W. Wang and N. Yu, “Estimate three-phase distribution line parameters
with physics-informed graphical learning method,” IEEE Trans. Power
Syst., vol. 37, no. 5, pp. 3577–3591, Sept. 2022.
[30] B. Huang and J. Wang, “Applications of physics-informed neural networks in power systems - a review,” IEEE Trans. Power Syst., vol. 38,
no. 1, pp. 572–588, Jan. 2023.
[31] S. Särkkä, Bayesian Filtering and Smoothing.
Cambridge, U.K:
Cambridge University Press, Jun. 2013.
[32] F. Sharifi, A. Mehrizi-Sani, and K. Tehrani, “Parameter estimation of
transient voltage signals with an unscented Kalman filter,” in North
American Power Symposium (NAPS), Salt Lake City, UT, Oct. 2022.
[33] E. Fouladi, F. Sharifi, and A. Mehrizi-Sani, “Online exciter controller
tuning for a synchronous condenser in a weak grid,” in IEEE 32nd Int.
Symp. Ind. Electron. (ISIE), Helsinki, Finland, Aug. 2023.
[34] F. van Wyk, Y. Wang, A. Khojandi, and N. Masoud, “Real-time sensor
anomaly detection and identification in automated vehicles,” IEEE Trans.
Intell. Transp. Syst., vol. 21, no. 3, pp. 1264–1276, Mar. 2020.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.
PAPER_TEXT
