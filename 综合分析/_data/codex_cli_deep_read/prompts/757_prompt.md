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
# [757] Multivariate Time Series Anomaly Detection Using Learnable Spatial-Temporal Graph Ordinary Differential Equations Network
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
编号：757
题名：Multivariate Time Series Anomaly Detection Using Learnable Spatial-Temporal Graph Ordinary Differential Equations Network
年份：2025
DOI：10.1109/tdsc.2025.3640165
来源：IEEE Transactions on Dependable and Secure Computing
PDF：paper/10.1109_TDSC.2025.3640165.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：图学习、知识图谱与威胁情报、入侵检测与网络异常检测
相关性：中相关，分数 8
已有代码状态：已下载；MAD-ODE -> source\MAD-ODE

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\757.txt
- 原始字符数：75483
- 本次发送字符数：75483
- 是否截断：False

代码包：
- 仓库：MAD-ODE
  - URL：https://github.com/AIOps-tech/MAD-ODE
  - 状态：downloaded
  - 本地目录：source\MAD-ODE
  - 顶层结构：.idea/、.ipynb_checkpoints/、LICENSE、README.md、Untitled.ipynb、__pycache__/、anormaly_detect.py、anormaly_detect1.py、anormaly_detect_gdn.py、anormaly_detect_jump.py、datasets/、demo.py、demo/、err_scores.py、eval_methods.py、evaluate.py、gdn/、graph/、jump/、lib/、mai.py、model/、modelode.py、nohup.out、odegcn.py、requirements.txt、runs/、script/、scripts/、src/
  - 主要语言：Python:78、Jupyter:1
  - README 标题：Hardware support、Installation、Data Preparation、Create data directories、msl、swat、wadi、smap、smap、Train Model
  - README 运行线索：Python 3.8, PyTorch 1.10, and CUDA version 11.3, and were trained on a server；bash pip install -r requirements.txt；bash # Create data directories；python -m scripts.generate_msl_dataset；python -m scripts.generate_swat_dataset；python -m scripts.generate_wadi_dataset；python -m scripts.generate_smap_dataset；python -m scripts.generate_smd_dataset
  - 关键文件：{"依赖环境": ["requirements.txt", "util/env.py"], "推理/演示入口": ["demo.py", "demo/demo.py", "demo/demo2.py", "demo/demo3.py", "lib/demo.py", "model/pytorch/demo.py"], "数据处理入口": ["script/dataloader.py", "util/preprocess.py"], "模型定义": ["modelode.py", "model/layers.py", "model/models.py", "model/pytorch/model.py", "src/models.py", "src1/models.py", "util/net_struct.py"], "训练入口": ["train.py"], "评估/测试入口": ["evaluate.py", "eval_methods.py", "test.py", "scripts/eval_baseline_methods.py"]}
  - 数据集线索：KDD、MSL、SMAP、SMD、SWaT、Tor、WADI、msl、smap、smd、swat、ton

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 2, MARCH/APRIL 2026

3723

Multivariate Time Series Anomaly Detection Using
Learnable Spatial-Temporal Graph Ordinary
Differential Equations Network
Shiming He , Qingqing Guo , Keyao Feng, Diqing Liang , Kun Xie , Member, IEEE,
and Pradip Kumar Sharma , Senior Member, IEEE

Abstract—Multivariate time series anomaly detection (MTSAD)
plays a critical role in the Internet of Things (IoT) by identifying
malfunctions and attacks. Graph Neural Networks (GNNs) have
been widely employed in MTSAD to capture spatial features but
require predefined and explicit graph structures. Graph Structure
Learning (GSL) addresses this limitation by jointly learning the
graph structure and downstream tasks. However, existing GSLbased MTSAD methods fail to effectively leverage prior knowledge
and struggle with insufficient GNN depth, limiting their ability
to capture long-range dependencies. To address these challenges,
we propose a multivariate time series anomaly detection method
based on a learnable spatio-temporal graph ordinary differential
equation network (STGODE), named MAD-ODE. Our approach
leverages hybird graph learning, which includes two types of graph
structures: a static similarity graph and a learnable graph. The
static similarity graph is constructed using prior knowledge and
provides a stable, interpretable representation of sensor dependencies. In contrast, the learnable graph captures complex relationships between sensors by optimizing its structure through
backpropagation. This hybird graph learning effectively incorporates both prior knowledge and learned dependencies, ensuring
robust and flexible modeling of sensor relationships. Furthermore,
we design a STGODE predictor, which operates on both graph
structures and employs continuous graph convolutional networks,
enabling it to capturing long-range spatio-temporal dependencies
for forecasting the next timestamp. Extensive experiments conducted on five datasets demonstrate that MAD-ODE achieves the
best average performance and maintains stable results compared
to existing methods.

Received 20 March 2025; revised 23 November 2025; accepted 30 November 2025. Date of publication 4 December 2025; date of current version 12
March 2026. This work was supported in part by the National Natural Science
Foundation of China under Grant 62025201 and Grant 62272062, in part by the
Science and Technology Innovation Program of Hunan Province under Grant
2023RC3139, and in part by the Natural Science Foundation of Hunan Province
under Grant 2025JJ50373. (Corresponding author: Kun Xie.)
Shiming He, Qingqing Guo, Keyao Feng, and Diqing Liang are with
the School of Computer Science and Technology and the Hunan Provincial Key Laboratory of Intelligent Processing of Big Data on Transportation, Changsha University of Science and Technology, Changsha
410114, China (e-mail: smhe_cs@csust.edu.cn; guoqingqing@stu.csust.edu.cn;
kyfeng@stu.csust.edu.cn).
Kun Xie is with the College of Computer Science and Electronics Engineering,
the Ministry of Education Key Laboratory of “Fusion Computing of Supercomputing and Artificial Intelligence,”, Hunan University, Changsha 410082, China
(e-mail: xiekun@hnu.edu.cn).
Pradip Kumar Sharma is with the Department of Computing Science, University of Aberdeen, AB24 3FX Aberdeen, U.K. (e-mail:
Pradip.sharma@abdn.ac.uk).
Digital Object Identifier 10.1109/TDSC.2025.3640165

Index Terms—Multivariate time series, graph neural networks,
IoT security, anomaly detection, spatial-temporal graph ordinary
differential equation network, graph structure learning.

I. INTRODUCTION
N THE Internet of Things (IoT), attacks can cause physical
damages to life-dependent physical processes. IoT attack detection approaches typically analyze three primary data sources:
sensor data [1], network traffic [2], [3], [4], and Supervisory
Control and Data Acquisition (SCADA) execution context [5].
Among these, sensor data directly reflects deviations in observed
physical states from expected behaviors, making it a critical
resource for detecting anomalies. Various sensors continuously
generate large volumes of time series data to monitor the critical
infrastructures. This data, collected from multiple sensors, is
referred to as multivariate time series (MTS). Abnormal changes
in MTS often indicate not only system attacks but also equipment failures. If these anomalies are not detected and mitigated
promptly, they can lead to catastrophic system failures, resulting
in significant economic losses [6], [7]. Given the importance of
timely anomaly detection, this paper focuses on sensor data, as
it offers a direct and reliable means of monitoring deviations in
physical processes.
For example, the Secure Water Treatment (SWaT) testbed
consists of six interconnected processes (P1–P6): raw water supply and storage, chemical dosing, ultrafiltration (UF),
dechlorination, reverse osmosis (RO), and RO permeate transfer and UF backwash, as shown in Fig. 1. Each process is
equipped with several sensors, which are named based on their
corresponding functions and processes. For instance, the sensor AIT-202 monitors the level of contaminants in the water.
Initially, the value of AIT-202 exceeded 7.05. However, at
12:04:10 on 28 June 2015, an attacker manipulated the sensor value and set it to 6. This malicious action caused the
chemical dosing pump P-203 to shut down, thereby disrupting
the chemical dosing process and adversely impacting water
quality. Therefore, multivariate time series anomaly detection
(MTSAD) plays an essential role in ensuring the reliability and
security of IoT systems [8].
In IoT systems, sensors are interdependent and interact with
one another. Recently, graph neural networks (GNNs) [9] have
been introduced into MTSAD to capture the relationships

I

1545-5971 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

3724

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 2, MARCH/APRIL 2026

Fig. 1. Example of an IoT anomaly on a Water Treatment System. The Secure Water Treatment (SWaT) testbed consists of six interconnected processes (P1–P6).
Each process is equipped with several sensors, which are named based on their corresponding functions and processes. For instance, the sensor AIT-202 monitors
the level of contaminants in the water. Initially, the value of AIT-202 exceeded 7.05. However, at 12:04:10 on 28 June 2015, an attacker manipulated the sensor
value and set it to 6. This malicious action caused the chemical dosing pump P-203 to shut down, thereby disrupting the chemical dosing process and adversely
impacting water quality.

