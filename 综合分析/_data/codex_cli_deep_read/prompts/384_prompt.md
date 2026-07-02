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
# [384] CLEAR: Spatial-Temporal Traffic Data Representation Learning for Traffic Prediction
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
编号：384
题名：CLEAR: Spatial-Temporal Traffic Data Representation Learning for Traffic Prediction
年份：2025
DOI：10.1109/tkde.2025.3536009
来源：IEEE Transactions on Knowledge and Data Engineering
PDF：paper/10.1109_TKDE.2025.3536009.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：无
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\384.txt
- 原始字符数：81195
- 本次发送字符数：81195
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
1672

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 37, NO. 4, APRIL 2025

CLEAR: Spatial-Temporal Traffic Data
Representation Learning for Traffic Prediction
James Jianqiao Yu , Senior Member, IEEE, Xinwei Fang , Shiyao Zhang , Member, IEEE,
and Yuxin Ma , Senior Member, IEEE

Abstract—In the evolving field of urban development, precise
traffic prediction is essential for optimizing traffic and mitigating
congestion. While traditional graph learning-based models effectively exploit complex spatial-temporal correlations, their reliance
on trivially generated graph structures or deeply intertwined adjacency learning without supervised loss significantly impedes their
efficiency. This paper presents Contrastive Learning of spatialtEmporal trAffic data Representations (CLEAR) framework, a
comprehensive approach to spatial-temporal traffic data representation learning aimed at enhancing the accuracy of traffic predictions. Employing self-supervised contrastive learning, CLEAR
strategically extracts discriminative embeddings from both traffic
time-series and graph-structured data. The framework applies
weak and strong data augmentations to facilitate subsequent exploitations of intrinsic spatial-temporal correlations that are critical for accurate prediction. Additionally, CLEAR incorporates
advanced representation learning models that transmute these
dynamics into compact, semantic-rich embeddings, thereby elevating downstream models’ prediction accuracy. By integrating with
existing traffic predictors, CLEAR boosts predicting performance
and accelerates the training process by effectively decoupling adjacency learning from correlation learning. Comprehensive experiments validate that CLEAR can robustly enhance the capabilities
of existing graph learning-based traffic predictors and provide
superior traffic predictions with a straightforward representation
decoder. This investigation highlights the potential of contrastive
representation learning in developing robust traffic data representations for traffic prediction.
Index Terms—Traffic prediction, spatial-temporal data,
contrastive learning, representation learning, self-supervised
learning.

Received 17 April 2024; revised 29 December 2024; accepted 26 January
2025. Date of publication 3 February 2025; date of current version 7 March 2025.
This work was supported in part by the National Natural Science Foundation of
China under Grant 62202217, in part by Guangdong Basic and Applied Basic
Research Foundation under Grant 2023A1515012889, and in part by Guangdong
Key Program under Grant 2021QN02X794. Recommended for acceptance by
T. Weninger. (Corresponding authors: Shiyao Zhang; Yuxin Ma.)
James Jianqiao Yu is with the School of Computer Science and Technology,
Harbin Institute of Technology, Shenzhen 518055, China, and also with the
Department of Computer Science, University of York, YO10 5GH York, U.K.
(e-mail: jqyu@ieee.org).
Xinwei Fang is with the Department of Computer Science, University of York,
YO10 5GH York, U.K. (e-mail: xinwei.fang@york.ac.uk).
Shiyao Zhang is with the School of Engineering, Great Bay University,
Dongguan 523000, China, and also with the Great Bay Institute for Advanced
Study (GBIAS), Dongguan 523000, China (e-mail: zhangshiyao@gbu.edu.cn).
Yuxin Ma is with the Department of Computer Science and Engineering, Southern University of Science and Technolgy, Shenzhen 518055, China
(e-mail: mayx@sustech.edu.cn).
Digital Object Identifier 10.1109/TKDE.2025.3536009

I. INTRODUCTION
In the ever-evolving landscape of urban development and
mobility management, the analysis and prediction of traffic data
play essential roles [1], [2]. Accurate traffic predictions allow
city planners, traffic management systems, and navigation services to anticipate and mitigate traffic issues, thereby enhancing
urban mobility [3]. By leveraging historical and real-time traffic
data, predictive models can forecast traffic dynamics, enabling
online monitoring of the transportation system and proactive
measures to traffic management [4].
In recent years, graph learning-based traffic predictors have
emerged as a dominant approach in the field of traffic data
analysis [2]. These models utilize the natural graph structure of
transportation networks, where intersections and road segments
are represented as nodes and edges, respectively. The strength of
graph-based models lies in their ability to capture the complex
spatial-temporal dependencies between these nodes, facilitating
more accurate and granular traffic predictions. By integrating
techniques such as Graph Convolutional Network (GCN) [5],
these models can effectively process and learn from the vast
amounts of spatial-temporal data generated by traffic systems,
thus significantly enhancing traffic prediction accuracy [6].
Despite their advantages, graph learning-based traffic predictors face significant challenges that impede their efficacy. The
first major challenge arises from the conventional method of
constructing graph node connectivity. Typically, these graphs
are formed based on geographic distances or traffic connectivity, ignoring the contextual relationships between nodes or the
temporal dynamics of traffic flow [7]. Static topology graphs do
not reflect the real-time, dynamic nature of traffic, which can
vary significantly due to various time-dependent factors such
as peak-valley flows [8]. There exists research on capturing
dynamic spatial correlations in spatiotemporal data by using
a learnt 3-D tensor [9]. Nonetheless, the number of additional
trainable parameters (e.g., the learnable adjacency matrix requires approx. 120M parameters for 1000-node 1-hour lookback
forecast) may overwhelm the model training process.
The second challenge pertains to the strong coupling of adjacency and data correlation learnings during model training
process used in these models. Except for static adjacency matrices, there are other traffic predictors utilizing one or more
learnable matrices to adaptively learn the adjacency relationships between nodes [10]. However, this method couples the
learning of adjacency information with that of the intrinsic

1041-4347 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

YU et al.: CLEAR: SPATIAL-TEMPORAL TRAFFIC DATA REPRESENTATION LEARNING FOR TRAFFIC PREDICTION

data correlation, leading to a complex bi-level optimization
problem. Such complexity increases the computational intensity of the training process, requesting notably more data and
computation to achieve optimal performance according to the
scaling law [11]. What makes the situation worse is that the
former typically does not have supervised loss information to
facilitate a guided search [12]. The complexity not only makes
the training process more challenging but also increases the risk
of overfitting or underfitting, thereby potentially reducing the
model’s overall effectiveness and adaptability to new data or
environments [13].
To bridge the research gap, we propose a novel CLEAR framework (Contrastive Learning of spatial-tEmporal trAffic data
Representations) specifically designed to address the aforementioned challenges in traffic prediction. CLEAR utilizes the power
of self-supervised contrastive learning [14], [15], [16] to extract
discriminative embeddings from both traffic time-series and
graph-structured data. The core principle of CLEAR revolves
around capturing intrinsic spatial and temporal correlations inherent in traffic data, leveraging these learned representations for
accurate traffic prediction, and facilitating seamless integration
with existing graph learning-based traffic predictors. CLEAR
employs a strategy of using weak and strong data augmentation
techniques to facilitate the contrastive representation learning
process, which enhances the model’s ability to understand diverse traffic patterns and respond to dynamic changes in the
network [17]. This approach allows CLEAR to dynamically
generate and update adjacency information that reflects the
real-time contextual relationships and connectivity changes over
time, effectively addressing the first challenge.
Moreover, by learning robust representations that encode essential traffic information and substituting the input data and/or
internal modules, CLEAR greatly simplifies the training process and difficulty of existing graph learning-based predictors.
Principally, CLEAR decouples the adjacency learning from data
correlation, thus mitigating the bi-level optimization complexity
associated with these models. The training of integrated models becomes more straightforward as CLEAR eliminates the
need for additional representation extraction steps during model
training [18]. By incorporating these representations, existing
predictors can also benefit from the rich semantic information
captured through self-supervised contrastive learning, thereby
enhancing their ability to model complex spatial and temporal
dependencies within traffic data, directly tackling the second
challenge.
The contributions of this paper are multifaceted:
r Design of the CLEAR Framework: We introduce CLEAR, a
novel learning framework that utilizes contrastive learning
to extract detailed and discriminative representations from
spatial-temporal traffic data. This framework is designed
to capture intrinsic correlations within traffic data to develop semantic-rich data representations for downstream
applications, e.g., traffic prediction.
r Data Augmentation Strategies: We develop specialized
data augmentation strategies that involve weak and strong
manipulation techniques. These strategies are critical for
enriching the training data and enabling the model to

1673

