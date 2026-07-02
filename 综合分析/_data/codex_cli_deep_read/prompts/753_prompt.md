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
# [753] Multimodal Anomaly Detection for Microservice Systems via Grassmann Manifolds-Based Graph Fusion
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
编号：753
题名：Multimodal Anomaly Detection for Microservice Systems via Grassmann Manifolds-Based Graph Fusion
年份：2026
DOI：10.1109/tsc.2026.3665382
来源：IEEE Transactions on Services Computing
PDF：paper/10.1109_TSC.2026.3665382.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：入侵检测与网络异常检测、图学习、知识图谱与威胁情报
相关性：中相关，分数 5
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\753.txt
- 原始字符数：70607
- 本次发送字符数：70607
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
1422

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 19, NO. 2, MARCH/APRIL 2026

Multimodal Anomaly Detection for Microservice
Systems via Grassmann Manifolds-Based
Graph Fusion
Shiming He , Keyao Feng, Kaixuan Meng, Kun Xie , Member, IEEE, and Xibin Zhao , Senior Member, IEEE

Abstract—Microservice architecture decomposes complex applications into multiple small, independent services, enabling independent deployment and scaling. However, microservice systems introduce complex and dynamic interactions between service instances.
When a service instance fails, it can significantly degrade the performance of the entire system, harm the user experience, and cause
substantial economic losses. Therefore, effective anomaly detection
for service instances is crucial to ensure system reliability. Metrics,
logs, and traces provide complementary insights into microservice
operations, and recent approaches have attempted to jointly exploit
these modalities for anomaly detection. However, the varying data
volumes per interval and heterogeneous data types across modalities, combined with the complex and elusive relationships between
them, make effective representation and learning challenging. To
address these limitations, we propose MGFusion, an unsupervised,
end-to-end multimodal anomaly detection method for microservice
systems using Grassmann manifolds-based graph fusion. MGFusion employs a robust method to unify metrics, logs, and traces
into time series, enabling consistent processing across modalities.
It leverages multiple graph structure learning (GSL) techniques to
explore multi-view relationships between the modalities. To mitigate the impact of data noise, we further introduce prior knowledge
based on the Adamic-Adar Index (AAI) and employ a Grassmann manifolds-based graph fusion method to combine multiple
basic graph structures. Finally, anomaly detection is achieved using Diffusion Convolutional Recurrent Neural Network (DCRNN)
predictors and anomaly score calculation. Extensive experiments
on a public dataset demonstrate that MGFusion effectively fuses
multimodal data and captures complex relationships, significantly
improving the accuracy and efficiency of anomaly detection. Compared to the state-of-the-art unsupervised multimodal anomaly

Received 30 June 2025; revised 11 December 2025; accepted 11 February
2026. Date of publication 16 February 2026; date of current version 10 April
2026. This work was supported in part by the National Natural Science Foundation of China under Grant 62025201, Grant 62272062, and Grant 62321166652,
in part by the Science and Technology Innovation Program of Hunan Province
under Grant 2023RC3139, in part by the Natural Science Foundation of Hunan
Province under Grant 2025JJ50373 and Grant 2024JJ3014, and in part by the
Research Foundation of Education Bureau of Hunan Province under Grant
25A0188. (Corresponding author: Kun Xie.)
Shiming He, Keyao Feng, and Kaixuan Meng are with the School of Computer Science and Technology, Hunan Provincial Key Laboratory of Intelligent
Processing of Big Data on Transportation, Changsha University of Science
and Technology, Changsha 410114, China (e-mail: smhe_cs@csust.edu.cn;
kyfeng@stu.csust.edu.cn; kaixuan@stu.csust.edu.cn).
Kun Xie is with the College of Computer Science and Electronics Engineering,
Ministry of Education Key Laboratory of “Fusion Computing of Supercomputing and Artificial Intelligence”, Hunan University, Changsha 410082, China
(e-mail: xiekun@hnu.edu.cn).
Xibin Zhao is with the School of Software, Tsinghua University, Beijing
100084, China (e-mail: zxb@tsinghua.edu.cn).
Digital Object Identifier 10.1109/TSC.2026.3665382

detection method, AnoFusion, MGFusion achieves an improvement
in the F1 score ranging from 11.1% to 15.3%.
Index Terms—Anomaly detection, multimodal data, graph
structure learning, graph fusion, grassmann manifolds.

I. INTRODUCTION
ICROSERVICE architecture has emerged as the dominant paradigm in modern software system design due to
its modularity, scalability, and ease of maintenance. By decomposing complex applications into small, independently deployable services, the microservice architecture enhances system
flexibility and maintainability. Instances (e.g., virtual machines
or containers) serve as operational entities of these services.
Microservice systems involve intricate and dynamic interactions among instances, including service invocations and resource competition [1], [2]. Anomalies in instances significantly
degrade system performance, adversely impacting user experience, and causing potential economic losses. Instance anomaly
detection, which identifies Anomalies or abnormal behaviors of
microservice instances by analyzing monitoring data, is essential
to ensure service reliability [3].
Microservice systems collect three primary types of status
data [4]: metrics, logs, and traces, as illustrated in Fig. 1. Metrics
are quantitative measures of system performance, typically presented as time series. Logs are semi-structured data generated
by “printf” statements or logging frameworks, recording key
system events [5]. Traces capture complete invocation chains
between services, with each invocation represented as a “span”
[6].
Fig. 1 shows an example of these data types. Metrics include
CPU usage rate, memory usage, and throughput, etc. Logs
contain timestamped entries with levels (e.g., ERROR) and
messages (e.g., “Try to get service’s inst, retry for 1 time... ”).
Traces include service caller, callee, timestamp, response time
(RT), and status codes. For instance, at timestamp 1625104624
(2021-07-01 09:57:04), the RT from service S3 to S4 is 10
seconds, with a status code of 200 (success). At timestamp
1625104625, the RT from S2 to S4 is 15 seconds, but the
status code is 500 (server error). These multimodal data offer
complementary insights into the system’s status, making them
invaluable for anomaly detection.
While single-modal anomaly detection methods [7], [8],
[9], [10] have achieved some success, they are inherently
limited. Anomalies often manifest differently across modalities,
as shown in Table I. For example, CPU contention is detectable
via metrics but not logs or traces. Conversely, code logic errors

M

1939-1374 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

HE et al.: MULTIMODAL ANOMALY DETECTION FOR MICROSERVICE SYSTEMS VIA GRASSMANN MANIFOLDS-BASED GRAPH FUSION

1423

TABLE I
MULTIMODAL DATA ABNORMAL MODES FOR DIFFERENT ANOMALIES (‘−’ INDICATES NO DETECTABLE ABNORMALITY)

Fig. 1. Multimodal status data. The metrics fail to capture anomalous behaviors in this case because the example represents a configuration error, as shown
in Table I. Such anomalies are exclusively reflected in logs and traces, rather
than in metrics.

Fig. 2. Key processes of early fusion-based multimodal anomaly detection,
with the unified conversion into time series as an example.

are reflected in logs and traces but not metrics. No single-modal
data can cover all anomaly types. Thus, multimodal analysis is
essential for comprehensive and accurate anomaly detection.
Data fusion is at the core of multimodal anomaly detection.
Based on the fusion stage, existing methods fall into three categories: late fusion, early fusion, and intermediate fusion [11].
Late fusion [12], [13], [14] combines independent detection
results from each modality using voting or weighting. Early
fusion [15], [16], [17], [18], [19], [20] converts multimodal
data into a unified format, while intermediate fusion [21], [22],
[23], [24] extracts features independently for each modality and
combines them.
Early fusion has gained prominence due to its ability to
capture inter-modal interactions early in the processing pipeline.
The core steps in early fusion-based multimodal anomaly detection consist of unified modality conversion, relationship learning, and graph-based anomaly detection. To illustrate this process, we take the conversion of data into a unified time series
format as an example, as illustrated in Fig. 2. In this approach,
multimodal data are transformed into time series and relationships between time series are modeled for anomaly detection