between sensors. However, GNNs require an explicit graph
structure, which is typically constructed using domain knowledge. Existing GNN-based anomaly detection methods, such as
MTAD-TF [10], MTAD-GAT [11], Arvalus [12], MDGAT [13],
DVGCRN [14], and GReLeN [15], rely on fixed graph structures
designed by experts. Unfortunately, in real-world scenarios, sensor dependencies or graph structures are often hidden, difficult
to infer, or expensive to acquire.
Graph Structure Learning (GSL) [16] offers a promising solution for these challenges when expert knowledge is unavailable,
sensor dependencies are unknown, or access costs are prohibitive [17]. GSL learns an optimal graph structure to capture
the dependencies between sensors and align with downstream
anomaly detection tasks. Although GSL-based methods have
shown potential in learning sensor relationships [18], existing
GSL-based MTSAD methods [19], [20], [21], [22], [23], [24],
[25], [26], [27], [28], [29], [30], [31], [32], [33] face the following challenges:
r Existing methods focus solely on graph structure learning and fail to utilize partial known information: Current
GSL-based anomaly detection methods primarily rely on
unknown graph structures during the learning process,
ignoring the potential benefits of incorporating partially
known information. As a result, these methods engage
in a largely blind learning process, leading to suboptimal
outcomes.
r Existing methods suffer from insufficient depth in
graph neural networks, limiting their ability to
capture long-distance dependencies between sensors:
Most GSL-based anomaly detection methods employ
spatio-temporal prediction models that separately model
spatial and temporal patterns without accounting for
their interactions, which significantly limits their
representational capacity. Furthermore, Graph Convolutional Networks (GCNs) struggle to achieve deep

node representations by merely increasing the number
of layers. Practical evidence shows that GCNs typically
achieve their best performance with just two layers, as
deeper GCNs suffer from the over-smoothing problem.
Over-smoothing causes all node representations to
converge to the same value, rendering deeper GCNs
ineffective. These limitations severely restrict the depth
of GCNs, making it challenging to capture rich spatial
features and long-distance dependencies, ultimately
hindering anomaly detection performance.
To address these challenges, we propose MAD-ODE, a
novel framework to enhance MTSAD by dynamically learning
graph structures and modeling long-distance dependencies using
spatio-temporal GCNs based on ordinary differential equations
(ODEs). The key contributions of MAD-ODE are summarized
as follows:
r Enhanced representation through hybrid graph learning:
To better capture and enrich the dependencies between
sensors, we exploit two kinds of graph structures: a static,
knowledge-driven similarity graph and a fully parameterized learnable graph. This hybrid graph learning significantly enhances the model’s representational capacity,
leveraging both learned and prior knowledge.
r Capturing long-distance spatio-temporal dependencies:
We introduce spatio-temporal graph ODE network
(STGODE) instead of discrete GCNs, which operates on
both the static similarity graph and the learned graph for
prediction and anomaly detection. This approach effectively captures long-distance spatio-temporal dependencies with continuous-time model, improving the model’s
resilience and enabling more accurate and robust multivariate time series predictions.
r Extensive evaluation on real-world datasets: We conducted comprehensive experiments on five publicly available real-world datasets. MAD-ODE achieves the best

HE et al.: MULTIVARIATE TIME SERIES ANOMALY DETECTION USING LEARNABLE SPATIAL-TEMPORAL GRAPH ORDINARY

average performance and maintains stable results compared to existing methods. This underscores the robustness
and reliability of MAD-ODE across diverse datasets and
anomaly detection tasks. The code of this work is publicly
available at https://github.com/AIOps-tech/MAD-ODE.
The rest sections of this paper are arranged as follows. Section II provides an overview of the related work.
Section III introduces some preliminary knowledge and defines
the problem. Section IV explains our proposed approach in
detail, including a general overview and the functionality of individual components. In Section V, we analyze the performance
and efficiency of the model through extensive experiments.
Finally, our work is concluded with a summary of our findings
and a discussion on future work in Section VI.
II. RELATED WORK
In addition to MTS sensor data, network traffic and SCADA
execution context are also utilized to enhance the safety and
security of IoT systems. For instance, Kitsune [2], EULER [3],
and HyperVision [4] focus on network traffic and encrypted traffic analysis for intrusion detection in IoT environments. These
methods have demonstrated high effectiveness in traffic-based
anomaly detection. On the other hand, SCAPHY [5] combines
SCADA execution context with physical sensor states to address
security issues in industrial control and cyber-physical systems.
By integrating these complementary data sources, SCAPHY
provides a comprehensive approach to detecting and mitigating
threats in complex industrial environments.
Research on MTSAD can be categorized into three principal
classes. The first class primarily utilizes temporal features to
detect anomalies, whereas the second class focuses on the spatial
features of MTS. The third class addresses anomaly detection
in cases where the spatial relationships are unknown.
A. Temporal Feature-Based Anomaly Detection
Temporal feature-based methods focus on capturing sequential patterns in time series data. Among these, Long Short-Term
Memory (LSTM) networks have been widely adopted due to
their ability to model temporal dependencies. For example,
LSTM-NDT [34] leverages LSTM to achieve superior predictive
performance while maintaining system interpretability by employing a nonparametric, dynamic, and unsupervised thresholding technique for anomaly detection. In contrast, MSCRED [35]
constructs a multi-scale feature matrix and uses conv-LSTM
neural architectures to encode inter-sensor correlations, enabling
anomaly detection and diagnosis via a residual feature matrix.
Additionally, MAD-GAN [36] employs LSTM as the backbone
within a Generative Adversarial Network (GAN) framework.
LSTM-DAE [37] proposes a two-stage framework, first identifying outlier candidates using operational cycle signals and
then analyzing temporal coherence in sensor data to detect
abnormalities. In contrast, LSTM-VAE [38] incorporates multimodal observations and temporal dependencies into a latent
space, reconstructs distributions, and evaluates anomalies using
reconstruction-based scores.

3725

Beyond LSTM, other recurrent neural networks (RNNs) are
also applied in MTSAD. For example, OmniAnomaly [39]
aims to learn the normal representation of time series data,
and then calculate reconstruction errors to effectively identify
anomalous points that deviate from the normal patterns, while
DAGMM [40] combines a deep self-encoding mechanism with
a Gaussian Mixture Model (GMM) to generate low-dimensional
representations and reconstruction errors for anomaly detection.
Neural ordinary differential equations (ODEs) [41] define a
vector field, enabling the continuous transformation of hidden
states. As an emerging family of neural networks, Neural ODEs
have demonstrated significant potential in modeling the dynamics of temporal data. Motivated by this, models such as LSTMODE and latent-ODE [42] integrate the strengths of LSTM,
VAE, and Neural ODEs to effectively detect anomalies in MTS
data, addressing challenges posed by sparsity and irregularity.
Recently, diffusion models have gained attention in MTS
anomaly detection due to their generative capabilities. For instance, MadSGM [43] utilizes the probability flow ODEs of
score-based generative models to synthesize samples and identify anomalies. Similarly, TimeADDM [44], a diffusion-based
anomaly detection framework, accelerates the reverse denoising process by employing an ODE solver, efficiently recovering latent features from noise to enhance anomaly detection
performance.
While these methodologies are rooted in temporal features,
they often do not take account of the intricate correlations
inherent in time series data [19].
B. Spatial Feature-Based Anomaly Detection
Spatial feature-based methods leverage the relationships between sensors to enhance anomaly detection. GNNs, particularly Graph Attention Networks (GATs), are pivotal for extracting features from graph-structured data, capturing both
inter-sensor relationships and time-varying dependencies. For
instance, MTAD-TF [10] combines multi-scale convolution
networks with GAT to model temporal and spatial patterns,
while MTAD-GAT [11] leverages GAT to uncover correlations
among univariate time series and their temporal dependencies,
integrating prediction and reconstruction for anomaly detection.
Similarly, Arvalus [12] models system components as nodes and
their interdependencies as edges, improving anomaly detection
precision. MDGAT [13] employs multi-head dynamic attention
to capture sensor dependencies across temporal and spatial
domains. DVGCRN [14] focuses on uncertain interrelations
in MTS data using reconstruction-based anomaly detection.
Lastly, GReLeN [15] utilizes Variational Autoencoders (VAE)
and Graph Convolutional Networks (GCN) to learn relationships
in MTS data, reconstruct graphs, and detect anomalies.
Although GNNs are effective in modeling spatial relationships, they rely on predefined graph structures, which are often
unavailable or expensive to obtain in real-world scenarios.
C. Unknown Spatial Relationship-Based Anomaly Detection
When explicit spatial relationships are unavailable, GSL provides a solution by learning the underlying graph structure

3726

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 2, MARCH/APRIL 2026

