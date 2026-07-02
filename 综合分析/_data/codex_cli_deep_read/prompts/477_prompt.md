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
# [477] Lightweight and Fast Time-Series Anomaly Detection via Point-Level and Sequence-Level Reconstruction Discrepancy
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
编号：477
题名：Lightweight and Fast Time-Series Anomaly Detection via Point-Level and Sequence-Level Reconstruction Discrepancy
年份：2025
DOI：10.1109/tnnls.2025.3565807
来源：IEEE Transactions on Neural Networks and Learning Systems
PDF：paper/10.1109_TNNLS.2025.3565807.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测
相关性：弱相关，分数 4
已有代码状态：已下载；LFTSAD -> source\LFTSAD

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\477.txt
- 原始字符数：67160
- 本次发送字符数：67160
- 是否截断：False

代码包：
- 仓库：LFTSAD
  - URL：https://github.com/infogroup502/LFTSAD
  - 状态：downloaded
  - 本地目录：source\LFTSAD
  - 顶层结构：README.md、data_factory/、img/、main.py、metrics/、model/、requirements.txt、scripts/、solver.py、utils/
  - 主要语言：Python:30、Shell:9
  - README 标题：Lightweight and Fast Time-Series Anomaly Detection via Point-Level and Sequence-Level Reconstruction、Framework、Requirements、Data、Code Description、There are six files/folders in the source、Usage、BibTex Citation、Lightweight and Fast Time-Series Anomaly Detection via Point-Level and Sequence-Level Reconstruction、Framework
  - README 运行线索：bash pip install -r requirements.txt；python file. You can adjustment all parameters in there.；python file. The training, validation, and testing processing are all in there；Python packages needed to run this repo；Python 3.6, PyTorch >= 1.4.0；bash python main.py；bash @ARTICLE{11006753,；bash pip install -r requirements.txt
  - 关键文件：{"依赖环境": ["requirements.txt"], "推理/演示入口": ["main.py"], "数据处理入口": ["metrics/vus/models/feature.py"], "评估/测试入口": ["metrics/evaluate_utils.py", "metrics/evaluator.py"]}
  - 数据集线索：MSL、SMAP、SMD、SWAT、SwaT、Tor、WaDi、msl、smap、smd、swat、tor

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

17295

Lightweight and Fast Time-Series Anomaly
Detection via Point-Level and Sequence-Level
Reconstruction Discrepancy
Lei Chen , Member, IEEE, Jiajun Tang , Ying Zou , Xuxin Liu , Xingquan Xie , and Guangyang Deng

Abstract—Unsupervised time-series anomaly detection (TSAD)
aims to identify anomalies in industrial sensing signals to ensure
production safety. As Industry 4.0 emerges, TSAD deployment
must migrate from resource-rich cloud to resource-limited edges
for real-time and fine-grained control. In this case, it raises
new targets with high accuracy, high timeliness, and low consumption for TSAD. However, existing models focus solely on
achieving high accuracy by building neural networks with deep
structures and large parameters. Consequently, these models
demand prohibitive training durations and computational overhead, which makes them unsuitable for edge deployment. To solve
this issue, an unsupervised lightweight and fast TSAD model,
namely, LFTSAD, is proposed via point-level and sequencelevel reconstruction discrepancy in this article. First, to achieve
high timeliness and low consumption, LFTSAD uses two twolayer multilayer perceptron networks (MLPs) to construct a
lightweight contrastive architecture with few parameters. Second, leveraging the lightweight architecture, a dual-branch
reconstruction network is designed to generate corresponding
reconstruction discrepancies from point-level and sequence-level
perspectives. Finally, a novel anomaly scoring scheme is designed
to combine point-level and sequence-level reconstruction discrepancies for more accurate anomaly detection. To the best of
our knowledge, this is the first work to develop a lightweight
All-MLP-based TSAD model for resource-limited edge devices.
Extensive experiments demonstrate that LFTSAD is 3–10 times
faster in timeliness, consumes only 1/2 of the resources, and
achieves accuracy that is either comparable to or superior to
several deep SOTA models. The source code of LFTSAD is here
https://github.com/infogroup502/LFTSAD
Index Terms—All-multilayer perceptron network (MLP)-based
anomaly detection, lightweight network and design, pointlevel and sequence-level, reconstruction discrepancy, time-series
anomaly detection (TSAD).

I. I NTRODUCTION
IME-series anomaly detection (TSAD) aims to identify
outliers or deviations in temporal data that record the state
of a continuous dynamic system [1]. Coming to Industry 4.0,

T

Received 23 August 2024; revised 29 March 2025 and 17 April 2025;
accepted 27 April 2025. Date of publication 19 May 2025; date of current
version 4 September 2025. This work was supported in part by the National
Natural Science Foundation of China under Grant 62103143 and Grant
62203164, in part by Hunan Provincial Natural Science Foundation of China
under Grant 2024JJ5162, and in part by the Scientific Research Fund of Hunan
Provincial Education Department under Grant 22B0471. (Corresponding
author: Lei Chen.)
The authors are with the School of Information and Electrical
Engineering, Hunan University of Science and Technology, Xiangtan
411201,
China
(e-mail:
chenlei@hnust.edu.cn;
jiajuntang@mail.
hnust.edu.cn;
1040134@hnust.edu.cn;
xuxinliu@mail.hnust.edu.cn;
xingquanxie@mail.hnust.edu.cn; guangyangdeng@mail.hnust.edu.cn).
Digital Object Identifier 10.1109/TNNLS.2025.3565807

time-series data exhibit new characteristics: complex temporal
dynamics, rare anomaly labels, and rapidly increasing data
volumes [2]. These characteristics undermine the effectiveness
of traditional statistical, machine-learning-based, supervised,
and semi-supervised TSAD models [3], compromising their
competitiveness. As a result, unsupervised deep-learningbased TSAD models, such as those using CNN, transformer,
and RNN architectures, have attracted significant attention
in recent years [4], [5], [6], [7], [8]. However, the existing
unsupervised TSAD models still face two main challenges.
A. Challenge
1) Balancing Timeliness, Resource Efficiency, and Accuracy: Traditional deep TSAD models are typically
deployed on resource-rich cloud servers, where they prioritize high accuracy using deep architectures and large
parameters [9], [10], [11], [12], [13], [14]. Consequently,
they require long training and detection time, along
with significant computational and storage resources.
As Industry 4.0 emerges, industrial production processes
require real-time and fine-grained intelligent monitoring
and management. This makes it necessary to migrate the
TSAD models from cloud servers to edge devices. However, edge devices typically have limited computational
and storage resources, which restricts their ability to run
complex deep models. For example, a Raspberry Pi 4b
has only 2-GB RAM and 1.5-GHz clock speed. Therefore, unsupervised TSAD models need to find a tradeoff
among timeliness, resource consumption, and accuracy
to ensure stable operation on resource-constrained edge
devices.
2) Constructing Powerful Anomaly Scoring Scheme: An
unsupervised TSAD model typically requires an
anomaly scoring scheme to evaluate observations at each
timestamp and detect anomalies. The existing schemes
can be mainly divided into three categories: reconstruction error-based [12], prediction error-based [9], and
hybrid error-based [10]. However, each of these schemes
has limitations, which makes it difficult to achieve both
high accuracy and low time overhead, particularly when
handling time-series data with complex features. As a
result, these schemes struggle to perform effectively on
resource-constrained edge devices.
B. Existing Solution
To address the first challenge, some approaches use parallel
computing [15] or federated learning [16] to accelerate the
speed of the existing deep TSAD models. However, they

2162-237X © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

17296

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

Fig. 1. Illustration of three anomaly scoring schemes. (a) Reconstruction error-based anomaly scoring. (b) Association discrepancy-based anomaly scoring.
(c) Reconstruction discrepancy-based anomaly scoring.