using Graph Neural Networks (GNNs). However, early fusion
faces several challenges:
r Inconsistent Data Volume and Type in Time Series Conversion: Conversion should align multimodal data to a unified
time interval. Multiple records may appear in a single
interval, and the data volume per interval and data type
often varies across modalities. While continuous data can
be averaged, event-based data (e.g., logs or traces) require
more nuanced handling to preserve semantic integrity.
Naive averaging of discrete data, such as status codes, can
lead to meaningless results. For example, for spans T1 and
T2 in the same interval (such as one minute), a status code
average of 350 (redirection) from 200 (success) and 500
(server error) is meaningless. Some works [19], [20] ignore
them directly, and some works [18] retain only the value of
the first span, discarding critical information (500 server
error).
r Noise in Raw Data Adversely Affects Relationship Learning: Accurate modeling of inter-time series dependencies forms the foundation of graph-based anomaly detection. Current approaches typically mine these relationships
guided by raw data. Noise in raw data, which includes
errors, interference, or loss that may occur during the
processes of data collection, transmission, and storage, can
mislead relationship learning and degrade the performance
of graph-based anomaly detection models.
r Limitations of Existing Relationship Learning Methods:
Current methods often fail to capture complex, multiview dependencies across modalities. For example, mutual information-based methods [18] can handle linear
correlations but struggle with nonlinear or hierarchical
dependencies. Graph structure learning (GSL) in singlemodal anomaly detection learns relationships among homogeneous nodes (e.g., metrics) but cannot generalize to
heterogeneous node types (e.g., cross-modal interactions)
directly.
To address these challenges, we propose MGFusion, a multimodal anomaly detection framework for microservice systems
based on Grassmann manifolds and graph structure learning.
The key innovations of MGFusion include:
r Robust Time Series Conversion: MGFusion statistically
aggregates continuous data, and employs frequency encoding to convert discrete data while preserving critical
information, addressing inconsistencies in data type.
r Noise-Resilient Relationship Learning: MGFusion leverages the Adamic-Adar Index similarity metric [25] to
guide relationship learning, reducing the impact of noise
by emphasizing meaningful node similarities.
r Grassmann Manifolds-Based Graph Fusion: MGFusion
learns multiple basic graph structures using different graph
structure learning methods and combines them via Grassmann manifolds-based fusion to preserve unique structural

1424

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 19, NO. 2, MARCH/APRIL 2026

properties and model complex and multi-view interdependencies.
Experimental results on public datasets demonstrate that
MGFusion outperforms nine state-of-the-art single-modal and
multimodal anomaly detection methods. For example, MGFusion improves the F1 score by 11.1% to 15.3% compared to
AnoFusion.
The remainder of this paper is organized as follows. Section II
reviews related work. Sections III to VII detail the MGFusion
framework and its components. Section VIII evaluates the proposed method and Section IX concludes the paper.
II. RELATED WORK
In this section, we summarize the related work on singlemodal and multimodal anomaly detection, highlighting key
methods, and their limitations.
A. Single-Modal Anomaly Detection
Single-modal anomaly detection focuses on analyzing individual data modalities such as metrics, logs, or traces to identify
anomalies. Each modality provides unique insight but is inherently limited in its ability to cover all possible anomaly types.
1) Metric-Based Anomaly Detection: Metrics, typically represented as time series, exhibit both intra-time series (within
individual metrics) and inter-time series (between different metrics) relationships. To effectively capture these relationships,
graph-based methods [26], [27] have been widely adopted. GSL
learns an optimal graph structure jointly with the downstream
anomaly detection task. GDN (Graph Deviation Network) [28]
is a pioneering GSL-based method that learns graph structures
using learnable node embeddings. Subsequent works, such as
FuSAGNet [29], GTA [30], and FuGLAD [31], extend this idea
by introducing sparse or multiple graph structures for better
anomaly detection performance.
2) Log-Based Anomaly Detection: Log anomaly detection
primarily employs sequence-learning models like Long ShortTerm Memory (LSTM) networks or Transformers. These models learn normal sequence patterns and predict the next log
template in an unsupervised manner. If the actual template is not
among the top k predictions, it is flagged as an anomaly. Representative methods include: DeepLog [9], LogAnomaly [32],
and Logsy [33]. Supervised or semi-supervised methods, such
as LogRobust [34] and NeuralLog [35], learn to distinguish between normal and abnormal sequences. LogBP-LoRA [36] combines pre-trained models with parameter-efficient fine-tuning
(LoRA) to enhance detection efficiency.
3) Trace-Based Anomaly Detection: Trace anomaly detection captures patterns in invocation chains or key performance
indicators (KPIs) of system traces. TraceAnomaly [37] represents each trace’s response time and invocation path as feature
vectors. TraceStream [38] uses tree-based dynamic tracking vectors to extract both structural and temporal features. CRISP [6]
constructs key paths in a top-down and bottom-up manner to
identify services impacted by end-to-end delays.
While effective in specific cases, single-modal anomaly detection methods are limited by their reliance on one type of data,
making them unable to detect all anomaly types.
B. Multimodal Anomaly Detection
Multimodal anomaly detection leverages the complementary
strengths of metrics, logs, and traces to improve detection

accuracy. Based on the stage of data fusion, multimodal methods
are categorized into late fusion, early fusion, and intermediate
fusion, as shown in Fig. 3.
1) Late Fusion: Late fusion was among the earliest approaches in multimodal anomaly detection. In this approach,
each modality is processed independently and the results
are combined using voting or weighting. PDiagnose [12],
MADMM [13], and MicroCBR [14] follow this approach. However, late fusion methods fail to model the interactions and
relationships between different modalities, limiting their ability
to capture complex cross-modal dependencies.
2) Early Fusion: Early fusion combines multimodal data at
the preprocessing stage by converting them into a unified format,
such as events or time series.
r Events: DeepTraLog [15] represents traces and logs as
invocation chain events. DiagFusion [16] constructs an
event dependency graph using embedding and data augmentation for anomaly classification. Nezha [17] builds
an event graph to locate anomalies, providing a graphical
explanation of root causes.
r Time Series: AnoFusion [18] converts multimodal data
into multivariate time series and constructs a multimodal
graph using mutual information to generate six adjacency
matrices for different modalities. MSTGAD [19] builds
a microservice graph from traces after converting multimodal data into time series. MRCA [20] uses variational
autoencoders (VAE) to learn normal patterns from multimodal data converted into time series.
In summary, events-based approaches are better suited for
root cause analysis due to their discrete nature, while time
series-based approaches are more effective for anomaly detection as they preserve temporal ordering. This ordering enables
the identification of evolving patterns and deviations over time.
Therefore, our method employs early fusion, converting multimodal data into time series for anomaly detection.
3) Intermediate Fusion: Intermediate fusion combines features extracted independently from different modalities.
SCWarn [21] uses LSTM to learn the temporal dependencies
in multimodal data. UAC-AD [22] combines modality-specific
features in a shared space. Hades [39] employs dual attention
layers to extract both cross-modal interactions and intra-modal
dependencies. Eadro [24] utilizes Hawkes processes and dilated causal convolution (DCC) layers to integrate multimodal
features. SIADA [23] fuses multimodal features using contextaware multigraph representation and recurrent encoders.
III. PROBLEM DEFINITION AND SOLUTION OVERVIEW
This section formally defines the problem of multimodal
anomaly detection in microservice instances, provides the solution formulation, and presents an overview of our proposed
approach.
A. Problem Definition
The goal of multimodal instance anomaly detection is to
identify abnormal behaviors at specific timestamps by analyzing
multimodal status data collected from a microservice instance.
Unlike methods that focus on anomaly detection across multiple
service instances, our approach is specifically tailored to detect
anomalies within a single instance at precise moments in time.
We assume that all collected status data for a given instance
are time-synchronized. Metrics are collected at regular intervals.

HE et al.: MULTIMODAL ANOMALY DETECTION FOR MICROSERVICE SYSTEMS VIA GRASSMANN MANIFOLDS-BASED GRAPH FUSION

Fig. 3.

1425

Multimodal Fusion Strategies: (a) Late Fusion, (b) Early Fusion, (c) Intermediate Fusion.

Logs are generated as event-triggered messages. Traces are
recorded when user requests invoke service interactions.
The multimodal data collected over N time intervals is denoted as DataM , DataL , and DataT for metrics, logs, and
traces, respectively. At each timestamp t, the anomaly ground
truth is represented as yt , where yt = 1 indicates an anomaly
and yt = 0 indicates normal behavior.
Given historical data within a sliding window w, denoted
as DataM [t − w, t], DataL [t − w, t], and DataT [t − w, t], the
anomaly detection task identifies whether an anomaly exists at
timestamp t, denoted as ŷt . This process is formalized as:
ŷt = F (DataM [t − w, t], DataL [t − w, t], DataT [t − w, t])
(1)
where F represents the anomaly detection model.
B. Solution Formulation
To fully exploit the benefits of early fusion, we adopt a multimodal anomaly detection paradigm that combines time series
conversion and graph structure learning. Before presenting the
solution overview, we formulate the key components of the
process.
1) Serialization of Multimodal Data: As illustrated in Fig. 2,
we convert all modalities into time series and combine them into
a unified multivariate time series. The conversion process can
be formalized as follows:
XMetrics = TSM(DataM ) ∈ RKM ×N ,
XLogs = TSL(DataL ) ∈ RKL ×N ,
XTraces = TST(DataT ) ∈ RKT ×N ,