directly from the data. GSL-based methods can be broadly
categorized into node feature-based similarity approaches and
fully parameterized approaches [45].
Node feature-based similarity approaches model graph structures by computing node-wise similarity using metric learning functions, such as cosine similarity or dot product. These
methods rely on the inherent features of nodes to measure
their pairwise relationships. GDN [19] learns inter-sensor relationships based on adaptive node features to detect anomalies from expected distributions. HGTMAD [20] integrates
GCNs and transformers to extract spatial and temporal features, while FuSAGNet [21] models interrelations using a fused
sparse self-encoder graph for anomaly predictions and reconstructions. TS-GAT [22] leverages prior data knowledge to
constrain graph learning, and methods like MEGA [23] and
DPGLAD [24] adopt unidirectional graph learning. Additionally, GSC-MAD [25] employs graph updating with smooth and
sparse constraints, while ACGSL [26] creates dynamic graph
representations through subsequence-based learning.
In contrast, fully parameterized methods treat each element
of the adjacency matrix as a learnable parameter. This parameterization allows the model to directly optimize the graph
structure, providing greater flexibility to capture complex and
latent relationships within the graph. GTA [27] use transformers
for predictions, identifying anomalies by evaluating the disparity
between predicted and actual values. GLAD [28] combines
GATs with transformers to extract global and local features, MGCLAD learns inter- and intra-signal correlations using directed
graphs, and MEGLAD [29] employs multiple GSL variations for
diverse correlations. Lastly, GSLAD [33] uses diffusion graph
convolution networks to detect anomalies.
Node feature-based similarity methods often rely on simple
K-nearest neighbors (KNN) graphs with degree constraints,
whereas fully parameterized GSL methods provide greater
flexibility. However, transformer-based methods such as GTA,
GLAD, and MGCLAD significantly increase computational
complexity, which can be a limiting factor in large-scale
applications.
III. THREAT MODEL AND PROBLEM DEFINITION
This paper focuses on anomaly detection in MTS of sensor
data. Below, we first give the threat model and define the fundamental concepts of MTS, graph structure learning and hybird
graph learning-based MTSAD.
A. Threat Model
We adopt a threat model similar to those used in existing works
on MTS of sensor data in industrial IoT, such smart water plant.
In this model, the attacker can maliciously manipulate critical
components such as the motorized valve, flow indication transmitter, pump, and consumers, or directly modify sensor readings.
These attacks can lead to severe physical consequences, including overflow of the primary tank, increased chemical levels
in the water, manipulation of tank draining and filling speeds,
disruption of water supply to consumers, contamination-induced
drainage of the primary grid, water leakage and pipe bursts,

intermittent water supply, and halting of chemical dosing to
raw water. For example, an attacker may target the elevated
reservoir (e.g., 2_LT_002) by manipulating the tank’s draining
and filling speeds. Additionally, the attacker could alter the
readings of water quality sensors (e.g., 1_AIT_001), causing the
raw water tank to drain unnecessarily. These coordinated actions
can disrupt the normal operation of the system and compromise
its safety and reliability.
We assume that adversaries cannot manipulate their behavior
to evade detection, as the primary target of these attacks involves
physical processes. Unlike purely cyber attacks, physical attacks
inherently produce observable changes in sensor data, making
them detectable when effective anomaly detection mechanisms
are in place. This assumption simplifies the threat model by
focusing on identifying deviations in physical system behaviors
caused by malicious activities. The sensor data collected for
training represents benign states without the presence of attacks.
This ensures that the model learns normal system behavior and
can effectively detect anomalies caused by malicious activities.
B. Multivariate Time Series
Multivariate time series data consists of a large number of
regularly spaced and uninterrupted samples, which are characterized by N indicators and M timestamps. It is denoted by
X = (x1 , x2 , . . ., xM )T ∈ RM ×N . The i-th indicator is defined
as xi = (xi1 , xi2 , . . ., xiM ). The t-th timestamp encompasses N
T
indicator values, which is defined as xt = (x1t , x2t , . . ., xN
t ) .
The history window on timestamp t with length ω is defined as
a subsequence Xt = (xt−ω , xt−ω+1 , . . ., xt−1 )T ∈ Rω×N .
For anomaly detection, when the label yt is 1, it means that
there is an anomaly at timestamp t. When the label yt is 0, it
means that timestamp t is normal.
C. Graph Structure Learning
For a given multivariate time series X ∈ RM ×N , the purpose
of graph structure learning is to construct a graph G = (V, E)
and its corresponding graph topology or adjacency matrix AL ∈
RN ×N . Nodes (V ) in the graph are the sensors that produce
the indicators, and the hidden relationships between sensors are
considered as edges (E).
AL = GSL(X),

(1)

where GSL() indicates graph structure learning function. The
binary adjacency matrix (AL ) stores the edge information in
the graph. AL
i,j is 1, which indicates an edge between node i
and node j. On the contrary, AL
i,j is 0, which indicates no edge
between node i and node j.
The constructed graph is subsequently fed into the downstream anomaly detection model, enabling a joint update of
parameters in both the detection model and the graph structure
learning model. Through this process, the graph structure is
iteratively refined. This iterative parameter update scheme ensures that the graph structure progressively adapts to the specific
requirements of the downstream anomaly detection task.

HE et al.: MULTIVARIATE TIME SERIES ANOMALY DETECTION USING LEARNABLE SPATIAL-TEMPORAL GRAPH ORDINARY

3727

IV. PROPOSED METHODOLOGY
A. Overview

Fig. 2. The framework of hybird graph learning-based multivariate time series
anomaly detection.

D. Hybird Graph Learning-Based Multivariate Time Series
Anomaly Detection
Hybrid graph learning-based MSTAD operates in a semiunsupervised manner (only normal time series instances are
given in the training set). Hybrid graph learning incorporates two
types of graph structures: the static similarity graph (AS ) and the
learnable graph (AL ), as shown in Fig. 2. The static similarity
graph AS is constructed based on similarities derived from the
raw data, providing a stable and interpretable representation of
relationships among nodes. In contrast, the learnable graph AL is
generated through GSL, enabling the model to adaptively capture complex dependencies. Given the historical subsequence
Xt , the model leverages both graph structures to predict the
subsequent value x̂t . The prediction error between the actual
value xt and the predicted value x̂t is treated as the anomaly
score, denoted as st . An anomaly is deemed to have occurred
at timestamp t if the anomaly score st exceeds a predefined
threshold T .
The process can be formally described as follows:

AS = Similarity(X),

(2)

x̂t = f (Xt , AS , AL ),

(3)

st = ϕ(xt , x̂t ),

1, if st > T,
ŷt =
0, if st ≤ T,

(4)
(5)

where Similartiy() indicates the similarity function, f () denotes
the prediction function, x̂t represents the prediction value of xt
at timestamp t, ϕ is the function used to calculate the anomaly
score, and T stands for the threshold.
This hybrid approach effectively combines prior knowledge
(captured by AS ) and dynamically learned relationships (captured by AL ) to enhance the detection of anomalies in complex
multivariate time series. By leveraging these complementary
graph structures and prediction task, the MSTAD framework
achieves robust and accurate anomaly detection without requiring labeled data.

To enrich and exploit the dependencies between sensors while
capturing long-distance spatio-temporal relationships, we propose MAD-ODE.
MAD-ODE exploits hybrid graph learning, integrating a
fully parameterized learnable graph with a static, knowledgedriven similarity graph. This hybrid graph learning enhances
the model’s representational capacity by leveraging both learned
and prior knowledge. Consequently, MAD-ODE comprises two
key graph components: the static similarity graph structure
generator and the graph structure learner.
To effectively model long-distance spatio-temporal dependencies, MAD-ODE employs a continuous-time model
STGODE as the predictor, replacing traditional discrete GCNs.
STGODE operates on both the static similarity graph and the
learned graph and to predict future values. The prediction errors
are then used as anomaly scores.
MAD-ODE consists of four key modules: the static similarity graph structure generator, the graph structure learner, the
STGODE [46] predictor, and the anomaly score and threshold
selection module, as illustrated in Fig. 3.
r Static similarity graph structure generator: This module
generates a static graph structure based on cosine similarity
between nodes (indicators), denoted as ACOS . It calculates
the cosine distance between indicators and selects the top-k
most similar nodes as neighbors for each node. The fixed
cosine graph structure provides a stable and complementary graph structure to the learned graph structure, enhancing the model’s robustness and improving the accuracy of
anomaly detection.
r Graph structure learner: This module generates a learnable graph structure, denoted as AF P M . Firstly, the fully
parameterized graph structure learner treats each element
of the adjacency matrix as an independent and learnable parameter. In addition, the graph learning process is guided by
a dynamic time warping (DTW) distance [47] prior graph.
The DTW prior graph effectively measures the similarity
between time series by capturing delay correlations and
ensuring invariance to time shifts.
r STGODE predictor: This module predicts the next timestamp value in the time series with the static graph ACOS
and the learned graph AF P M . It uses a continuous GCN
with residual connections to address the issue of excessive
smoothing in traditional GCNs, which can cause node
representations to converge to identical values. The predictor takes sub-sequences of the multivariate time series
(generated using a sliding window), and the adjacency
matrices of the static graph and the learned graph as input
to predict the value at the next timestamp.
r Anomaly scores and threshold selection: This module identifies anomalies based on the prediction error. Anomaly
scores are derived from the prediction error between the
predicted values and the ground truth. A higher anomaly
score indicates a higher likelihood of an anomaly. A
threshold is selected to distinguish between normal and

3728

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 2, MARCH/APRIL 2026

Fig. 3. The framework of MAD-ODE. MAD-ODE consists of four key modules: the static similarity graph structure generator, the graph structure learner, the
STGODE predictor, and the anomaly score and threshold selection module. MAD-ODE exploits hybrid graph learning, which integrates a fully parameterized
learnable graph with a static, knowledge-driven similarity graph, enhancing the model’s representational capacity. MAD-ODE employs STGODE as the predictor
to effectively model long-distance spatio-temporal dependencies. STGODE operates on both the learned graph and the static similarity graph to predict future
values. The prediction errors are then used as anomaly scores.