require significant computational resources and large storage due to multithreaded processing and distributed learning.
Other methods either apply compression techniques (pruning
and quantization) to reduce redundant parameters [17], [18]
or use shallow CNN or multilayer perceptron network (MLP)
networks to replace time- or resource-consuming modules
[19], [20] in the existing deep models. In this case, model
parameters and computation times are reduced, achieving a
balance between high accuracy and high timeliness. However, these methods still rely on deep structures, which limit
their optimization capabilities in terms of time and resource
efficiency. Thus, they are unsuitable for stable operation in
resource-constrained environments.
To address the second challenge, a novel association
discrepancy-based anomaly scoring scheme is introduced in
2022 [21], as shown in Fig. 1(b). In the proposed scheme,
it states that compared with normal timestamps, anomalous
timestamps in the time-series data exhibit stronger associations with local neighbors and weaker associations with
global neighbors. Based on this work, several advanced TSAD
models, such as AnomalyTrans (ATran) [21] and DCdetector
(DCDet) [22], are proposed in the past two years, achieving
high accuracy by capturing fine-grained short- and long-term
contextual information. However, the computational complexity of fine-grained context processing leads to high time and
resource consumption. Therefore, this novel scoring scheme
is not well-suited for high-timeliness TSAD applications on
resource-limited edge devices.
In summary, current acceleration schemes and accuracy
optimization methods fail to achieve an effective tradeoff
among speed, resource efficiency, and accuracy on resourcelimited edge devices. To meet the demands of real-time TSAD
at the edge devices, a more direct and effective solution is to
design lightweight TSAD models using simple networks and
shallow structures. Among neural networks, MLPs are particularly well-suited due to their simplicity and efficiency. This
makes All-MLP architectures a promising choice for balancing
timeliness, low resource consumption, and accuracy. Although
some existing TSAD models, such as PatchAD (PaAD) [19]
and USAD [20], adopt All-MLP designs, they still rely on
deep structures. For example, PaAD uses a deep transformer
with MLP units, while USAD builds an autoencoder using
two multilayer MLPs. Therefore, a gap remains in developing
TSAD models based solely on shallow All-MLP architectures
(e.g., one or two layers) for edge deployment. However, shallow structures inherently offer limited representation capacity,

making it challenging to simultaneously ensure high accuracy,
fast inference, and low resource usage.
C. New Insight
To fill such a gap, this article aims to develop an unsupervised lightweight TSAD model based only on the two-layer
MLP architecture for deployment on resource-limited edge
devices. For this goal, two bottlenecks need to be addressed.
The first challenge lies in how to solely use two-layer MLPs
to design a lightweight architecture with high speed, accuracy, and low consumption. To address this, the association
discrepancy-based scoring scheme is used to guide architecture construction. However, traditional fine-grained association
calculations are time- and resource-intensive, as each timestamp must evaluate associations with all the neighbors
individually, as shown in Fig. 1(b). This complexity makes
fine-grained association processing infeasible for a two-layer
MLP network. To overcome this, a reconstruction-discrepancybased scheme is proposed by fusing reconstruction-based
and association discrepancy-based scoring schemes, as shown
in Fig. 1(c). Instead of computing each association value
explicitly, we focus on learning whether a strong association
exists between a timestamp and its neighbors, significantly
simplifying the process. Based on this approach, two two-layer
MLPs are used to perform contrastive reconstruction learning
of “local neighbors-to-a timestamp” and “global neighborsto-same timestamp” respectively. A small difference between
the two reconstruction outputs indicates strong associations
with both local and global neighbors, suggesting a normal
timestamp. In contrast, a large discrepancy is interpreted as
an anomaly. To the best of our knowledge, the fusion of
reconstruction error-based and association discrepancy-based
scoring schemes has not been previously explored.
The second challenge is enhancing detection accuracy of
the designed lightweight architecture. Typically, outliers in
time series persist across multiple timestamps and can be
categorized as explicit or implicit, as presented in Fig. 2.
In explicit outliers [Fig. 2(a)], the association pattern of
each anomalous timestamp (x1 ) with its point-level neighbors
deviates significantly from that of normal timestamps (y1 ). In
this case, the lightweight architecture can accurately identify
anomalous timestamps. However, implicit outliers present a
greater challenge, as only some timestamps exhibit association
patterns that significantly deviate from normal timestamps,
while others appear similar. As illustrated in Fig. 2(b), the
association pattern of x2 with its point-level neighbors closely

CHEN et al.: LFTSAD VIA POINT-LEVEL AND SEQUENCE-LEVEL RECONSTRUCTION DISCREPANCY

17297

Fig. 2. Two types of anomalies in time series. (a) Explicit outlier. (b) Implicit outlier.

resembles that of y2 , increasing the risk of misclassification. To
address this issue, we expand the analysis beyond individual
timestamps. Instead of relying solely on x2 , we consider a
subsequence centered around x2 as its substitute, as shown in
the elliptical region of Fig. 2(b). This extended view reveals
that the association pattern of the substitute subsequence of x2
with its sequence-level neighbors differs significantly from that
of y2 . By incorporating both the point-level and sequence-level
perspectives, our lightweight architecture enhances detection
accuracy for both the explicit and implicit outliers.
Based on these insights, an unsupervised lightweight and
fast TSAD model, namely, LFTSAD, is proposed via pointlevel and sequence-level reconstruction discrepancy. LFTSAD
comprises four two-layer MLPs: two form the point-level
reconstruction branch, and the other two constitute the
sequence-level reconstruction branch. Reconstruction discrepancies from both the branches are combined to detect
timestamp-level anomalies, enabling deployment on resourcelimited edge devices.
D. Contribution
The main contributions of this work are outlined as follows.
1) A lightweight All-MLP-based TSAD model LFTSAD
is proposed to identify anomalies quickly and efficiently
on resource-limited edge devices. Specifically, LFTSAD
uses four parallelizable two-layer MLPs to construct a
lightweight dual-branch contrastive reconstruction network from both the point-level and sequence-level
perspectives. To the best of our knowledge, this is
the first work to develop a lightweight All-MLP-based
TSAD model for resource-limited edge devices.
2) A novel reconstruction discrepancy-based anomaly scoring scheme is designed, which effectively combines
point-level and sequence-level reconstruction discrepancies to accurately identify both the explicit and implicit
anomalies.
3) Extensive experiments are conducted on 14 public
datasets and two edge devices: Raspberry Pi 4b and
NVIDIA Jetson Xavier NX. The experimental results
demonstrate that LFTSAD outperforms several deep
SOTA models in timeliness and resource consumption while achieving comparable or superior accuracy.
Specifically, LFTSAD ranks first or second on more
than half of the eight evaluation metrics across the 14
datasets. Moreover, its detection time is 3–10 times
faster than that of deep SOTA models.
II. R ELATED W ORK
Since our model is built upon the association discrepancybased scoring scheme and All-MLP architecture, related work
on these two topics is summarized as follows [5].

A. Association Discrepancy-Based TSAD
In 2022, association discrepancy-based anomaly scoring scheme was proposed for unsupervised timestamp-level
anomaly detection [21]. In the past two years, several advanced
TSAD models based on association discrepancy have been
proposed and demonstrated strong performance [23], [24],
[25].
For example, the ATran model [21] uses a learnable Gaussian kernel for local associations and a multihead attention
mechanism for global associations. The MAN-QSM model
[25] adds a mask learning mechanism into the association
discrepancy learning process to enhance detection accuracy.
The DCDet model [22] designs an attention-based dual-branch
contrastive learning architecture to capture both the local and
global associations. The Dual-TF model [23] further learns
time-frequency granularity discrepancies to identify anomalies. The SiET model [24] considers the spatial association
of multiple variables and uses spatiotemporal association discrepancies for anomaly detection.
In summary, the association discrepancy-based scoring
scheme effectively identifies timestamp-level anomalies in
time-series data. However, the fine-grained association calculation is time-consuming and resource-intensive. As a result, the
existing association discrepancy-based TSAD models require
extensive training and testing times, as well as substantial
CPU/GPU and storage resources. Furthermore, these models
are typically designed for resource-rich cloud environments.
Consequently, they incur higher resource consumption and
time overhead, making them unsuitable for stable deployment
in resource-constrained edge environments.
B. All-MLP-Based Time-Series Analysis
In recent years, several deep TSAD models have used simple MLP networks to enhance model timeliness by replacing
time-consuming or resource-intensive modules. For instance,
the PaAD model [19] uses MLPs to replace the attention module, thereby reducing the time overhead of anomaly detection.
Similarly, the ANNet model [26] optimizes the LSTM cell
using the simple MLP. In addition, the USAD model [20]
uses two multilayer MLPs to design an autoencoder network
for anomaly detection. Overall, the existing All-MLP-based
TSAD models are still in the early stages of research. Despite
offering certain improvements in timeliness compared with
other models, their enhancements remain insufficient. Moreover, these models still rely on deep architectures, resulting in
high resource consumption. This constraint hinders their stable
deployment on resource-limited edge devices.
In contrast, All-MLP-based models have rapidly emerged
in time-series forecasting over the past two years. For example, the FiLM model [27] conducts extensive experiments