learn robust features from diverse traffic patterns, thereby
improving the generalizability of the learned models.
r Representation Learning Models: We devises comprehensive representation learning models for both time-series
and graph-structured traffic data. These models are capable of encoding crucial traffic dynamics into compact,
information-rich embeddings, which are essential for accurately predicting traffic conditions.
r Traffic Predictor Based on Representations: We propose a
simple-yet-effective traffic predictor that benefits from the
representations learned by CLEAR. This predictor utilizes
the embeddings to predict future traffic conditions, demonstrating how learned representations can achieve accurate
traffic predictions.
r Bootstrapping Graph Learning-Based Predictors: We
present novel bootstrapping techniques that integrate
CLEAR with existing graph learning-based predictors.
These techniques leverage the rich semantic embeddings
from CLEAR to bootstrap existing traffic prediction models for performance improvements.
The remainder of this paper is structured as follows: Section II
reviews related work in graph learning-based traffic predictors
and contrastive representation learning. Section III outlines the
preliminary definitions and problem formulation specific to this
study. Section IV details the CLEAR framework, including
our proposed data augmentation strategies and representation
learning models, and discusses the integration of CLEAR with
existing graph learning-based predictors. Section V describes
the experimental setup and presents a comprehensive evaluation
of CLEAR’s performance across various datasets. Section VI
concludes the paper, summarizing our contributions and suggesting avenues for future research.
II. RELATED WORK
In this section, we briefly review the related work on graph
learning-based traffic predictors and contrastive representation
learning. The audience are referred to [6], [19], [20], [21] for
more thorough discussions and analyses.
A. Graph Learning-Based Traffic Predictors
Graph deep learning has emerged as a transformative approach in traffic prediction, utilizing the rich spatial interconnections within traffic systems to significantly enhance prediction accuracy [6]. This evolution from traditional time-series
models to complex graph-based approaches has catalyzed the
development of more sophisticated predictive tools, capable of
understanding the intricate dynamics of traffic flow that are critical for accurate real-time traffic prediction. Given the extensive
body of related work in this field, this section focuses on a few
pivotal models due to page limits.
One of the pioneering models in this domain is Graph
WaveNet [10], which ingeniously combines graph neural networks with WaveNet’s temporal convolutional approach. This
model is designed to capture spatial dependencies through
graph convolutions while utilizing dilated causal convolutions
to handle temporal sequences efficiently. By integrating these

1674

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 37, NO. 4, APRIL 2025

two mechanisms, Graph WaveNet addresses both spatial and
temporal aspects of traffic data, leading to improved accuracy
in short-term traffic prediction. Its ability to model dynamic
spatial structures without predefined adjacency matrices sets it
apart, allowing it to adapt to various traffic scenarios and predict
potential congestions with higher precision.
Another exemplary model is the Dynamic Graph Convolutional Recurrent Network (DGCRN) [22], which introduces an
innovative approach to traffic prediction by addressing the dynamic nature of road network correlations. Unlike static models,
DGCRN uses hyper-networks to capture dynamic characteristics
from node attributes, updating the parameters of its filters at
each time step to reflect ongoing changes. This allows for the
creation of a dynamic graph that integrates with a pre-defined
static graph, offering a more accurate representation of real-time
traffic conditions.
Recently, the introduction of Transformers in traffic prediction like the Spatio-Temporal Adaptive Embedding Transformer
(STAEformer) has brought new dimensions to this field [23].
The STAEformer leverages the Transformer architecture known
for its effectiveness in natural language processing to the realm
of traffic prediction. It utilizes a novel spatio-temporal adaptive
embedding that enhances the model’s ability to capture complex
spatio-temporal relationships. STAEformer highlights the effectiveness of combining advanced embedding techniques with the
self-attention mechanism of transformers, providing a powerful
tool for traffic prediction that surpasses many traditional and
graph-based methods.
Despite these advancements, the field of graph deep learning
for traffic prediction faces several challenges. The (semi-)static
nature of many graph constructions does not reflect the dynamic
changes in real-world traffic conditions over time. Further, the
computational intensity of these models, especially those based
on transformers, poses difficulties for efficient model training
on large-scale networks.

local smoothness of time series to establish temporally stationary
neighborhoods. Further, the STEP algorithm introduces a pretraining model to spatial-temporal graph neural networks [18],
utilizing long-term historical data to enhance the contextual
understanding essential for accurate multivariate time-series
forecasting. Additionally, the Contrastive Seasonal-Trend representation learning framework (CoST) innovatively applies contrastive learning to disentangle seasonal and trend components of
time series data [28]. By incorporating both time and frequency
domain contrastive losses, CoST effectively learns discriminative features that significantly outperform traditional methods on
multivariate time series prediction, underscoring its robustness
across different neural architectures and regression models.
While the aforementioned representation learning approaches
achieve satisfactory results in general time-series tasks, their
capability of bootstrapping arbitrary graph learning-based traffic
preditors generally remains unknown. This is among the primary
objectives of CLEAR.
When confining the graph-structured data into grid-based
presentations, self-supervised learning approaches have been
applied to learn spatial-temporal representations. Notable past
efforts include [29] and [30]. In the former, the proposed ST-SSL
framework utilizes an integrated module with temporal and spatial convolutions to encode information across space and time.
It employs adaptive augmentation on traffic flow data and incorporates two self-supervised learning auxiliary tasks to enhance
the main traffic prediction task with spatial and temporal heterogeneity awareness. Further, the method in [30] introduces a
contrastive self-supervision approach to predict fine-grained urban flows by leveraging correlated spatial and temporal patterns.
It employs self-supervised tasks to extract high-level representations from flow data and utilizes a fine-tuning network combined
with three pre-trained encoder networks for enhanced performance. While both methods achieved promising results in their
respective tasks, they are limited to grid-based traffic data and
require non-trivial effort to adapt to graph-structured traffic data.

B. Contrastive Representation Learning
Contrastive representation learning develops an embedding
space where similar instances are grouped together and dissimilar ones are separated. This approach is employed across various
fields including natural language processing, computer vision,
and time-series analysis. InfoNCE loss [24], SimCLR [15], and
MoCo [25] are among the general and classical contrastive
representation learning models that utilize pairs of positive and
negative examples to refine this space, achieving robust results
and setting the foundation for more sophisticated methods.
While contrastive representation learning for traffic data is
relatively scarce, recent years have witnessed advancements
on contrastive time-series representation learning. For example,
the Time-Series representation learning framework via Temporal and Contextual Contrasting (TS-TCC) represents a significant advancement in exploiting unlabeled time-series data [26].
TS-TCC utilizes dual view augmentations to transform raw
time-series into correlated views, employing a novel temporal
contrasting module that challenges the model with a cross-view
prediction task. Another innovative approach is the Temporal
Neighborhood Coding (TNC) [27], which leverages the inherent

III. PRELIMINARIES
In this section, we first introduce the definitions and notations
to be used in this paper. Then, we define the spatial-temporal
traffic data representation learning and prediction problem.
A. Definitions
Definition 1 (Traffic Network): In this work, the traffic network is conceptualized as a directed graph G(V, E), where V
represents the set of traffic data sensing locations, such as induction loops and surveillance cameras. The nodal connectivity, E,
is typically defined by geographical adjacency, which informs
the creation of the adjacency matrix A. We contend that this
conventional approach to defining E and A fails to adequately
capture the complexities of traffic dynamics. To address this,
we advocate for the use of representation learning to develop
semantically rich embeddings that enhance our construction of
adjacency information.
Definition 2 (Spatial-temporal Traffic Data): A set of spatialtemporal traffic data comprises multiple time-dependent variables captured from traffic sensors distributed across V. This

YU et al.: CLEAR: SPATIAL-TEMPORAL TRAFFIC DATA REPRESENTATION LEARNING FOR TRAFFIC PREDICTION

1675

Fig. 1. Overall architecture of the proposed CLEAR framework. In the illustration, “T-S.” and “G. D.” denotes “time-series” and “graph data”, respectively.
“Feat. Proj.” means “Feature Projection”.

data is represented as X = {xi,t } within a real number space
R|V|×|T |×F , where T indicates the discrete time horizon of the
examined traffic data, and F denotes the types of data observed,
such as speed and flow. Notably, the traffic datasets used in
subsequent experiments are univariate (i.e., F = 1); thus, we
omit this dimension in subsequent discussions for clarity.

B. Problem Formulation
Definition 3 (Traffic Data Representation Learning): The
objective of representation learning in traffic data analysis is
to identify low-dimensional representations for the time-series
data of each traffic sensor and for the graph-structured data
encompassing all sensors at any given time. Specifically, an
embedding function ω : RT → RD maps the past T traffic observations at node i ∈ V into a D-dimensional vector in a compact latent space, where D is significantly less than |V| × |T |,
optimizing for computational efficiency and model simplicity.
Another embedding function ϑ : R|V| → RD translates all traffic
observations across V at any arbitrary point in time into a similarly concise D-dimensional embedding. These two embedding
functions are crafted to encapsulate the most informative and
compact features of both traffic time-series and graph data.
Definition 4 (Traffic Prediction): Traffic prediction aims to
forecast H-dimensional future traffic conditions based on X
by projecting the next L time steps of traffic data across all
sensors, denoted by X̂ ∈ R|V|×L×H . Drawing parallels to X,
for the traffic datasets focused on speed and flow, predictions
are typically univariate, thus H = 1 is maintained throughout
subsequent experiments to simplify the notations.
Definition 5 (Traffic Predictor Bootstrapping): Current
graph-based traffic predictors leverage spatial-temporal correlations in diverse ways. Traffic predictor bootstrapping centers
on utilizing representations derived from the well-trained embedding functions ω and ϑ. These representations replace certain
input components and/or internal modules within the predictors,
thereby enhancing prediction accuracy and streamlining model
training.