anomalous sub-sequences. If the anomaly score exceeds
the threshold, the prediction timestamp is classified as an
anomaly; otherwise, it is considered normal.
In the following subsections, we give the details of each
components.
B. Static Similarity Graph Structure Generator
The purpose of this module is to leverage known information
from the raw time series data to construct a static graph structure
ACOS . This graph captures the relationships (similarities) between sensors, which is essential for downstream tasks such as
anomaly detection. It calculates the similarity between sensors

using cosine distance. The formula for cosine similarity is:


cos xi , xj =

xi • xj
,
xi  • xj 

(6)

where cos(·) denotes cosine distance calculation function, r
denotes dot product,  ·  denotes magnitude, and xi denotes
i-th sensor values.
For each sensor i, the module selects the top k most similar
sensors as its neighbors. k can adjust the sparsity of the static
graph’s adjacency matrix and reduce the training cost.



(7)
= 1, j ∈ topk cos xi , xj ,
ACOS
i,j

HE et al.: MULTIVARIATE TIME SERIES ANOMALY DETECTION USING LEARNABLE SPATIAL-TEMPORAL GRAPH ORDINARY

3729

where ACOS
represents the connection between sensors i and j,
i,j
˙
and topk() selects the top k most similar sensors for each sensor
i.
The static similarity graph structure offers a stable and interpretable representation of the relationships between sensors.
This static graph serves as a complementary component to the
dynamically learned graph structure discussed in Section IV-C,
providing a robust foundation for capturing inherent sensor
dependencies.

we utilize the DTW distance [47] to construct prior graph and
guide the graph learning process.
Given two time series Y = (y1 , y2 , . . ., yn ) and Z =
(z1 , z2 , . . ., zm ), a cost matrix D ∈ Rn×m is introduced, where
Di,j = |yi − zj |.

C. Graph Structure Learner

where Dc is the cumulative cost matrix computed by dynamic
programming.
The DTW distance is used to compute the similarity matrix
S DT W ∈ RN ×N for all pairs of sensors:

FPM

for
Graph structure learner obtains a suitable graph A
anomaly detection task by jointly training with the downstream
task. It consists of two main parts: the fully parameterized graph
structure learner and the DTW prior graph. Firstly, the fully
parameterized graph structure learner treats each element of the
adjacency matrix as an independent and learnable parameter.
In addition, the graph learning process is guided by the DTW
distance prior graph ADT W . This guidance allows the model
to incorporate meaningful structural information, improving its
ability to model complex spatio-temporal dependencies.
1) Fully parameterized graph structure learner: It is a flexible
learner and treats the elements in adjacency matrix as free
learnable parameters. These parameters are updated through
backpropagation, enabling the generation of a customized and
optimal graph structure tailored to the specific requirements
of downstream tasks. However, since adjacency matrices are
typically binary (composed of 0 s and 1 s), gradient-based
optimization becomes challenging.
To address this, the Gumbel-Softmax technique [48] is employed to convert discrete parameters into continuous ones,
enabling backpropagation. The Gumbel-Softmax trick is used
to sample from a categorical distribution while maintaining
differentiability. The process of Gumbel-Softmax is defined as
follows:
g = − log(− log(u)), u  Uniform(0, 1),
 

exp log π1i,j +g i,j /τ
 ,

z1i,j = 
log πvi,j +g i,j /τ
v∈{0,1} exp

(8)
(9)

where u represents the sample extracted from a Uniform(0,1)
distribution, g i,j follows a Gumbel distribution, and π1i,j denotes
the values of the i-th row and j-th column of the probability
matrix π1 ∈ RK×K which signifies the probability that node i is
connected to node j in the graph. Here, τ serves as a temperature
parameter. As τ approaches 0, z1i,j tends towards 0 or 1, making
the distribution more discrete.
Ultimately, the i-th row and j-th column in the adjacency
PM
PM
are assigned the value of z1i,j , causing AF
to
matrix AF
i,j
i,j
i,j
be set to 1 with the probability of π1 .
2) DTW prior graph: Due to delay correlation in time series, there may be noise in the prior graph by the Euclidean
distance [49]. Compared with the Euclidean distance and cosine
distance, DTW distance can capture delay correlations and ensure invariance to time shifts. Therefore, according to Ref. [32],

Dc (i, j) = Di,j + min(Dc (i − 1, j), Dc (i, j − 1),
Dc (i − 1, j − 1)),
DTW(Y, Z) = Dc (n, m),

DT W
Si,j
= DTW(xi , xj ),

(10)
(11)

(12)

where xi , xj represent the time series of sensors i and j,
respectively.
The adjacency matrix of DTW prior graph ADT W is constructed by thresholding the similarity matrix:

DT W
<ε
1, Si,j
DT W
,
(13)
=
Ai,j
0, otherwise
where ε is a parameter to determine the sparsity of adjacency
matrix.
D. STGODE Predictor
Traditional GCNs adopt a discrete formulation, where information is aggregated from n-order neighbors using n layers.
However, such discrete GCNs face two significant limitations:
(1) they suffer from over-smoothing when stacking multiple
layers, and (2) they struggle to effectively capture long-distance
dependencies due to limited receptive fields.
To address these issues, we employ the STGODE model [46]
as the predictor. Unlike traditional Spatio-Temporal GCNs,
STGODE leverages temporal convolutional networks and a continuous GCN formulation based on ODEs. This continuous formulation allows the model to capture long-range spatio-temporal
dependencies more effectively. The STGODE predictor operates on both the learned graph and the static similarity graph,
combining the advantages of dynamically learned structural
information and stable, knowledge-driven priors to enhance
prediction accuracy and robustness.
1) Neural ODEs: Neural ODEs [41] consider a continuoustime (depth) model,
 t
 t
dx
dτ = x(0) +
f (x(τ ), τ )dτ, (14)
x(t) = x(0) +
0 dτ
0
where f (x(τ ), τ ) will be parameterised by a neural network to
model the hidden dynamic. We can backpropagate the process
through an ODE solver without any internal operations, which
allows to build it just as a block for the whole neural network.
2) Continuous GCN with ODE: Inspired by Neural ODEs,
the continuous GCN with ODE can be represented in tensor

3730

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 2, MARCH/APRIL 2026

formate [50] as follows:
 s+1
H0 ×1 Aτ ×2 U τ ×3 W τ dτ,
H(s) =

(15)

0

A=

1
1
α
(I + D− 2 AD− 2 ),
2

(16)

where H0 denotes the initial input, ×i denotes the tensor matrix
multiplication on mode i, W and U are learnable parameter
matrices, and s is a continuous variable of layer n in discrete
GCN. D is the degree matrix of A, A is the regularized adjacency
matrix, and α ∈ (0, 1) is a hyperparameter. The ODE formulation allows the model to capture long-distance dependencies and
avoid over-smoothing by integrating information continuously
across layers. The ODE can get an analytical solution by the
ODESolver.
3) STGODE structure: A STGODE block [46] consists of two
temporal convolutional networks (TCN) layers and an ODESolver with a “sandwich” structure. It can extract spatio-temporal
features and capture long-distance dependencies.

Xt
,l = 0
l
=
,
(17)
Htcn
l−1
σ(W l ∗dl Htcn
) , l = 1, 2, . . . , L
H(s) = ODESolver

dH(s)
, H0 , s ,
ds

(18)

dH(s)
= H(s)×1 (A − I) + H(s)×2 (U − I)
ds
+ H(s)×3 (W − I) + H0 ,

(19)

l
where Xt is the input of TCN, Htcn
is the output of the l-th
l
layer of TCN, W denotes the l-th convolution kernel, dl = 2l−1
denotes exponential dilation rate.
To take full advantage of known dependency and learned
dependency, we design a STGODE predictor with hybrid graph
learning (two kinds of graphs) for predicting future behavior:
the static similarity graph and the learned graph. The input of
the STGODE predictor consists of the above static and learned
adjacency matrices ACOS , AF P M and the multivariate time
series subsequence Xt . After passing two STGODE layers,
max-pooling aggregates information. Finally, the output is fed
into a multilayer perceptron (MLP) layer to obtain the final
single-step prediction result (xt ).

E. Loss Function
The total loss function includes two components: the prediction loss and the graph learning loss.
The prediction loss lossp measures the discrepancy between
the predicted values and the ground truth for the MTS prediction
task. It is defined as the average absolute error (MAE) across all
sensors:
K

1
xi − xit ,
lossp =
K i=1 t

(20)

where xit and xit represent the prediction and the ground truth of
the i-th sensor at timestamp t, severally.

To enhance the caliber of the fully parameterized graph structure, we use DTW prior graph to guide the graph learning.
The graph learning loss lossg is introduced to improve the
quality of the fully parameterized graph structure (AF P M ) by
incorporating the DTW distance graph (ADT W ). It is defined as
the cross-entropy between the two adjacency matrices:


W
PM
W
−ADT
log AF
− 1 − ADT
lossg =
i,j
i,j
i,j
ij



PM
.
× log 1 − AF
i,j

(21)

The total loss function combines the prediction loss and the
graph learning loss, weighted by a regularization parameter.
loss = lossp + λ1 lossg ,