17298

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

learning algorithms, particularly for anomaly detection, are
used to extract insights from the collected data. However, the
rapid expansion of cloud tasks in Industry 4.0 brings latency
and resource-utilization challenges. To address these issues,
many analysis models are being migrated from the cloud to
the edge for high timeliness performance.
This article assumes that M sensors are used to gather the
operating states of an industrial production process. After T
collections, the generated data are a time series, formulated
as X = {x1 , . . . , xT } ∈ R M×T . Specifically, a time series
consists of a time dimension and a variable dimension. For
the time dimension, X = {xt ∈ R M×1 }Tt=1 , where xt represents
observations from M sensors at the tth timestamp. For the
M
variable dimension, X = {xm ∈ R1×T }m=1
, where xm represents
observations from T timestamps at the mth sensor.

Fig. 3. Industry 4.0 scenario.

to demonstrate that MLP networks can replace the CNN or
attention networks. Based on this finding, the Solar-Mixer
model [28] constructs an All-MLP architecture to perform
time-series forecasting. To enhance prediction performance,
the HDMixer model [29] designs a stacked-MLP network to
learn both the temporal and spatial features among multiple
variables. However, these models still rely on deep structures
and large parameters. Their timeliness and resource efficiency
are inadequate, making them less competitive for deployment
on resource-constrained edge devices. To address this issue,
several customized lightweight All-MLP-based forecasting
models have been proposed. For instance, the FreTS model
[30] uses a shallow complex-valued MLP network to directly
learn time-series features in the frequency domain. The FITS
model [31] directly uses a two-layer MLP to simulate interpolation process in the frequency domain. Notably, the FITS
model has fewer than 10 K parameters, achieving high speed,
low consumption, and high accuracy.
In summary, forecasting models based on shallow All-MLP
architecture demonstrate their effectiveness in timeliness, accuracy, and resource consumption. This highlights the feasibility
of adopting similar architectures to design TSAD models that
can operate stably on resource-limited edge devices. However, the existing TSAD models still rely on deep structures
and large parameters, which prevent their direct deployment
on resource-limited edge devices. Thus, a gap remains in
developing a TSAD model that exclusively leverages a shallow All-MLP architecture for efficient and stable edge-based
anomaly detection.
III. P RELIMINARY
A. Industry 4.0 Scenario
In Industry 4.0, multiple heterogeneous sensors, such as
vibration and angle sensors, are installed at different locations
to enable intelligent and fine-grained monitoring and management of the production process, as shown in Fig. 3. Typically,
these sensors collect different signals of industrial production
at a fixed frequency. The acquired data, encoding industrial process dynamics, are transmitted via multiple network
modalities (WiFi, 5G, Ethernet) and protocols (Modbus, UDP,
TCP) to resource-constrained edge gateways or hosts. At the
edge, sampled data are aggregated and forwarded to resourcerich cloud platforms for in-depth analysis. Advanced machine

B. Problem Statement
This article aims to build an LFTSAD model. First, a time
series X is divided into an unlabeled training set X1 and a
labeled test set X2 . Second, the unlabeled X1 is used to train
our lightweight model. Third, the trained model scores each
timestamp in X2 as follows:
Scoret = TSAD (xt )

(1)

where xt ∈ R M×1 denotes the observations at the tth timestamp
in X2 . Finally, this score is used to determine whether a
timestamp is an anomaly, as defined below

1, if Scoret ≥ λ
ȳt =
(2)
0, otherwise
where λ is the preset threshold, ranging from 0 to 1. If ȳt = 1,
the tth timestamp is an anomaly; otherwise, it is normal. We
aim for the predicted labels of each timestamp in X2 by our
lightweight TSAD model to closely match the true labels.
IV. P ROPOSED M ODEL
A. Model Overview
To pursue triple goals of high accuracy, high timeliness,
and low consumption, an unsupervised LFTSAD model is
proposed. The overview of LFTSAD is presented in Fig. 4,
which comprises three components. Note that the first two
components complement each other and can be executed in
parallel.
1) Point-Level Reconstruction Discrepancy Learning: As
shown in Fig. 4(a), this component generates point-level
reconstruction discrepancy for each timestamp from a
point-level perspective. Technically, a customized sampling strategy is first designed to generate point-level
local and global neighbors for each timestamp. Second,
a shared two-layer MLP is used to perform “local
neighbors-to-one timestamp” reconstruction learning.
Third, another two-layer MLP is used to perform “global
neighbors-to-same timestamp” reconstruction learning.
Finally, the difference of two reconstruction values is
point-level reconstruction discrepancy for a given timestamp.
2) Sequence-Level Reconstruction Discrepancy Learning:
Complementing the first component, this one generates sequence-level reconstruction discrepancy for
each timestamp from a sequence-level perspective, as

CHEN et al.: LFTSAD VIA POINT-LEVEL AND SEQUENCE-LEVEL RECONSTRUCTION DISCREPANCY

17299

Fig. 4. Overview of the LFTSAD model. (a) Point-level reconstruction discrepancy learning. (b) Sequence-level reconstruction discrepancy learning.
(c) Reconstruction discrepancy-based anomaly scoring.

shown in Fig. 4(b). Specifically, a customized sequencelevel sampling strategy generates sequence-level local
and global neighbors for each timestamp. Then, two
two-layer MLPs are used to perform contrastive reconstruction learning on “local neighbors-to-a substitute
sequence” and “global neighbors-to-same substitute
sequence,” respectively. Finally, the difference between
two reconstruction sequences yields the sequence-level
reconstruction discrepancy for a given timestamp.
3) Reconstruction Discrepancy-Based Anomaly Scoring:
This one combines point-level and sequence-level reconstruction discrepancies to assess whether a timestamp is
anomalous.
Fig. 5. (a) Point-level and (b) sequence-level sampling.

B. Point-Level Reconstruction Discrepancy Learning
As shown in Fig. 2, time-series data inherently exhibit various characteristics, including seasonal and periodic patterns,
while outliers generally span multiple timestamps and significantly deviate from these normal patterns. In this context,
a normal timestamp maintains associations not only with its
adjacent timestamps (local neighbors) but also with distant
timestamps (global neighbors), reflecting periodic and seasonal
dependencies. In contrast, an anomalous timestamp is primarily associated with its local neighbors within the same outlier
and lacks associations with distant global neighbors. Based
on this principle, two two-layer MLPs are used to separately
learn local and global associations for each timestamp from
a point-level perspective, as presented in Fig. 4(a). Notably,
the point-level learning process is variable-independent for
multivariate time series. In this process, each variable is
processed in parallel while sharing the same two MLPs.
1) Point-Level Sampling: A customized point-level sampling strategy is designed to quickly generate local and global
neighbors for each timestamp, as shown in Fig. 5(a). The
process involves four steps: 1) multiple overlapping sequences
are randomly extracted using a look-back window of length
WIN; 2) each sequence is divided into P1 nonoverlapping
segments, each segment containing P2 timestamps, ensuring
P1 × P2 = WIN; 3) these segments are stacked into a 2-D

matrix of size P1 × P2 ; and 4) local neighbors of a timestamp
at position (i, j) correspond to other timestamps in row i, while
global neighbors are those in column j.
In the 2-D matrix, timestamps in the same row share
local neighbors, while those in the same column share global
neighbors. For multivariate time series, the sampling of each
variable operates independently and can be executed in parallel, further enhancing efficiency.
2) Local Association Learning: Association calculation is
typically a fine-grained process in which the relationship of
each timestamp with its neighbors must be assessed. For
example, if a timestamp has P2 neighbors, P2 associations
must be computed. Such complexity exceeds the capability
of a two-layer MLP. To address this issue, this article directly
uses all the neighbors to reconstruct each timestamp. Accurate
reconstruction indicates a strong association with its neighbors,
while poor reconstruction suggests a weak association. This
approach significantly simplifies the association calculation
process while maintaining effectiveness.
Specifically, a two-layer MLP is used to learn local associations at each timestamp. This shallow MLP consists of an
input layer with P2 −1 neurons, a hidden layer with d neurons,
and an output layer with a single neuron. The input and hidden
layers form the first fully connected layer (FCL), containing

17300

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

(P2 − 1)×d trainable parameters. The hidden and output layers
constitute the second FCL, with d × 1 trainable parameters.
To speed up training, dropout and ReLU activation functions
are applied to each neuron in the hidden layer.
For the tth timestamp of the mth variable, its local neighbors
1×(P2 −1)
are defined as LP(xtm ) = {xim }t−1
. Its local
i=t−P2 ∈ R
association learning process is detailed below.
The P2 − 1 local neighbors are first fed into the first-FCL
to learn local association features