(2)

where TSM(), TSL(), and TST() denote the time series conversion functions for metrics, logs, and traces, respectively. KM ,
KL , and KT represent the number of converted time series for
metrics, logs, and traces, respectively, and N is the total number
of time intervals.
The combined multivariate time series is represented as:
⎡
⎤
XMetrics
X = ⎣ XLogs ⎦ ∈ RK×N ,
(3)
XTraces
where K = KM + KL + KT is the total number of converted
time series. At each timestamp t, xt ∈ RK represents the multivariate data. For a historical window of size w, the sub-time

series at timestamp t is represented as:
Xt = [xt−w , xt−w+1 , . . . , xt−1 ] ∈ RK×w .
The anomaly detection task converts to determine whether an
anomaly occurs at timestamp t, given the historical data Xt .
2) Graph Construction: GNNs have proven effective for
multivariate time series anomaly detection. To leverage GNNs,
we construct a graph G = (V, E) for the converted multivariate
time series with the following components:
- Nodes (V ): Each node represents a converted time series,
with the total number of nodes given by |V | = K.
- Edges (E): Edges represent hidden relationships between
the converted time series.
Since the relationships between time series are unknown,
we employ GSL to dynamically learn an adjacency matrix
A ∈ RK×K . Each element A(i,j) indicates the presence of a
connection between nodes i and j, where A(i,j) = 1 denotes
an edge, and A(i,j) = 0 denotes no edge. The adjacency matrix
captures dependency relationships that are critical for accurate
anomaly detection.
3) Anomaly Detection: Using the learned graph structure A,
GNNs model inter-time series relationships to facilitate anomaly
detection. The detection process involves the following steps:
GSL dynamically learns the adjacency matrix A. Given the
historical sub-time series Xt and the learned graph structure
A, the model predicts the value of xt at timestamp t, denoted
as x̂t ∈ RK . An anomaly score st is calculated based on the
difference between the predicted value x̂t and the actual value
xt . An anomaly is detected at timestamp t if the anomaly score
st exceeds a predefined threshold.
The anomaly detection process can be formally defined as:
A = GSL(X),
x̂t = f(Xt , A),
st = ϕ(xt , x̂t ),

1, if st > T,
ŷt =
0, if st ≤ T,

(4)

where A is the learnable adjacency matrix, GSL() represents
the graph learning function, f() is the prediction function, ϕ() is
the anomaly scoring function, x̂t ∈ RK is the predicted value,
and ŷt is the binary anomaly detection result. An anomaly is
detected at timestamp t if st > T .

1426

Fig. 4.

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 19, NO. 2, MARCH/APRIL 2026

The framework of MGFusion.

C. Solution Overview
In microservice systems, multimodal data often exhibit complex and multi-view relationships that are challenging to model
effectively. To address this, we propose MGFusion, an efficient framework for multimodal anomaly detection. MGFusion
transforms multimodal data into time series representations,
incorporates structured prior knowledge to guide graph structure
learning, and employs Grassmann manifolds-based graph fusion
to combine multiple basic graph structures, enabling the learning
of complex and multi-view relationships. The framework of
MGFusion is illustrated in Fig. 4, which comprises four main
components:
r Data Preprocessing: MGFusion employs a robust method
to convert all multimodal data into a unified time series
format to preserve critical information. This process produces the converted multivariate time series X, derived
from the raw metrics DataM , logs DataL , and traces
DataT .
r Structured Prior Knowledge Extraction: MGFusion leverages the Adamic-Adar Index to evaluate node similarity and extract structured prior knowledge θt . This prior
knowledge provides guidance for graph structure learning,
helping to reduce the impact of noise and enhance the
accuracy of relationship modeling.

r Fusion of Graph Structure Learning: MGFusion employs
three basic GSL methods to generate multiple basic graph
structures: A1 , A2 , and A3 . These graphs capture different perspectives of the relationships among the converted
multivariate time series. To effectively combine these basic
graphs and represent the complex, multi-view relationships, MGFusion uses Grassmann manifolds-based graph
fusion. The resulting fused graph structure, denoted as A,
encodes the optimal relationships for anomaly detection.
r Prediction and Anomaly Detection: MGFusion uses
the Diffusion Convolutional Recurrent Neural Network
(DCRNN) to predict future values x̂t of the multivariate
time series. Anomaly scores are calculated based on the
difference between the predicted values x̂t and the actual
observed values xt . If the anomaly score exceeds a predefined threshold, the timestamp t is flagged as anomalous.
In the following sections, we provide a detailed explanation
of each step in the framework.
IV. DATA PREPROCESSING
The aim of data preprocessing is to robustly convert all
multimodal data into a unified time series format. This step
ensures that metrics, logs, and traces—each with unique

HE et al.: MULTIMODAL ANOMALY DETECTION FOR MICROSERVICE SYSTEMS VIA GRASSMANN MANIFOLDS-BASED GRAPH FUSION

characteristics—are consistently represented, making them suitable for further analysis and anomaly detection.
When converting multimodal data into aligned time series,
all raw data must be mapped to values within fixed intervals
(e.g., one minute). This process presents a challenge because
multiple records may occur within a single interval, and the data
volume per interval often varies across modalities. For instance,
as shown in Fig. 1, two log messages (L1, L2) and two spans
(T1, T2) are generated at 2021-07-01 09:57. The core task of
this conversion process is to aggregate multiple records within an
interval into a single unified representation. Metrics are typically
represented as continuous data, while logs are semi-structured
text and discrete in nature. Traces, on the other hand, include
both response time (a continuous variable) and status codes (a
discrete variable). A general aggregation method is averaging;
however, applying naive averaging to discrete data, such as status
codes, can lead to meaningless or misleading results.
Therefore, careful consideration of the data type is essential
when designing aggregation strategies for multimodal time series conversion. For robust time series conversion, continuous
data are aggregated using statistical methods, while discrete
data are converted using frequency encoding, which counts the
occurrences of each event type per interval. This ensures that
meaningful information is preserved.
r Metric Preprocessing: Metrics provide valuable insights
into the performance of services and machine states (e.g.,
CPU usage, memory usage, and throughput). In practice,
low-variance metrics are filtered out, as they are statistically less likely to contain meaningful anomaly information. This step reduces the dimensionality of the data while
retaining critical metrics. After preprocessing, metrics are
represented as:
XMetrics = TSM(DataM ) ∈ RKM ×N ,
where N is the number of timestamps, and KM is the
number of selected metrics.
r Log Preprocessing: Logs are semi-structured data that
record system status and significant events. To process logs,
a log parsing tool, such as Drain [40], is used to convert
semi-structured log messages into structured log templates.
Each log is mapped to a log template. Frequency encoding
is applied to count the occurrences of each template per
interval, resulting in a time series representation of logs:
XLogs = TSL(DataL ) ∈ RKL ×N ,
where K is the number of unique log templates.

L
r Trace Preprocessing:
Traces capture the execution process

of user requests in microservices. They provide response
time statistics and feedback on server status. The response
time of all traces within each interval is aggregated into
four statistical features: mean, median, range, and standard deviation. Status codes in the traces are categorized
into five response categories based on their first digit, as
detailed in Table II. Unlike AnoFusion [18], which retains
only the status code of the first span, our method applies
frequency encoding to count the occurrences of each response category (e.g., 2xx, 4xx, 5xx, etc.) per minute. This
process generates five additional time series, ensuring that
all status codes within an interval are preserved. Traces are
represented as:
XTraces = TST(DataT ) ∈ RKT ×N ,

1427

TABLE II
STATUS CODE CATEGORIES