(22)

where paramete λ1 is the regularization amplitude parameter
that controls the influence of the graph learning loss on the total
loss.
F. Anomaly Scores and Threshold Selection
The purpose of anomaly detection is to identify the abnormal
situation that deviates from the normal behavior by comparing the ground truth and prediction. Initially, anomaly scores
are computed separately for every sensor. Subsequently, these
individual scores are aggregated to derive the anomaly scores
corresponding to each specific timestamp. Once the anomaly
score at timestamp t exceeds the predetermined threshold, the
system flags the corresponding timestamp as anomalous.
For each sensor i at timestamp t, the prediction error Erri (t)
is calculated as the absolute difference between the ground truth
(xit ) and the predicted value (xit ) :
Erri (t) = xit − xit

(23)

This error quantifies how much the predicted value deviates
from the true observed value. Larger errors indicate a potential
anomaly.
To maintain uniformity among sensors with varying value
scales, the prediction errors undergo a standardization procedure. This normalization rescales the errors into a standard
metric using the mean (μi ) and standard deviation (σi ) of the
errors for sensor i:
Erri (t) − μi
(24)
si (t) =
σi
This step ensures that sensors with larger ranges do not dominate
anomaly detection, enabling fair comparisons between sensors.
To compute the overall anomaly score at a given timestamp
t, the system selects the maximum normalized error across all
sensors:
s(t) = max si (t)
i

(25)

This approach assumes that the most anomalous sensor at a given
timestamp determines the timestamp’s overall anomaly score.
Grid search technology is pivotal for determining the optimal
threshold. In grid search, the upper and lower bounds of the
threshold are defined as the maximum and minimum values
of s(t), respectively. All possible thresholds are exhaustively

HE et al.: MULTIVARIATE TIME SERIES ANOMALY DETECTION USING LEARNABLE SPATIAL-TEMPORAL GRAPH ORDINARY

searched with a step size of 0.01. For each threshold, the resulting
predictions are compared to the ground truth to compute the F1
score. The threshold yielding the highest F1 score is selected
as the optimal threshold. In addition, we use the point adjustment strategy for anomaly scores to improve anomaly detection
accuracy.
G. Complexity Analysis
In the MAD-ODE framework, the construction of graph
structures plays a critical role in determining the performance
and efficiency of the model. Therefore, we analyze the time
complexity of generating the static similarity graph, the DTW
distance graph, and the learned graph.
r Static Similarity Graph: The static similarity graph is
constructed based on the cosine similarity between nodes
(indicators). For a pair of sensors with a sequence length
of M , the time complexity of cosine similarity is O(M ).
For a graph with N nodes, the cosine similarity must be
computed for each pair of nodes. Since there are N × N
node pairs, the time complexity of generating the static
similarity graph is O(N 2 M ).
r DTW Distance Graph: The DTW distance graph is constructed by calculating the DTW similarity between pairs
of sensors. For a pair of sensors with a sequence length of
M , the time complexity of the DTW distance is O(M 2 )
due to the need for dynamic programming to compute
the cumulative cost matrix. For N × N sensor pairs, the
overall time complexity for constructing the DTW distance
graph is O(N 2 M 2 ).
r Learned Graph: The fully parameterized graph structure
treats each element of the adjacency matrix as a freely
learnable parameter. The adjacency matrix is of size N ×
N , and during training, the parameters are updated iteratively. The time complexity of updating these parameters
is proportional to the number of parameters, resulting in a
time complexity of O(N 2 ) for fully parameterized graph
structure learning.
Combining these three components, the overall time complexity of generating the graph structures in the MAD-ODE
framework is dominated by the DTW distance graph and is
O(N 2 M 2 ).

3731

TABLE I
DATASET DESCRIPTION

normal operations, while the remaining 4 days include multiple
attack scenarios.
The Water Distribution (WADI) dataset is an extension of
the SWaT platform and represents a more comprehensive water
treatment, storage, and distribution. This dataset contains data
from 127 sensors and actuators, collected over 16 days. Of these,
14 days represent normal operations, while the remaining 2
days simulate attack scenarios, making it suitable for anomaly
detection tasks.
The Mars Science Laboratory (MSL) dataset includes 55
indicators from 27 entities on NASA’s Mars rover, while the Soil
Moisture Active Passive (SMAP) dataset contains 25 indicators
from 55 entities, representing soil and telemetry data collected
by NASA. Each dataset consists of a training subset and a testing
subset, with anomalies in both testing subsets explicitly labeled.
The sample interval for both datasets is set to 1 minute. To
preserve privacy, the timestamp information has been removed.
In the MSL dataset, the training sequences of 27 entities range
from 179 to 4048, while the testing sequences span from 1096
to 6100. Similarly, in the SMAP dataset, the training sequence
lengths of 55 entities vary between 52 and 2621, and the testing
sequence lengths range from 7244 to 8640.1
The Server Machine Dataset (SMD) is a 5-week-long dataset
from a large Internet company collected and made publicly
available [51]. It contains data from 28 server machines each
one monitored by 38 metrics. SMD is divided into two subsets
of equal size: the first half is the training set and the second half
is the testing set.
For the SWaT and WADI datasets, raw data is down-sampled
to a time resolution of 10 seconds. The median value within
each 10-second interval is extracted to ensure robustness against
noise. Anomalies in the SWaT and WADI datasets are tagged
based on ground truth labels provided in the datasets.
B. Experimental Setup

V. EXPERIMENT AND PERFORMANCE ANALYSIS
A. Datasets
In this section, five publicly available real-world datasets are
utilized for evaluating the performance of the anomaly detection
framework. Key statistics about these datasets are summarized
in Table I. All the training sets only include normal time series
instances. Below is a detailed description of each dataset:
The Secure Water Treatment (SWaT) dataset originates from
a water treatment test bench supervised by the Singapore Public
Utilities Bureau. This dataset captures 11 days of continuous
24-hour operation, during which network traffic and data from
51 sensors and actuators were recorded. The first 7 days represent

1) Metrics: To evaluate the performance of the proposed
method and compare it with baseline methods, three key metrics
are employed: precision (Prec), recall (Rec), and the F1 score
(F1). These metrics are defined as follows:
TP
,
TP + FP
TP
,
Rec =
TP + FN
Prec ∗ Rec
,
F1 = 2 ∗
Prec + Rec

Prec =

1 https://github.com/khundman/telemanom

(26)
(27)
(28)

3732

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 2, MARCH/APRIL 2026

where TP, TN, FP, and FN are the number of true positives, true
negatives, false positives, and false negatives.
2) Baselines: The proposed method is compared with 16
baseline methods, including machine learning and deep learning
approaches, to assess its effectiveness. Below is a summary of
these methods:
r Autoencoder (AE): It reconstructs the input data using
an autoencoder and uses the reconstruction error as the
anomaly score.
r Isolation Forest (IF): It is a tree-based anomaly detection
algorithm that effectively identifies anomalies or outliers
in datasets that differ significantly from the majority.
r DAGMM [40]: This method combines deep autoencoders
with Gaussian mixture models to capture the underlying
distribution of normal data and identify anomalies based
on reconstruction errors.
r LSTM-NDT [34]: This method utilizes LSTM to capture
contextual information and dependencies in sequential data
for anomaly detection.
r LSTM-VAE [38]: This method projects multimodal observations and time dependencies into a latent space and reconstructs the expected distribution using an LSTM-based
VAE.
r MAD-GAN [36]: This method uses LSTM as the underlying model in a GAN framework to capture the time series
data’s temporal correlation.
r OmniAnomaly [39] aims to learn the normal representation
of time series data, and then calculate reconstruction errors
to effectively identify anomalous points that deviate from
the normal patterns.
r USAD [52]: This method trains an encoder–decoder framework in an adversarial manner to achieve fast and efficient
training.
r MTAD-GAT [11]: This method treats the relationships
between indicators as a complete graph and employs a GAT
to detect anomalies.
r GDN [19]: This method constructs a graph structure using
pairwise cosine similarities between nodes, utilizes GAT
to learn dependencies between time series and perform
prediction.
r FuSAGNet [21]: This method learns the graph structure
using the pairwise cosine similarity between recursive
sensor embeddings. It obtains a sparse representation of
the input data by a sparse autoencoder and integrates it
into a GAT to perform sensor behavior prediction.
r GTA [27]: This method automatically learns the graph
structure through a direct approach and employs graph convolution combined with a transformer-based architecture
to capture temporal dependencies.
r MGCLAD [29]: This method achieves anomaly detection
by concurrently learning intra- and inter-signal graph structures, capturing temporal context and dependencies between signals. It performs anomaly detection by comparing
inputs and reconstructing outputs.
r MEGLAD [30]: This method employs an alternate multiple graph structure learning approach to capture sensor relationships from various perspectives, minimizing

TABLE II
METHOD PARAMETERS