h1 xtm = ReLU LP xtm × W11
(3)
where h1 ∈ R1×d is the output, and W11 ∈ R(P2 −1)×d are the
parameters of the first-FCL.
Then, h1 is input into the second-FCL to reconstruct xtm

x̃tm = h1 xtm × W12
(4)
where x̃tm ∈ R is the local reconstruction value, and W12 ∈ Rd×1
are the parameters of the second-FCL.
3) Global Association Learning: Another two-layer MLP
is adopted to capture global associations at each timestamp.
This MLP has the same structure as the first MLP, comprising
only two FCLs and P1 ×d parameters. For the tth timestamp of
the mth variable, its global neighbors are defined as GP(xtm ) =
P1 −1
1×(P1 −1)
m
. The global association calculation
{xt−
j×P2 } j=1 ∈ R
process is detailed as follows.
The P1 − 1 global neighbors are input to the first-FCL to
learn global associated features



(5)
h2 xtm = ReLU GP xtm × W21
where h2 ∈ R1×d is the output, and W21 ∈ R(P1 −1)×d are the
parameters of the first-FCL.
Then, h2 is input into the second-FCL to reconstruct xtm

x̄tm = h2 xtm × W22
(6)
where x̄tm ∈ R is the global reconstruction value, and W22 ∈
Rd×1 are the parameters of the second-FCL.
4) Loss: The local and global association learning processes form two complementary branches. To align their
reconstruction values, the mean squared error (mse) loss is
used as the contrastive learning objective
LossP =

M

WIN

m=1

t=1

2
1 X 1 X m
x̃t − x̄tm
M
WIN

(7)

where M is the number of variables, and WIN is the number
of timestamps in one sample.
Notably, for each timestamp, the difference between the two
reconstruction outputs defines the point-level reconstruction
discrepancy.
C. Sequence-Level Reconstruction Discrepancy Learning
Outliers in time series can be categorized as explicit or
implicit, as presented in Fig. 2. Compared with explicit
outliers, implicit outliers exhibit more complex patterns. In
implicit outliers, some timestamps share similar association
patterns with normal data, while others exhibit significant deviations. In this context, point-level reconstruction discrepancy
may misidentify anomalous timestamps. To address this issue,
an additional reconstruction discrepancy learning process is
introduced from a sequence-level perspective to enhance detection accuracy. Specifically, two two-layer MLPs are used to

perform contrastive reconstruction on “local neighbors-to-a
substitute sequence” and “global neighbors-to-same substitute
sequence,” respectively. The difference between the two reconstructed sequences yields the sequence-level reconstruction
discrepancy for each timestamp.
1) Sequence-Level Sampling: A customized sequence-level
sampling process is designed to quickly generate sequencelevel local and global neighbors for each timestamp, as shown
in Fig. 5(b). The process also consists of four steps: 1)
multiple overlapping sequences of length WIN are randomly
extracted from the time series X in parallel; 2) each sequence is
divided into S 1 nonoverlapping segments, and each segment is
further partitioned into S 2 nonoverlapping subsegments, each
containing S 3 timestamps, ensuring S 1 × S 2 × S 3 = WIN;
3) the S 1 segments are stacked to form a 2-D matrix of size
S 1 × (S 2 × S 3 ); and 4) for a timestamp at row i and column
j, its subsegment serves as its substitute. The remaining
subsegments in row i are treated as local neighbors, while
those in column j provide global neighbors.
2) Local Association Learning: A two-layer MLP network
is used to perform “local neighbors-to-a substitute sequence”
reconstruction from the sequence perspective. The input layer
contains (S 2 − 1)×S 3 neurons, the hidden layer has d neurons,
and the output layer contains S 3 neurons. This MLP consists
of two FCLs with a total of S 2 × S 3 × d parameters. For
the tth timestamp of the mth variable, the value is denoted as
xtm ∈ R. Its substitute sequence is SEQ(xtm ) = {xim }ti=t−S 3 , and
3
local neighbors are LS(xtm ) = {xim }t−S
i=t−[(S 2 −1)×S 3 ] . The sequencelevel local reconstruction process is described below.
First, the (S 2 − 1) × S 3 local neighbors are input into the
first-FCL to learn local association features



h3 xtm = ReLU LS xtm × W31
(8)
where h3 ∈ R1×d is the output, and W31 ∈ R[(S 2 −1)×S 3 ]×d are
the parameters of the first-FCL.
Then, h3 is input into the second-FCL to reconstruct the
substitute sequence SEQ(xtm ) of the tth timestamp


g xtm = h3 xtm × W32
SEQ
(9)
g tm ) ∈ R1×S 3 is the local reconstruction sequence,
where SEQ(x
3
and W2 ∈ Rd×S 3 are the parameters of the second-FCL.
3) Global Association Learning: Another two-layer MLP
network is used to perform “global neighbors-to-same substitute sequence” reconstruction. The input layer contains
(S 1 − 1) × S 3 neurons, the hidden layer has d neurons,
and the output layer contains S 3 neurons. This MLP has
only S 1 × S 3 × d parameters. For the tth timestamp of the
mth variable, its global neighbors are defined as GS (xtm ) =
j×(S 2 ×S 3 )
S 1 −1
{{xim }t−
i=t− j×(S 2 ×S 3 )−S 3 } j=1 .
First, the (S 1 − 1) × S 3 global neighbors are input to the
first-FCL to learn the global association features



h4 xtm = ReLU GS xtm × W41
(10)
where h4 ∈ R1×d is the output, and W41 ∈ R[(S 1 −1)×S 3 ]×d are
the parameters of first-FCL.
Next, h4 is further input into the second-FCL to reconstruct
the substitute sequence of the tth timestamp


SEQ xtm = h4 xtm × W42
(11)
where SEQ(xtm ) ∈ R1×S 3 is the global reconstruction sequence,
and W42 ∈ Rd×S 3 are the parameters of second-FCL.

CHEN et al.: LFTSAD VIA POINT-LEVEL AND SEQUENCE-LEVEL RECONSTRUCTION DISCREPANCY

17301

Algorithm 1 LFTSAD

Fig. 6. Reconstruction discrepancy-based anomaly scoring.

4) Loss: The mse function is used again as the contrasting
learning loss
M

WIN

m=1

t=1

2
1 X 1 X g m
LossS =
SEQ xt − SEQ xtm .
M
WIN

(12)

D. Reconstruction Discrepancy-Based Anomaly Scoring
As illustrated in Fig. 6, a novel reconstruction discrepancybased anomaly scoring scheme is designed.
First, a to-be-tested timestamp xt ∈ R M×1 is input into
the point-level reconstruction discrepancy learning component,
where M variables are processed in parallel to produce M
point-level reconstruction discrepancies. The final point-level
discrepancy for xt is calculated as the average of these
M
values, formulated as ScoreP (xt ) = mean({ScoremP }m=1
), where
P
Scorem denotes the point-level discrepancy on the mth variable. Second, the to-be-tested timestamp xt is fed into the
sequence-level learning component to produce M sequencelevel reconstruction discrepancies. The final sequence-level
discrepancy is produced as the average of these values, forM
mulated as ScoreS (xt ) = mean({ScoreSm }m=1
). Third, the final
anomaly score for xt is generated as follows:
Score (xt ) = α × ScoreP (xt ) + (1 − α) × ScoreS (xt )

(13)

where α is a predefined hyperparameter within [0 ∼ 1]. Setting
α = 0 considers only the sequence-level discrepancy, while
α = 1 considers only the point-level discrepancy. Finally, the
anomaly score is used in (2) to determine whether timestamp
xt is anomalous.
E. Algorithm and Complexity Analysis
The pseudocode for LFTSAD is shown in Algorithm 1.
Complexity Analysis: The computational cost of LFTSAD comprises three components: point-level reconstruction,
sequence-level reconstruction, and anomaly scoring.
1) Point-Level Reconstruction Learning: This component
consists of three stages: point-level sampling, local
reconstruction, and global reconstruction. In the sampling stage, local and global neighbors are generated
for each timestamp across all the M variables in parallel. The computational complexity of this process is
O(T × (P1 + P2 )), where T is the number of timestamps,
and P1 and P2 represent the numbers of global and local
neighbors per timestamp, respectively. Next, two independent two-layer MLPs are used for local and global