where KT = 9 (four RT statistics and five response categories).
After obtaining the three types of time series, we synchronize and merge them. Metrics, logs, and traces are normalized
and combined into a new multivariate time series X ∈ RK×N ,
where K = KM + KL + KT is the total number of time series.
This preprocessing method is designed with a certain level of
generality and can be applied to different datasets. Meanwhile,
we adapt a flexible strategy to handle different situations of data
loss. In practice, for a small amount of missing data or when the
missing data is independent, we use data imputation methods to
recover the missing values. However, in cases of continuous and
extensive data loss (e.g., when data for an entire day is missing),
we remove the corresponding records to ensure data quality.
Taking the data in Fig. 1 as an example, Fig. 5 illustrates
serialization and graph construction.
- Logs: Two log messages at 2021-07-01 09:57 are parsed into
Template1 and Template2, resulting in the converted log time
series for 09:57 as [1, 1, 0, . . . , 0]T . At 09:58, one log message
is parsed into Template2, resulting in [0, 1, 0, . . . , 0]T .
- Traces: For spans T1 and T2, the RT statistics are calculated
as mean = 12.5, median = 12.5, range = 5, and standard
deviation = 2.5. Status codes are categorized into 2XX and
5XX. For span T3 and T4, the RT statistics are calculated as
mean = 10, median = 10, range = 0, and standard deviation =
0, with the status code categorized into 2XX. The converted trace
time series for 09:57 is [12.5, 12.5, 5, 2.5, 0, 1, 0, 0, 1]T , and for
09:58 is [20, 20, 0, 0, 0, 2, 0, 0, 0]T . As a result, both the 2XX
and 5XX status codes are preserved, effectively addressing the
issue outlined in the first challenge.
Treating each time series as a node, the converted multivariate
time series can be represented as the graph G = (V, E) where
the relationships between the nodes (time series) are initially
unknown. To uncover these hidden relationships, graph structure
learning is employed to dynamically learn the optimal adjacency
matrix.
V. STRUCTURAL PRIOR KNOWLEDGE EXTRACTION
To guide graph structure learning, we incorporate prior knowledge, typically represented as a prior graph derived from raw
data. This prior graph is generally constructed based on node
feature similarity. However, in real-world scenarios, data noise
can distort node feature representations, leading to spurious or
noisy edges in the graph. These artifacts degrade the quality of
the learned graph structure and negatively impact the performance of downstream anomaly detection task.
To mitigate the impact of noisy edges, we propose a structural
prior graph generation method based on the Adamic-Adar Index
(AAI). AAI accounts for the importance of neighbors, effectively
capturing true relationships between nodes while reducing the
influence of data noise. The process consists of two stages:

1428

Fig. 5.

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 19, NO. 2, MARCH/APRIL 2026

Serialization of multimodal data and graph construction.

constructing an initial graph and refining it using the AAI to
create a structured prior graph.
A. Initial Prior Graph Construction
We start by constructing an initial prior graph using a
similarity-thresholding approach [41]. Node features are extracted using two one-dimensional convolutional layers (Conv)
followed by a fully connected layer (FC), as shown in (5). Cosine
similarity is calculated between feature vectors of nodes, as
shown in (6). Nodes with similarity scores above a predefined
threshold τ are treated as neighbors, forming the initial prior
graph θt .




(i)
(i)
,
(5)
Vt = FC Conv Conv xt
cos



(i)
(j)
Vt , Vt



(i)

=

Vt

(i)

(j)

Vt  · Vt 

,

(6)

(i)

where xt = [xit−w , xit−w+1 , . . . , xit−1 ] ∈ Rw is the historical
(i)
subsequence of node i at timestamp t, Vt is the extracted
feature vector for node i, and  ·  represents the vector norm.
(i)
The set of neighbors for each node i is denoted by Γt .


(i)
(i)
(j)
>τ .
(7)
Γt = j | cos Vt , Vt
B. Adamic-Adar Index-Based Refinement
The AAI is a node-local similarity metric that emphasizes the
contribution of low-degree shared neighbors, as these are more
informative in similarity measurement than high-degree ones.
The AAI between nodes i and j is defined as:
AAI (i,j) =

1
,
(u) |
ln
|Γ
(j)

where top_k selects the indices of the k nodes with the highest
AAI scores.
By prioritizing low-degree neighbors, AAI suppresses the impact of noisy or spurious edges caused by data noise. The graph
structure learned using this prior knowledge is more robust and
adaptable to the requirements of downstream anomaly detection
task.
VI. FUSION OF GRAPH STRUCTURE LEARNING

(j)

· Vt

for all pairs of nodes in the initial prior graph. Each node i selects
the k nodes with the highest AAI scores as its neighbors. The
refined structural prior graph is represented by the adjacency
matrix θt .


(i,j)
θt
(9)
= 1, if j ∈ top_k AAI (i,:) ,

(8)

u∈Γ(i) ∩Γ

where Γ(i) and Γ(j) are the neighbor sets of nodes i and j, and
|Γ(u) | is the degree of neighbor u.
AAI assigns higher importance to neighbors of low degrees,
reducing the influence of noisy, high-degree nodes. Using AAI,
we refine the initial prior graph as follows. We calculate the AAI

To represent the complex relationships between converted
time series from multiple views, we first employ three basic
graph structure learning methods to learn the relationships.
These methods capture different perspectives of node interactions. Then, we use Grassmann manifolds-based graph fusion
to combine the learned graphs into a unified structure.
A. Basic Graph Structure Learning
To enhance the quality of graph structure learning, we
use three representative GSL methods: K-Nearest Neighbors,
Causal Graph Learning, and Full Parameterization Method.
Each method captures node interactions from a distinct perspective, providing a comprehensive understanding of relationships such as similarity and causality. Together, these methods provide complementary insights into the structure of the
graph, enabling the construction of a high-quality adjacency
matrix that reflects both direct and indirect interactions among
nodes.
r K-Nearest Neighbors Method (K-Neighbor): This method
constructs edges based on cosine similarity between node
embeddings, constructing edges between nodes with the
closest relationships. For each node i, a learnable embedding vector E (i) is generated. The k-nearest neighbors
are selected based on cosine similarity to construct the

HE et al.: MULTIMODAL ANOMALY DETECTION FOR MICROSERVICE SYSTEMS VIA GRASSMANN MANIFOLDS-BASED GRAPH FUSION

adjacency matrix A1 :
(i,j)

S1

(i,j)

A1



(i)
(j)
= cos Et , Et
=
=

1,
0,

(i)

(j)

E t · Et
(i)

(j)

Et  · Et 


(i,:)
if j ∈ top_k S1
,
otherwise.

,

(10)

(11)

Here, top_k selects the indices of the k nodes with the
highest similarity.
r Causal Graph Learning (CGL): This method captures
causal impacts between nodes by constructing an asymmetric adjacency matrix, capturing the influence of one node
on another. The Source and destination embeddings (E1
and E2 ) are learned for each node. The adjacency matrix
A2 is derived as:
M1 = tanh(φE1 β1 ),
M2 = tanh(φE2 β2 ),

S2 = ReLU tanh φ M1 M2T − M2 M1

(i,:)
(i,j)
A2 = 1, if j ∈ top_k(S2 ) ,
0, otherwise.

1) Grassmann Manifold: Grassmann manifold is a mathematical framework about the geometric property of linear subspaces. It views all linear subspaces of the same dimension as a
manifold, represented by Gr(n, p). It includes all n-dimensional
linear subspaces in a p-dimensional euclidean space, denoted by
the set of orthogonal matrices Y .


(18)
Gr(n, p) = Y |Y ∈ Rn×p , Y T Y = I .
For an adjacency matrix Ai of i-th basic graph, its Laplacian matrix Li has a complete set of orthonormal eigenvectors,
denoted by eigenvector matrices Ui :
−1

−1

Li = Di 2 (Di − Ai ) Di 2 ,
Li = Ui Λi UiT , UiT Ui = I,

(19)

, (14)

where Di ∈ RK×K is the degree matrix of Ai , Li ∈ RK×K
is the symmetrically normalized Laplacian matrix of Ai , Ui ∈
RK×p is the eigenvector matrix, and Λi ∈ Rp×p is the eigenvalue
diagonal matrix.
Ui lies on the Grassmann manifold Gr(K, p):

(15)

Ui ∈ Gr(K, p).

(12)

T

1429

(13)

where the asymmetric structure captures directionality. The
(i,:)
top k largest values in A2 are retained as edges.
r Full Parameterization Method
(FPM): This method uses
Gumbel Softmax to directly learn the graph structure. A
probability matrix π1 ∈ RK×K determines edge existence:
g (i,j) = − log(− log(u)), u ∼ Uniform(0, 1),
(16)
 

(i,j)
exp log π1 + g (i,j) /τ
(i,j)
  , (17)