information loss. Additionally, it uses an extended prior
graph generating method to adaptively select neighbors by
enhancing the weights of highly correlated nodes.
r FuGLAD [31]: This method employs three kinds of typical
graph structure learners to capture as many relationship
types among sensors as possible and exploits the prior
similarity to evaluate the importance of all learned graphs
and adaptively learn the fusion weight instead of the direct
average weight.
r MSTGAD [32]: MSTGAD uses dynamic time warping
distance as prior knowledge to effectively capture delay
correlations and designs an ensemble predictor to ensure
high prediction accuracy and stable anomaly scores.
3) Experimental Parameter Setting: The experimental parameter configurations are detailed in Table II. All experiments
were conducted using Python 3.8, PyTorch 1.10, and CUDA
version 11.3, on a server equipped with an Intel (R) Xeon
(R) Platinum 8255c CPU and an NVIDIA RTX 4090 GPU.
According to Ref. [19], the k in static graph is set to 10, window
size w is set to 12. According to Ref. [32], the in DTW distance
graph is set to 0.6.
4) Baseline Method Parameter Setting: For the baseline
methods, we set the sliding window size ω in GDN and FuSAGNet to 5, and GTA to 60. The baseline is configured according
to the source code or open-source code.

C. Detection Performance and Efficiency
As shown in Table III, our method achieves either the best
or the second-best performance on individual datasets and
consistently achieves the best average performance across all
datasets. This demonstrates the robustness and generalization
capability of our approach in handling diverse anomaly detection
tasks. While MGCLAD demonstrates the best performance on
the WADI dataset, its performance is significantly weaker on
the other four datasets. Similarly, MSTGAD achieves superior
results on the SWaT and SMAP datasets but performs poorly
on WADI. In contrast, our method introduces a hybrid graph
learning approach that incorporates a static graph structure to
enhance the robustness of anomaly detection models. By leveraging the STGODE predictor, our approach effectively captures
long-distance dependencies between sensors, producing more
representative predictions. This design not only improves the
model’s adaptability to diverse datasets but also ensures stable
and accurate anomaly detection performance across varying
scenarios. To filter false positives and enhance precision, our

HE et al.: MULTIVARIATE TIME SERIES ANOMALY DETECTION USING LEARNABLE SPATIAL-TEMPORAL GRAPH ORDINARY

3733

TABLE III
PRECISION, RECALL, AND F1 SCORE ON THE DATASETS

TABLE IV
PERFORMANCE AND EFFICIENCY ACROSS DATASETS

model could be further processed using density-aware clustering
or voxel-based neighborhood analysis [53], [54].
The performance of all methods on the WADI dataset is
lower compared to other datasets. This is because the WADI
dataset has a longer sequence length, more indicators, and a
lower anomaly rate, as shown in Table I. However, on the WADI
dataset, with the help of the static similarity graph structure
and the graph structure learning module, we enrich and uncover
dependencies between sensors. By leveraging long-distance dependency relationships captured by the STGODE-based predictor, our method continues to demonstrate superior performance
compared to other baseline methods. This demonstrates that our
method is effective in handling high-dimensional time series and
scenarios with sample imbalance, making it suitable for practical
applications.
The performance metrics, Area Under the Curve (AUC) and
Area Under the Precision-Recall Curve (AUPR), are critical for
evaluating the predictive accuracy and precision of the model
without the need for manual threshold setting. These metrics
provide a robust and threshold-independent assessment of model
performance, making them particularly suitable for anomaly
detection tasks with imbalanced datasets. As shown in Table IV,
the results show that all datasets achieve high AUC and AUPR
values, indicating strong model performance across different
data characteristics.
As shown in Table IV, the training time required for all
datasets is remarkably short, with a maximum of 30 epochs.
Specifically, the MSL dataset has the shortest training time,
while the WADI dataset requires the longest training time.
Nevertheless, even for WADI, the training time of epoch is only
119.8 seconds. This efficiency in training is highly advantageous
for experimental workflows and iterative model development,

significantly reducing the time required for experimentation and
enabling faster progress. We also include the inference time of
our system in Table IV to provide a clear measurement of the
overall detection latency, i.e., the time from anomaly onset to
alarm generation. The most time-consuming component of the
system is the ODEs module. This is due to the computational
complexity involved in solving the equations to model dependencies in the data.

D. Ablation Experiment
To validate the effectiveness of the hybrid graph learning
(the static and learned graph structures), we conduct ablation
experiments. First, the STGODE predictor is evaluated using
only the static graph (Only COS) or only the learned graph (Only
FPM). Additionally, we introduce a self-adaptive graph learning structure (ADP) [55] to replace one of these components.
ADP+COS indicates that the STGODE predictor is supported
by both the static graph and the self-adaptive graph learning
structure. Similarly, ADP+FPM means that the STGODE predictor is supported by both the fully parameterized learned graph
and the self-adaptive graph learning structure.
The adjacency matrix of the self-adaptive graph is defined as
follows:



AADP = SoftMax ReLU E1 E2T ,

(29)

where E1 , E2 ∈ RN ×e represent two node embedding dictionaries initialized with learnable parameters.
The experimental results are presented in Table V. Using
only the static graph or the fully parameterized graph results
in a decline in model performance. This demonstrates that both
graph structures are indispensable and play a critical role in
the model’s performance. Moreover, when either of these graph
structures is replaced with the self-adaptive graph learning structure, the model’s performance decreases. This further confirms
the effectiveness of our proposed static graph structure and fully
parameterized graph structure.

3734

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 2, MARCH/APRIL 2026

TABLE V
ABLATION EXPERIMENT

TABLE VI
PERFORMANCE WITH NOISE AND MISSING VALUES

Fig. 4.

The impact of window size.

E. Parameter Influence
To evaluate the stability of our method under different parameter settings, we analyze the impact of hyperparameters on
model performance.
1) Window Size: In this experiment, we set the window size
w to 6, 12, 15, 21, and 30. The performance of models with
different window sizes is shown in Fig. 4.
For the SMAP, MSL and SMD datasets, the window size has
a negligible impact on the detection results. However, for the
SWaT and WADI datasets, increasing the window size tends to
degrade the model’s performance. This is because larger window
sizes may obscure short anomalies, making accurate detection
more challenging.
2) Graph Loss Regularization Parameter: We analyze the
impact of the graph loss regularization parameter λ1 , which is set
to 1, 5, 10, 15, and 20, across the five datasets. The experimental
results are shown in Fig. 5. Excessively large values of λ1 can
lead to overfitting in the graph structure learning, negatively
affecting the model’s performance. On the other hand, smaller
values of λ1 tend to yield more stable experimental results.
Therefore, it is recommended to choose smaller values for the
graph loss regularization parameter.

Fig. 5.

The impact of prediction weight parameter.

F. Robustness
To address concerns regarding the system’s performance under real-world conditions, we conduct experiments to evaluate
the robustness of our anomaly detection framework. Specifically,
we introduce the following perturbations to simulate practical
challenges. Gaussian noise with a standard deviation of 0.1 is
added to the sensor data to simulate measurement inaccuracies.
Portions of the data are randomly removed at rates of 1%, 2%,
and 5% to mimic sensor outages or communication failures.
As shown in Table VI, the results demonstrate that the performance of our framework is largely unaffected by noise and
missing data in the MSL and SMD datasets. However, a slight
performance degradation is observed in the SWaT, WADI, and
SMAP datasets. These results highlight the robustness of our
framework under typical real-world perturbations.
G. Case Study
As shown in Fig. 6, we conduct a case study to reveal the
meaning of the learned graph structure. Fig. 6 (Left)presents
a subset of the graph structure learned by our method, while
Fig. 6 (Right) displays the predicted results of the corresponding
sensor values. Specifically, during the timestamps from 1180

HE et al.: MULTIVARIATE TIME SERIES ANOMALY DETECTION USING LEARNABLE SPATIAL-TEMPORAL GRAPH ORDINARY

Fig. 6.

3735

Left: Partial graph structure learned on SWaT dataset. Right: Understand the relationship between sensors with ground truth and prediction.

to 1237, sensor AIT-202 was subjected to an attack, which we
highlighted in red in the graph. In the water treatment process,
sensors interact with one another. Due to these interactions,
the attack on AIT-202 caused the dosing pump P203 to cease
operation. As the subsequent water treatment steps progressed,
the permeability conductivity analyzer AIT-501 was ultimately
affected at timestamp 1530, as shown in Fig. 6 (Right).
Our model accurately predicts the changes in AIT-501,
demonstrating its effectiveness. Additionally, Fig. 6 (Left) precisely captures the dependency relationships among the three
sensors involved in this case study.
VI. CONCLUSION AND FUTURE WORK
In this work, we propose the multivariate time series anomaly
detection method based on learnable STGODE. Our approach
employs an STGODE-based predictor with hybrid graph learning, which integrates both the static graph structure and the
fully parameterized learned graph structure. This hybrid design
enables the model to effectively capture long-distance dependencies among sensors, accurately forecast future sensor behaviors,
and significantly improve the F1 score. Compared to baseline
methods, MAD-ODE demonstrates superior and stable performance in detecting anomalies across multivariate time series
data. By leveraging the complementary strengths of static and
learnable graph structures, MAD-ODE ensures both robustness
and adaptability in complex IoT environments. In future work,
a promising direction is to incorporate false-positive filtering
mechanisms as a post-processing step. We aim to extend this
approach to diagnose anomalies in IoT systems, enabling a
deeper understanding of their root causes and further enhancing
system reliability.
REFERENCES
[1] S. He et al., “A joint matrix factorization and clustering scheme for
irregular time series data,” Inf. Sci., vol. 644, 2023, Art. no. 119220.
[2] Y. Mirsky, T. Doitshman, Y. Elovici, and A. Shabtai, “Kitsune: An ensemble of autoencoders for online network intrusion detection,” in Proc.
25th Annu. Netw. Distrib. Syst. Secur. Symp., San Diego, CA, USA,
Feb. 2018, pp. 1–15 [Online]. Available: https://www.ndss-symposium.
org/wp-content/uploads/2018/02/ndss2018_03A-3_Mirsky_paper.pdf