reconstruction, respectively. The first MLP reconstructs
each timestamp using its local neighbors, while the
second MLP uses global neighbors for reconstruction.
Both the operations are performed in parallel across the
M variables to improve computational efficiency. For
local reconstruction via the first MLP, the computational
complexity is
0
0
11
B
B
CC
O @T × @(P2 − 1) × d + „ƒ‚…
1 × d AA
„ ƒ‚ …
1st−layer

2nd−layer

where (P2 −1), d, and 1 represent the number of neurons
in the input, hidden, and output layers, respectively. The
first and second layers contribute (P2 − 1) × d and 1 × d
operations. Similarly, for global reconstruction using the
second MLP, the complexity is
11
0
0
CC
B
B
O @T × @(P1 − 1) × d + „ƒ‚…
1 × d AA
„ ƒ‚ …
1st−layer

2nd−layer

with (P1 −1)×d and 1×d corresponding to the operations
in the first and second layers, respectively. In summary,

17302

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

the overall complexity of this component is O(T ×(P1 +
P2 ) × (d + 1)).
2) Sequence-Level Reconstruction Learning: This component also includes three stages: sequence-level sampling,
local reconstruction, and global reconstruction. First,
sequence-level sampling generates local and global
neighbors for each timestamp. Its complexity is O(T ×
(S 1 + S 2 + S 3 )), where S 1 and S 2 are the numbers
of global and local neighbors, and S 3 is the length
of the substitute sequence. Second, the third two-layer
MLP performs local reconstruction using sampled local
neighbors. The complexity is
0
0
11

TABLE I
DATASETS

B
B
CC
O @T × @((S 2 − 1) × S 3 ) × d + S 3 × d AA
ƒ‚
… „ ƒ‚ …
„
1st−layer

2nd−layer

where (S 2 − 1) × S 3 , d, and S 3 represent the numbers
of neurons in the input, hidden, and output layers,
respectively. The first layer contributes (S 2 − 1) × S 3 × d
operations, and the second layer contributes S 3 × d.
Finally, the fourth two-layer MLP performs global
reconstruction using sampled global neighbors. The
complexity is
0
0
11
B
B
CC
O @T × @((S 1 − 1) × S 3 ) × d + S 3 × d AA .
„
ƒ‚
… „ ƒ‚ …
1st−layer

2nd−layer

In summary, the overall complexity of this component
is O(T × (S 1 + S 2 ) × S 3 × d + T × (S 1 + S 2 + S 3 )).
3) Anomaly Scoring: Based on the outputs of point-level
and sequence-level reconstruction, two reconstruction
discrepancies are computed and merged to produce the
final anomaly score for each timestamp. This score
determines whether the timestamp is anomalous. The
computational complexity is O(T × 2M), where T is the
number of timestamps and M is the number of variables
Notably, the first two components are carried out in
parallel, and P1 + P2 < (S 1 + S 2 ) × S 3 . In summary,
by ignoring relatively small terms—O(T × 2M), O(T ×
(S 1 +S 2 +S 3 )), and O(T ×(P1 +P2 )×(d+1))—the overall
computational complexity of the proposed LFTSAD
model is approximated as: O(T × (S 1 + S 2 ) × S 3 × d).
This complexity is nearly linear with respect to T, since
(S 1 + S 2 ) × S 3 × d  T in practical scenarios.
V. E XPERIMENT
A. Experimental Goal
The following questions are addressed in the experiments.
1) RQ-1 (Accuracy): Can the model outperform baselines on univariate and multivariate time-series anomaly
detection?
2) RQ-2 (Deployability and Timeliness): How efficient is
the model in terms of timeliness and resource consumption on resource-constrained edge devices?
3) RQ-3 (Ablation): Does each proposed component contribute to overall performance?
4) RQ-4 (Sensitivity): How sensitive is the model to different parameter settings?

B. Dataset
In all, 14 publicly available real-world time-series datasets
are used, including six univariate and eight multivariate
datasets, as listed in Table I. These datasets span multiple
domains to ensure fair and unbiased evaluation.
1) Multivariate Datasets: MSL records the status of multiple
sensors on the Mars rover. GECCO contains drinking water
quality data from IoT sensors. SWAN provides temporal data
from solar photospheric vector magnetograms. PSM includes
25-D monitoring data from eBay server machines. SMAP
presents soil samples and telemetry data from Mars rovers.
SMD stores resource usage traces from 28 servers over five
weeks. SWAT collects 51-D sensor data from a public water
treatment system. WADI offers 127-D monitoring data from
an industrial control system.
2) Univariate datasets. ECG contains electrocardiogram
data with ventricular premature beats. MITDB includes 48
half-hour two-channel ECG recordings. SVDB consists of 78
half-hour ECG tracings with supraventricular arrhythmia. UCR
features natural sequences with single anomalies. UCR-AUG
provides augmented data based on the original UCR datasets.
Occupancy records the information of temperature, humidity,
light, and CO2 levels.
C. Baseline and Metric
1) Baseline: To validate the effectiveness of the LFTSAD,
16 representative state-of-the-art (SOTA) models are selected
as baselines, as listed in Table II. These baselines are selected
based on their network structure, scoring scheme, and use of
All-MLP architecture, where GDN, MAD-GAN (MGAN), and
CSTGL are customized for multivariate time series and cannot
be applied to univariate time series.
1) Network Structure: DCDet, PaAD, ATran, DTAAD,
USAD, TGFLOW (MTGF), CSTGL, GDN, MGAN,
OmniAnomaly (Omni), and NASA-LSTM (LSTM)
adopt deep structures with numerous parameters. In
contrast, IForest, FADSD, ADNEv, LTFAD, COUTA,
and LFTSAD (Ours) use shallow structures with few
parameters.
2) Scoring Scheme: LFTSAD, ATran, DCDet, and PaAD
use association discrepancy-based scoring schemes. The
other models rely on reconstruction error-based or prediction error-based scoring schemes.

CHEN et al.: LFTSAD VIA POINT-LEVEL AND SEQUENCE-LEVEL RECONSTRUCTION DISCREPANCY

17303

TABLE II
BASELINES

3) All-MLP Architecture: LFTSAD, PaAD, LTFAD, and
USAD are based on All-MLP architectures. Among
them, LFTSAD and LTFAD adopt shallow architectures,
whereas PaAD and USAD use deeper ones.
2) Metric: For comprehensive evaluation, eight widely
used metrics [2], [44], [45] are used: Accuracy (Acc), Precision (Pre), Recall (Rec), F1-pointwise (F1), Affiliation-F1
(F1Af ), F1-point-adjusted (F1PA ), VUS ROC (V ROC), and
VUS PR (V PR). All the metrics range from 0 to 1, with
higher values indicating better TSAD performance.
D. Experimental Environment
All the experiments are conducted on a Windows 11 system
with an Intel Core i7-10700KF CPU, NVIDIA GeForce RTX
3090 GPU (24-GB GPU-RAM), and 64-GB RAM. The LFTSAD model is implemented in Python using PyCharm and is
publicly available at here. Official Python implementations of
baseline models are obtained from the authors’ repositories,
as listed in Table II. The grid-search-based autotuning method
is used to find the optimal parameters for all the models.
E. RQ-1 (Accuracy)
To answer RQ-1, LFTSAD is evaluated against 16 baselines
on 14 datasets, including eight multivariate and six univariate
datasets, using eight evaluation metrics.
Tables III and IV present the detection accuracy of 17
models on 14 datasets. In two tables, bold text indicates the
best performance, while underlined text denotes the secondbest performance. From two tables, several findings can be
observed.
1) Overall Performance: LFTSAD, DTAAD, ADNev,
DCDet, FADSD, ATran, MGAN, LTFAD, and Omni
outperform other baselines. For example, on the MSL
dataset, LFTSAD achieves an Acc of 0.9907, Pre of
0.9509, and V ROC of 0.9300, while USAD scores
only 0.7299 for Acc, 0.7198 for Pre, and 0.6102
V ROC.