A3 = 
(i,j)
log πv + g (i,j) /τ
v∈{0,1} exp
where u is a random sample drawn from the Uniform(0, 1)
distribution, and g (i,j) follows the Gumbel distribution.
The parameter τ is the temperature parameter, controlling
the sharpness of the Gumbel-Softmax distribution. As τ
(i,j)
approaches 0, A3
converges to either 0 or 1, making
the Gumbel-Softmax distribution behave like a categorical
(i,j)
distribution. The adjacency matrix element A3 is 1 with
(i,j)
probability π1 , reflecting the likelihood of a connection
between nodes i and j.
B. Grassmann Manifolds-Based Graph Fusion
After generating the three graphs (A1 , A2 , A3 ), the critical
challenge lies in effectively combining them. The combining
methods include averaging and weighted averaging. While simple averaging offers a straightforward solution, it fails to account
for the relative importance of each graph structure. Alternatively,
similarity-weighted averaging risks distorting the original structural properties of the constituent graphs. Grassmann manifoldsbased subspace fusion can merge multiple subspaces or graphs
into a representative subspace while preserving the geometric
features of each subspace or graph [42]. Therefore, we combine
them using Grassmann manifolds to preserve their geometric
properties.

(20)

The three graphs are mapped to the Grassmann manifold through
their eigenvector matrices U1 , U2 , U3 .
2) Subspace Fusion on Grassmann Manifolds: The goal of
subspace fusion is to find a representative subspace U0 that:
(1) Integrates information from U1 , U2 , U3 , (2) Preserves the
geometric structure of each subspace. Therefore, two objectives
need to be minimized.
The first objective is to preserve the geometric features of
each subspace. 
It can be achieved by minimizing the Laplacian
quadratic form 3i=1 tr(U T Li U ).
The second objective is to minimize the projection distance
between the representative subspace and each subspace Ui :
3

d2 (U, Ui ) = min

min

U ∈RK×p

U ∈RK×p

i=1
3

= min

U ∈RK×p

⎛
⎝p −

i=1
3

= min

U ∈RK×p

3

p

p

sin2 θij

i=1 j=1

⎞
cos2 θij ⎠

j=1

p − tr U U T Ui UiT



i=1
3

= min 3p −
U ∈RK×p


tr U U T Ui UiT .

Finally, the optimization problem is as follows:

3
3
tr(U T Li U ) + α 3p −

min

U ∈RK×p

i=1

s.t. U T U = I,

(21)

i=1



tr(U U T Ui UiT ) ,

i=1

(22)

where the first term preserves geometric properties and the
second term minimizes projection distances between U0 and Ui .
The parameter α controls the balance between these two terms.

1430

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 19, NO. 2, MARCH/APRIL 2026

Applying the Rayleigh-Ritz theorem to solve the optimization
problem (22), the Laplacian matrix L0 for the fused graph is:
3

L0 =

3

Li − α
i=1

Ui UiT .

(23)

i=1

Finally, the adjacency matrix A0 is derived as follows:
A0 = D0 − L0 .

(24)

3) Graph Sparsification and Finalization: The adjacency
matrix of the combined graph may contain negative values,
whereas real-world graphs typically have non-negative adjacency matrices. Therefore, we apply a piecewise linear unit
function to eliminate negative values.
To reduce computational complexity, we sparsify A0 by retaining only the top k edges for each node:
 (i,j)
(i,j)
(i,j)
(25)
Â
= A0 , if A0 ∈ top_k(A0 ),
0,
otherwise.
The final symmetric adjacency matrix is:
Â + ÂT
.
(26)
2
This Grassmann manifolds-based graph fusion effectively integrates multiple graph structures while preserving their unique
properties, enabling robust graph representation.
A=

VII. DCRNN PREDICTOR AND ANOMALY DETECTION
Based on the combined graph, MGFusion predicts future
values using a spatio-temporal GNN and detects anomalies by
analyzing the differences between predictions and actual values.

Ct = tanh (WC ◦ [xt  (Rt ◦ Ht−1 )] + bC ) ,

(29)

Ut = sigmoid (WU ◦ [xt  Ht−1 ] + bU ) ,

(30)

Ht = Ut ◦ Ht−1 + (1 − Ut ) ◦ Ct ,

(31)

where  denotes concatenation, xt ∈ RK represents the input
values at timestamp t, and Ht represents the node features at
timestamp t.
The diffusion convolutional recurrent layer takes xt and the
previous node features Ht−1 as inputs and outputs the updated
node features Ht .
DCRNN Prediction Process: DCRNN employs an encoderdecoder architecture for time series prediction. The prediction
process comprises the following steps. The encoder processes
the input sequence xt from timestamp t − ω to t − 1. It sequentially updates the node features for each timestamp, resulting
in the aggregated node features Ht−1 . The decoder takes the
encoded node features Ht−1 as input. Using a diffusion convolutional recurrent layer, the decoder predicts the future values
x̂t at timestamp t.
By combining diffusion convolution for spatial dependencies
and GRU for temporal dynamics, DCRNN provides a highly
effective framework for spatio-temporal modeling and accurate
time series prediction.
B. Loss Function
The model’s objective is to minimize the prediction error
while ensuring the quality of the learned graph structure. The
total loss function consists of three components:
Prediction Loss:The mean absolute error (MAE) is used as
prediction loss:
K
 i

1
x̂t − xit  ,
lossp =
K i=1

A. DCRNN Predictor
The DCRNN is a powerful spatio-temporal GNN that effectively captures both spatial and temporal dependencies. Compared to conventional Graph Convolutional Networks, DCRNN
is more suitable for time series prediction due to its ability to
model complex interactions over both space and time. DCRNN
integrates two key components: diffusion convolution for capturing spatial relationships and Gated Recurrent Unit (GRU) for
modeling temporal dynamics.
Diffusion Convolution: The diffusion convolution mechanism
aggregates L-hop neighbor features and is defined as:
L

WQ ◦ Y =



i 
i
Q
Q
−1
wi,1
Y, (27)
DO
DI−1 AT
A + wi,2

i=0

where ◦ represents the diffusion convolution operation, A is the
combined adjacency matrix, DO and DI are the out-degree and
Q
Q
, wi,2
, and bQ are learnable
in-degree matrices, respectively, wi,1
parameters, and L is the diffusion degree (a hyperparameter).
This mechanism allows DCRNN to aggregate multi-hop spatial dependencies while preserving the directionality of the
graph.
Diffusion Convolutional Recurrent Layer: The diffusion convolutional recurrent layer combines diffusion convolution with
GRU to capture spatio-temporal dynamics. The equations governing the layer are as follows:
Rt = sigmoid (WR ◦ [xt  Ht−1 ] + bR ) ,

(28)

(32)

where x̂it and xit are the predicted and actual values for the i-th
time series, respectively.
Graph Structure Learning Loss: To improve graph quality,
the structured prior graph θt is used as prior knowledge. The
GSL loss [43] is defined as the cross-entropy between θt and the
learned graph A:
(i,j)

lossg =

−θt

(i,j)

log A(i,j) − (1 − θt

) log(1 − A(i,j) ).

ij

(33)
L2 Regularization: To reduce overfitting, an L2 regularization
term is added:
λ2 w22 ,

(34)

where w represents the model parameters.
The total loss function is as follows:
loss = lossp + λ1 lossg + λ2 w22 ,

(35)

where λ1 and λ2 are regularization coefficients.
C. Anomaly Score
To detect anomalies, we calculate an anomaly score based on
the deviation of predicted values from actual values.

HE et al.: MULTIMODAL ANOMALY DETECTION FOR MICROSERVICE SYSTEMS VIA GRASSMANN MANIFOLDS-BASED GRAPH FUSION

Prediction Error: The prediction error for the i-th time series
at timestamp t is:


(i)
(36)
Errt = xit − x̂it  .

1431

TABLE III
DATASET STATISTICS

Standardization: To ensure consistency in different time series, the prediction error is standardized.
(i)

(i)

st =

Errt − μ(i)
,
σ (i)

(37)

TABLE IV
METHOD PARAMETERS

where μ(i) and σ (i) are the mean and standard deviation of
(i)
Errt , respectively.
Anomaly Score: The maximum standardized prediction error
across all time series is the anomaly score for timestamp t:
(i)

Errt − μ(i)
.
(38)
i
i
σ (i)
Threshold Selection: The optimal threshold for anomaly detection is determined using grid search. The search range is
defined by the minimum and maximum values of st . The threshold that achieves the highest F1 score is selected. To improve
robustness, a point adjustment strategy is applied to smooth the
anomaly detection results.
With this procedure, MGFusion effectively detects anomalies
based on accurate predictions.
In the Artificial Intelligence for IT Operations (AIOps) field,
the MGFusion framework can serve as a core component
of intelligent operation and maintenance platforms for realtime monitoring and anomaly detection. By MGFusion, operation and maintenance teams can achieve automatic anomaly
detection.
(i)

st = max st = max