IV. CONTRASTIVE LEARNING OF SPATIAL-TEMPORAL TRAFFIC
DATA REPRESENTATIONS
In this section, we present CLEAR (Contrastive Learning of
spatial-tEmporal trAffic data Representations), a novel learning
framework designed to extract rich representations of spatial and
temporal traffic data. The design principle of CLEAR revolves
around capturing intrinsic spatial and temporal correlations inherent in traffic data, leveraging these learned representations for
accurate traffic prediction, and facilitating seamless integration
with existing graph learning-based traffic predictors.
A. Overview
Fig. 1 presents an overview to the architecture of the proposed CLEAR framework. CLEAR employs self-supervised
contrastive learning to extract discriminative embeddings from
both traffic time-series and graph data, following the SimCLR
contrastive training architecture [15]. By applying composition strategies of weak and strong data augmentation strategies, CLEAR learns robust representations that encode essential information regarding traffic flow, congestion patterns, and
anomaly detection, enabling comprehensive analysis and modeling of transportation systems. For time-series representation,
CLEAR utilizes a series of Transformer encoders to capture
long-range dependencies and develop latent representations.
Similarly, for spatial data, CLEAR employs a graph-embedded
Transformer encoder architecture to process graph-structured
data and extract spatial representations. Both are then fed into
a traffic predicting decoder to generate predictions for future
time steps.
Further, the CLEAR-learned representations can be leveraged to enhance or replace the spatial and temporal correlation
learning components of existing graph-based predictors, thus
seamlessly integrated with these predictors for performance
improvements. By incorporating these representations, existing predictors can benefit from the rich semantic information
captured through self-supervised contrastive learning, thereby
enhancing their ability to model complex spatial and temporal
dependencies within traffic data. The training of integrated

1676

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 37, NO. 4, APRIL 2025

models becomes more straightforward as CLEAR eliminates
the need for additional representation extraction steps during
model training. Note that when integrating CLEAR with existing
predictors, only the Transformer-powered time-series and graph
data encoders are adopted. The contrastive learning components,
namely, the data augmentation strategies and the contrastive loss,
are used to train the encoder parameters.
In the following sub-sections, we delve into the methodology
of CLEAR, detailing the process of representation learning
(Section IV-B and IV-C), its direct application in traffic prediction (Section IV-D), and its integration with existing traffic
predictors equipped with various spatial-temporal correlation
mining strategies (Section IV-E).
B. Traffic Time-Series Representation Learning
Understanding the temporal dynamics within traffic data is
essential for its comprehensive analysis and effective modeling.
These temporal dynamics encapsulate crucial information regarding the evolution of traffic flow, congestion patterns, and
anomaly detection, which are fundamental for devising efficient
transportation strategies and intelligent traffic management systems. Additionally, each traffic sensor possesses a time-series,
which, in the context of transportation graph G, can be regarded
as its nodal data feature. Node representations can be thereupon learnt from the corresponding time-series by adopting a
time-series encoder f T (·), and subsequently used to explore the
spatial correlation among nodes across the graph.
CLEAR utilizes self-supervised contrastive learning to construct the discriminative embedding space for traffic time-series.
Contrastive learning operates on the principle of maximizing agreement between similar instances (positive samples)
while minimizing agreement between dissimilar ones (negative samples) within a latent space. At an arbitrary time t,
each node i ∈ V has a historical traffic data feature xi,t =
{xi,t , xi,t−1 , . . . , xi,t−T +1 } ∈ RT . We employ the approach of
applying weak and strong augmentations to this time-series as
shown in Fig. 2 and perform cross-view contrastive learning to
learn robust nodal representations. Particularly, the weak augmentation is achieved by a moving-average-and-jitter strategy,
where the moving average of length M is calculated on xi,t and
the result is further perturbed by Gaussian noise N (0, σ 2 ):
2
x̃w
i,t = MA(xi,t ; M ) + N (0, σ ),

Fig. 2.

An example of the source and augmented time-series.

Fig. 3.

CLEAR time-series encoder.

(1)

where MA(·; M ) is the moving-average function with padding.
Further, the strong augmentation is done by a probablistic-swapand-jitter strategy for a more significant perturbation to the timeseries. We first divide the original time-series xi,t into chunks
xi,t [c] of length C. Then, we randomly select half of all chunks
to form a set C and apply a random permutation function π(·)
over the set. The result is subsequently perturbed by Gaussian
noise N (0, σ 2 ) to construct the strongly augmented time-series:

xi,t [π(c)] + N (0, σ 2 ) if c ∈ C
s
x̃i,t [c] =
.
(2)
otherwise
xi,t [c] + N (0, σ 2 )
As empirically demonstrated in [15], applying compositions of
data augmentation operations (principle of (1), (2)) is critical for

effective representation learning. Both augmented time-series
are then passed to the time-series encoder f T to calculate their
latent space embeddings.
As depicted in Fig. 3, encoder f T of CLEAR utilizes the
Transformer encoder architecture to capture long-range timeseries dependencies from the augmented data. f T starts with an
input 1 × 1 convolution layer to first project the traffic timeseries, typically univariate or in low dimensions, into a higherdimensional context space, which is subsequently superimposed
with a learnable positional encoding p. As the semantics of

YU et al.: CLEAR: SPATIAL-TEMPORAL TRAFFIC DATA REPRESENTATION LEARNING FOR TRAFFIC PREDICTION

time-series are generally more straightforward than languages
for which Transformer was originally designed for, we apply
three Transformer encoders over the projected input:
(0)

hi,t = Conv1×1 (x̃i,t ) + p,



(l)
(l−1)
(l−1)
+ hi,t , 1 ≤ l ≤ 3,
h̃i,t = MHA BN hi,t



(l)
(l)
(l)
hi,t = MLP BN h̃i,t
+ h̃i,t , 1 ≤ l ≤ 3,



(3)
,
hi,t = FC MeanPool hi,t

(3a)
(3b)
(3c)
(3d)

where Conv1×1 (·) is the 1 × 1 convolution, MHA(·) is
the multi-headed self-attention1 , MLP(·) is the multi-layer
perceptron with two fully-connected layers of 2048 neurons
and a non-linear ReLU activation function, BN(·) is the batch
normalization operation, FC(·) is the fully-connected layer,
and MeanPool(·) is the mean pooling operation, respectively.
Notably, a learnable positional encoding is adopted over the
canonical sinosoidal ones in favor of the former’s capability
in maintaining time-series’ periodic feature and the better experimental performance to be demonstrated in Section V-E.
Additionally, pre-norm residual links are adopted to produce
more stable gradient values during model training [32]. The
final hi,t ∈ RD is the learnt D-dimensional representation of
s
the input augmented time-series x̃i,t ∈ {x̃w
i,t , x̃i,t }.
Given an arbitrary t, there are in total |V| number of xi,t
samples in the dataset, leading to 2 × |V| augmented time-series,
T s
weakly or strongly done. We use f T (x̃w
i,t ) and f (x̃i,t ) as a
pair of positive samples, and the other augmented time-series
as negative samples. In order to further preserve the semantic
information in representations developed from f T , we concatenate the encoder with a concluding time-series feature projection
head g T (·) before training the model with contrastive loss, which
can be accordingly formulated as follows:
⎛


s

exp sim zw
i,t , zi,t /τ
T
⎝− log
 


 =
k=i
w
s
i∈V t∈T
k∈V exp sim zi,t , zk,t /τ
⎞


/τ
exp sim zsi,t , zw

 i,t   ⎠ ,
− log
(4)
k=i
s , zw
/τ
exp
sim
z
i,t
k,t
k∈V
where sim(a, b) = aT b/a · b is the cosine similarity calculation, zi,t = g T (hi,t ) = W(2) ReLU(W(1) hi,t ), and τ denotes a temperature parameter. Principally, each weakly augmented time-series is contrastively tested against all strongly
augmented time-series, and vice versa. As the contrastive loss
in (4) forces the model to learn data transformation-agnostic
projections zi,t , information useful for downstream traffic tasks
may be removed in the process [15]. The perceptron feature
projection head g T (·) is introduced to isolate this transformationinvariant training step and maintain more context in hi,t . This
hypothesis is empirically verified in Section V-E by testing the
performance of including hi,t in (4), stand-alone or jointly.
1 Following [31], we adopt eight heads in each multi-headed self-attention
calculation.

1677

C. Traffic Graph Data Representation Learning
The aforementioned time-series encoder f T (·) is not sufficient
in identifying the temporal correlation within traffic data. Rather,
it essentially embeds time-series corresponding to traffic nodes
in transportation networks, and the result indeed illustrates the
inter-nodal dependency, i.e., spatial correlation. The missed is
a graph data encoder f G (·) that takes the traffic data at an
arbitrary time to compute their embeddings, so that multiple
time instances can develop their correlation with these numerical
representations. Further, such embeddings intrinsically capture
the spatial dependency among traffic nodes in the condensed representation without confined by explicit geographical adjacency
information, thereby dynamically exploits the spatial correlation for traffic prediction. In CLEAR, we employ a contrastive
learning-based representation learning paradigm to establish the
graph data encoder, aiming at projecting traffic graph data into
a semantic-rich embedding space.
Following the same contrastive sample augmentation principle of spatial data representation learning, traffic data feature
ut = {xi,t | ∀i ∈ V} ∈ R|V| at an arbitrary time t is augmented
by a periodic-average-and-jitter strategy as the weak one and
a one-hop-average-and-jitter strategy as the strong one. Particularly, the former first calculates the average traffic data at
t and that of the same time-of-day and day-of-week in the
last week (denoted by t − 1wk), with a further Gaussian noise
perturbation:
2
ũw
t = (ut + ut−1wk )/2 + N (0, σ ).