2) Stability: LFTSAD, ADNev, ATran, LTFAD, DCdet, and
DTAAD show the most stable performance across eight
metrics, followed by GDN, PaAD, FADSD, Omni, and
LSTM. For example, on the ECG and UCR datasets,
LFTSAD ranks first three times and second once.
3) Anomaly Scoring Scheme: Association discrepancybased models, such as LFTSAD, DCDet, AnomalyTrans, and PaAD, outperform others. For example, on
the SWAT and WADI datasets, DCdet and ATran surpass
DTAAD, CSTGL, and Omni.
4) Deep or Shallow Structures: Deep models generally
outperform shallow ones (COUTA, FADSD, IForest).
However, shallow models like LFTSAD, ADNev, and
LTFAD outperform several deep models. For example,
on the Occupancy dataset, F1PA scores are 0.9919 for
LFTSAD, 0.9877 for ADNEv, 0.8679 for PaAD, 0.9048
for DTAAD, and only 0.6811 for IForest.
5) All-MLP Architecture: LFTSAD and LTFAD are better
than PaAD and USAD.
6) In Summary: LTFSAD achieves top-two rankings in
more than one-half of the eight metrics, but its performance in traditional F1 scores is weaker. These
results highlight the effectiveness of the lightweight AllMLP architecture and reconstruction discrepancy-based
scoring.
F. RQ-2 (Deployability and Timeliness)
To address RQ-2, a PC and two resource-limited edge
devices are selected to deploy the 17 models and detect
anomalies on the MSL dataset. In edge devices, the Raspberry
Pi 4b has a 1.5-GHz ARM Cortex-A72 processor and 2-GB
RAM, while the Jetson Xavier NX is equipped with a six-core
Carmel ARMv8.2 processor with 8 GB of RAM.
1) Timeliness and Resource Consumption: Table V lists
the timeliness and resource consumption of the 17 models on
PC and two edge devices, where Ot indicates out-of-memory.
Several key observations are made:

17304

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

TABLE III
ACCURACY ON M ULTIVARIATE DATASETS

CHEN et al.: LFTSAD VIA POINT-LEVEL AND SEQUENCE-LEVEL RECONSTRUCTION DISCREPANCY

17305

TABLE IV
ACCURACY ON U NIVARIATE DATASETS

1) Model Parameters: IForest, FADSD, and LFTSAD have
the fewest and second-fewest parameters. Overall, shallow models require significantly fewer parameters than
deep models. For example, the number of parameters is
0 for IForest, 12.6 K for LFTSAD, 4741 K for ATran,
and 258.6 K for CSTGL.
2) Timeliness: Shallow models (LFTSAD, ADNEv,
LTFAD, FADSD, COUTA, IForest) show faster training
and testing times compared with deep models. On the
PC, with a batch size of 128, LFTSAD completes one
epoch in 26.5 s while DTAAD and DCdet take 148 and
271.8 s respectively.
3) Computing and Storage Consumption: Shallow models
consume significantly fewer CPU/GPU and RAM/GPURAM resources. For instance, on Jetson Xavier NX,

CPU usage is 38% for LFTSAD, compared with 53.8%
for CSTGL and 62.2% for GDN. On Raspberry Pi 4B (2
GB RAM), DCdet uses 402-MB RAM, while LFTSAD
uses only 185 MB.
2) Deployability: Fig. 7 shows the deployment results on
Raspberry Pi 4b, where all the models except PaAD are
successfully deployed. Lightweight and shallow models are
easier to deploy compared with deep models. Moreover, due to
frequent production process changes, deployed models must be
updated regularly. Lightweight models like IForest, FADSD,
and LFTSAD can be updated directly on edge devices with
minimal data and communication overhead.
3) Summary: Thanks to its lightweight All-MLP architecture with four parallel two-layer MLPs, LFTSAD runs
efficiently and stably on resource-constrained edge devices.

17306

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

TABLE V
T IMELINESS AND R ESOURCE C ONSUMPTION A NALYSIS

TABLE VI
E FFECTIVENESS OF T HREE A BLATION E XPERIMENTS

Fig. 7. Deployment results on Raspberry Pi 4b.

G. RQ-3 (Ablation)
To answer RQ-3, three ablation experiments are conducted.
Specifically, two univariate datasets (ECG and MITDB), three
multivariate datasets (MSL, PSM, and SWAN), and three
metrics (Pre, Rec, and F1PA ) are chosen for this experiment.
1) Point-Level and Sequence-Level Learning: These two
components are essential to LFTSAD, complementing each
other to improve detection accuracy. In this experiment,
three configurations are compared: 1) only point-level learning; 2) only sequence-level learning; and 3) point-level and

sequence-level joint learning. Table. VI(a) presents the detection performance of the three configurations.
1) Overall Performance: Joint learning consistently outperforms individual configurations across all the metrics
and datasets. For example, on the MSL dataset, F1PA
is 0.9321 for point level, 0.9480 for sequence level, and
0.9721 for joint learning.
2) Comparison of Individual Configurations: Each configuration shows advantages on different datasets and
metrics. For instance, point-level learning achieves better

CHEN et al.: LFTSAD VIA POINT-LEVEL AND SEQUENCE-LEVEL RECONSTRUCTION DISCREPANCY

17307

Fig. 8. Detection results for explicit and implicit outliers. (a) Explicit outlier in the univariate dataset UCR (2180–2280). (b) Implicit outlier in the first
variable of MSL dataset MSL (62450–62560). (c) Mixed outlier in the univariate dataset UCR AUG (1600–2600).

Pre and F1PA on MITDB, while sequence-level learning
performs better on MSL. This implies that the two
configurations complement each other.
To further evaluate these two components, an explicit outlier
from UCR, an implicit outlier from the first variable of MSL,
and a mixed outlier from UCR AUG are extracted. Fig. 8
shows plots of the detection results of these two components
on the three outliers. It is clear that point-level learning performs better in detecting explicit outliers, while sequence-level
learning is more effective for implicit outliers. For example,
on the explicit outlier in UCR, point-level learning accurately
identifies the entire outlier but misclassifies a normal timestamp. In contrast, sequence-level learning partially detects
the outlier while avoiding false positives. In summary, these
results demonstrate that point-level and sequence-level joint
learning enhances anomaly detection accuracy by leveraging
their complementary strengths.
2) Reconstruction Discrepancy-Based Anomaly Scoring:
This is another key component of LFTSAD. In this experiment, it is compared with two alternatives: the average
reconstruction error-based scheme and the maximum reconstruction error-based scheme. Table. VI(b) illustrates the
effectiveness of the three scoring schemes.
1) Overall Performance: The reconstruction discrepancybased scheme outperforms both the alternatives. It
achieves the highest scores across all the metrics and
datasets, with an average improvement of 6.51%.
2) Comparison of Alternatives: The maximum error-based
scheme yields better Pre on ECG, MITDB, and MSL,
while the average scheme achieves higher Rec and F1PA
on MSL and SWAN.
3) In Summary: reconstruction error-based scoring is less
effective in a two-layer All-MLP architecture, as shallow
MLPs struggle to achieve accurate reconstruction.
3) Lightweight All-MLP Architecture: LFTSAD uses four
parallel two-layer MLPs to construct a lightweight All-MLP
architecture. This design ensures high timeliness and low
resource consumption. To validate its effectiveness, two comparison schemes are designed by replacing the two-layer MLPs
with two-layer RNNs and two-layer CNNs. Table. VI(c) lists
the detection performance of three schemes.
1) Overall Performance: The two-layer MLP architecture
consistently outperforms the other two. For instance, on
MITDB, it achieves a Rec score of 1, compared with
0.8982 for the two-layer CNN and 0.5665 for the twolayer RNN.
2) Stability: The two-layer MLP architecture performs better across all the five datasets and three metrics.
3) In Summary: Within a shallow architecture, the MLP
network demonstrates higher efficiency than both the
RNNs and CNNs. This observation suggests that RNNs