VIII. EXPERIMENTS
In this section, we perform evaluation experiments to address
the following research questions:
r RQ1 (Detection Performance and Efficiency): Is our
method superior to baseline methods in terms of anomaly
detection performance and efficiency?
r RQ2 (Ablation Study): How does each component of MGFusion contribute to its overall performance?
r RQ3 (Parameter Sensitivity): How sensitive is MGFusion
to variations in key parameters?
A. Experimental Setup
1) Dataset: We conduct experiments using the General
AIOps Atlas (GAIA) dataset1 provided by CloudWise. GAIA is
a comprehensive dataset designed for AIOps research, covering
tasks such as anomaly detection, log analysis, and anomaly localization. The dataset simulates a system consisting of five hosts
serving both PC and mobile users simultaneously. It includes
five microservices deployed across ten instances, with operators
injecting five types of anomalies: system stuck, process crash,
log-in failure, file missing, and access denied.
Each microservice maintains two separate instances (e.g.,
‘Webservice1’ and ‘Webservice2’). Despite providing the same
service functionality, these instances exhibit significant operational variations, such as differences in log templates, data
volumes, and metric variations. To account for these differences,
1 https://github.com/CloudWise-OpenSource/GAIA-DataSet

we perform instance-level anomaly detection and evaluate two
configurations of the dataset:
r D1: Includes three services: ‘Mobservice’, ‘Loginservice’,
and ‘Redisservice’.
r D2: Covers all services (D1 + ‘Dbservice’ + ‘Webservice’).
For the experiments, we analyze half a month of data. The
detailed dataset statistics are presented in Table III.
2) Baselines: We compare MGFusion with ten state-ofthe-art methods, including single-modal and multimodal approaches. The single-modal anomaly detection methods include OmniAnomaly [44], AnomalyTrans [45], Deeplog [9],
LogRobust [34], and SwissLog [46]. The multimodal anomaly
detection methods with two modalities, include MADMM [13],
SCWarn [21], and Hades [39]. The multimodal anomaly detection methods with three modalities are MSTGAD [19] and
AnoFusion [18].
While there is a significant body of excellent work in the
field of multimodal anomaly detection, such as Nezha, Eadro,
and MRCA [20], a direct comparison with these methods is
unfortunately not feasible due to differences in task objectives.
Nezha, Eadro, and MRCA aim to detect whether an anomaly
has occurred in the entire system and, if so, locate the root
microservice causing the issue. However, these methods do not
address the identification of which specific microservices exhibit
anomalous behavior.
3) Experimental Environment and Setup: The experimental
parameter configurations are detailed in Table IV. MGFusion
is implemented using PyTorch. All experiments are conducted
in Python 3.8 and PyTorch 1.10, with CUDA 11.3 for GPU
acceleration. The hardware environment includes an Intel(R)
Core(TM) i7-13700KF CPU and an NVIDIA RTX 4060 GPU.
The multimodal dataset is divided into training and testing
sets. The training set contains the first 70% of the data from
each instance. The testing set contains the remaining 30%.
4) Evaluation Metrics: We use standard metrics for anomaly
detection, including precision (P rec), recall (Rec), and F1 score
(F 1), defined as follows:
TP
,
TP + FP
TP
,
Rec =
TP + FN

P rec =

(39)
(40)

1432

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 19, NO. 2, MARCH/APRIL 2026

TABLE V
PERFORMANCE COMPARISON AMONG DIFFERENT METHODS. THE HIGHEST AND SECOND-HIGHEST RESULTS ARE HIGHLIGHTED WITH BOLDFACE AND
UNDERLINE

F1 = 2 ×

P rec × Rec
,
P rec + Rec

(41)

where T P , F P and F N represent the number of true positives,
false positives, and false negatives, respectively.
We also consider the training time and interfere time as
metrics to evaluate the efficiency.
B. Detection Performance and Efficiency (RQ1)
1) Detection Performance: In this experiment, we compare
the performance of MGFusion against all baseline methods.
Specifically, we evaluate precision, recall, and F1 score across
different datasets. However, since MADMM is not an opensource method, it is not feasible to apply MADMM to the
D2 dataset and obtain the necessary performance metrics for
comparison. MSTGAD focuses on anomaly detection across all
service instances in a system, requiring traces from all service instances. Consequently, it can only support the D2 dataset, which
contains all instances from the GAIA dataset. This approach
results in extremely large multimodal datasets and takes over 7
hours to process the GAIA dataset, even when limited to the first
20,000 data points (seconds) with a training-to-testing ratio of
7:3.
As shown in Table V, MGFusion outperforms all baseline
methods on both datasets, achieving the best F1 scores of 0.958
on D1 and 0.968 on D2. Single-modal anomaly detection methods, such as OmniAnomaly and AnomalyTrans, demonstrate
limited performance due to their inability to leverage multimodal
information. In contrast, dual-modal methods significantly improve detection accuracy by incorporating relationships between
metrics and logs. While supervised and semi-supervised methods generally achieve higher performance, MGFusion, despite
being fully unsupervised, matches or surpasses the F1 scores
of top supervised methods by leveraging the benefits of trace
data. Trace data captures important contextual and temporal information that enhances the model’s ability to detect anomalies.
Furthermore, it outperforms all existing unsupervised methods,
highlighting its exceptional capability to detect anomalies in
unlabeled datasets.
As shown in Fig. 6, the ROC curves for the two datasets (D1
and D2) exhibit AUC of 0.976 for D1 and 0.977 for D2. These
results further highlight the effectiveness and superiority of our
method in anomaly detection.

Fig. 6.

The ROC-AUC curve of the model.
TABLE VI
COMPARISON OF DETECTION EFFICIENCIES

2) Detection Efficiency: We further evaluate the efficiency of
MGFusion by comparing its training and inference times with
AnoFusion [18] on both datasets. As shown in Table VI, MGFusion demonstrates significantly shorter training and inference
time.
AnoFusion relies on complex multi-layer graph transformation networks and graph attention networks to model relationships between multimodal data, resulting in higher computational complexity. In contrast, MGFusion leverages DCRNN
for prediction, which reduces training time while maintaining
high performance. Additionally, MGFusion’s faster inference
time makes it more suitable for real-time systems.
In summary, MGFusion achieves state-of-the-art detection
performance while significantly improving computational efficiency, making it a highly effective solution for anomaly detection in real-world systems.
C. Ablation Experiment (RQ2)
To demonstrate the contribution and importance of each component of MGFusion, we create four variants of MGFusion and

HE et al.: MULTIMODAL ANOMALY DETECTION FOR MICROSERVICE SYSTEMS VIA GRASSMANN MANIFOLDS-BASED GRAPH FUSION

Fig. 7.

1433

F1 scores of MGFusion under different parameter.
TABLE VII
PERFORMANCE COMPARISON AMONG DIFFERENT VARIANTS

conduct a series of experiments to compare their performance.
The variants are defined as follows:
r MGFusion w/o Graph Fusion: To evaluate the importance
of the multiple graphs and graph fusion, this variant uses
only the FPM in place of the three graph structure learners.
r MGFusion w/o Grassmann: This variant removes the
Grassmann manifolds-based graph fusion and instead combines graphs based on their similarity to the prior graph.
This evaluates the impact of Grassmann manifolds-based
graph fusion.
r MGFusion w/o Prior Knowledge: To examine the role of
prior knowledge in guiding GSL, this variant eliminates
the GSL loss, effectively removing the influence of prior
knowledge.
r MGFusion w/o DCRNN: To evaluate whether DCRNN
is the optimal choice, we replace DCRNN with SpatialTemporal Graph Convolutional Networks (STGCN) [47].
Table VII reports the average precision, recall, and F1 scores
of the four variants. The results indicate the following.
The three GSL methods provide complementary perspectives
for capturing complex node relationships, which cannot be fully