(5)

The latter aggregates the values of one-hop neighboring nodes
for any arbitrary node, and use the Gaussian noise-perturbed
average value as the strongly augmented data:

ũst = usi,t | ∀i ∈ V ,
(6a)



xj,t / Vt1 (i; At ) + N (0, σ 2 ),
(6b)
usi,t =
j∈V 1 (i;At )

where Vt1 (·; At ) is the self-containing one-hop neighboring
function of an input node on the graph according to the adjacency
defined by At ∈ B|V|×|V| . When augmenting ut , we propose to
employ the previous spatial data representations after feature
projection zi,t to construct preliminary nodal adjacency as follows

 
at,ij = sim g T f T (xi,t ) , g T f T (xj,t ) ,
(7a)

1 if at,ij is among top − λ in{at,ik | ∀k ∈ V}
At [i, j] =
,
0 otherwise
(7b)
instead of using geographical adjacency as defined in E. Hypothetically, the projected representation embeds more semantic information about traffic dynamics than the road network
connectivity and facilitates better data augmentation on ut . We
present empirical studies in Section V-E supporting this claim.
s
With the two augmented graph data samples (ũw
t and ũt
with adjacency At ), we further adopt a variant of Transformer
architecture to process the graph-structured data, depicted in
Fig. 4. Three encoder layers are adopted after an input 1 × 1

1678

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 37, NO. 4, APRIL 2025

relationships within the input data, ultimately enabling it to
generate rich representations. The final qt ∈ RD is the learnt
s
representation of the input augmented graph data ũt ∈ {ũw
t , ũt }.
G
The contrastive loss of f (·) follows a similar principle of
f T (·). Given a traffic dataset, there are |T | graph data samples
U = {ut | t ∈ T }. The loss is accordingly defined as (c.f. (4)):


exp (sim(vtw , vts )/τ )
− log r=t
G =
w
s
r∈U exp (sim(vt , vr )/τ )
t∈T

exp (sim(vts , vtw )/τ )
,
(9)
− log r=t
s
w
r∈U exp (sim(vt , vr )/τ )

Fig. 4. CLEAR graph data encoder. The feature projection shares the same
structure as that in Fig. 3 with the linear transformations replaced by graph
convolutions.

where vt = g G (qt ) is the graph feature projection head with two
sequential graph convolution operations and a non-linear ReLU
in-between. By this design, CLEAR is capable of adaptively
capturing the dynamic spatial correlations within traffic graph
slices independently across time steps. This flexibility allows
the spatial correlation to be different over time and relaxes the
reliance on a fixed or predefined spatial structure. Furthermore,
the framework’s ability to autonomously learn spatial relationships from data aligns with the concept of adaptability seen in
advanced traffic prediction models like Graph WaveNet.
D. Traffic Prediction With Traffic Data Representations

convolution layer for feature projection:
(0)
qt = Conv1×1 (ũt ) ,
(l)



(l−1)



(l)



(l−1)



q̇t = BN qt
, q̈t = BN At qt
,


(l)
(l)
(l)
q̄t = MHA q̇t + q̇t , 1 ≤ l ≤ 3,


(l)
(l)
(l)
(l)
(l)
q̃t = MHA q̄t , q̈t , q̈t + q̄t , 1 ≤ l ≤ 3,


(l)
(l)
(l)
qt = MLP BN(q̃t ) + q̃t , 1 ≤ l ≤ 3,



(3)
(3)
qt = FC MeanPool qt At qt
,

(8e)

In the previous sub-sections, we introduced two selfsupervised representation learning models for generating taskagnostic traffic data embeddings. These representations can be
utilized in downstream traffic data mining tasks, where traffic
prediction is among the most prominent ones. The objective of
the task is to develop a prediction function f : R|V|×T → R|V|×L
that takes the historical traffic data as input and develop those
for the next L time instances.
Given the original traffic data X ∈ R|V|×|T | and xi,t ⊂
X, qt ⊂ X, CLEAR extracts the latent time-series and graph
data representations at current time t with data encoders

(8f)

hi,t = f T (xi,t ), qt = f G (ut ),

(8a)
(8b)
(8c)
(8d)

where we abuse the notation of MHA(·, ·, ·) to use the first
input as the query of multi-head self-attention and the latter
two as the key and value [31], respectively. Comparing (8)
with the standard Transformer encoder in (3), we highlight the
introduction of an additional inter-layer attention in (8d). The
model incorporates both intra-level attention (8c) and inter-level
attention (8d) mechanisms to effectively capture dependencies
and relationships within and across different levels of abstraction
in the input graph-structured. Intra-level attention facilitates
the exchange of information between nodes within the same
level of the graph hierarchy, enabling nodes to update their
embeddings based on their local neighborhoods. On the other
hand, inter-level attention allows nodes to exchange information
with neighboring nodes across different levels of abstraction,
facilitating the understanding of the global graph structure. After
(3)
the stacking encoders, the resulting output qt is passed to
a two-layer graph pooling MLP to generate the embedding.
The model thereby efficiently processes and learns complex

(10)

respectively. Subsequently, a traffic predicting decoder f F (·)
develops the predicted values. We follow the principle of Graph
Attention neTwork (GAT) [33] and devise to use the nodal relationship defined by hi,t to aggregate traffic data representations
by graph convolution defined as follows:2

h̄i =
hT
(11)
i,t hj,t W (hi,t qt ) ,
j∈V 1 (i;At )

where W ∈ RD ×2D is a trainable weight matrix. Following
the graph convolution, f F (·) adopts two convolutional layers
with kernel sizes of 1 × D and 1 × 1 and a ReLU activation
in-between, and the final output channel number is L. After
decoding, the output matrix X̂ ∈ R|V|×L corresponds to the
L-step traffic prediction of each node in V. The decoder is
2 The presented GAT-based model is among many possible choices for the
predictor. Simpler structures like MLP or more complex ones like Transformer
can also be adopted.

YU et al.: CLEAR: SPATIAL-TEMPORAL TRAFFIC DATA REPRESENTATION LEARNING FOR TRAFFIC PREDICTION

trained with mean absolute error between the predicted X̂ and
the ground truth:
F =

L
 

|x̂i,t+Δ − xi,t+Δ | .

(12)

i∈V t∈T Δ=1

E. Bootstrapping Existing Graph Learning-Based Predictors
In addition to empowering downstream traffic data mining
tasks, the learned representations from CLEAR possess versatility beyond standalone prediction models. These embeddings
can also integrate with existing graph learning-based traffic
predictors, replacing or enhancing their spatial and temporal
correlation learning components. The merit lies on a recognition
that the integration of graph structure learning and data correlation mining often presents a tightly coupled scenario, where the
learning task becomes a complex bilevel optimization problem
due to the absence of supervised loss information for graph
structure learning. This interplay underscores the importance
of devising strategies that effectively leverage learned representations to complement or bootstrap existing graph-based
predictors, decoupling the adjacency matrix learning from the
spatial-temporal data prediction task. The former is outsourced
and preprocessed by the prepositional representation learning,
so that the predictors can focus on training the forecast model
without concerning on another learning task.
Current graph learning-based predictors can be broadly categorized into four patterns based on how spatial-temporal correlation is defined or mined. By examining these patterns, we can
effectively illustrate how the representations learned by CLEAR
can be integrated with and enhance existing predictors. Each category represents a distinct strategy for capturing and exploiting
spatial-temporal correlations within traffic data, offering unique
opportunities for integration with learned representations.
Category 1 (C1): Static adjacency matrix based on geoadjacency. Using a statically defined adjacency matrix based
on nodal distance for G is arguably the most straightforward
approach for integrating domain knowledge on the spatial correlation. Example usages are presented in [34], [35]. For this
pattern, we can directly replace the original adjacency matrix,
commonly denoted by A, with At as defined in (7) to score an
intuitive-yet-effective performance improvement:
A ← At ,

(13)

where the current timestamp of prediction is adopted as the t in
At .
C2: Adaptive adjacency matrix based on representation
learning. Another commonly adopted strategy is to employ two
learnable node embedding matrices (e.g., E1 and E2 as in [10]),
whose softmax-ed multiplication softmax(ReLU(E1 ET
2 )) is
considered as the spatial dependency weights Ãadp between pairs
of nodes. For this pattern, we can also intuitively replace the
learnable weights by the time-series representations hi,t learnt
by CLEAR:


,
(14)
Ãadp ← softmax ReLU Ht HT
t

1679

where matrix Ht ∈ R|V|×D is constructed by stacking hi,t , ∀i ∈
V as rows.
C3: Spatial and temporal attention. Besides using an adjacency matrix to capture the spatial data correlation, attention
mechanism is another approach to represent the data dependency
within either the spatial domain or the temporal domain, or both.
Typically, the attention values are still derived from trainable
nodal or temporal representations, e.g., in [36], [37], which can
be substituted by CLEAR-generated ones:



α = {αi,j } = softmax ReLU (Ht W1 ) (Ht W2 )T w ,




β = {βt,τ } = softmax ReLU (QW3 ) (QW4 )T



(15a)
,
(15b)