[3] I. J. King and H. H. Huang, “Euler: Detecting network lateral movement via
scalable temporal graph link prediction,” in Proc. 29th Annu. Netw. Distrib.
Syst. Secur. Symp., San Diego, CA, USA, Apr. 2022, pp. 1–36. [Online].
Available: https://www.ndss-symposium.org/ndss-paper/auto-draft-227/
[4] C. Fu, Q. Li, and K. Xu, “Detecting unknown encrypted malicious traffic
in real time via flow interaction graph analysis,” in Proc. 30th Annu.
Netw. Distrib. Syst. Secur. Symp., San Diego, CA, USA, Feb./Mar. 2023,
pp. 1–18 [Online]. Available: https://www.ndss-symposium.org/ndsspaper/detecting-unknown-encrypted-malicious-traffic-in-real-time-viaflow-interaction-graph-analysis/
[5] M. Ike, K. Phan, K. Sadoski, R. Valme, and W. Lee, “Scaphy: Detecting
modern ICS attacks by correlating behaviors in SCADA and physical,”
in Proc. 44th IEEE Symp. Secur. Privacy, San Francisco, CA, USA,
May 2023, pp. 20–37, doi: 10.1109/SP46215.2023.10179411].
[6] S. He, Z. Li, J. Wang, and N. N. Xiong, “Intelligent detection
for key performance indicators in industrial-based cyber-physical systems,” IEEE Trans. Ind. Informat., vol. 17, no. 8, pp. 5799–5809,
Aug. 2021.
[7] J. Liu et al., “A generic framework for finding special quadratic elements
in data streams,” IEEE/ACM Trans. Netw., vol. 32, no. 4, pp. 3269–3284,
Aug. 2024.
[8] S. He et al., “Fine-grained multivariate time series anomaly detection in
iot,” Comput., Mater. Continua, vol. 75, no. 3, pp. 5027–5047, May 2023.
[9] J. Zhou et al., “Graph neural networks: A review of methods and applications,” AI Open, vol. 1, pp. 57–81, 2020.
[10] Q. He, Y. Zheng, C. Zhang, and H.-Y. Wang, “MTAD-TF: Multivariate
time series anomaly detection using the combination of temporal pattern
and feature pattern,” Complexity, vol. 2020, pp. 1–9, 2020.
[11] H. Zhao et al., “Multivariate time-series anomaly detection via graph
attention network,” in Proc. IEEE Int. Conf. Data Mining, 2020,
pp. 841–850.
[12] D. Scheinert, A. Acker, L. Thamsen, M. K. Geldenhuys, and O. Kao,
“Learning dependencies in distributed cloud applications to identify and
localize anomalies,” in Proc. IEEE/ACM Int. Workshop Cloud Intell., 2021,
pp. 7–12.
[13] L. Zhou, Q. Zeng, and B. Li, “Hybrid anomaly detection via multihead
dynamic graph attention networks for multivariate time series,” IEEE
Access, vol. 10, pp. 40967–40978, 2022.
[14] W. Chen, L. Tian, B. Chen, L. Dai, Z. Duan, and M. Zhou, “Deep
variational graph convolutional recurrent network for multivariate time
series anomaly detection,” in Proc. Int. Conf. Mach. Learn., 2022,
pp. 3621–3633.
[15] W. Zhang, C. Zhang, and F. Tsung, “GRELEN: Multivariate time series
anomaly detection from the perspective of graph relational learning,” in
Proc. 31st Int. Joint Conf. Artif. Intell., 2022, pp. 2390–2397.
[16] Y. Zhu et al., “A survey on graph structure learning: Progress and opportunities,” 2021, arXiv:2103.03036.
[17] D. Chai, L. Wang, and Q. Yang, “Bike flow prediction with multi-graph
convolutional networks,” in Proc. 26th ACM SIGSPATIAL Int. Conf. Adv.
Geograph. Inf. Syst., 2018, pp. 397–400.
[18] H. Pang et al., “Asymptotic consistent graph structure learning for multivariate time series anomaly detection,” IEEE Trans. Instrum. Meas.,
vol. 73, 2024, Art. no. 2509510.

3736

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 2, MARCH/APRIL 2026

[19] A. Deng and B. Hooi, “Graph neural network-based anomaly detection in
multivariate time series,” in Proc. AAAI Conf. Artif. Intell., 2021, vol. 35,
pp. 4027–4035.
[20] R. Gao, W. He, L. Yan, D. Liu, Y. Yu, and Z. Ye, “Hybrid graph transformer
networks for multivariate time series anomaly detection,” J. Supercomput.,
vol. 80, no. 1, pp. 642–669, 2024.
[21] S. Han and S. S. Woo, “Learning sparse latent graph representations for
anomaly detection in multivariate time series,” in Proc. 28th ACM SIGKDD
Conf. Knowl. Discov. Data Mining, 2022, pp. 2977–2986.
[22] W. Zhang, P. He, C. Qin, F. Yang, and Y. Liu, “A graph attention
network-based model for anomaly detection in multivariate time series,”
J. Supercomput., vol. 80, no. 6, pp. 8529–8549, 2024.
[23] J. Wang, S. Shao, Y. Bai, J. Deng, and Y. Lin, “Multiscale wavelet graph
autoencoder for multivariate time-series anomaly detection,” IEEE Trans.
Instrum. Meas., vol. 72, 2023, Art. no. 2502911.
[24] S. He, G. Li, J. Wang, K. Xie, and P. Sharma, “UNI-directional graph
structure learning-based multivariate time series anomaly detection with
dynamic prior knowledge,” Int. J. Mach. Learn. Cybern., vol. 16, pp.
267–283, May 2024.
[25] Z. Zhang, Z. Geng, and Y. Han, “Graph structure change-based anomaly
detection in multivariate time series of industrial processes,” IEEE Trans.
Ind. Informat., vol. 20, no. 4, pp. 6457–6466, Apr. 2024.
[26] H. Pang et al., “Asymptotic consistent graph structure learning for multivariate time-series anomaly detection,” IEEE Trans. Instrum. Meas.,
vol. 73, 2024, Art. no. 2509510.
[27] Z. Chen, D. Chen, X. Zhang, Z. Yuan, and X. Cheng, “Learning graph
structures with transformer for multivariate time-series anomaly detection in iot,” IEEE Internet Things J., vol. 9, no. 12, pp. 9179–9189,
Jun. 2022.
[28] X. Zhou, C. Dai, W. Wang, and T. Qiu, “Global-local association discrepancy for multivariate time series anomaly detection in IIoT,” IEEE Internet
Things J., vol. 11, no. 7, pp. 11287–11297, Apr. 2024.
[29] S. Qin, L. Chen, Y. Luo, and G. Tao, “Multiview graph contrastive learning
for multivariate time-series anomaly detection in IoT,” IEEE Internet
Things J., vol. 10, no. 24, pp. 22401–22414, Dec. 2023.
[30] S. He, G. Li, Q. Guo, and K. Xie, “Multi-graph structure learning-based
multivariate time series anomaly detection with extended prior knowledge,” in Proc. 27th Int. Conf. Comput. Supported Cooperative Work Des.,
2024, pp. 109–114.
[31] S. He, G. Li, K. Xie, and P. K. Sharma, “Fusion graph structure learningbased multivariate time series anomaly detection with structured prior
knowledge,” IEEE Trans. Inf. Forensics Secur., vol. 19, pp. 8760–8772,
2024.
[32] S. He, Q. Guo, G. Li, K. Xie, and P. K. Sharma, “Multivariate time series
anomaly detection based on multiple spatio-temporal graph convolution,”
IEEE Trans. Instrum. Meas., vol. 74, 2025, Art. no. 3500714.
[33] S. He et al., “Graph structure learning-based multivariate time series
anomaly detection in Internet of Things for human-centric consumer applications,” IEEE Trans. Consum. Electron., vol. 70, no. 3, pp. 5419–5431,
Aug. 2024.
[34] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Soderstrom,
“Detecting spacecraft anomalies using LSTMS and nonparametric dynamic thresholding,” in Proc. Proc. 24th ACM SIGKDD Int. Conf. Knowl.
Discov. Data Mining, 2018, pp. 387–395.
[35] C. Zhang et al., “A deep neural network for unsupervised anomaly detection and diagnosis in multivariate time series data,” in Proc. AAAI Conf.
Artif. Intell., 2019, vol. 33, pp. 1409–1416.
[36] D. Li, D. Chen, B. Jin, L. Shi, J. Goh, and S.-K. Ng, “MAD-GAN:
Multivariate anomaly detection for time series data with generative
adversarial networks,” in Proc. Int. Conf. Artif. Neural Netw., 2019,
pp. 703–716.
[37] K.-J. Jeong, J.-D. Park, K. Hwang, S.-L. Kim, and W.-Y. Shin, “Twostage deep anomaly detection with heterogeneous time series data,” IEEE
Access, vol. 10, pp. 13704–13714, 2022.
[38] D. Park, Y. Hoshi, and C. C. Kemp, “A multimodal anomaly detector for robot-assisted feeding using an LSTM-based variational autoencoder,” IEEE Robot. Automat. Lett., vol. 3, no. 3, pp. 1544–1551,
Jul. 2018.
[39] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, 2019, pp. 2828–2837.
[40] B. Zong et al., “Deep autoencoding Gaussian mixture model for unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Representations,
2018, pp. 1–19.