replicated by a single GSL method (e.g., FPM). Consequently,
the performance of MGFusion significantly degrades when
Graph Fusion is removed (MGFusion w/o Graph Fusion).
The Grassmann manifolds-based graph fusion module is critical, as it preserves the distinct structural properties of basic
graphs while constructing a unified representation. Removing
this component leads to a notable performance drop, underscoring its necessity.
The prior graph serves as a structural guide for graph learning.
Removing prior knowledge (MGFusion w/o Prior Knowledge)
results in a decline in precision, highlighting the importance of
this inductive bias for robust anomaly detection.
The DCRNN plays a crucial role in MGFusion. In Table VII,
when the DCRNN is replaced by STGCN (MGFusion w/o
DCRNN), the model’s performance significantly decreases, especially in terms of precision.
D. Parameter Sensitivity (RQ3)
To evaluate the stability and robustness of MGFusion, we
analyze the influence of key hyperparameters.
1) Window Size ω: We investigate the impact of the sliding
window size by varying it from 5 to 60. Fig. 7 shows the
experimental results, which highlight the following trends.
Excessively large windows (e.g., > 35) introduce too much
seasonal variation, making it challenging to reconstruct the current state and degrading anomaly detection performance. Overly
small windows (e.g., < 15) fail to capture sufficient historical
context, leading to suboptimal learning and reduced detection
accuracy. Optimal performance is achieved with a window size
between 15 and 35, where a balance is struck between capturing
historical patterns and avoiding excessive noise.
2) Hyperparameter α: The Grassmann manifolds-based
graph fusion framework uses two key components: the contributions of basic graph structures and the constraints of common
structures. The hyperparameter α balances these components

1434

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 19, NO. 2, MARCH/APRIL 2026

during the fusion process. When α = 0, the fusion process
considers only basic graph structures, ignoring subspace consistency constraints. As α increases, the framework emphasizes
the global structural information encoded in common structures,
progressively aligning subspaces.
We evaluate the impact of α by varying its value from 0 to
1 in steps of 0.1. Fig. 7 shows the results. When α = 0.5, the
information complementarity between the basic graph structures
and the common structures is insufficient, leading to suboptimal
fusion performance. Increasing α to 0.7 strengthens subspace
consistency constraints, enhancing performance by aligning the
global structures more effectively.
These results highlight the importance of balancing local and
global structural information for optimal graph fusion.
3) k in K-Nearest Neighbors Graph Structure Learning: In
K-nearest neighbors graph structure learning, the value of K
determines the number of nearest neighbors to consider when
constructing the graph. Selecting an appropriate K value is
therefore critical for achieving optimal performance. To verify
this, we conducted experiments by varying K within a range
from 10 to 80. The results showed that the model achieved the
best performance when K = 40. This highlights the importance
of tuning K to ensure the graph accurately captures the relationships among data points.
4) Diffusion Degree L: In our analysis of the diffusion degree
L parameter in DCRNN, we systematically varied L from 1 to 8
to evaluate its impact on model performance. The results demonstrated that the model performed optimally when L = 4, striking
a balance between capturing complex temporal dependencies
and mitigating the risk of overfitting. This finding underscores
the importance of carefully selecting the diffusion degree L to
fully leverage DCRNN’s strengths in anomaly detection tasks.
IX. CONCLUSION
To fully exploit the potential of multimodal data in microservice systems, we propose MGFusion, an innovative, unsupervised, end-to-end multimodal anomaly detection method. MGFusion effectively transforms metrics, logs, and traces into time
series using a robust time series conversion approach, enabling
consistent processing across all modalities. It leverages GSL
methods to capture the intricate relationships between the converted multivariate time series. Additionally, MGFusion incorporates prior knowledge through AAI and employs Grassmann
manifolds-based graph fusion to enhance the accuracy and reliability of the learned graph structures. By integrating DCRNN
predictors and an anomaly score calculation mechanism, MGFusion achieves efficient and accurate anomaly detection,
thereby ensuring service reliability in complex microservice
systems. In future, we aim to explore dynamic fusion techniques
to better handle the evolving relationships between different
modalities.
REFERENCES
[1] S. Li, L. D. Xu, and S. Zhao, “5G Internet of Things: A survey,” J. Ind.
Inf. Integr., vol. 10, pp. 1–9, 2018.
[2] Q. Lin, H. Zhang, J. Lou, Y. Zhang, and X. Chen, “Log clustering based
problem identification for online service systems,” in Proc. Int. Conf. Softw.
Eng., 2016, pp. 102–111.
[3] X. Zhou et al., “Fault analysis and debugging of microservice systems:
Industrial survey, benchmark system, and empirical study,” IEEE Trans.
Softw. Eng., vol. 47, no. 2, pp. 243–260, Feb. 2021.

[4] R. Picoreti, A. P. do Carmo, F. M. de Queiroz, A. S. Garcia, R. F. Vassallo,
and D. Simeonidou, “Multilevel observability in cloud orchestration,” in
Proc. IEEE 16th Int. Conf. Dependable, Autonom. Secure Comput., 16th
Int. Conf. Pervasive Intell. Computing, 4th Int. Conf. Big Data Intell.
Comput. Cyber Sci. Technol. Cong., 2018, pp. 776–784.
[5] Y. Fu et al., “Investigating and improving log parsing in practice,” in Proc.
30th ACM Joint Eur. Softw. Eng. Conf. Symp. Found. Softw. Eng., 2022,
pp. 1566–1577.
[6] S. Nedelkoski, J. Cardoso, and O. Kao, “Anomaly detection from system
tracing data using multimodal deep learning,” in Proc. IEEE 12th Int. Conf.
Cloud Comput., 2019, pp. 179–186.
[7] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga, “USAD:
Unsupervised anomaly detection on multivariate time series,” in Proc.
ACM Int. Conf. Knowl. Discov. Data Mining, 2020, pp. 3395–3404.
[8] M. Ma et al., “Jump-starting multivariate time series anomaly detection
for online service systems,” in Proc. USENIX Annu. Techn. Conf., 2021,
pp. 413–426.
[9] M. Du, F. Li, G. Zheng, and V. Srikumar, “DeepLog: Anomaly detection
and diagnosis from system logs through deep learning,” in Proc. ACM
SIGSAC Conf. Comput. Commun. Secur., 2017, pp. 1285–1298.
[10] S. Ying et al., “An improved KNN-based efficient log anomaly detection
method with automatically labeled samples,” ACM Trans. Knowl. Discov.
Data, vol. 15, no. 3, pp. 34:1–34:22, 2021.
[11] Q. Zhang et al., “Provable dynamic fusion for low-quality multimodal
data,” in Proc. Int. Conf. Mach. Learn., 2023, pp. 41753–41769.
[12] C. Hou, T. Jia, Y. Wu, Y. Li, and J. Han, “Diagnosing performance issues
in microservices with heterogeneous data source,” in Proc. IEEE Int.
Conf. Parallel Distrib. Process. Appl., Big Data Cloud Comput., Sustain.
Comput. Commun., Social Comput. Netw., 2021, pp. 493–500.
[13] P. Wang, X. Zhang, Z. Cao, and Z. Chen, “MADMM: Microservice system
anomaly detection via multi-modal data and multi-feature extraction,”
Neural Comput. Appl., vol. 36, no. 25, pp. 15739–15757, 2024.
[14] F. Liu et al., “MicroCBR: Case-based reasoning on spatio-temporal fault
knowledge graph for microservices troubleshooting,” in Proc. 30th Int.
Conf. Case-Based Reasoning Res. Develop., 2022, pp. 224–239.
[15] C. Zhang et al., “DeepTraLog: Trace-log combined microservice anomaly
detection through graph-based deep learning,” in Proc. Int. Conf. Softw.
Eng., 2022, pp. 623–634.
[16] S. Zhang et al., “Robust failure diagnosis of microservice system through
multimodal data,” IEEE Trans. Serv. Comput., vol. 16, no. 6, pp.
3851–3864, Nov./Dec. 2023.
[17] G. Yu, P. Chen, Y. Li, H. Chen, X. Li, and Z. Zheng, “Nezha: Interpretable
fine-grained root causes analysis for microservices on multi-modal observability data,” in Proc. 31st ACM Joint Eur. Softw. Eng. Conf. Symp.
Found. Softw. Eng., 2023, pp. 553–565.
[18] C. Zhao et al., “Robust multimodal failure detection for microservice
systems,” in Proc. ACM Int. Conf. Knowl. Discov. Data Mining, 2023,
pp. 5639–5649.
[19] J. Huang, Y. Yang, H. Yu, J. Li, and X. Zheng, “Twin graph-based anomaly
detection via attentive multi-modal learning for microservice system,” in
Proc. 38th IEEE/ACM Int. Conf. Automat. Softw. Eng., 2023, pp. 66–78.
[20] Y. Wang, Z. Zhu, Q. Fu, Y. Ma, and P. He, “MRCA: Metric-level root cause
analysis for microservices via multi-modal data,” in Proc. IEEE/ACM Int.
Conf. Automat. Softw. Eng., 2024, pp. 1057–1068.
[21] N. Zhao et al., “Identifying bad software changes via multimodal anomaly
detection for online service systems,” in Proc. ACM Joint Eur. Softw. Eng.
Conf. Symp. Found. Softw. Eng., 2021, pp. 527–539.
[22] H. Liu et al., “UAC-AD: Unsupervised adversarial contrastive learning for
anomaly detection on multi-modal data in microservice systems,” IEEE
Trans. Serv. Comput., vol. 17, no. 6, pp. 3887–3900, Nov./Dec. 2024.
[23] X. Jiang, H. Luo, Y. Sun, and M. Guizani, “Fast anomaly detection for IoT
services based on multisource log fusion,” IEEE Internet Things J., vol.
11, no. 6, pp. 9405–9419, Mar. 2024.
[24] C. Lee, T. Yang, Z. Chen, Y. Su, and M. R. Lyu, “Eadro: An end-to-end
troubleshooting framework for microservices on multi-source data,” in
Proc. Int. Conf. Softw. Eng., 2023, pp. 1750–1762.
[25] C. Wu et al., “Using adamic-Adar index algorithm to predict volunteer
collaboration: Less is more,” 2023, arXiv:2308.13176.
[26] P. Ni, R. Okhrati, S. Guan, and V. Chang, “Knowledge graph and deep
learning-based text-to-graphQL model for intelligent medical consultation
chatbot,” Inf. Syst. Front., vol. 26, no. 1, pp. 137–156, 2024.
[27] P. Lai et al., “CogNLG: Cognitive graph for KG-to-text generation,” Expert
Syst. J. Knowl. Eng., vol. 41, no. 1, 2024, Art. no. e13461.
[28] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. AAAI Conf. Artif. Intell., 2021, pp.
4027–4035.