and CNNs require deeper structures and more parameters to fully exploit their capabilities.
H. RQ-5 (Sensitivity)
To address RQ-5, two key parameters are evaluated.
1) Parameter α: The parameter α, ranging from [0,1],
balances point-level and sequence-level anomaly scores to
generate the final score. When α = 1, only the point-level
score is used; when α = 0, only the sequence-level score
is applied. Fig. 9(a) shows plots of performance changes
across five datasets under α parameters. In the figure, green
lines represent univariate datasets, and red lines represent
multivariate datasets.
1) Focusing on Univariate Datasets: All the green lines
(univariate datasets) gradually increase at first, and then
drop sharply. Their performance is relatively stable
within [0, 0.4].
2) Considering Multivariate Datasets: All the red lines rise
rapidly first and then remain stable. Their performance
is relatively stable within [0.7, 1.0].
3) In Summary: The stable intervals for parameter α are [0,
0.4] for univariate datasets and [0.7, 1.0] for multivariate
datasets. This finding suggests that point-level learning
is more effective for univariate datasets, while sequencelevel learning performs better on multivariate datasets.
In univariate data, outliers typically deviate clearly from
normal values, favoring point-level learning. In contrast,
multivariate outliers often span multiple dimensions,
making sequence-level learning more suitable.
2) Number of MLP Layers: It is another important parameter influencing timeliness and resource consumption of
LFTSAD. Fewer layers result in a lighter model with fewer
parameters, lower resource usage, and higher timeliness, but
reduced representation capability. More layers improve representation but increase parameter count, resource consumption,
and reduce timeliness. Fig. 9(b) displays how performance
varies with different MLP layers. In the figure, performance
improves initially, and then declines sharply as layers increase.
The best results are achieved with two layers across all the
datasets and metrics. Therefore, a two-layer MLP is optimal
for the lightweight LFTSAD, as deeper networks increase
overfitting risk and require higher dropout rates, while shallower ones limit learning capacity.
I. Discussion
This article focuses on high-speed, low-consumption, and
high-accuracy timestamp-level anomaly detection on resourcelimited edge devices. Extensive experiments demonstrate that
the LFTSAD model successfully achieves all the three objectives.

17308

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 9, SEPTEMBER 2025

Fig. 9. Sensitivity analysis. (a) Parameter α. (b) Layer of MLP.

1) High Speed: Timeliness and deployability experiments
show that LFTSAD requires significantly less detection time compared with deep TSAD models. Roughly
speaking, LFTSAD is 3–10 times faster than other deep
models. This advantage stems from the LFTSAD model
being lightweight, with a shallow structure and few
parameters, using only four parallel two-layer MLPs.
In addition, the parallel learning process across M variables and two branches further enhances the speed of
LFTSAD.
2) Low Resource Consumption: Attributed to its shallow
and lightweight All-MLP architecture, LFTSAD exhibits
significantly lower resource consumption compared with
other deep models. Specifically, LFTSAD has only 126
K parameters, which is 1/10–1/50 of the parameter count
of other deep models. On the Raspberry Pi 4b, the
CPU usage of LFTSAD is only half that of other deep
models. This efficiency allows LFTSAD to be deployed
on resource-constrained devices like the Raspberry Pi
4b, which has only 2G of RAM.
3) High Accuracy: Accuracy and ablation experiments
show that LFTSAD ranked first or second in over half
of the eight metrics across most datasets. For example, LFTSAD ranked in the top two on seven metrics
for the UCR and UCR-AUG datasets and six metrics
for the MSL dataset. These results can be attributed
to the accuracy-enhancing strategies: “point-level and
sequence-level contrastive reconstruction learning” and
“reconstruction discrepancy-based anomaly scoring.”
VI. C ONCLUSION
This article addresses the challenge of real-time, efficient
anomaly detection in resource-constrained edge environments
by the proposed LFTSAD—an unsupervised, lightweight, AllMLP-based anomaly detection model. Unlike traditional deep
neural networks with large parameters, LFTSAD uses only
four parallelizable two-layer MLP networks, offering a shallow architecture with few parameters. This design ensures

high timeliness and low resource consumption, making it
well-suited for deployment on resource-limited edge devices.
In addition, LFTSAD integrates point-level and sequencelevel perspectives to design a reconstruction discrepancy-based
anomaly scoring scheme for accurate anomaly detection.
Comparative evaluations on 14 real-world datasets and two
edge platforms (Raspberry Pi 4b and Jetson Xavier NX)
demonstrate its superiority. Specifically, LFTSAD operates
3–10 times faster than deep-learning-based SOTA models on
Raspberry Pi 4b. Accuracy results further confirm its effectiveness, with LFTSAD ranking first or second in more than
six metrics across the UCR, UCR AUG, and MSL datasets.
However, the proposed LTFSAD method still has several limitations. First, the performance of LTFSAD shows
sensitivity to the parameter α on certain datasets. Second,
spatial correlations between variables are not explicitly considered in the current model. Third, LFTSAD currently lacks
the capability for online updates and federated distributed
deployment. To overcome these limitations, future work will
focus on three directions. 1) developing a more robust and
accurate All-MLP-based model by integrating time-frequency
learning and applying pruning or quantization techniques; 2)
designing a spatiotemporal joint learning framework based
on the All-MLP architecture to capture both the temporal
and spatial dependencies; and 3) building a real-time, online
anomaly detection system that supports federated deployment
on resource-constrained edge devices.
R EFERENCES
[1]

G. Li and J. J. Jung, “Deep learning for anomaly detection in multivariate
time series: Approaches, applications, and challenges,” Inf. Fusion,
vol. 91, pp. 93–102, Mar. 2023.
[2] A. Garg, W. Zhang, J. Samaran, R. Savitha, and C.-S. Foo, “An evaluation of anomaly detection and diagnosis in multivariate time series,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 6, pp. 2508–2517,
Jun. 2022.
[3] G. Li, Z. Yu, K. Yang, M. Lin, and C. L. Philip Chen, “Exploring
feature selection with limited labels: A comprehensive survey of semisupervised and unsupervised approaches,” IEEE Trans. Knowl. Data
Eng., vol. 36, no. 11, pp. 6124–6144, Nov. 2024.
[4] S.-E. Benkabou, K. Benabdeslem, V. Kraus, K. Bourhis, and B. Canitia,
“Local anomaly detection for multivariate time series by temporal
dependency based on Poisson model,” IEEE Trans. Neural Netw. Learn.
Syst., vol. 33, no. 11, pp. 6701–6711, Nov. 2022.
[5] Z. Zamanzadeh Darban, G. I. Webb, S. Pan, C. Aggarwal, and M. Salehi,
“Deep learning for time series anomaly detection: A survey,” ACM
Comput. Surv., vol. 57, no. 1, pp. 1–42, Oct. 2024.
[6] Z. Zhong, Z. Yu, Z. Fan, C. L. P. Chen, and K. Yang, “Adaptive memory
broad learning system for unsupervised time series anomaly detection,”
IEEE Trans. Neural Netw. Learn. Syst., early access, Jun. 26, 2024, doi:
10.1109/TNNLS.2024.3415621.
[7] W. Deng, J. Feng, and H. Zhao, “Autonomous path planning via sand
cat swarm optimization with multi-strategy mechanism for unmanned
aerial vehicles in dynamic environment,” IEEE Internet Things J., early
access, Feb. 20, 2025, doi: 10.1109/JIOT.2025.3542587.
[8] D. Guo, Z. Zhang, B. Yang, J. Zhang, H. Yang, and Y. Lin, “Integrating
spoken instructions into flight trajectory prediction to optimize automation in air traffic control,” Nature Commun., vol. 15, no. 1, p. 9662,
Nov. 2024.
[9] T. Ergen and S. S. Kozat, “Unsupervised anomaly detection with LSTM
neural networks,” IEEE Trans. Neural Netw. Learn. Syst., vol. 31, no. 8,
pp. 3127–3141, Aug. 2020.
[10] Y. Zhang, Y. Chen, J. Wang, and Z. Pan, “Unsupervised deep anomaly
detection for multi-sensor time-series signals,” IEEE Trans. Knowl. Data
Eng., vol. 35, no. 2, pp. 2118–2132, Feb. 2023.
[11] F. Li, J. Chen, L. Zhou, and P. Kujala, “Investigation of ice wedge
bearing capacity based on an anisotropic beam analogy,” Ocean Eng.,
vol. 302, Jun. 2024, Art. no. 117611.

CHEN et al.: LFTSAD VIA POINT-LEVEL AND SEQUENCE-LEVEL RECONSTRUCTION DISCREPANCY