[41] T. Q. Chen, Y. Rubanova, J. Bettencourt, and D. Duvenaud, “Neural
ordinary differential equations,” in Proc. 31st Annu. Conf. Adv. Neural
Inf. Process. Syst., S. Bengio, H. M. Wallach, H. Larochelle, K. Grauman,
N. Cesa-Bianchi, and R. Garnett, Eds., Montréal, Canada, Dec. 2018, pp.
6572–6583.
[42] J. H. Fririksson and E. Ågren, “Neural ordinary differential equations for
anomaly detection,” Master Degree Thesis, Kungliga Tekniska högskolan,
Jan. 4, 2022.
[43] H. Lim, S. Park, M. J. K. Lee, S. Lim, and N. Park, “MADSGM: Multivariate anomaly detection with score-based generative models,” in Proc. 32nd
ACM Int. Conf. Inf. Knowl. Manage., I. Frommholz, F. Hopfgartner, M.
M. Lee, M. Oakes, M. L. Zhang, and R. L. T. Santos, Eds., Birmingham,
U.K., Oct. 2023, pp. 1411–1420.
[44] R. Hu, X. Yuan, Y. Qiao, B. Zhang, and P. Zhao, “Unsupervised anomaly
detection for multivariate time series using diffusion model,” in Proc.
IEEE Int. Conf. Acoust., Speech Signal Process., Seoul, Republic of Korea,
Apr. 2024, pp. 9606–9610.
[45] Y. Liu, Y. Zheng, D. Zhang, H. Chen, H. Peng, and S. Pan, “Towards
unsupervised deep graph structure learning,” in Proc. ACM Web Conf.,
Lyon, France, Apr. 2022, pp. 1392–1403, doi: 10.1145/3485447.3512186.
[46] Z. Fang, Q. Long, G. Song, and K. Xie, “Spatial-temporal graph ODE
networks for traffic flow forecasting,” in Proc. 27th ACM SIGKDD Conf.
Knowl. Discov. Data Mining, Virtual Event, Singapore, Aug. 2021, pp.
364–373.
[47] H. Sakoe and S. Chiba, “Dynamic programming algorithm optimization
for spoken word recognition,” IEEE Trans. Acoust., Speech, Signal Process., vol. ASSP-26, no. 1, pp. 43–49, Feb. 1978.
[48] E. Jang, S. Gu, and B. Poole, “Categorical reparameterization with
gumbel-softmax,” in Proc. 5th Int. Conf. Learn. Representations, Toulon,
France, Apr. 2017, pp. 24–26. [Online]. Available: https://openreview.net/
forum?id=rkE3y85ee
[49] K. Choi, J. Yi, C. Park, and S. Yoon, “Deep learning for anomaly detection
in time-series data: Review, analysis, and guidelines,” IEEE Access, vol. 9,
pp. 120043–120065, 2021.
[50] L. A. C. Xhonneux, M. Qu, and J. Tang, “Continuous graph neural
networks,” in Proc. 37th Int. Conf. Mach. Learn., Jul. 2020, vol. 119,
pp. 10432–10441.
[51] Y. Su, C. Zhao, R. N. Liu, W. Sun, and D. Pei, “Robust anomaly detection
for multivariate time series through stochastic recurrent neural network,”
in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, A. V.
Teredesai, Y. K. Li, R. Rosales, E. Terzi, and G. Karypis, Eds. Anchorage,
AK, USA, Aug. 2019, pp. 2828–2837.
[52] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga, “USAD:
Unsupervised anomaly detection on multivariate time series,” in Proc.
26th ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2020, pp.
3395–3404.
[53] B. A. AlAhmadi, L. Axon, and I. Martinovic, “99% false positives: A
qualitative study of SOC analysts’ perspectives on security alarms,” in
Proc. 31st USENIX Secur. Symp., K. R .B. Butler and K. Thomas, Eds.,
Boston, MA, USA, Aug. 2022, pp. 2783–2800. [Online]. Available: https:
//www.usenix.org/conference/usenixsecurity22/presentation/alahmadi
[54] C. Fu, Q. Li, K. Xu, and J. Wu, “Point cloud analysis for ML-based
malicious traffic detection: Reducing majorities of false positive alarms,”
in Proc. ACM SIGSAC Conf. Comput. Commun. Secur., W. Meng, C. D.
Jensen, C. Cremers, and E. Kirda, Eds. Copenhagen, Denmark, Nov. 2023,
pp. 1005–1019, doi: 10.1145/3576915.3616631.
[55] Z. Wu, S. Pan, G. Long, J. Jiang, and C. Zhang, “Graph wavenet for
deep spatial-temporal graph modeling,” in Proc. 28th Int. Joint Conf. Artif.
Intell., S. Kraus, Ed., Macao, China, Aug. 2019, pp. 1907–1913.

Shiming He received the BS degree in information
security and the PhD degree in computer science and
technology from Hunan University, China, in 2006
and 2013, respectively. She is currently a Professor
with the School of Computer Science and Technology, Changsha University of Science and Technology,
Changsha, China. Her research interests include machine learning, data analysis, AIOps, and anomaly
detection.

HE et al.: MULTIVARIATE TIME SERIES ANOMALY DETECTION USING LEARNABLE SPATIAL-TEMPORAL GRAPH ORDINARY

Qingqing Guo received the BS degree from Hunan Agricultural University, in 2022. He is currently
working toward the MS degree in computer technology with the Changsha University of Science and
Technology. His research interests include deep learning, data analysis, and anomaly detection.

Keyao Feng received the BS degree from East China
Jiaotong University in 2023. She is currently working
toward the MS degree in software engineering with
the Changsha University of Science and Technology.
Her research interests include deep learning, graph
structure learning, and anomaly detection.

Diqing Liang received the PhD degree in computer
software and theory from Central South University,
China, in 2017. He is currently a Senior Engineer with
the Information Construction Management Department of the Changsha University of Science & Technology, Changsha, China. His research interests include artificial intelligence, Big Data, and cyberspace
security.

3737

Kun Xie (Member, IEEE) received the PhD degree in computer application from Hunan University, Changsha, China, in 2007. She has authored or
coauthored more than 100 articles in major journals
and conference proceedings, including journals such
as IEEE/ACM Transactions on Networking, IEEE
Transactions on Mobile Computing, IEEE Transactions on Computers, IEEE Transactions on Parallel and Distributed Systems,IEEE Transactions on
Wireless Communications, and IEEE Transactions on
Services Computing, and conferences, including SIGMOD, INFOCOM, ICDCS, SECON, DSN, and IWQoS. Her research interests
include cover network measurement, network security, Big Data, and AI.
Pradip Kumar Sharma (Senior Member, IEEE) received the PhD degree in CSE from the Seoul National
University of Science and Technology, South Korea,
in 2019. He was a postdoctoral research fellow in
the Department of Multimedia Engineering with the
Dongguk University, South Korea. He was a software
engineer with MAQ Software, India, and involved on
variety of projects, proficient in building largescale
complex data warehouses, OLAP models, and reporting solutions that meet business objectives and align
IT with business. He is currently an assistant professor
of Cybersecurity in the Department of Computing Science with the University of
Aberdeen, U.K. He has authored or coauthored many technical research papers
in leading journals from IEEE, Elsevier, Springer, and MDPI. Some of his
research findings are authored or coauthored in the most cited journals. His
current research interests are focused on the areas of Cybersecurity, Blockchain,
Edge computing, SDN, and IoT security. He has been an expert reviewer for
IEEE TRANSACTIONS, Elsevier, Springer, and MDPI journals and magazines.
He is listed in the world’s Top 2% scientists for citation impact during the
calendar year 2019 by Stanford University, Stanford, CA, USA. He has also
been invited to serve as the technical programme committee member and the
chair in several reputed international conferences such as IEEE DASC 2021,
IEEE CNCC 2021, CSA 20202, IEEE ICC2019, IEEE MENACOMM’19, and
3ICT 2019. He is also an associate editor for Peer-to-Peer Networking and
Applications, Human-centric Computing and Information Sciences, Electronics
(MDPI), and Journal of Information Processing Systems journals. He is a guest
editor of international journals of certain publishers such as IEEE, Elsevier,
Springer, MDPI, and JIPS. He was the recipient of the top 1% reviewer in
computer science by Publons Peer Review Awards 2018 and 2019, Clarivate
Analytics.
PAPER_TEXT