where α and β are the attention matrices between nodes and
between timestamps, respectively, and matrix Q ∈ R|T |×D is
constructed by stacking all qt of input timestamps as rows.
C4: Spatial and temporal representation learning. There are
also graph learning-based traffic predictors that comprehensively utilize learnt spatial and temporal representations for
prediction, [23], [38] for examples. For such models, we may
directly utilize hi,t as the representation for node i, qt as the representation for time t, and hi,t qt if the representation for node
i at time t is required, respectively. One thing that may sounds
counter-intuitive is that we uses “time-series representation” hi,t
for node embedding and vice versa, yet the principle is grounded
on the fact that each node i corresponds to a hi,t at an arbitrary
time t, making it effectively representing the semantic context
of a node, i.e., node representation. The same applies for graph
data representation qt , which encapsulates context of all nodes
in the graph at time t into a dense numerical representation.
While the aforementioned bootstrapping methods apply to a
wide range of graph learning-based traffic predictors, it is essential to acknowledge that these patterns may not exhaustively
capture all strategies employed in the literature. However, their
underlying principles provide a foundation upon which both
existing and future graph learning-based traffic predictors can
be built. Each pattern offers unique opportunities for leveraging learned representations to enhance predictor performance,
demonstrating the adaptability and versatility of the CLEAR
framework in traffic data analysis and prediction.

V. EXPERIMENTS
In this section, we present a series of comprehensive experiments on four real-world datasets to show the effectiveness
of CLEAR on traffic prediction and bootstrapping other graph
learning-based predictors. We first introduce the experimental configurations, including the datasets, baseline methods,
performance evaluation metrics, and implementation details
of CLEAR. Subsequently, we answer the following research
questions (RQs) by demonstrating and discussing the simulation
results:

1680

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 37, NO. 4, APRIL 2025

TABLE I
STATISTICAL INFORMATION OF DATASETS

r RQ1: Can the traffic data representations learnt by CLEAR
provide outstanding traffic predicting accuracy compared
to state-of-the-art baselines?
r RQ2: Can CLEAR bootstrap existing graph learning-based
traffic predictors?
r RQ3: How does representations by CLEAR perform in
multi-step traffic prediction?
r RQ4: How does CLEAR improve model training efficiency?
r RQ5: How do the implementation details of CLEAR affect
bootstrapping performance?
A. Experimental Setup
1) Datasets: In this work, we conduct experiments on four
small-to-large-scale traffic prediction datasets:
r Beijing is a traffic speed dataset collected by [39] from the
major roads in Beijing, China. The dataset contains speed
values of 3126 sensors from May 12, 2022 to July 25, 2022.
Traffic speed is recorded every five minutes.
r NI-SH is a traffic speed dataset collected by NavInfo from
selected roads in Shanghai, China. The dataset contains
speed values of 1830 sensors from January 2, 2019 to June
15, 2019. Traffic speed is recorded every five minutes.
r PeMS04 is a traffic flow dataset collected by California
Transportation Agencies Performance Measurement System in the Bay Area of United States. The dataset contains
flow volumes of 307 sensors from January 1, 2018 to
February 28, 2018. Traffic volume is recorded every five
minutes.
r METR-LA is a traffic speed dataset collected from the
loop-detectors on the Los Angeles County road network
of United States. The dataset contains flow volumes of
207 sensors from March 1, 2012 to June 27, 2012. Traffic
volume is recorded every five minutes.
All four datasets are collected by different agencies. Their
statistical information is summarized in Table I. For a fair comparison, we adopt the chronological 7/1/2 split to generate the
training, validation, and testing data. Bayesian Gaussian CANDECOMP/PPARAFAC tensor decomposition model [40] is employed to interpolate the missing values in all datasets. Z-score
normalization is adopted to improve the model training stability.
2) Baselines: → + CLEAR
We select a wealth of state-of-the-art traffic prediction baseline methods in the following experiments:
r Historical Average (HA) predicts future traffic based on the
historical average traffic volume at each spatial-temporal
location.

r Vector Auto-Regression (VAR) models capture the dependencies between multiple time series variables, making
predictions based on their own lagged values and the lagged
values of other variables in the system.
r Support Vector Regressor (SVR) utilizes training data to
estimate a regression function that generalizes well to
unseen data points.
r Autoregressive Integrated Moving Average (ARIMA) is
widely used for time-series prediction by modeling the relationship between an observation and a number of lagged
observations and error terms.
r ASTGCN [35] proposes an attribute-augmented spatiotemporal graph convolutional network to enhance spatiotemporal accuracy in predicting traffic by integrating external factors as dynamic and static attributes into the model
through an attribute-augmented unit.
r STSGCN [34] captures localized spatial-temporal correlations through synchronous modeling mechanisms and
accommodating heterogeneities with multiple modules for
different time periods.
r STGODE [41] captures spatial-temporal dynamics through
tensor-based ordinary differential equations, facilitating
deeper networks and synchronous utilization of spatialtemporal features, while employing a well-designed temporal dilated convolution structure.
r Graph WaveNet [10] introduces a graph neural network
architecture designed for spatial-temporal graph modeling,
effectively capturing hidden spatial dependencies and handling long sequences with a stacked dilated 1D convolution
component.
r AGCRN [42] proposes adaptive modules, including a node
adaptive parameter learning one and data adaptive graph
generation one,to enhance graph convolutional network
capabilities for capturing fine-grained spatial and temporal
correlations in traffic series automatically.
r GMAN [37] utilizes an encoder-decoder architecture with
spatio-temporal attention blocks to model the impact of
spatio-temporal factors on traffic conditions.
r STWave+ [36] mitigates distribution shift with a
disentangle-fusion framework, employing a dual-channel
spatio-temporal network to model trends and events separately, and incorporating self-supervised learning and
multi-scale graph wavelet positional encoding for efficient
dynamic spatial correlation modeling.
r STAEFormer [43] introduces a spatio-temporal adaptive
embedding, enhancing vanilla transformers for superior
performance in traffic prediction by effectively capturing
intrinsic spatio-temporal relations and chronological information in traffic time series.
r GMSDR [38] introduces a multi-step dependency relation
scheme in recurrent neural networks, seamlessly integrating with graph-based neural networks for spatial-temporal
prediction.
r DGCRN [22] utilizes hyper-networks to extract dynamic
characteristics from node attributes, generating dynamic
graphs at each time step and integrating them with predefined static graphs, with an efficient training strategy.

YU et al.: CLEAR: SPATIAL-TEMPORAL TRAFFIC DATA REPRESENTATION LEARNING FOR TRAFFIC PREDICTION

Fig. 5.

1681

Performance comparison of baselines, CLEAR-bootstrapped baselines, and the CLEAR Predictor.

Among the baselines, HA, VAR, SVR, and ARIMA are
statistical methods, while all others are state-of-the-art graph
learning-based traffic predictors.
3) Performance Metrics: We evaluate the performance of
CLEAR and all baseline methods by three widely-adopted metrics in traffic prediction [10], [23], [36], [37], namely, Mean
Absolute Error (MAE), Root Mean Square Error (RMSE), and
Mean Absolute Percentage Error (MAPE).
4) Implementation Details: We set the prediction horizon L
to 12. The length of time-series in generating their corresponding
representation T is set to the number of samples in one day, i.e.,
288 at a 5min sampling interval. The dimensionality D of learnt
traffic data representations (hi,t and qt ) is 256. The movingaverage horizon M in (1) is set to 12. The probablistic-swap
length C in (2) is set to 2h. The nodal adjacency threshold λ in
(7) is empirically set to the total number of edges in each dataset’s
geographical adjacency matrix. The number of attention heads
in Transformer encoders is set to 8. We adopted the Adam
optimizer [44] with an initial learning rate of 5 × 10−4 and
weight decay of 10−4 . We applied a mini-batch size of 128.
CLEAR and baseline methods are implemented with Python and
Pytorch. All experiments are conducted on the Viking cluster
provided by the University of York with NVIDIA H100 GPUs.
B. Traffic Prediction Performance (RQ1, RQ2)
In this sub-section, we present empirical results on employing the proposed CLEAR for traffic prediction and bootstrapping graph learning-based traffic predictors. Among the baseline approaches, ASTGCN, STSGCN, and STGODE are C1

predictors c.f. Section IV-E, Graph WaveNet and AGCRN are
C2 predictors, GMAN and STWave+ are C3 predictors, STAEFormer, GMSDR, and DGCRN are C4 predictors. We test all
baselines, their CLEAR-bootstrapped variants (Section IV-E),
and the CLEAR predictor (Section IV-D) on all four datasets.
The traffic predicting accuracy statistics are presented in Fig. 5
and Table II. Each graph learning-based baselines has the results
from both its original model (denoted by its name) and the
corresponding CLEAR-bootstrapped variant, denoted by the
following line with the tag “ → + CLEAR”. Fig. 5 presents
the comparison of all baselines, and their CLEAR-bootstrapped
variants, and the CLEAR predictor. Note that HA, VAR, SVR,
and ARIMA do not have CLEAR-bootstrapped variants, as
they are not graph learning-based predictors. CLEAR predictor
cannot be further bootstrapped. Additionally, Table II provides
the numerical results of the best-performing approaches for a
more precise comparison. In the table, top-3 performance from
all baselines and CLEAR predictor is underlined.
We first use Fig. 5 and Table II to answer RQ1, i.e., does the
CLEAR predictor work well in traffic prediction when compared
with state of the arts. The simulation results indicate that the
CLEAR predictor, even with a quite simplistic convolutional
representation decoder, can achieve the 3 rd best prediction performance in Beijing dataset, the 2nd in NI-SH, 4th in PeMS04,
and 3 rd in METR-LA regarding MAE. While STAEFormer
develops better predicting results in the first three datasets over
CLEAR predictor, the MAE performance gap is not overwhelming: 0.111km/h on Beijing, 0.047km/h on NI-SH, and 0.408vh
on PeMS04. Indeed, the best performing baseline on METR-LA,
DGCRN, outperforms the CLEAR predictor by 0.029 km/h.