[12] W. Li et al., “Fault diagnosis using variational autoencoder GAN and
focal loss CNN under unbalanced data,” Struct. Health Monitor., vol. 24,
no. 3, Jul. 2024, Art. no. 14759217241254121.
[13] M. Li, J. Li, Y. Chen, and B. Hu, “Stress severity detection in
college students using emotional pulse signals and deep learning,”
IEEE Trans. Affect. Comput., early access, Mar. 4, 2025, doi: 10.1109/
TAFFC.2025.3547753.
[14] H. Chen, Y. Sun, X. Li, B. Zheng, and T. Chen, “Dual-scale complementary spatial–spectral joint model for hyperspectral image classification,”
IEEE J. Sel. Topics Appl. Earth Observ. Remote Sens., vol. 18,
pp. 6772–6789, 2025.
[15] N. Bai, X. Wang, R. Han, Q. Wang, and Z. Liu, “PAFormer: Anomaly
detection of time series with parallel-attention transformer,” IEEE Trans.
Neural Netw. Learn. Syst., vol. 36, no. 2, pp. 3315–3328, Feb. 2025.
[16] R. Xu, H. Miao, S. Wang, P. S. Yu, and J. Wang, “PeFAD: A parameterefficient federated framework for time series anomaly detection,” in
Proc. 30th ACM SIGKDD Conf. Knowl. Discovery Data Mining, Aug.
2024, pp. 3621–3632.
[17] M. Pietroń, D. Żurek, K. Faber, and R. Corizzo, “Towards efficient deep
autoencoders for multivariate time series anomaly detection,” in Proc.
Int. Conf. Comput. Sci., Jan. 2024, pp. 461–469.
[18] M. Pietroń, D. Żurek, K. Faber, A. Wójcik, and R. Corizzo, “AD-NEv+–
–The multi-architecture neuroevolution-based multivariate anomaly
detection framework,” in Proc. Genetic Evol. Comput. Conf. Companion,
Jul. 2024, pp. 607–610.
[19] Z. Zhong, Z. Yu, Y. Yang, W. Wang, and K. Yang, “PatchAD: A
lightweight patch-based MLP-mixer for time series anomaly detection,”
2024, arXiv:2401.09793.
[20] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,”
in Proc. 26th ACM SIGKDD Int. Conf. Knowl. Disc. Data Min., 2020,
pp. 3395–3404.
[21] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer: Time
series anomaly detection with association discrepancy,” in Proc. Int.
Conf. Learn. Represent. (ICLR), Jan. 2021, pp. 1–20.
[22] Y. Yang, C. Zhang, T. Zhou, Q. Wen, and L. Sun, “DCdetector: Dual
attention contrastive representation learning for time series anomaly
detection,” in Proc. 29th ACM SIGKDD Int. Conf. Knowl. Discovery
Data Mining (KDD), 2023, pp. 3033–3045.
[23] Y. Nam et al., “Breaking the time-frequency granularity discrepancy in
time-series anomaly detection,” in Proc. ACM Web Conf., May 2024,
pp. 4204–4215.
[24] W. Xiong, P. Wang, X. Sun, and J. Wang, “SiET: Spatial information
enhanced transformer for multivariate time series anomaly detection,”
Knowl.-Based Syst., vol. 296, Jul. 2024, Art. no. 111928.
[25] J. Zhong et al., “A masked attention network with query sparsity
measurement for time series anomaly detection,” in Proc. IEEE Int.
Conf. Multimedia Expo (ICME), Jul. 2023, pp. 2741–2746.
[26] G. Sivapalan, K. K. Nundy, S. Dev, B. Cardiff, and D. John, “ANNet:
A lightweight neural network for ECG anomaly detection in IoT edge
sensors,” IEEE Trans. Biomed. Circuits Syst., vol. 16, no. 1, pp. 24–35,
Feb. 2022.
[27] T. Zhou et al., “FiLM: Frequency improved legendre memory model for
long-term time series forecasting,” in Proc. Adv. Neural Inf. Process.
Syst., Jan. 2022, pp. 12677–12690.
[28] Z. Zhang, J. Wang, Y. Xia, D. Wei, and Y. Niu, “Solar-mixer: An efficient
end-to-end model for long-sequence photovoltaic power generation
time series forecasting,” IEEE Trans. Sustain. Energy, vol. 14, no. 4,
pp. 1979–1991, Apr. 2023.
[29] K. Yi et al., “Frequency-domain MLPs are more effective learners in
time series forecasting,” in Proc. Adv. Neural Inf. Process. Syst., Jan.
2023, pp. 76656–76679.
[30] Y. Qin, H. Luo, F. Zhao, Y. Fang, X. Tao, and C. Wang, “Spatio-temporal
hierarchical MLP network for traffic forecasting,” Inf. Sci., vol. 632,
pp. 543–554, Jun. 2023.
[31] Z. Xu, A. Zeng, and Q. Xu, “FITS: Modeling time series with 10k
parameters,” in Proc. 12th Int. Conf. Learn. Represent., Jan. 2023,
pp. 1–24.
[32] L. Chen et al., “Frequency-domain spectrum discrepancy-based fast
anomaly detection for IIoT sensor time-series signals,” IEEE Trans.
Instrum. Meas., vol. 74, pp. 1–16, 2025.
[33] L. Chen, X. Cao, T. He, Y. Xu, X. Liu, and B. Hu, “A lightweight allMLP time–frequency anomaly detection for IIoT time series,” Neural
Netw., vol. 187, Jul. 2025, Art. no. 107400.
[34] L.-R. Yu, Q.-H. Lu, and Y. Xue, “DTAAD: Dual TCN-attention networks
for anomaly detection in multivariate time series data,” Knowl.-Based
Syst., vol. 295, Jul. 2024, Art. no. 111849.

17309

[35] M. Pietroń, D. Żurek, K. Faber, and R. Corizzo, “AD-NEv: A scalable multilevel neuroevolution framework for multivariate anomaly
detection,” IEEE Trans. Neural Netw. Learn. Syst., early access, Aug.
14, 2024, doi: 10.1109/TNNLS.2024.3439404.
[36] Y. Zheng et al., “Correlation-aware spatial–temporal graph learning
for multivariate time-series anomaly detection,” IEEE Trans.
Neural Netw. Learn. Syst., vol. 35, no. 9, pp. 11802–11816,
Sep. 2024.
[37] H. Xu, Y. Wang, S. Jian, Q. Liao, Y. Wang, and G. Pang, “Calibrated
one-class classification for unsupervised time series anomaly detection,”
IEEE Trans. Knowl. Data Eng., vol. 36, no. 11, pp. 5723–5736, Nov.
2024.
[38] Q. Zhou, J. Chen, H. Liu, S. He, and W. Meng, “Detecting multivariate
time series anomalies with zero known label,” in Proc. AAAI Conf. Artif.
Intell., Jun. 2023, vol. 37, no. 4, pp. 4963–4971.
[39] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. AAAI Conf. Artif. Intell. (AAAI),
May 2021, pp. 4027–4035.
[40] D. Li, D. Chen, B. Jin, L. Shi, J. Goh, and S.-K. Ng, “MAD-GAN:
Multivariate anomaly detection for time series data with generative
adversarial networks,” in Proc. Int. Conf. Artif. Neural Netw. (ICANN),
2019, pp. 703–716.
[41] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Disc. Data
Min., 2019, pp. 2828–2837.
[42] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and
T. Söderström, “Detecting spacecraft anomalies using LSTMs
and nonparametric dynamic thresholding,” in Proc. 24th
ACM SIGKDD Int. Conf. Knowl. Disc. Data Min., 2018,
pp. 387–395.
[43] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation forest,” in Proc. 8th
IEEE Int. Conf. Data Min., Dec. 2008, pp. 413–422.
[44] J. Paparrizos, P. Boniol, T. Palpanas, R. S. Tsay, A. Elmore, and
M. J. Franklin, “Volume under the surface: A new accuracy evaluation
measure for time-series anomaly detection,” Proc. VLDB Endowment,
vol. 15, no. 11, pp. 2774–2787, Jul. 2022.
[45] S. Kim, K. Choi, H.-S. Choi, B. Lee, and S. Yoon, “Towards a rigorous
evaluation of time-series anomaly detection,” in Proc. AAAI Conf. Artif.
Intell., Jan. 2021, pp. 7194–7201.
Lei Chen (Member, IEEE) received the M.Sc.
degree in computer science and engineering and
the Ph.D. degree in automatic control and electrical engineering from Hunan University, Changsha,
China, in 2012 and 2017, respectively.
He is currently an Associate Professor with the
School of Information and Electrical Engineering, Hunan University of Science and Technology,
Xiangtan, China. His current research interests
include anomaly detection, lightweight design, time
series analysis, deep learning, and big data analysis.

Jiajun Tang received the B.Eng. degree in automation from Hunan Institute of Science and Technology, Yueyang, China, in 2023. He is currently
pursuing the master’s degree in control science and
engineering with Hunan University of Science and
Technology, Xiangtan, China.
His current research interests include data-driven
anomaly detection, deep learning, and fault diagnosis.

Ying Zou, photograph and biography not available at the time of publication.
Xuxin Liu, photograph and biography not available at the time of publication.
Xingquan Xie, photograph and biography not available at the time of
publication.
Guangyang Deng, photograph and biography not available at the time of
publication.
PAPER_TEXT