HE et al.: MULTIMODAL ANOMALY DETECTION FOR MICROSERVICE SYSTEMS VIA GRASSMANN MANIFOLDS-BASED GRAPH FUSION

[29] S. Han and S. S. Woo, “Learning sparse latent graph representations for
anomaly detection in multivariate time series,” in Proc. ACM Int. Conf.
Knowl. Discov. Data Mining, 2022, pp. 2977–2986.
[30] Z. Chen, D. Chen, X. Zhang, Z. Yuan, and X. Cheng, “Learning graph
structures with transformer for multivariate time-series anomaly detection
in IoT,” IEEE Internet Things J., vol. 9, no. 12, pp. 9179–9189, Jun. 2022.
[31] S. He, G. Li, K. Xie, and P. K. Sharma, “Fusion graph structure learningbased multivariate time series anomaly detection with structured prior
knowledge,” IEEE Trans. Inf. Forensics Secur., vol. 19, pp. 8760–8772,
2024.
[32] W. Meng et al., “LogAnomaly: Unsupervised detection of sequential and
quantitative anomalies in unstructured logs,” in Proc. Int. Joint Conf. Artif.
Intell., 2019, pp. 4739–4745.
[33] S. Nedelkoski, J. Bogatinovski, A. Acker, J. Cardoso, and O. Kao, “Selfattentive classification-based anomaly detection in unstructured logs,” in
Proc. IEEE Int. Conf. Data Mining, 2020, pp. 1196–1201.
[34] S. Xue, H. Chen, and X. Zheng, “Detection and quantification of anomalies
in communication networks based on LSTM-ARIMA combined model,”
Int. J. Mach. Learn. Cybern., vol. 13, no. 10, pp. 3159–3172, 2022.
[35] V. Le and H. Zhang, “Log-based anomaly detection without log parsing,” in
Proc. 36th IEEE/ACM Int. Conf. Automat.Softw. Eng., 2021, pp. 492–504.
[36] S. He, Y. Lei, Y. Zhang, K. Xie, and P. K. Sharma, “Parameter-efficient
log anomaly detection based on pre-training model and LORA,” in Proc.
IEEE 34th Int. Symp. Softw. Rel. Eng., 2023, pp. 207–217.
[37] P. Liu et al., “Unsupervised detection of microservice trace anomalies
through service-level deep Bayesian networks,” in Proc. IEEE Int. Symp.
Softw. Rel. Eng., 2020, pp. 48–58.
[38] T. Zhou et al., “TraceStream: Anomalous service localization based on
trace stream clustering with online feedback,” in Proc. IEEE Int. Symp.
Softw. Rel. Eng., 2023, pp. 601–611.
[39] C. Lee, T. Yang, Z. Chen, Y. Su, Y. Yang, and M. R. Lyu, “Heterogeneous
anomaly detection for software systems via semi-supervised cross-modal
attention,” in Proc. Int. Conf. Softw. Eng., 2023, pp. 1724–1736.
[40] P. He, J. Zhu, Z. Zheng, and M. R. Lyu, “Drain: An online log parsing
approach with fixed depth tree,” in Proc. IEEE Int. Conf. Web Serv., 2017,
pp. 33–40.
[41] I. Elsharkawi, H. Sharara, and A. Rafea, “SViG: A similarity-thresholded
approach for vision graph neural networks,” IEEE Access, vol. 13, pp.
19379–19387, 2025.
[42] R. Ghiasi, H. Amirkhani, and A. Bosaghzadeh, “Multi-view graph structure learning using subspace merging on Grassmann manifold,” Multimedia Tools Appl., vol. 82, no. 11, pp. 17135–17157, 2023.
[43] C. Shang, J. Chen, and J. Bi, “Discrete graph structure learning for forecasting multiple time series,” in Proc. Int. Conf. Learn. Representations,
2021, pp.1–14.
[44] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. ACM Int. Conf. Knowl. Discov. Data Mining, 2019, pp.
2828–2837.
[45] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer: Time series
anomaly detection with association discrepancy,” in Proc. Int. Conf. Learn.
Representations, 2022, pp.1–20.
[46] X. Li, P. Chen, L. Jing, Z. He, and G. Yu, “SwissLog: Robust anomaly
detection and localization for interleaved unstructured logs,” IEEE Trans.
Dependable Secur. Comput., vol. 20, no. 4, pp. 2762–2780, Jul./Aug. 2023.
[47] S. Yan, Y. Xiong, and D. Lin, “Spatial temporal graph convolutional
networks for skeleton-based action recognition,” in Proc. AAAI Conf. Artif.
Intell., 2018, pp. 7444–7452.
Shiming He received the BS degree in information
security and the PhD degree in computer science and
technology from Hunan University, China, in 2006
and 2013, respectively. She is currently a professor
with the School of Computer Science and Technology, Changsha University of Science and Technology,
Changsha, China. Her research interests include machine learning, data analysis, AIOps, and anomaly
detection.

1435

Keyao Feng received the BS degree from East China
Jiaotong University, in 2023. She is currently working
toward the MS degree in software engineering with
the Changsha University of Science and Technology.
Her research interests include deep learning, graph
structure learning, and anomaly detection.

Kaixuan Meng received the BS degree from the
East China University of Technology, in 2023. He is
currently working toward the MS degree in computer
science and technology with the Changsha University
of Science and Technology. His research interests
include deep learning, data analysis, graph structure
learning, and anomaly detection.

Kun Xie (Member, IEEE) received the PhD degree
in computer applications from Hunan University, in
2007 and subsequently conducted postdoctoral research with The Hong Kong Polytechnic University.
She is currently a second-level professor and doctoral
supervisor with Hunan University. She serves as the
director with the Ministry of Education Key Laboratory for Supercomputing and Artificial Intelligence
Converged Computing, and as a chair of both the
Academic Committee and the Degree Committee of
the School of Information Science and Engineering,
Hunan University. She has published more than 130 papers in top-tier conferences and journals, including SIGMOD, CCS, INFOCOM, ICDE, SIGMETRICS, IEEE/ACM Transactions on Networking, IEEE Transactions on Mobile
Computing, IEEE Transactions on Parallel and Distributed Systems, IEEE
Transactions on Services Computing, IEEE Transactions on Information Forensics and Security, IEEE Transactions on Knowledge and Data Engineering, and
IEEE Transactions on Dependable and Secure Computing. Her research has long
focused on computer networks, network security, and artificial intelligence.

Xibin Zhao (Senior Member, IEEE) received the
PhD degree from Jiangsu University, in 2004. He
has published more than 200 papers in international
conferences and journals such as S&P, Usenix Security, IEEE Transactions on Information Forensics and
Security, NeurIPS, IEEE Transactions on Networking, IEEE Transactions on Computer-Aided Design
of Integrated Circuits and Systems, IEEE Transactions on Pattern Analysis and Machine Intelligence,
AAAI, IEEE Transactions on Industrial Electronics,
and IEEE Transactions on Industrial Informatics.
His research interests include software security, network security, artificial
intelligence, enterprise information systems, industrial networks, and intelligent
manufacturing.
PAPER_TEXT