1682

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 37, NO. 4, APRIL 2025

TABLE II
NUMERICAL RESULTS OF BEST-PERFORMING BASELINES, CLEAR-BOOTSTRAPPED BASELINES, AND THE CLEAR PREDICTOR

TABLE III
RELATIVE MAE IMPROVEMENT / DEGRADATION OF ADOPTING CLEAR TO
BOOTSTRAP BASELINES

We credit the outstanding plain performance of STWave+ and
STAEFormer to their effective exploitation of traffic representations, which primarily relies on discrete wavelet transform
and Transformer. In this context, the GAT-CNN-CNN structure
adopted by CLEAR Predictor c.f. Section IV-D is far from as
with efficacy, resulting in the performance gap. We further tested
offline with a straightforward linear projection decoder head in
place of the GAT-CNN-CNN structure on Beijing dataset: MAE
performance minusculely drops to 3.238 at an approximately
0.56% relative degradation. Consequently, our answer to RQ1
is, though not the best-performing method, the CLEAR predictor can provide outstanding and highly competitive predictions
compared with the state-of-the-art baselines.
What makes CLEAR truly stand out is its superior bootstrapping capability. To make the statistics more comprehensible,
we summarize the relative MAE improvement/degradation of
adopting CLEAR to bootstrap graph learning-based predictors
in Table III. The table indicates that the traffic data representations generated by CLEAR can almost consistently improve

the predicting accuracy of all graph learning-based predictor
baselines. The improvement is particularly notable on datasets
with large and complex transportation networks (Beijing and
NI-SH) and baselines with relatively straightforward spatialtemporal correlation mining strategies. Particularly, C1, C2, and
C3 predictors experience an average 10.171% improvement on
MAE. These results demonstrates the superiority of CLEAR
representations on bootstraping graph learning-based traffic predictors for better spatial-temporal data correlation mining on
large graphs. The other datasets, namely, PeMS04 and METRLA have much smaller graphs and respectively noncomplex
spatial-temporal correlation. Therefore, existing predictors are
more likely to exhaustively exploit such correlation for traffic
prediction. Nonetheless, CLEAR can still improve the predicting
accuracy by approximately 3.832% for the first three categories.
This can be attributed to the more semantic-rich time-variant
adjacency matrix (C1), more robust representation-based adjacency matrix (C2), and better semantic-empowered attention
scores (C3) developed by CLEAR.
Moving forward to C4-type predictors, we figured that the
2.518% improvements, while still statistically significant with
node-wise Wilcoxon signed-rank tests, are not as remarkable
as the first two categories. This observation is grounded on the
nature of these baselines, which also explicitly extract spatial and
temporal traffic data representations by learnable parameters.
As a result, well-trained baseline models, in principle, can learn
semantic-rich embeddings for the downstream prediction task.
In the meantime, the incorporation of CLEAR relieves the training difficulty by decoupling the graph structure learning (i.e.,
representation learning) from the main data correlation mining
during model optimization. We may expect, and get verified in
Section V-D, that the computation burden and training time of
respective models can be non-trivially reduced. Datasets with
large graphs but less samples can benefit more from CLEAR
bootstrapping, as the spatial-temporal correlation mining is more
challenging. Alongside being a computationally efficient representation learning substitute for C4 predictors, CLEAR can
still obtain better prediction results due to the lighter training
difficulty. Therefore, we conclude that CLEAR can bootstrap
existing graph learning-based traffic predictors with notable
accuracy improvements (RQ2).

YU et al.: CLEAR: SPATIAL-TEMPORAL TRAFFIC DATA REPRESENTATION LEARNING FOR TRAFFIC PREDICTION

1683

Fig. 6. Multi-step MAE performance of graph learning-based predictor baselines and their respective CLEAR-bootstrapped variants on the Beijing and PeMS04
datasets.

TABLE IV
RELATIVE PERFORMANCE IMPROVEMENT OF CONTRASTIVE
REPRESENTATION FRAMEWORKS ON BEIJING DATASET

Fig. 7.
ysis.

Lastly, we adopt the current art of contrastive representation
learning frameworks, namely, TS-TCC, TNC, and CoST, to
bootstrap the best-performing graph learning-based predictors
(STWave+ and STAEFormer). The publicly available source
code of respective frameworks is utilized to generate representations for traffic time-series, and the same bootstrapping
strategies in Section IV-E is applied. Simulation results on
Beijing dataset are presented in Table IV, indicating that CLEAR
outperforms all contrastive representation learning frameworks

Visualization of CLEAR representations by principal component analin enhancing the predicting accuracy of graph learning-based
predictors. We further visualize the representations learnt by
CLEAR on the Beijing dataset by principal component analysis
in Fig. 7. The graph data representations in Fig. 7(a) are colorcoded by the time-of-day, and each point in Fig. 7(b) refers
to the traffic dynamics of a sensor. The scatter plots shows
that the contrastive representation learning effectively groups
similar traffic dynamics and repels opposite ones. We credit the

1684

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 37, NO. 4, APRIL 2025

performance of CLEAR to its ability to effectively capture both
temporal and spatial dependencies within traffic data, which are
essential for accurate traffic prediction but the latter is missing
in compared frameworks.
C. Multi-Step Prediction Performance (RQ3)
Multi-step traffic prediction also plays a pivotal role in the
efficacy of graph learning-based traffic predictors, as it enables
insights into traffic trends and patterns over extended periods and
allows for better downstream services. Therefore, investigating
how representations by CLEAR perform in multi-step traffic
prediction scenarios is essential for comprehensively evaluating
their effectiveness and applicability in real-world traffic prediction tasks.
In this sub-section, we extend the prediction horizon to
12 steps, i.e., 1h, on the Beijing and PeMS04 datasets for their
distinct network sizes, with all graph learning-based predictor
baselines and their respective CLEAR-bootstrapped variants.
The simulation results are depicted in Fig. 6, where the horizontal axes denote the predicting horizon from one to twelve
and the vertical axes are the MAE values in km/h (Beijing)
and vh, respectively. From the plots, it can be observed that
the performance improvement of CLEAR over all baselins are
further enlarged with the expanding predicting horizon. On
the larger-scale Beijing dataset, the four types of predictors
embrace 13.342%, 12.566%, 10.519%, and 8.354% MAE improvements at the 12th predicting horizon, leading to an overall
average 11.126% performance boost c.f. 8.909% at the first step.
The advancement persists on the smaller PeMS04 dataset with
the corresponding type improvements at the 12th horizon to be
6.764%, 5.595%, 5.009%, and 3.588%, overall an 5.226% up
from the first step 3.056%. The substantial gains achieved by
CLEAR across multiple prediction steps underscore its effectiveness in capturing and leveraging long-term temporal and
spatial dependencies within traffic data, affirming its potential
to significantly enhance the capabilities of graph learning-based
traffic predictors in real-world applications (RQ3).
D. Model Training Efficiency (RQ4)
Efficiency in model training is a crucial aspect in the development and deployment of machine learning models, particularly
in the context of large-scale traffic prediction tasks. With the
ever-increasing volume and complexity of traffic data, the computational resources required for training graph learning-based
traffic predictors can become a bottleneck, hindering the scalability and practicality of these models. Therefore, investigating
how CLEAR improves model training efficiency is essential for
assessing its feasibility and effectiveness in real-world applications.
In this sub-section, we delve into a comprehensive analysis
of the size, computational complexity, and training time of
both baseline models and their CLEAR-bootstrapped variants.
Particularly, we calculate the number of trainable parameters,
floating-point operations (FLOPs) for each forward pass calculation on the large-scale Beijing dataset, and measure the
relative model training time reduced without and with CLEAR

bootstrapping strategies. The empirical results are presented in
Table V. In this table, we also present the relative parameter and
FLOPs reduction by introducing CLEAR as well as the relative
training time changed besides the raw data. Note that for the
relative training time changed column, two values are presented
where the former employs available CLEAR representations
and the latter includes the CLEAR model training time over
the respective base model’s.
The simulation result table clearly indicate that CLEAR can
effectively reduce the model size (# parameters) and complexity
(# FLOPs) for C2, C3, and C4 baselines, thereby improves the
model training efficiency. This can be credited to the decoupling of graph structure learning and the main data correlation
mining, where the former is pre-achieved by CLEAR. Further, the semantic-rich adjacency matrices employed in C1-type
baselines, while do not reduce the model footprint, help the
model converge faster with efficacy. When we take the CLEAR
model training time into account, Graph WaveNet experience a
non-negligible increase in the total training time. Nonetheless,
considering its performance gain (+10.368% c.f. Table I) and
relative short base model training time (approx. 2.6h), we consider CLEAR still an effective bootstrapping method for Graph
WaveNet.
E. Ablation Study (RQ5)
In the design of CLEAR, we adopt a few structural designs
to improve model capacity and facilitate better performance.
Particularly, we employ a learnable positional encoding (Learn
PE) for time-series in (3) substituting the more straightforward sinusoidal encoding, pre-norm residual connections (Pre-N
Res.) in (3), (8) instead of the post-norm connection proposed
in [31], and feature projection heads (Proj. Head) g T (·) and
g G (·) following [15]. Finally, we adopt the contrastive learning
paradigm to train the representation learning model.
To verify their efficacy in the model performance, we construct a series of CLEAR ablations and test their performance
on the Beijing dataset with both the Graph WaveNet base model
and the CLEAR predictor. We create a series of CLEAR variants
with tags “A” to “G” to denote the ablation of the Learn PE,
Pre-N Res. and Proj. Head designs. Additionally, we remove the
contrastive learning parts in CLEAR, namely, data augmentation
and contrastive loss (replaced by reconstruction loss), to create
the ablated model “CLEAR” with a variant “CLEAR-PH” that
further removes the projection head layers. Note that Beijing
dataset is selected for its large-scale traffic network size. Table VI
presents the experimental results. Comparing the performance
metrics among different rows, an easy conclusion can be made
that all the designs contribute to better CLEAR performance in
terms of both traffic prediction and predictor bootstraping, and
the contrastive learning paradigm plays a critical part in generating semantic-rich representations. The results generally accord
with previous studies on the respective designs, namely, [15],
[32], [45]. One minor discrepancy lies in the performance boost
by projection heads, which lead to over 10% improvement rather
than the approximately 3% in Table VI. We hypothesize that the
information loss induced by the contrastive loss, conjectured

YU et al.: CLEAR: SPATIAL-TEMPORAL TRAFFIC DATA REPRESENTATION LEARNING FOR TRAFFIC PREDICTION

1685

TABLE V
MODEL SIZE, COMPLEXITY, AND TRAINING TIME REDUCTION ON BEIJING DATASET

TABLE VI
ABLATION PERFORMANCE OF CLEAR ON BEIJING DATASET

in [15], is less significant on time-series and graph data than
images as originally investigated. Despite this trivial difference,
the simulation results verify and agree with the literature that
the feature projection heads indeed introduces more robust and
semantic-rich data representations for downstream tasks, i.e.,
traffic prediction in this context.
F. Discussion on Limitations
The proposed CLEAR framework demonstrates significant
advancements in spatial-temporal traffic data representation
learning but is not without limitations. The complexity of the
framework, particularly its reliance on dual-branch contrastive
learning and Transformer-based encoders, introduces computational overhead that might limit its scalability in resourceconstrained environments. Additionally, CLEAR depends on
complete input data for representation extraction, which could
restrict its applicability to datasets with missing or noisy observations: further data imputation approaches are required as
pre-processors and they may undermine the representation learning performance. Further, while CLEAR decouples adjacency
matrix learning from spatial-temporal correlation extraction,
this approach may not outperform the ideal case of tightly

coupled learning in scenarios with abundant computational resources, training data, and carefully tailored models. Though the
GAT-based predictor within CLEAR performs competitively,
its relatively simple architecture does not outperform certain
state-of-the-art predictors, emphasizing CLEAR’s role as a representation learning framework over a standalone predictor.
Despite these limitations, CLEAR’s ability to enhance the performance of existing graph-based predictors highlights its practicality and potential for impact. By decoupling adjacency matrix
learning from spatial-temporal correlation extraction, CLEAR
reduces the training complexity of integrated models and offers a
flexible, task-agnostic representation learning paradigm. Future
work could address these limitations by exploring data imputation mechanisms, simplifying the architecture, and adapting
CLEAR for a broader range of traffic analytics task decoders.
VI. CONCLUSION
This paper introduces the CLEAR (Contrastive Learning of
spatial-tEmporal trAffic data Representations) framework that
leverages the power of self-supervised contrastive learning to
extract meaningful embeddings from both traffic time-series
and graph-structured data, facilitating more accurate traffic

1686

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 37, NO. 4, APRIL 2025

predictions. By employing both weak and strong data augmentation techniques, CLEAR enhances its robustness and
generalization in generating semantic-rich data representations
within diverse traffic datasets. Its specialized models capture
critical temporal and spatial dependencies, allowing seamless
integration with existing traffic prediction models, increasing
their accuracy and reducing model training complexity without
significant modifications.
Experimental evaluations across four real-world datasets validate CLEAR’s superior ability to predict future traffic and
bootstrap graph learning-based predictors. Multi-step prediction
tests and ablation studies confirm its robustness and the strategic
efficacy of its design, and a thorough look into the model training
efficiency indicate its efficiency in decoupling the graph adjacency learning and data correlation learning processes during
training. These experiments substantiate the framework’s utility
in real-world applications, making it a promising approach to be
integrated in traffic prediction methods.
Looking ahead, the CLEAR framework opens several avenues
for further research. Future work could explore the extension
of this framework to other types of downstream intelligent
transportation tasks. As the CLEAR framework is designed to
be modular and flexible, it can be adapted to other traffic-related
tasks with tailor-made representation decoders, somehow similar to the Traffic Prediction Decoder in Fig. 1. Additionally,
further refinement of the data augmentation and representation
learning techniques could yield even more robust models capable of handling increasingly complex datasets.
REFERENCES
[1] S. Guo, Y. Lin, H. Wan, X. Li, and G. Cong, “Learning dynamics and
heterogeneity of spatial-temporal graph data for traffic forecasting,” IEEE
Trans. Knowl. Data Eng., vol. 34, no. 11, pp. 5415–5428, Nov. 2022.
[2] D. A. Tedjopurnomo, Z. Bao, B. Zheng, F. M. Choudhury, and A. K. Qin,
“A survey on modern deep neural network for traffic prediction: Trends,
methods and challenges,” IEEE Trans. Knowl. Data Eng., vol. 34, no. 4,
pp. 1544–1561, Apr. 2022.
[3] J. Liu et al., “Urban flow pattern mining based on multi-source heterogeneous data fusion and knowledge graph embedding,” IEEE Trans. Knowl.
Data Eng., vol. 35, no. 2, pp. 2133–2146, Feb. 2023.
[4] L. Lin, J. Li, F. Chen, J. Ye, and J. Huai, “Road traffic speed prediction: A
probabilistic model fusing multi-source data,” IEEE Trans. Knowl. Data
Eng., vol. 30, no. 7, pp. 1310–1323, Jul. 2018.
[5] T. N. Kipf and M. Welling, “Semi-supervised classification with graph convolutional networks,” in Proc. Int. Conf. Learn. Representations, Toulon,
France, 2017, pp. 1–14.
[6] S. Rahmani, A. Baghbani, N. Bouguila, and Z. Patterson, “Graph neural
networks for intelligent transportation systems: A survey,” IEEE Trans.
Intell. Transp. Syst., vol. 24, no. 8, pp. 8846–8885, Aug. 2023.
[7] Y. Li, R. Yu, C. Shahabi, and Y. Liu, “Diffusion convolutional recurrent
neural network: Data-driven traffic forecasting,” in Proc. Int. Conf. on
Learn. Representations, Vancouver, Canada, 2018, pp. 1–16.
[8] J. J. Q. Yu, “Graph construction for traffic prediction: A data-driven
approach,” IEEE Trans. Intell. Transp. Syst., vol. 23, no. 9, pp. 15 015–15
027, Sep. 2022.
[9] L. Han, B. Du, L. Sun, Y. Fu, Y. Lv, and H. Xiong, “Dynamic and multifaceted spatio-temporal deep learning for traffic speed forecasting,” in
Proc. ACM SIGKDD Conf. Knowl. Discov. Data Mining, Singapore, 2021,
pp. 547–555.
[10] Z. Wu, S. Pan, G. Long, J. Jiang, and C. Zhang, “Graph WaveNet for deep
spatial-temporal graph modeling,” in Proc. Int. Joint Conf. Artif. Intell.,
Macao, China, 2019, pp. 1907–1913.
[11] Y. Bahri, E. Dyer, J. Kaplan, J. Lee, and U. Sharma, “Explaining neural
scaling laws,” Proc. Nat. Acad. Sci. USA, vol. 121, no. 27, Jun. 2024,
Art. no. e2311878121.

[12] L. Franceschi, M. Niepert, M. Pontil, and X. He, “Learning discrete
structures for graph neural networks,” in Proc. Int. Conf. Mach. Learn.,
2019, pp. 1–20.
[13] H. Lin, Y. Fan, J. Zhang, and B. Bai, “REST: Reciprocal framework for spatiotemporal-coupled predictions,” in Proc. Web Conf., 2021,
pp. 3136–3145.
[14] S. Chopra, R. Hadsell, and Y. LeCun, “Learning a similarity metric discriminatively, with application to face verification,” in Proc. IEEE Comput.
Soc. Conf. Comput. Vis. Pattern Recognit., 2005, pp. 539–546.
[15] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, “A simple framework
for contrastive learning of visual representations,” in Proc. Int. Conf. Mach.
Learn., 2020, pp. 1597–1607.
[16] Y. Gong, T. He, M. Chen, B. Wang, L. Nie, and Y. Yin, “Spatio-temporal
enhanced contrastive and contextual learning for weather forecasting,”
IEEE Trans. Knowl. Data Eng., vol. 36, no. 8, pp. 4260–4274, Aug. 2024.
[17] Y. Tian, C. Sun, B. Poole, D. Krishnan, C. Schmid, and P. Isola, “What
makes for good views for contrastive learning,” in Proc. Adv. Neural Inf.
Process. Syst., 2020, pp. 6827–6839.
[18] Z. Shao, Z. Zhang, F. Wang, and Y. Xu, “Pre-training enhanced spatialtemporal graph neural network for multivariate time series forecasting,” in Proc. ACM SIGKDD Conf. Knowl. Discov. Data Mining, 2022,
pp. 1567–1577.
[19] X. Luo, C. Zhu, D. Zhang, and Q. Li, “STG4Traffic: A survey and benchmark of spatial-temporal graph neural networks for traffic prediction,”
Jul. 2023, arXiv:2307.00495.
[20] X. Ren, W. Wei, L. Xia, and C. Huang, “A comprehensive survey on selfsupervised learning for recommendation,” Apr. 2024, arXiv:2404.03354.
[21] T. Uelwer et al., “A survey on self-supervised representation learning,”
Aug. 2023, arXiv:2308.11455.
[22] F. Li et al., “Dynamic graph convolutional recurrent network for traffic
prediction: Benchmark and solution,” ACM Trans. Knowl. Discov. Data,
vol. 17, no. 1, pp. 9:1–9:21, Feb. 2023.
[23] M. Liu, H. Huang, H. Feng, L. Sun, B. Du, and Y. Fu, “PriSTI: A
conditional diffusion framework for spatiotemporal imputation,” in Proc.
IEEE Int. Conf. Data Eng., 2023, pp. 1927–1939.
[24] A. van den Oord, Y. Li, and O. Vinyals, “Representation learning with
contrastive predictive coding,” Jul. 2018, arXiv: 1807.03748.
[25] K. He, H. Fan, Y. Wu, S. Xie, and R. Girshick, “Momentum contrast for
unsupervised visual representation learning,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2020, pp. 9726–9735.
[26] E. Eldele et al., “Time-series representation learning via temporal and
contextual contrasting,” in Proc. Int. Joint Conf. Artif. Intell., 2021,
pp. 2352–2359.
[27] S. Tonekaboni, D. Eytan, and A. Goldenberg, “Unsupervised representation learning for time series with temporal neighborhood coding,” in Proc.
Int. Conf. Learn. Representations, 2021, pp. 1–17.
[28] G. Woo, C. Liu, D. Sahoo, A. Kumar, and S. Hoi, “CoST: Contrastive
learning of disentangled seasonal-trend representations for time series
forecasting,” in Proc. Int. Conf. Learn. Representations, 2022, pp. 1–17.
[29] J. Ji et al., “Spatio-temporal self-supervised learning for traffic flow
prediction,” in Proc. AAAI Conf. Artif. Intell., 2023, pp. 4356–4364.
[30] H. Qu, Y. Gong, M. Chen, J. Zhang, Y. Zheng, and Y. Yin, “Forecasting
fine-grained urban flows via spatio-temporal contrastive self-supervision,”
IEEE Trans. Knowl. Data Eng., vol. 35, no. 8, pp. 8008–8023, Aug. 2023.
[31] A. Vaswani et al., “Attention is all you need,” in Proc. Adv. Neural Inf.
Process. Syst., 2017, pp. 6000–6010.
[32] R. Xiong et al., “On layer normalization in the transformer architecture,”
in Proc. Int. Conf. Mach. Learn., 2020, pp. 10 524–10 533.
[33] P. Veličković, G. Cucurull, A. Casanova, A. Romero, P. Liò, and Y. Bengio,
“Graph attention networks,” in Proc. Int. Conf. Learn. Representations,
2018, pp. 1–12.
[34] C. Song, Y. Lin, S. Guo, and H. Wan, “Spatial-temporal synchronous graph
convolutional networks: A new framework for spatial-temporal network
data forecasting,” in Proc. AAAI Conf. Artif. Intell., 2020, pp. 914–921.
[35] J. Zhu, Q. Wang, C. Tao, H. Deng, L. Zhao, and H. Li, “AST-GCN:
Attribute-augmented spatiotemporal graph convolutional network for traffic forecasting,” IEEE Access, vol. 9, pp. 35 973–35 983, 2021.
[36] Y. Fang et al., “When spatio-temporal meet wavelets: Disentangled traffic
forecasting via efficient spectral graph attention networks,” in Proc. IEEE
Int. Conf. Data Eng., 2023, pp. 517–529.
[37] C. Zheng, X. Fan, C. Wang, and J. Qi, “GMAN: A graph multi-attention
network for traffic prediction,” in Proc. AAAI Conf. Artif. Intell., 2020,
pp. 1234–1241.
[38] N. Liu, X. Wang, D. Bo, C. Shi, and J. Pei, “Revisiting graph contrastive
learning from the perspective of graph spectrum,” in Proc. Adv. Neural Inf.
Process. Syst., 2022, pp. 1–12.

YU et al.: CLEAR: SPATIAL-TEMPORAL TRAFFIC DATA REPRESENTATION LEARNING FOR TRAFFIC PREDICTION

[39] Z. Cai et al., “MemDA: Forecasting urban time series with memory-based
drift adaptation,” in Proc. ACM Int. Conf. Inf. Knowl. Manage., 2023,
pp. 193–202.
[40] X. Chen, Z. He, and L. Sun, “A Bayesian tensor decomposition approach
for spatiotemporal traffic data imputation,” Transp. Res. Part C, Emerg.
Technol., vol. 98, pp. 73–84, Jan. 2019.
[41] Z. Fang, Q. Long, G. Song, and K. Xie, “Spatial-temporal graph ODE
networks for traffic flow forecasting,” in Proc. ACM SIGKDD Conf. Knowl.
Discov. Data Mining, 2021, pp. 364–373.
[42] L. Bai, L. Yao, C. Li, X. Wang, and C. Wang, “Adaptive graph convolutional recurrent network for traffic forecasting,” in Proc. Adv. Neural Inf.
Process. Syst., 2020, pp. 17 804–17 815.
[43] H. Liu et al., “Spatio-temporal adaptive embedding makes vanilla transformer SOTA for traffic forecasting,” in Proc. ACM Int. Conf. Inf. Knowl.
Manage., 2023, pp. 4125–4129.
[44] D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,”
in Proc. Int. Conf. Learn. Representations, 2015, pp. 1–15.
[45] G. Zerveas, S. Jayaraman, D. Patel, A. Bhamidipaty, and C. Eickhoff, “A
Transformer-based framework for multivariate time series representation
learning,” in Proc. ACM SIGKDD Conf. Knowl. Discov. Data Mining,
2021, pp. 2114–2124.

James Jianqiao Yu (Senior Member, IEEE) received
the BEng and PhD degree in electrical and electronic
engineering from the University of Hong Kong, Pokfulam, Hong Kong, in 2011 and 2015, respectively.
He is a professor with the School of Computer Science and Technology, Harbin Institute of Technology, Shenzhen. He was a postdoctoral fellow with
the University of Hong Kong from 2015 to 2018.
He held professorship/lectureship with the Southern
University of Science and Technology, China and
University of York, U.K. from 2018 to 2024. His
general research interests are in data mining, multi-modal learning, intelligent
transportation systems, and embodied artificial intelligence. His work is now
mainly on spatial-temporal data mining, multi-modal foundation model, and
forecasting and logistics of future transportation systems. He has published
more than 100 academic papers in top international journals and conferences,
and representative papers have been selected as ESI highly cited papers. He was
the World’s Top 2% Scientists since 2020 and of career by Stanford University.
He is an Editor of IEEE Transactions on Intelligent Transportation Systems and
IET Smart Cities.

1687

Xinwei Fang is a lecturer with the Department of
Computer Science at the University of York, U.K. His
research focuses on the design and development of
trustworthy autonomous systems by understanding,
detecting, and mitigating uncertainties that may arise
at various stages of these systems through methods such as machine learning, model checking, and
statistical analysis.

Shiyao Zhang (Member, IEEE) received the BS degree (Hons.) in electrical and computer engineering
from Purdue University, West Lafayette, IN, USA, in
2014, the MS degree in electrical engineering from
the University of Southern California, Los Angeles,
CA, USA, in 2016, and the PhD degree from the
University of Hong Kong, Hong Kong SAR, China,
in 2020. He was a postdoctoral research fellow with
the Academy for Advanced Interdisciplinary Studies, Southern University of Science and Technology
from 2020 to 2022, and a research assistant professor
with the Research Institute for Trustworthy Autonomous Systems, Southern
University of Science and Technology from 2022 to 2024. He is currently
an assistant professor with the School of Engineering, Great Bay University.
His research interests include intelligent transportation systems, autonomous
driving, embodied AI, and transportation electrification.

Yuxin Ma (Senior Member, IEEE) received the BEng
and PhD degrees from Zhejiang University, China. He
is a tenure-track associate professor with the Department of Computer Science and Engineering, Southern
University of Science and Technology (SUSTech),
China. Before joining SUSTech, he worked as a postdoctoral research associate in VADER Lab, CIDSE,
Arizona State University. His primary research interests are in the areas of visualization and visual analytics, focusing on explainable AI, high-dimensional
data, and spatiotemporal data.
PAPER_TEXT
