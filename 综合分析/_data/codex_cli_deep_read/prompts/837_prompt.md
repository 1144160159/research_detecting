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
# [837] Unraveling Spatio-Temporal Foundation Models via the Pipeline Lens: A Comprehensive Review
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
编号：837
题名：Unraveling Spatio-Temporal Foundation Models via the Pipeline Lens: A Comprehensive Review
年份：2026
DOI：10.1109/tkde.2026.3651536
来源：IEEE Transactions on Knowledge and Data Engineering
PDF：paper/10.1109_TKDE.2026.3651536.pdf
已有粗分类：数据集、基准、综述与开源工具
二级关联：时序、日志、KPI 与云原生异常检测
相关性：弱相关，分数 4
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\837.txt
- 原始字符数：144788
- 本次发送字符数：140043
- 是否截断：True

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
2040

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 3, MARCH 2026

Unraveling Spatio-Temporal Foundation Models via
the Pipeline Lens: A Comprehensive Review
Yuchen Fang, Hao Miao , Yuxuan Liang , Member, IEEE, Liwei Deng , Yue Cui ,
Ximu Zeng , Graduate Student Member, IEEE, Yuyang Xia, Yan Zhao , Senior Member, IEEE,
Torben Bach Pedersen , Senior Member, IEEE, Christian S. Jensen , Fellow, IEEE,
Xiaofang Zhou , Fellow, IEEE, and Kai Zheng , Senior Member, IEEE
(Survey Paper)

Abstract—Spatio-temporal data proliferates in numerous
real-world domains, such as transportation, weather, and energy.
Spatio-temporal deep learning models aims to utilize useful
patterns in such data to support tasks like prediction, imputation,
and anomaly detection. However, previous one-to-one deep learning
models designed for specific tasks typically require separate
training for each use case, leading to increased computational and
storage costs. To address this issue, one-to-many spatio-temporal
foundation models have emerged, offering a unified framework
capable of solving multiple spatio-temporal tasks. These foundation
models achieve remarkable success by learning general knowledge
with spatio-temporal data or transferring the general capabilities
of pre-trained language models. While previous surveys have
explored spatio-temporal data and methodologies separately, they
have ignored a comprehensive examination of how foundation
models are designed, selected, pre-trained, and adapted. As a result,
the overall pipeline for spatio-temporal foundation models remains
unclear. To bridge this gap, we innovatively provide an up-to-date
review of previous spatio-temporal foundation models from the
pipeline perspective. The pipeline begins with an introduction
to different types of spatio-temporal data, followed by details of
data preprocessing and embedding techniques. The pipeline then
Received 6 May 2025; revised 3 November 2025; accepted 26 December
2025. Date of publication 12 January 2026; date of current version 13 February
2026. This work was supported in part by NSFC under Grant 62472068, in part
by the Municipal Government of Quzhou under Grant 2024D036, and in part
by DFF Inge Lehmann under Grant 4303-00014. Recommended for acceptance
by Y. Gao. (Corresponding authors: Yan Zhao; Kai Zheng.)
Yuchen Fang, Ximu Zeng, and Yuyang Xia are with the University of
Electronic Science and Technology of China, Chengdu 610054, China (e-mail:
fangyuchen@std.uestc.edu.cn; ximuzeng@std.uestc.edu.cn; xiayuyang@std.
uestc.edu.cn).
Hao Miao is with the The Hong Kong Polytechnic University, Hong Kong
SAR, China (e-mail: hao.miao@polyu.edu.hk).
Yuxuan Liang is with the Hong Kong University of Science and Technology,
Guangzhou Guangzhou 510530, China (e-mail: yuxliang@outlook.com).
Liwei Deng, Torben Bach Pedersen, and Christian S. Jensen are with Aalborg
University, 9220 Aalborg, Denmark (e-mail: lide@cs.aau.dk; tbp@cs.aau.dk;
csj@cs.aau.dk).
Yue Cui and Xiaofang Zhou are with the Hong Kong University of Science and Technology, Hong Kong SAR, China (e-mail: ycuias@cse.ust.hk;
zxf@me.com).
Yan Zhao is with the Shenzhen Institute for Advanced Study, University of
Electronic Science and Technology of China, Shenzhen 518100, China (e-mail:
zhaoyan@uestc.edu.cn).
Kai Zheng is with the University of Electronic Science and Technology
of China, Chengdu 610054, China, and also with the Shenzhen Institute for
Advanced Study, University of Electronic Science and Technology of China,
Shenzhen 518100, China (e-mail: zhengkai@uestc.edu.cn).
Digital Object Identifier 10.1109/TKDE.2026.3651536

presents a novel data property taxonomy to divide existing methods
according to data sources and dependencies, providing efficient and
effective model design and selection for researchers. On this basis,
we further illustrate the training objectives of primitive models, as
well as the adaptation techniques of transferred models. Overall,
our survey provides a clear and structured pipeline to understand
the connection between core elements of spatio-temporal
foundation models while guiding researchers to get started quickly.
Additionally, we introduce emerging opportunities such as multiobjective training in the field of spatio-temporal foundation models,
providing valuable insights for researchers and practitioners.
Index Terms—Foundation models, spatio-temporal data, pretraining, adaptation.

I. INTRODUCTION
PATIO-TEMPORAL data are continuously generated from
various real-world domains including transportation, energy, and weather. These data inherently exhibit an intricate
temporal evolution over time and complex spatial interactions
across different regions [1]. Various types of spatio-temporal
data (e.g., trajectory data, traffic data, and video data) share
common challenges in capturing spatio-temporal dependencies,
requiring specialized methods to competently extract inherent
correlations. The mining and analysis of these spatio-temporal
correlations play a crucial role in building intelligent systems,
enabling real-world applications to support decision-making in
fundamental tasks including planning, reasoning, and anomaly
detection.
In recent years, considerable progress has been made in
spatio-temporal data mining by one-to-one specialized models
based on the development of deep learning. These methods
lie in the spatio-temporal modeling capabilities of sequential
and spatial neural networks, such as recurrent neural networks
(RNNs) [2], Transformers [3], convolution neural networks
(CNNs) [4], and graph neural networks (GNNs) [5]. Nevertheless, addressing the wide range of spatio-temporal tasks across
diverse applications requires training numerous task-specific
models, which demands substantial computational resources
and incurs significant costs. Fortunately, with the advent of
self-supervised learning strategies and the discovery of scaling
laws [6], foundation models have been designed in the natural

S

1041-4347 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

FANG et al.: UNRAVELING SPATIO-TEMPORAL FOUNDATION MODELS VIA THE PIPELINE LENS: A COMPREHENSIVE REVIEW

2041

TABLE I
COMPARISON BETWEEN OUR SURVEY AND RELATED SURVEYS. COMMON SPATIO-TEMPORAL DATA CATEGORIES CONSIDERED IN THIS SURVEY—TRAJECTORIES
(T), EVENTS (E), ST GRIDS (G), VIDEOS (V), AND ST GRAPHS (H). THE CLASSIFICATION CRITERIA ARE DETAILED IN SECTION II. FOR TRAINING PRIMITIVE
MODELS, OBJECTIVES INCLUDE REGRESSION (R), MASKED MODELING (M), CONTRASTIVE (C), AND DIFFUSION (D). MOREOVER, THE ADAPTATION TECHNIQUES
FOR TRANSFERRED MODELS INCLUDE PROMPT ENGINEERING (P), FEATURE ENHANCEMENT (F), CROSS-DOMAIN ALIGNMENT (A), AND SUPERVISED
FINE-TUNING (S).

Fig. 1.

The paradigm of spatio-temporal foundation models (STFMs).

language processing and computer vision communities to universally solve multiple tasks through resource-efficient few-shot
fine-tuning or even resource-free zero-shot prompting without
additional training [7], [8].
With the remarkable success of foundation models in natural
language processing (e.g., ChatGPT), the concept of one-tomany foundation models has been introduced as an attractive
and promising direction in spatio-temporal communities. As
illustrated in Fig. 1, the goal of spatio-temporal foundation
models is to learn general spatio-temporal knowledge within a
single universal model. This enables the same model to handle a
wide range of spatio-temporal tasks across different applications
and objectives, significantly reducing the reliance on numerous
task-specific models and thus lowering both training and storage
costs. By increasing the training scale of spatio-temporal data
and using general self-supervised learning objectives to derive
primitive foundation models, or transferring the general knowledge of pre-trained foundation models from other fields such
as natural language processing to derive transferred foundation
models, the effectiveness of current spatio-temporal foundation
models has been validated on various tasks, showing the promising prospect of the universal framework to advance this field.
Despite recent improvements of spatio-temporal foundation
models (STFMs), existing surveys on this topic still face several
key challenges. 1) Weak linkage between data and models:
As illustrated in Table I, while previous surveys do describe
various categories of spatio-temporal data, they often overlook
critical steps in the data harmonization process such as embedding techniques. This omission creates confusion regarding
how spatio-temporal data is effectively aligned with foundation

models. 2) Lack of property consideration: Prior surveys tend to
adopt coarse-grained classifications of STFMs (e.g., data type
and deep learning methodology perspectives) without explaining why similar methodologies are applied to different data that
share common characteristics. These taxonomies ignore deep insights from data properties in selecting or designing foundation
models. 3) Fragmented presentation: Existing surveys tend to
discuss spatio-temporal data, foundation models, training objectives, and transfer adaptation techniques in isolation. This siloed
approach prevents a cohesive understanding of what models, objectives, and adaptation strategies should be utilized for different
spatio-temporal tasks, datasets, and real-world applications.
To address the issue of fragmented descriptions, our survey
offers a comprehensive examination of the entire pipeline of
spatio-temporal foundation models (STFMs), systematically
presenting the workflow from data harmonization and model
conception to training, adaptation, and real-world application.
In addition to a brief overview of spatio-temporal data and
available datasets, our survey—illustrated in the bottom of
Fig. 2—provides a detailed account of data preprocessing, embedding techniques, and side information associated with various spatio-temporal data categories, thereby completing the first
stage of the STFM pipeline: data harmonization. By leveraging
side information and appropriate preprocessing methods, the
quality of spatio-temporal data can be significantly enhanced,
which in turn improves the performance of STFMs. Furthermore, due to the unique characteristics of spatio-temporal data
such as spatial and temporal dependencies, which differ fundamentally from other data types (e.g., language data), embedding
techniques play a critical role in aligning data with STFMs.
These techniques effectively bridge the gap between raw spatiotemporal data and model input representations.
The second step of STFM pipelines is to construct models
based on diverse data. To mitigate the confusion brought by the
coarse-grained data type or methodology taxonomies, as shown
in the middle of Fig. 2, we present a data property taxonomy
on STFMs. At the top of our taxonomy, STFMs are classified
into two main categories: primitive and transferred models.
This classification is based on whether the models are trained
directly on primitive spatio-temporal data or transferred from
models that are pre-trained on other data, such as text-based
language models or image-based vision models. Furthermore,
we divide not only primitive models into temporal, spatial,
and spatio-temporal classes according to clear data dependencies, but also transferred models into vision, language, and

2042

Fig. 2.

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 3, MARCH 2026

The pipeline of STFMs.

multi-modal classes based on the available data modalities. The
data property taxonomy provides efficient and effective model
design and selection because deep learning methods used for
the same category under our taxonomy are based on the same
data sources, dependencies, or modalities and can be extended
to other data types.
The third stage of STFM pipelines delves into training objectives for primitive models and adaptation techniques for
transferred models, as shown in the top of Fig. 2. Through an indepth analysis of these methodologies, we highlight their respective advantages and challenges across different data categories,
tasks, or application scenarios. In the final stage of the pipeline,
we examine the current applications of STFMs, showcasing
their broad real-world impact across domains such as energy,
finance, weather, healthcare, transportation, and public services,
as illustrated in Fig. 1.
By presenting clear and step-by-step pipelines, our survey not
only organizes and clarifies the core components of STFMs but
also highlights the deeper connections between them, facilitating
the rapid and effective deployment of these models. Moreover,
as shown in Table I, existing surveys often overlook key aspects
such as essential spatio-temporal data types, training objectives,
and adaptation techniques, resulting in an incomplete understanding of STFMs. Our survey addresses this gap by covering
the most comprehensive range of these elements, providing a

more holistic perspective on available data sources and their
corresponding model training and adaptation methods. Finally,
we discuss the current challenges facing STFMs and explore
future opportunities for advancing the field.
The main contributions of this survey are summarized as
follows.
r Comprehensive and up-to-date review. Our paper presents
the most extensive and current survey of spatio-temporal
foundation models (STFMs), covering a broad spectrum
of data types, models, training objectives, and adaptation
techniques.
r Novel property taxonomy. We propose an innovative data
property taxonomy that categorizes STFMs from coarse to
fine levels based on data sources and their dependencies,
enabling more efficient and effective model design and
selection.
r Novel pipeline-oriented survey. To the best of our knowledge, this is the first survey to examine STFMs from a
pipeline perspective, offering the research community a
systematic understanding of how these models are developed and why they achieve superior performance.
r Identification of future research opportunities. We outline
key challenges in applying foundation models to spatiotemporal tasks, with the goal of guiding future research
and inspiring the development of more advanced STFMs.

FANG et al.: UNRAVELING SPATIO-TEMPORAL FOUNDATION MODELS VIA THE PIPELINE LENS: A COMPREHENSIVE REVIEW

2043

TABLE II
SUMMARY OF NOTATION

The structure of our survey is as follows. We begin by reviewing the crucial data harmonization process in Section II. Following this, Section III focuses on the model design and training
objectives of primitive foundation models. Next, in Section IV,
we delve into transferred foundation models, exploring model
selection and transfer adaptation. Section V introduces a broad
range of applications where spatio-temporal foundation models have demonstrated significant impact. Beyond the pipeline
aspects, Section VI identifies emerging opportunities and open
research challenges in the field. Finally, Section VII provides a
conclusion of the key components of our survey.
II. DATA HARMONIZATION
As shown in the bottom of Fig. 2, data harmonization is the
first step of pipelines to align raw spatio-temporal data with deep
learning methods, which have three important components. The
left element is preprocessing, which demonstrates data standardization (e.g., noise filtering) and feature extraction (e.g., temporal pattern decoupling) processes. The middle element is embedding, which transforms preprocessed data into low-dimensional
numerical representations, including tokenization techniques to
break data into smaller units, spatial embeddings to capture spatial relationships, temporal embeddings to encode time-related
features, and frequency embeddings to analyze frequency-based
characteristics. Moreover, incorporating additional information
through retrieval, exogenous data, and multi-modal inputs can
further improve the performance of STFMs. The pipelines from
preprocessing to embedding generation, enhanced by side information, create rich and structured representations of data for
STFMs.
However, spatio-temporal data vary widely in format, resolution, acquisition methods, and semantics, so the community employs data harmonization practices tailored to each
category. We therefore organize them into five canonical
categories—trajectory, event, video, spatio-temporal grid, and
spatio-temporal graph—using two orthogonal criteria: (i) spatial
dynamics and (ii) data acquisition. Spatially, video, ST grid, and
ST graph data are anchored to fixed spatial units (pixels, cells,
sensors/nodes), whereas trajectories and events involve moving
entities or discrete occurrences not tied to a fixed unit. By acquisition, ST grids typically come from satellite or reanalysis products, ST graphs from fixed sensor networks or infrastructure,
videos from cameras, trajectories from GPS/mobile devices,
and events from reporting news or logs. These criteria yield
distinct representations and feature structures: videos as dense
3-channel sequences on a pixel, ST grids as multi-band fields
over regular cells, ST graphs as node time series with irregular
spatial distributions, trajectories as variable-length coordinate
sequences, and events as sparse time-stamped records with
categorical attributes. Because data formats, feature schemas,
and acquisition characteristics differ, preprocessing, embedding,
and auxiliary-information integration strategies are not identical.
Accordingly, we introduce each category in turn below.
To improve readability and reduce potential ambiguity, we
provide a comprehensive notation table (Table II) that consolidates all symbols used throughout the paper.

A. Trajectory Data
1) Data Description: Spatio-temporal trajectory data, such
as vehicle and pedestrian trajectories, refer to sequences of
movement locations recorded with specific timestamps by edge
devices like mobile phones, which can be formulated as X =
{(lt , τt )|t = 1, 2, . . ., N } ∈ RN ×3 , where lt = (lngt , latt ) denotes the location of the tth point, τt represents the recorded
time stamp of the tth point, and N denotes the length of the
input trajectory [14], [15], [16].
2) Data Preprocessing: To train a foundation model with
high-quality spatio-temporal trajectory data, many data preprocessing methods have been proposed such as trajectory
compression, noise filtering, and map-matching. Specifically,
UniTraj [17] filters out meaningless short trajectories and unrealistic fast trajectories, and PTR [18] inserts placeholder tokens
into low-sampling trajectories to transform them into a uniform
sampling interval. Besides, map-matching techniques [19] are
commonly used in many methods [17], [18], [20], [21] to align
recorded spatio-temporal trajectories with realistic road network
paths. This is necessary since edge devices used for recording
trajectories suffer from errors by building obstructions, poor
phone service, and receiver noise [22].
3) Data Embedding: To incorporate spatio-temporal patterns of individual trajectories into foundation models, various spatio-temporal embeddings are used in current methods.
KGTS [23] uses a knowledge graph to bring local spatial information into spatial embeddings, MMTEC [24] provides an
index-fetching technique to add spatial semantic information of
road segments into spatial embeddings, and GTR [25] combines
the graph- and segment-based spatial information as comprehensive embeddings. RETE [26] leverages learnable Fourier embedding to capture periodicity in distance and time intervals, and
UniTraj [17] uses rotary position embedding [27] to maintain
spatio-temporal relative positional information of trajectories
for capturing patterns. Moreover, PTR [18] and START [20]
introduce time-of-day and day-of-week temporal embeddings
to assist foundation models in learning personalized behavior
patterns at specific times. With the assistance of powerful spatiotemporal patterns and travel semantics, trajectory foundation
models can be universally adapted to diverse downstream tasks.

2044

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 3, MARCH 2026

4) Side Data: To further enhance the understanding of travel
semantics in trajectories of foundation models, external text descriptions of locations and POI categories are used as additional
information [18], [28]. Moreover, geographic features such as
road network data can constrain trajectories to valid routes [29],
[30] and time-related features such as day-of-week can influence
commuting patterns in human mobility trajectories [18].
B. Event Data
1) Data Description: Spatio-temporal event data, such as
political events and epidemic outbreaks, refer to a series of
quintuples (s, r, o, l, t), where s and o are entities, r is a binary
relation between s and o, l, and t indicate the location and
time when event (s, r, o) occurs, respectively. Notably, although
location information is often ignored by existing event-related
models, the quintuple formulation provides a more general
representation of an event. Moreover, t is generally a discrete
representation of time, such as day, week, and month, which is
based on the practical requirements of an application.
2) Data Preprocessing: Spatio-temporal event data are often
represented by graph structures to better model the underlying
dependencies among entities and relations. For example, ONSEP [31] uses a temporal knowledge graph (TKG) to structure the time-sequenced events as a series of multi-relational
directed graphs denoted as T KGt = {G1 , G2 , . . . , Gt }, where
each Gi = (V, R, Ei ) consists of the events in time i. Here, V
and R denote the sets of entities and relation types, respectively,
and Ei contains a set of event quintuples at time stamp t.
Similarly, Xia et al. [32] explore and incorporate high-order
historical dependencies in TKGs into large language models to
improve event inference accuracy. Different from these studies
that transform the event forecasting problem into a knowledge
graph completion task, Deng et al. [33] focus on political
event forecasting and instead formulate it as a classification
problem. Specifically, they divide features into two categories,
i.e., static Sl and dynamic Xt−k+1:t,l , for each location l, and
aim to learn a classifier f (Sl , Xt−k+1:t,l ) → Yt∗ ,l that maps the
input to a binary event vector Yt∗ ,l ∈ {0, 1}M at the future time
stamp t∗ for the target location l. Here, Sl denote a set of static
features such as population and political ideology, Xt−k+1:t,l
are the collection of dynamic features for location l before time
stamp t within a historical window, and M indicates the number
of possible event types that can occur concurrently, where the
dynamic features can include TKGs or other data formats.
3) Data Embedding: In order to precisely forecast the occurrence of an event, various sources of information, including
text content and causal relationships among events, need to be
taken into account. For example, DynamicGCN [34] constructs
dynamic graphs based on document-based point-wise mutual
information, where each node represents a word extracted from
an article. These nodes are then encoded with word embedding
vectors pre-trained on the Wikipedia database [35]. Recently,
numerous methods have incorporated large language models
(LLMs) for event forecasting [31], [32], [36], [37], [38], [39].
These methods typically encode historical events by prompt
engineering techniques and use LLM-derived text embeddings

for reasoning and prediction. For example, Yuan et al. [39]
utilize an explainable TKG reasoning model, e.g., TLogic [40],
to generate reasoning path embeddings between entities s and
o, and then generate the prediction and explanation by polished
or revised prompts.
4) Side Data: Generally, events can be concisely represented
as quintuples (s, r, o, l, t), denoting the entity, relation, location,
and time. Such a representation has been commonly employed
in existing graph-based event forecasting studies [41], [42], as
it effectively captures the structural relationships among events.
Nevertheless, such representations often lack the rich contextual
information needed for accurate forecasting. To address this
limitation, researchers incorporate side information, such as
retrieved news articles [31] and generated content [39], which
provide additional context relevant to specific query events. For
instance, Yuan et al. [39] devise a prompt-based mechanism to
exploit the generative potential of ChatGPT, thereby generating
more diverse and coherent context documents in response to a
given query event. This enriched context helps improve both the
precision and robustness of event forecasting models.
C. Spatio-Temporal Grid Data
1) Data Description: Spatio-temporal grid data, such as traffic flow, crime, and weather data, consist of sequential observations over regularly partitioned grids that span cities or
larger geographical areas. These data sequences are typically
collected from either automated sources (e.g., satellites, sensors)
or human-reported statistics. Formally, this type of data can be
C
formulated as X ∈ RL×H×W ×C , where xi,j
t ∈ R indicates the
collected features of the grid cell in the ith row and j th column
at time stamp t. Next, L, H, W , and C denote the length of the
sequence, the number of rows in the grid data, the number of
columns in the grid data, and the number of features collected
per grid cell, respectively.
2) Data Preprocessing: To address the issue of varying data
scales in training a foundation model, normalization methods,
such as Z-score [43] and Min-Max [44] normalization, are
commonly applied to transform features into a fixed range. To
reduce computation needs in training foundation models with
high spatial resolutions, a patching technique is used to merge
some adjacent grids into a patch [45]. In detail, the original
spatial resolution H × W will be patched into a small feature
W
map with the resolution H̄ × W̄ , where H̄ = H
h , W̄ = w , and
h × w is the size of each patch. Moreover, 3D patching is
further adopted on spatio-temporal grid data to merge grids from
spatio-temporal dimensions simultaneously [44], i.e., the shape
L × H × W is patched into L̄ × H̄ × W̄ , where L̄ = Ll and
the patch size is l × h × w. Besides, to extract seasonal and
trend information, methods like Fast Fourier transform (FFT)
and daily flashback techniques are often used, capturing essential
temporal patterns that enhance model understanding [46], [47].
3) Data Embedding: Projection layers are typically used
to transform numerical spatio-temporal grid data into highdimensional representations. To preserve the order and proximity of spatio-temporal grid data within Transformers, diverse positional embedding techniques are designed, including temporal

FANG et al.: UNRAVELING SPATIO-TEMPORAL FOUNDATION MODELS VIA THE PIPELINE LENS: A COMPREHENSIVE REVIEW

embeddings (e.g., learnable embeddings [43] or sinusoidal encodings [44]) and spatial embeddings (e.g., earth-specific positional biases [45] and ground sample distance embeddings [48]).
Moreover, task-specific embeddings are applied to the variability
in feature types and dimensions across different datasets and
tasks [49], ensuring flexibility and alignment with different
tasks.
4) Side Data: Spatio-temporal grid tasks incorporate various
external features, including temporal features like holiday, time
of day, and day of week; environmental features like temperature
and wind speed (beyond the primary input); and spatial features
like POI category distributions and structural attributes of road
networks. These external features are either directly integrated
into primitive foundation models or converted into textual descriptions for transferred foundation models [46], [50].

D. Video Data
1) Data Description: Spatio-temporal video data is composed of a series of consecutive images. Each image is formed
by regularly spaced pixels with RGB colors, which can be
3
formulated as X ∈ RL×H×W ×3 , where xi,j
t ∈ R indicates the
th
th
RGB values of the pixel in the i row and j column of the
tth frame. Next, L, H, and W denote the number of frames in
the video and the spatial resolution (height and width) of each
frame, respectively.
2) Data Preprocessing: Similar to spatio-temporal grid data,
video data often require patching when processed by models
without the pre-trained vision foundation models [51], where
the patched shape is L̄ × H̄ × W̄ with the patch size l × h × w.
Notably, video data can be directly fed into pre-trained vision
foundation models, e.g., ViT [52], without any preprocessing
operations [53], [54].
3) Data Embedding: For foundation models that do not use
pre-trained vision backbones, pre-trained tokenization models,
such as VQ-GAN and VQ-VAE, should be utilized on the video
data to transform raw pixels into discrete embedded tokens [55],
[56]. Alternatively, pre-trained image models, such as CLIP ViTL/14 [57], are leveraged to process each video frame independently instead of using pre-trained video models to embed pixels
into visual features with temporal semantics [58], [59]. To obtain
LLM-compatible embeddings for video understanding tasks,
models like pre-trained Q-former from BLIP [60] should be
applied on each embedded frame followed by pre-trained image
models [53], [54]. Moreover, temporal positional embeddings
can be added to frame-level representations after embedding
the video data since temporal dependencies are often ignored in
pre-trained tokenization, vision, and multi-modal models [61].
4) Side Data: Video-text pairs from text corpora are essential
external factors for multi-modal video tasks, such as video
question answering and video understanding [58], [59]. For
single-modality-based prediction tasks, captions of each frame
should be automatically derived through pre-trained visionlanguage models [62]. Moreover, the audio modality and future
action conditions are often considered as auxiliary information
to support video-based tasks [61], [62].

2045

E. Spatio-Temporal Graph Data
1) Data Description: Spatio-temporal graph data, such as
traffic speed, electroencephalography (EEG), and electricity
data, refer to sequential observations recorded by irregularly
distributed sensors in a spatial modeled as graphs. This type of
data can be defined as X ∈ RL×N ×C , where xnt ∈ RC denotes
the feature vector recorded by sensor n at time stamp t. Next,
L, N , and C denote the length of the sequence, the number of
observations, and the number of features for each observation.
The key difference between spatio-temporal grid data and graph
data lies in how spatial correlations are defined. In graph data,
spatial correlations are manually defined by various spatial
metrics rather than relying on explicitly adjacent grid cells, as
is the case with grid data.
2) Data Preprocessing: For learning intricate temporal patterns of spatio-temporal graph data, time series decoupling
techniques such as wavelet decomposition and seasonal-trend
decomposition procedure based on loess are applied on spatiotemporal graph data to isolate different temporal patterns and
avoid mutual influence [63], [64], [65]. Moreover, long spatiotemporal graph sequences are typically selected as input for
most STFMs [66], [67], [68]. The input sequence with length
L is segmented into L̄ non-overlapping patches to decrease the
complexity of the foundation models, because the information
density of original spatio-temporal graph sequences is lower
than texts, where the temporally patched sequences can be
mathematically formulated as L̄ = Ll , and l denotes the capacity
of each patch. Moreover, to efficiently model the spatial dimension of graph data, an irregular spatial patching technique has
been proposed [69]. Specifically, indices of N observations are
reordered so that spatially adjacent observations are arranged
consecutively, allowing N to be divided into N̄ non-overlapping
patches. This segmentation decreases the complexity of the
spatial dimension, where the spatially patched sequences can
be mathematically formulated as N̄ = N
n , where n denotes the
capacity of each patch.
3) Data Embedding: To further enable the foundation models to grasp structural and periodic characteristics of spatiotemporal graph data, various temporal and spatial embeddings
have been proposed and integrated as part of the model inputs. For example, the learnable point embeddings [66], [67],
fixed point embeddings (e.g., day-of-week embeddings [68],
[70], [71]), and power spectral density-based frequency embeddings [65], [72] have been successively proposed as temporal
embeddings, serving as one of the model’s input components.
In terms of spatial embeddings, sinusoidal embeddings [68], distance embeddings [73], and eigenvectors-based graph spectral
embeddings [71] are utilized to inject essential spatial structure
information into foundation models. By incorporating these
spatial, temporal, frequency, and spectral embeddings, spatiotemporal graph foundation models gain a deeper understanding
of the structural and periodic nature of spatio-temporal graph
data, significantly enhancing their generalization capabilities
across diverse tasks and domains.
4) Side Data: Similar to spatio-temporal grid tasks, spatiotemporal graph tasks also incorporate temporal features like

2046

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 3, MARCH 2026

TABLE III
SUMMARY OF USED DATASETS IN STFMS

holiday, time of day, and day of week and spatial factors like POI
category distributions and structural attributes of road networks.
Moreover, as weather is correlated with wind power generation,
temperature and humidity are often used as exogenous variables
in spatio-temporal graph-based power foundation models [74].
F. Representative Datasets and Statistics
The emergent abilities of general-purpose models are heavily
influenced by the size and quality of the training data. This
suggests that as the model encounters more diverse and highquality data, it becomes more capable of generalizing across a

wide range of tasks. For spatio-temporal models, which capture
patterns over both space and time, the diversity and richness of
the data are crucial for effectively identifying complex spatiotemporal relationships. As illustrated in Table III, we summarize
the trajectory, event, spatio-temporal grid, video, and spatiotemporal graph datasets adopted across different spatio-temporal
foundation models, including the spatial size, temporal range,
sampling interval of the temporal dimension, and the recorded
features of data.
These datasets are widely used in various real-world applications, e.g., transportation, weather, healthcare, energy, financial, and public services. As shown in Table III, one of the

FANG et al.: UNRAVELING SPATIO-TEMPORAL FOUNDATION MODELS VIA THE PIPELINE LENS: A COMPREHENSIVE REVIEW

significant challenges highlighted is the variability across
datasets, even within the same application domain (e.g., transportation or healthcare). For example, spatial size, temporal
range, and sampling intervals can differ widely, making it difficult for a single foundation model to generalize across these
differences. This could lead to issues where a model trained on
one dataset performs poorly on another due to the mismatched
characteristics of the data. The heterogeneity of the datasets adds
complexity to model training and deployment, as models may
struggle to adapt to different scales and granularities of data.
Another challenge is the comparison between the scale of spatiotemporal datasets and that of LLMs. Spatio-temporal datasets
tend to be much smaller in scale, often in the million-item
range, compared to LLMs, which can be trained on datasets with
billions of items. This suggests that while LLMs benefit from
massive amounts of data, spatio-temporal foundation models
may have limited scalability due to the smaller size and specialized nature of the datasets available. The fact that many smaller
datasets are used to train these models indicates that scaling them
up to the same size as LLMs may not be feasible, or at least may
not yield the same performance improvements. On the other
hand, the statement about scaling laws also hints at a potential
trade-off between data quality and quantity for spatio-temporal
foundation models. While increasing the quantity of data might
improve a model’s performance, the effectiveness of spatiotemporal models might be more dependent on the quality and
relevance of the data rather than sheer size. This is particularly
important in fields like healthcare, weather, or transportation,
where specific domain knowledge and high-quality data may
matter more than the raw scale. In summary, the heterogeneity of
spatio-temporal data poses challenges, and while scaling these
models is important, it’s likely that other factors such as data
quality and domain relevance will play a more significant role
in improving performance than only increasing dataset size.
III. PRIMITIVE SPATIO-TEMPORAL FOUNDATION MODELS
As an essential branch of spatio-temporal foundation models,
primitive models refer to foundation models pre-trained with
primitive spatio-temporal data, which can be generalized across
different downstream tasks. To derive primitive spatio-temporal
foundation models, as illustrated in Fig. 2, model architectures
need to be carefully designed based on spatio-temporal properties of the embedded data. Then the presented primitive STFM
is trained with specific self-supervised learning objectives to
achieve general capabilities according to the input data category
and the applied downstream task. We present the detailed model
design and objectives below.
A. Model Design
In this study, we present the model design of STFMs according
to three categories: temporal models, spatial models, and spatiotemporal models. For temporal models, spatial dependencies are
not taken into account due to insignificant spatial distinguishability of spatio-temporal data [106]. For spatial models, temporal
dependencies are not taken into account because of unclear
and unstable temporal patterns of spatio-temporal data [106].

2047

For spatio-temporal models, spatio-temporal dependencies are
simultaneously needed because of the significant spatial distinguishability and temporal patterns of the input data.
1) Temporal Models: A key aspect of primitive spatiotemporal foundation models is to capture the complex temporal
dependencies, such as trend and seasonality [107]. Specifically, to model short-term temporal dependencies, recurrent
neural networks, such as GRU [108] and LSTM [109], are
often adopted, especially for spatio-temporal trajectory and
graph data [72], [110], [111]. However, recurrent neural networks fall short in capturing long-term temporal dependencies [112]. To address this problem, Vanilla Transformer is
utilized in temporal-only foundation models, e.g., TrajFM [113],
UniTraj [17], EEGPT [114], and STD-MAE [68], to model
long-term temporal dependencies. In particular, patch embedding layers are often used before Transformers for long-term
spatio-temporal graph data [66], [115], with the aim of reducing computation costs. Further, the pure MLP architecture is
adopted in TTM [116] to substitute Transformers for efficient
long-term time series modeling. In terms of efficient trajectory
modeling, the neural controlled differential equation is proposed in MMTEC [24]. In addition to the above-mentioned
discriminative foundation models, diffusion model based methods [117] have also been proposed for generative tasks, e.g., ControlTraj [30] and Score-CDM [63]. For conditional temporalonly diffusion models, the attention mechanism is widely used
in the denoising networks to learn temporal patterns from conditional input. For example, ControlTraj [30] and FGTI [64]
adopt geo-attention and time-frenquency attention to learn road
constraints in trajectory generation and frequency knowledge
in spatio-temporal graph imputation, respectively. Besides, frequency kernel supported global convolution is proposed as the
denoising network in Score-CDM [63] to replace attention for
spatio-temporal graph imputation.
Beyond architectural considerations, temporal-only models
are primarily suited to data whose generative process is dominated by time-evolving dynamics and exhibits clear temporal
regularities. Typical inputs include ST graph data (e.g., energy demand, financial indicators, physiological signals such as
EEG/ECG), event sequences, and temporally ordered trajectories when spatial heterogeneity is weak or explicitly controlled.
In these settings, temporal models are appropriate because their
inductive bias emphasizes sequence order, enabling efficient
representation learning even when spatial coordinates are noisy,
sparse, or non-informative.
2) Spatial Models: Topology-constrained spatio-temporal
data often exhibit complex spatial dependencies [118], including
local and global spatial correlations [107]. Local spatial correlations are always reflected by the first law of geography, i.e.,
things that are near are more related than things that are far
away. Moreover, global spatial correlations also exist in spatiotemporal data due to the regional functionality. Thus, another
line of research focuses on capturing spatial correlations by
means of foundation models for spatio-temporal data. To model
local spatial dependencies, existing studies often use graph
neural networks in various tasks [119], [120] with a pre-defined
topology (e.g., road networks and paths) [121]. However, it is

2048

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 3, MARCH 2026

difficult to fully pre-define the complex spatial dependencies by
spatial topologies, where global spatial correlations are often
ignored [99], [118]. To address this problem, Vision Transformers are utilized in foundation models to capture global spatial
dependencies of spatio-temporal grid data [43], [48], [49], [122],
[123]. Further, UniST [44] and PanGu-Weather [124] apply
the Vision Transformer on the 3D-patched grid data to capture
cross-time spatial dependencies. Moreover, FourCastNet [125]
leverages the Fourier neural operator to substitute the attention
mechanism in Transformers for efficient grid data-based global
spatial correlations modeling. To combine the advantages of
graph neural networks and Transformers, G2PTL [73] integrates
the graph Transformer into the geography foundation model,
where the spatial correlation matrix calculated by attention
is refined by a pre-defined spatial topology and thus a more
realistic matrix is derived. Moreover, generative foundation
models with only spatial diffusion are also explored for crime
risk inference [88] and trajectory generation [126]. Specifically,
the concatenation-based conventional U-Net [88] and the crossattention enhanced U-Net [46] are used in the diffusion model
to capture conditional spatial knowledge of grid data effectively.
Models that focus exclusively on spatial dependencies are
preferentially applied to data where the principal signal is encoded in the spatial arrangement, topology, or field structure
and temporal variation is either negligible or can be aggregated.
Representative inputs include static or quasi-static grids (remote sensing imagery, climate reanalyses at single time slices),
videos, and spatial fields derived from PDEs. In these settings,
temporal sampling is sparse, asynchronous, or confounded by
nonstationary regimes, spatial-only modeling can avoid spurious
temporal signals and yield stable estimates driven by geometry,
adjacency, and regional functional dependencies.
3) Spatio-Temporal Models: Spatio-temporal models aim
to learn intricate spatial and temporal correlations simultaneously [71], [74]. Orginally, the trajectory foundation model
KGTS [23] combines recurrent neural networks and graph neural networks to learn temporal and spatial correlations, respectively. Recently, to efficiently capture long-term temporal dependencies, temporal convolutions and Transformers emerge, which
are combined with graph neural networks to build foundation
models across spatio-temporal data [20], [71], [127], [128]. On
the spatial aspect, the traditional graph neural networks with
limited local receptive fields are also upgraded by hypergraph
neural networks, hierarchical graph neural networks, and Transformers in spatio-temporal graph and grid tasks [65], [74], [87]
due to their capabilities to capture global spatial correlations.
Moreover, MSTEM [129] integrates all of the spatio-temporal
convolutions and spatio-temporal Transformers into one foundation model to learn long-short spatio-temporal knowledge for
event forecasting. For generative conditional diffusion models, spatio-temporal convolutions and Transformers are often
chosen as the denoising network for historically-concatenated
spatio-temporal graph data [130], [131]. Moreover, in addition to
spatio-temporal Transformers, spatio-temporal cross-attention
is used on unmasked trajectories in the traffic signal control
model DiffLight [132] to capture spatio-temporal condition
information.

Fig. 3. The regression modeling objective, where and indicate the unknown
future observation and active parameters, respectively.

While integrating spatial and temporal modules can yield
richer representations, the effectiveness of spatio-temporal fusion depends on data properties and the fusion strategy. Gains
are most likely when clear temporal patterns coexist with meaningful spatial heterogeneity or inter-location coupling, whereas
weak temporal regularity or spatial indistinguishability can limit
the benefit. Therefore, model design should be informed by diagnostics of temporal autocorrelation, spatial correlation scales,
and cross-lag dependencies.
B. Training Objectives
Training objectives are also crucial for primitive STFMs, and
aim to guide the direction of model updates for achieving satisfactory results. We present four promising training objectives
in STFMs. We begin with regression modeling, exploring how
it learns universal historical knowledge. Then, we study masked
modeling, pointing out the importance of learning knowledge
from bidirectional spatio-temporal contexts. Next, we focus
on contrastive learning, emphasizing its role in learning generalizable representations of spatio-temporal data. Finally, we
introduce the diffusion generation, revealing its potential for
generative pre-training.
1) Regression Modeling: Inspired by the success of autoregressive trained large language and vision models [133], regression has become a powerful self-supervised optimization
function during the pre-training stage based on the sequence
properties of spatio-temporal data. The regression paradigm is
shown in Fig. 3, where STFMs are trained by the historical ST
data and aim to forecast the future.
For example, PointGPT [134] directly forecasts point
patches autoregressively during the pre-training phase for point
cloud-based tasks. To achieve a universal trajectory model,
UVTM [135] and TrajFM [113] support different trajectoryrelated tasks, which autoregressively generate future features
with the mask placeholder. Moreover, FourCastNet [125] iteratively utilizes the output of the trained high-resolution weather

FANG et al.: UNRAVELING SPATIO-TEMPORAL FOUNDATION MODELS VIA THE PIPELINE LENS: A COMPREHENSIVE REVIEW

Fig. 4. The masked modeling objective, where and indicate the masked
observation and active parameters, respectively.

forecasting model as the input of the next timestamp in the inference stage. Apart from autoregressive training, OpenCity [71]
trains a large foundation model for traffic forecasting with the
regression function, which aims to perform forecasting only
once. In addition, FengWu [122] treats the numerical weather
prediction as a multi-task regression problem based on the view
that the prediction of each variable can be treated as a independent task. ClimaX [43] proposes a randomized forecasting
objective for foundation model training, where the goal is to
predict an arbitrary set of input variables at an arbitrary time
into the future. LaBraM [136] pre-trains a neural tokenizer
model through predicting the Fourier spectrum of the EEG
time series. Further, the EEGPT [114] and iVideaoGPT [137]
perform next-token prediction on the EEG and video data, which
transform the sequential input data into tokens via embedding
techniques. Besides, the next-frame and next-scale predictions
are also explored in video-related tasks [138], [139]. However,
most existing regression-based methods rely on the iterative
prediction paradigm, which requires significant computational
resources and fails to adapt to streaming settings. It is promising
to invent new methods to improve efficiency and mitigate time
series distribution shifts in the future.
In practice, regression-based training offers direct alignment
with forecasting objectives and end-to-end efficiency without
complex sampling or reconstruction pipelines. However, it is
sensitive to error accumulation and exposure bias in longhorizon forecasting, and may overfit short-term trends unless
regularized or enhanced with curriculum learning, scheduled
sampling, or probabilistic outputs.
2) Masked Modeling: Benefiting from the success of masked
language and image modeling, e.g., BERT [140] and masked
autoencoder (MAE) [141], masked modeling has emerged as a
significant pre-training strategy for spatio-temporal foundation
models [142], [143], [144], [145]. As shown in Fig. 4, the conventional MAE randomly masks tokens, allowing its encoder to
learn from unmasked tokens and the decoder to recover masked
ones.

2049

At the beginning, STEP [66] uses the conventional MAE
on the temporal dimension of spatio-temporal graph data to
pre-train a foundation model for learning the robust representation of long input, which can be used to construct dynamic
graphs in traffic forecasting. In addition, GPT-ST [67] uses
cluster-aware masking to replace the random masking in STEP
for cross-cluster knowledge learning. However, both of them
only pre-trained an auxiliary tool instead of a model that can
be directly applied to downstream tasks. Therefore, Brant [65]
masks the neural signal to train a spatio-temporal encoder-only
intracranial neural signal foundation model for analyzing a broad
range of tasks. PowerPM [74] follows this paradigm to pre-train
a power foundation model with a hierarchical spatial encoder.
Next, UniTraj [17] proposes block masking and key points
masking on the trajectory data to achieve a trajectory foundation
model. Different from the above methods that mask tokens
on the temporal dimension, Scale-MAE [48], G2PTL [73] and
WeatherGFM [49] pre-train foundation models by masking the
spatial dimension of grid data, which can handle various downstream tasks in terms of geographic and weather. Further, PointMAE [146] uses the MAE on the patched tokens of 3D point
cloud to train a point cloud foundation model, TFMAE [147]
masks time series with small amplitude in the frequency domain,
and EMSTGAE [148] leverages the graph masking strategy
for the spatio-temporal graph data. Consequently, UniST [44]
combines spatial and temporal masking to pre-train a foundation
model related to spatio-temporal grid tasks across different
applications. Moreover, STD-MAE [68] reveals that using two
separate spatial and temporal MAEs during the pre-train stage
can achieve better performance in traffic forecasting. However,
most existing masked modeling methods fail to contend with
distribution shifts when meeting streaming spatio-temporal data,
resulting in significant performance degradation. In addition,
current methods are mostly used on high-density information
data such as spatio-temporal graph data [66], and the performance of using the masked technique on spatio-temporal data
with low-density information such as event data needs to be
further improved in the future.
Therefore, the strengths of masked modeling include efficient
self-supervision that encourages learning semantically meaningful structure from partial observations and robustness to missing
data common in sensor and mobility streams. However, its weaknesses involve potential bias toward reconstructing low-level
statistics rather than task-relevant dynamics, sensitivity to mask
ratio and strategy that can affect spatial–temporal coherence,
and possible misalignment between reconstruction objectives
and downstream predictive goals unless complemented by forecasting or contrastive signals.
3) Contrastive Learning: Contrastive learning [149] exhibits
strong capabilities in aligning representations of different views
of data to improve performance, which has been verified in
vision [150], language [151], and graph [152] tasks. Contrastive
learning is also a mainstream pre-training strategy in spatiotemporal data mining [123], [147], [153], [154], [155], [156],
and the process of contrastive learning is shown in Fig. 5.
STGCL [157] first explores the effectiveness of contrastive pre-training in traffic forecasting, and designs four

2050

Fig. 5.

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 3, MARCH 2026

The contrastive training objective, where indicates active parameters.

spatio-temporal data augmentation strategies (edge masking
and input masking on the spatial domain, and temporal shifting and input smoothing on the temporal domain) to derive
different views of data as the positive sample for contrastive
learning. STSSL [127] and SPGCL [158] further propose an
adaptive spatio-temporal graph augmentation strategy to avoid
the hand-craft issue. Using contrastive learning differently on
the same representation granularity of the data, CL-TSim [110]
and TrajCL [159] incorporate contrastive learning into route
representation learning and trajectory similarity learning, respectively, with diverse point- (distorting and masking) and
trajectory-level (truncating and simplification) augmentation
strategies. To perform spatio-temporal graph contrastive learning on different granularities, ST-HSL [87] considers representations achieved from convolution and hypergraph convolution as different views for effective spatio-temporal modeling.
In particular, the convolution and hypergraph convolution in
ST-HSL can collaboratively enhance each other to mitigate
data sparsity, which is important for various ST tasks, e.g.,
crime prediction. However, these methods mainly focus on one
specific downstream task and are hard to generalize to other
domains or tasks. To address this problem, AutoST [119] proposes an automated spatio-temporal graph contrastive learning
paradigm to adaptively derive different views. The automated
contrastive paradigm on the heterogeneous graph neural network
is implemented by a random walk with learnable Gaussian
noise, which alleviates noise and distribution heterogeneity.
FlashST [70] uses contrastive learning on the prompt embedding
to ensure a consistent distribution across diverse downstream
tasks based on an optimized uniform embedding distribution.
To learn a universal trajectory representation for downstream
tasks, START [20], JGRM [111], and MMTEC [24] utilize the
map-matched road network as a positive view to introduce travel
semantics into the foundation model. PTrajM [28] further uses
the closest POI to each trajectory point as another positive POI
view to enhance travel semantics. To deal with the multi-modal
urban spatial image and text description data, UrbanCLIP [160]

Fig. 6.

The diffusion generation objective, where indicates active parameters.

and MM-Path [161] designs an urban foundation model with
language-image contrastive pre-train. Specifically, representations from different modals that have the same semantics are
aligned by contrastive learning, and the cross-modal-enriched
model achieves significant improvements in downstream tasks.
In this context, the advantages of contrastive-based models include strong representation transfer under diverse environments
and the ability to encode invariances across spatial neighborhoods and temporal contexts. However, its limitations stem from
sensitivity to augmentation design and view construction (which
may distort spatio-temporal semantics), potential reliance on
large batches or memory banks to provide informative negatives, and a possible gap between spatio-temporal instance-level
discrimination and task-specific objectives that may require
additional supervision or fine-tuning.
4) Diffusion Generation: Denoising diffusion models have
achieved prominence in unsupervised visual generation
tasks [162], [163] due to their abilities to learn distributions
of intricate unlabeled data, which can adapt to unsupervised
spatio-temporal grid and video tasks [63], [132], [164], [165]. As
shown in Fig. 6, denoising diffusion models first add Gaussian
noise to transform data (forward process) into standard Gaussian
and then utilize a network to learn data reconstruction from noise
(reverse process).
To adapt diffusion models with spatio-temporal forecasting,
DiffSTG [130] and MaTCHS [166] treat the history data as
the condition in the reverse process and concatenate it with
the noised data to generate target future. Subsequently, CaPaint [167] utilizes the discovered causal data as the condition
to generate multiple sequences. On the other hand, SPDiff [168]
and DiffCrime [88] utilize two independent channels in the
denoising network to learn representations of noised data and
the history condition, which can mitigate the negative influence caused by the discrepancy of the data. Moreover, DiffTraj [126] utilizes a diffusion model for trajectory recovery, and
the recorded motion properties serve as conditions. In particular,
the forecasting task is considered as a special case of recovery

FANG et al.: UNRAVELING SPATIO-TEMPORAL FOUNDATION MODELS VIA THE PIPELINE LENS: A COMPREHENSIVE REVIEW

in USTD [131], i.e., the future to be predicted is a missing
value to be recovered. To further extract deterministic conditional knowledge, existing studies in imputation, forecasting,
and fine-grained inference like DSTPP [169], PriSTI [170],
DiffUFlow [46], and FGTI [64] leverage an external network
to learn representations of condition inputs and use the crossattention to capture deterministic information from conditional
inputs. Further, to decrease the optimization difficulty in the
denoising process, ControlTraj [30] pre-trains a road representation network with the masked modeling to embed topology
constraints of road segments as conditional information for trajectory generation. USTD [131] also pre-trains a spatio-temporal
graph neural networks with the masked modeling to capture
dependencies of conditions. Additionally, SaSDim [171] replaces the conventional stochastic differential equation with its
probabilistic high-order form to more accurately estimate the
variance of the noise in spatial time series and PhyDA [172]
presents a physically regularized diffusion objective to keep
consistency with physical laws in atmospheric systems, which
can address the data generation bias.
In practice, the strengths of diffusion-based methods lie in
strong generative fidelity and calibration for complex spatiotemporal distributions and a natural ability to handle missing
data via controllable perturbations. However, they also entail
substantial computational cost due to many diffusion steps
(impacting both training and inference latency), sensitivity to
noise schedules and samplers that can affect spatio-temporal
coherence, and a potential mismatch between generative metrics
and downstream predictive accuracy unless augmented with
additional objectives or guidance.
IV. TRANSFERRED SPATIO-TEMPORAL FOUNDATION MODELS
Transferred spatio-temporal foundation models transfer the
generalized knowledge of pre-trained foundation models trained
on one or more other domains, such as language and vision, for
spatio-temporal tasks. As shown in Fig. 2, to derive a transferred
spatio-temporal foundation model, the pre-trained foundation
model from other domains is first selected according to the
corresponding data modalities. Then the pre-trained model is
adapted to the specific spatio-temporal task and application by
transforming the model or spatio-temporal data. In the following, we provide a detailed discussion about model selection and
transfer adaptation.
A. Model Selection
In this section, we divided the mainstream pre-trained foundation models into three categories according to the data modality,
i.e., vision, language, and multi-modal models.
1) Pre-Trained Vision Models: There have been many vision
foundation models in recent years that range from convolutionbased ResNet [173] to Transformer-based ViT [174]. Trained
on large-scale image and video corpora, these models provide
transferable visual representations that reduce labeled data requirements, accelerate convergence, and improve downstream
accuracy without task-specific training. As a popular backbone,
they preprocess frames of spatio-temporal video data to deliver

2051

stronger frame-level features and better temporal consistency.
Early studies use pre-trained spatio-temporal convolution models to extract local visual and temporal features. For example, DCLR [153] leverages the pre-trained R(2+1)D-18 [175]
to obtain general spatio-temporal representations, yielding improved retrieval and recognition performance relative to training from scratch. Moreover, Transformer architectures exhibit
strong learning capabilities in vision. MAESTL [142], VideoMAE [144], and CaPaint [167] adopt patch-based pre-trained
ViTs with masked modeling, which has been shown to enhance video representation quality, improve robustness to occlusion/missing frames, and boost performance on standard video
understanding benchmarks. Additionally, LLM-AR [176] and
iVideoGPT [137] first apply vector quantization (e.g., VQGAN,
VQVAE) to obtain token sequences, then train Transformerbased foundation models. Tokenization enables efficient longhorizon modeling and reduces compute, while maintaining competitive generation and prediction quality. To further improve
video understanding, large-scale ViT-G [177] is employed in
VideoChat [53] and MovieChat [54], which results in stronger
multimodal alignment and more accurate temporal grounding in
video question answering and dialogue.
These pre-trained vision models reduce labeled data requirements, speed up convergence, and improve downstream accuracy for spatio-temporal tasks, while enhancing robustness
to occlusion and missing frames and strengthening temporal
consistency across video. Tokenization-based pipelines further
enable efficient long-horizon modeling with competitive generation and prediction quality, and large-capacity ViTs provide
more accurate temporal grounding in video understanding.
2) Pre-Trained Language Models: Pre-training a universal
model to solve diverse language tasks has led to general-purpose
LLMs with strong reasoning and compositional abilities. The
most notable example is ChatGPT [178]. Spatio-temporal information (e.g., time, location, events, and numerical values) can
be naturally expressed in text, enabling LLMs to assist ST tasks
through instruction following and chain-of-thought reasoning,
which reduces task-specific engineering and improves sample
efficiency. A straightforward usage pattern is to convert ST data
into textual prompts and iteratively interact with LLMs to complete the target task. For instance, QWEN [179], GLM [180], and
GPT [178] are employed in MAS4POI [181], LLMob [182], and
ST-GIA+[183] to interpret human intent from trajectories, yielding more accurate next-location prediction and more realistic
trajectory generation. Similarly, GPT, QWEN, and Mixtral [184]
are used for spatio-temporal event understanding [31], [185],
where LLM reasoning helps uncover causal relations and improves the quality of event forecasting. Beyond instruction use,
transferred foundation models directly feed ST sequences into
LLM backbones to leverage their strong sequential modeling:
masked/regressive BERT [18], [186] and GPT-2 [187], [188],
[189], [190] enable self-supervised imputation and forecasting
with fewer labels and faster convergence. To combine reasoning with sequence prediction, AuxMobLCast [191] uses BERT
for context knowledge of historical trajectories and GPT-2 for
prediction, while Llama-based models [192] in ST-LLM [193],
LLM4POI [194], and ExpTime [39] further improve predictive

2052

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 3, MARCH 2026

accuracy and interpretability by unifying domain instructions
with temporal patterns.
These LLM-based approaches reduce annotation demand,
provide interpretability through natural-language rationales, improve location and event forecasting quality, and enable flexible
zero- or few-shot transfer to new cities or domains. Typical
gains come from stronger temporal reasoning, better handling
of sparse or incomplete inputs, and the ability to integrate
heterogeneous side information via text.
3) Pre-Trained Multi-Modal Models: Spatio-temporal data
often appear across modalities (e.g., image and text), motivating
pre-trained multi-modal models that align cross-modal representations so that images can be grounded in language and
vice versa. This alignment enables label-efficient transfer, robust
retrieval and grounding, and unified modeling across views. For
urban region profiling, UrbanCLIP [160], USPM [195], and
UrbanVLP [196] employ image-to-text pipelines (e.g., LLaMAAdapterV2 [197], SPHINX-V2 [198]) to generate rich textual
descriptions from satellite imagery, providing informative side
information that improves downstream classification and clustering. For video understanding, the CLIP image encoder [57]
is applied to video frames [61] so that language models can access aligned visual features, improving temporal grounding and
question answering. This is possible because CLIP’s image and
text encoders are aligned via contrastive learning. Conversely,
CLIP’s text encoder conditions video generation [51], [56],
enhancing semantic controllability and faithfulness to prompts.
Moreover, image–text encoders are jointly used to compute
CLIP scores, which guide answer retrieval in video QA [59] and
support navigation in street-view environments [199], leading
to better retrieval precision and instruction.
Multi-modal pre-training enhances cross-modal transfer, improves semantic grounding and retrieval accuracy, enables controllable generation, and enriches ST models with languageaccessible descriptions—benefits that translate into more accurate profiling, better video QA, and more reliable navigation.
B. Transfer Adaptation
Existing transferred adaptation methods, as a form of transferring pre-trained foundation models for spatio-temporal tasks,
employ various transformations on pre-trained models and primitive spatio-temporal data to bridge the gap between them,
enabling effective transfer adaptation. Despite significant differences in their design, transfer adaptation in spatio-temporal tasks
can be categorized into four representative approaches: prompt
engineering, feature enhancement, cross-domain alignment, and
supervised fine-tuning.
1) Prompt Engineering: The most important challenge for
transferred spatio-temporal foundation models is to bridge the
domain gap between original spatio-temporal data and pretrained foundation models. It is intuitive to employ prompt
engineering [200] to facilitate pre-trained foundation models
understanding spatio-temporal data.
Existing prompt engineering methods for spatio-temporal
foundation models can be divided into two categories: 1) directly
incorporating numeric data into texts and 2) transforming

Fig. 7.

Prompt engineering, where indicates frozen parameters.

numeric data into textual descriptions. The former directly
embeds numeric values into predefined templates directly
(e.g., “The average temperature is {value} degrees”) [191],
[201], [202]. In contrast, the latter converts numeric data into
textual representations aiming to leverage the powerful memory
capabilities of large language models. This is typically achieved
by replacing numeric values with categorical labels based on predefined rules, such as using “D1” to denote data within the first
bin [203]. These numeric-to-text transformations enable large
language models to process quantitative data within their textual
reasoning frameworks, albeit in a more coarse-grained manner.
To further improve accuracy, recent studies emphasize enriching
prompts with contextual information, such as historical trends,
statistical summaries, or metadata relevant to the task [191],
[202], [204], [205]. These methods are particularly valuable in
domain-specific applications. For instance, in terms of stock
price prediction, one study [203] constructs prompts, which
include instructions, company profiles, historical temporal
news summaries, and categorized stock price time series to
enhance predictions. This design allows large language models
to integrate cross-sequence information from multiple stocks
and leverage their inherent knowledge to generate forecasts and
explanations. In real-world applications, incorporating timely
background information into contextual prompts helps the
model identify temporal patterns and domain-specific nuances,
leading to more accurate and robust performance. Additionally,
few-shot examples are frequently employed to further enhance
prediction performance [203], [206]. For example, a limited
number of samples (3-shot, 10-shot, and 25-shot) are provided
to the large language model to contextualize it for the specific
task [206]. These samples are embedded into textual templates
to form question-answer pairs, which enhance the large
language model in understanding the task structure and context.
The large language model is subsequently trained on these
few-shot examples to learn a task-specific prompt embedding,
which is appended to each sample during inference. Moreover,
TEST [204] uses soft prompting to refine prediction accuracy
by generating task-specific embeddings that improve the large

FANG et al.: UNRAVELING SPATIO-TEMPORAL FOUNDATION MODELS VIA THE PIPELINE LENS: A COMPREHENSIVE REVIEW

2053

Fig. 8. Feature enhancement, where and indicate frozen and active parameters,
respectively.

Fig. 9. Cross-Domain alignment, where and indicate frozen and active parameters, respectively.

language model’s comprehension of the input data. These soft
prompts are trained using the loss derived from outputs of the
large language model and ground truth of the task, effectively
bridging the gap between the large language model and the
specific requirements of time series forecasting tasks. According
to existing studies [201], [203], we observe that the performance
of STFMs is highly dependent on manually designed prompts,
and thus it requires improving the generalization of prompt
engineering techniques in the future.
2) Feature Enhancement: Benefiting from the powerful text
and image understanding capabilities of pre-trained foundation
models, the high-level semantic features of spatio-temporal text
and image data can be extracted for downstream tasks.
For example, VideoChat [53] first extracts visual semantic
features from video contents by the pre-trained video foundation
model, and then feeds these features into large language models
to conduct the video question answering. R2A [59] further
utilizes the pre-trained vision encoder of the CLIP model [57] to
extract semantic features of each frame of the input video, and
then retrieve the top-k similar texts to answer the question of the
input video. In addition, UrbanCLIP [160] and USPM [195] use
pre-trained image-to-text models [197], [207] to generate captions of urban images, which represents the text modality for the
subsequent contrastive training. Moreover, CLIP-LSTM [100]
transforms the stock data into texts and images and then leverage the pre-trained CLIP encoders to extract the features from
language and visual domains, which is beneficial to market forecasting. Further, ChatGNN [208] and RealTCD [209] directly
leverage large language models to generate spatial correlations
for spatio-temporal graph data. Specifically, ChatGNN feed the
detail description of companies and daily media information
into ChatGPT [178] to derive adjacency matrices of companies
for stock prediction. RealTCD inputs the textual information
of industrial systems into a large language model to reveal
temporal causal relationships for anomaly detection. Different
from ChatGNN and RealTCD, LA-GCN [210] utilizes the pretrained BERT [140] to encode the texts of labels and joints of

the skeleton data to build the distance-based adjacency matrix
for skeleton-based action recognition. Next, PromptGAT [211],
Orca [212], LLMPOI [213], and ST-GIA+ [183] utilize a pretrained large language model to generate predictions or embeddings as the input of the subsequent tasks based on the
spatio-temporal prompts, e.g., weather and road information
in spatio-temporal graph tasks, and locations and categories
in spatio-temporal trajectory tasks. Finally, LLMob [182], UrbanKGent [214], MAS4POI [181], and CoMaPOI [215] use
large language models to design a multi-agent collaboration
system for spatio-temporal trajectory tasks. These methods feed
the detailed description of trajectories into a large language
model, which generates complete or fine-grained trajectories
for recovery or up-sampling tasks, and then uses different large
language models to refine or verify the previously generated trajectories. Although feature-enhanced STFMs achieved superior
performance utilizing generated side information, it remains a
problem to alleviate potential noise and fake information caused
by the hallucination of pre-trained models.
3) Cross-Domain Alignment: Pre-trained large language
models can also be directly used as the backbone for spatiotemporal modeling considering their powerful context inference
capabilities. Existing methods often align the spatio-temporal
data with the text and then feed the aligned data into frozen
large language models for downstream spatio-temporal tasks.
VideoLLM [51] uses a trainable projection-based semantic translator to transform the visual spatial features into the
textual embedding space of large language models for video
understanding tasks. To inject temporal information into the
aggregated frame-level representation for video understanding, MovieChat [54] and Video-LLaMA [61] train a querying Transformer of the BLIP2 [60] model before the projection layer. LLM-AR [176] proposes a VQ-VAE-based [216]
linguistic projection layer to reprogram the action signal in
videos into language sentences through the human inductive
bias, such as Zipf’s law [217], and the hyperbolic codebook. VideoPoet [218] utilizes the pre-trained text and visual

2054

Fig. 10.

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 3, MARCH 2026

Supervised fine-tuning, where indicates active parameters.

foundation models to derive the aligned text and visual tokens. Additionally, FrozenBiLM [58] adds a trainable projection
layer between the frozen Transformer blocks of large language
models, which enhances the video question answering due to
the multi-cycle alignment. For the spatio-temporal graph tasks,
embedding- and reprogramming-based alignment in foundation
models have been proposed [219]. Specifically, STG-LLM [189]
concatenated the time-of-day and day-of-week embeddings with
the projected spatio-temporal graph enabling periodicity-aware
large language models. REPST [190] aligns the spatio-temporal
graph data with the textual embedding space by reprogramming the data from most correlated pre-trained word embeddings. TimeCMA [220] utilizes similarity retrieval-based crossmodality alignment to incorporate text information into time
series. In addition, a trainable output projection layer [50] is
added into transferred foundation models to convert the transferred results into the original spatio-temporal domain. Although
many existing methods focus on cross-domain data alignment,
they mainly rely on simple addition and concatenation and fail
to capture the complex relationships.
4) Supervised Fine-Tuning: Supervised fine-tuning retrains
the pre-trained model with the domain-specific data and has
become a popular technique to align pre-trained foundation
models with spatio-temporal data. This is because the data of the
specific realm in the supervised fine-tuning is able to incorporate
domain knowledge into the pre-trained large language models.
In the early stage, the supervised fine-tuning techniques have
been adopted in the textual-related spatio-temporal tasks (e.g.,
geo-entity representation and geospatially language understanding). Specifically, SPABERT [186] and GeoLM [221] directly
retrains full parameters of BERT [140] with geo-texts due to
the same modality of the source model and target task. AuxMobLCast [191] retrains all parameters in BERT-based encoder
and GPT-based [178] decoder for human mobility forecasting,
which aligns the source model and target task by transforming
the numerical mobility data into language sentences. However,
fine-tuning full parameters in pre-trained large language models
is inefficient and be restricted in resource-constrained environments. To improve efficiency, partial fine-tuning methods
emerge. Specifically, GATGPT [187] combines graph attention
and a pre-trained large language model for spatio-temporal

imputation, where the model only fine-tunes the weights of
layer normalization modules in the pre-trained large language
model during the supervised training stage. To preserve the
sequential modeling capabilities acquired during pre-training,
ST-LLM [193] further fine-tunes the last few attention layers
in the pre-trained large language model for traffic forecasting.
Moreover, TPLLM [188], PTR [18], and FOTraj [222] incorporate the well-known parameter-efficient fine-tuning method,
low-rank adaptation [7], into the pre-trained large language
model for traffic forecasting, trajectory recovery, and trajectory
anomaly detection, respectively. Specifically, in the supervised
fine-tuning stage, two low-rank matrices are matrix multiplied
to substitute original attention weights of the pre-trained large
language model, which can significantly reduce the number of
parameters and improve the efficiency of fine-tuning. To further
decrease computation costs of fine-tuning, LLM4POI [194] uses
not only the low-rank adaptation but also the 4-bit quantization
technique for the next point-of-interest recommendation. While
low-rank and quantization techniques reduce parameter redundancy during the supervised fine-tuning, they may also degrade
model performance, particularly in complex tasks.
V. APPLICATIONS
Next, we discuss primary application domains of STFMs.
As shown in Fig. 1, STFMs are widely adopted in various
domains, encompassing energy, finance, weather, healthcare,
transportation, and public services.
A. Energy
Primitive spatio-temporal foundation models for diverse energy applications have been designed including demand-side
management, grid stability, and consumer behavior analysis.
This is because of the abundant electricity time series and the
inherent hierarchical spatial correlations of multiple electricity
time series [74]. Moreover, one of the most compelling use
cases of STFMs in energy is in the predictive maintenance of
renewable energy sources, like wind turbines and solar panels.
For example, models trained on historical data of turbine performance and environmental conditions (such as wind speed
and temperature) can predict when a turbine is likely to fail
or require maintenance, which reduces downtime and improve
the efficiency of wind farms by anticipating mechanical issues
before they occur, optimizing maintenance schedules, and minimizing operational disruptions [223], [224].
B. Finance
Portfolio management [225], fraud detection [226], and stock
market prediction [166] are highly essential for the financial
industry, and the implicit inter-relations across multiple time
series of stock and supply–demand of enterprises are expected to
be considered in them [227], [228]. Thus, proposed finance foundation models can capture not only temporal correlations but
also spatial dependencies. In particular, spatial correlations are
shown to provide better trading and investing [98]. Beyond traditional financial analytics, spatial crowdsourcing has emerged

FANG et al.: UNRAVELING SPATIO-TEMPORAL FOUNDATION MODELS VIA THE PIPE

[...正文过长，此处由批处理脚本仅做上下文截断；请在结论中说明该限制...]

rillions of parameters. As for
spatio-temporal foundation models, it is also vital to prove that
performance is positively correlated with the data scale across
different model sizes. The scalability of spatio-temporal foundation models determines whether this research line is meaningful
(i.e., the large model represents the capability to improve performance as the data scale increasing) and provides valuable guidance for training and fine-tuning foundation models effectively.
However, the size of current spatio-temporal foundation models
is not sufficient to support the scaling law [71], [113]. Larger
models and more data are still needed to derive the emergence
of LLM-like spatio-temporal capabilities.

F. Public Services

VI. FUTURE OPPORTUNITIES
Although STFMs have achieved remarkable performance recently, several avenues for future work remain open.

E. Transportation
Massive amounts of transportation data have been generated by human, vehicles, and roads in recent years, which
provides the possibility to use foundation models for various
downstream transportation-related tasks to assist daily travel.

B. Efficiency
Despite current achievements in spatio-temporal foundation
models, they remain highly complex, leading to expensive computation needs. Particularly, the size of large-scale data-based

2056

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 3, MARCH 2026

primitive foundation models and large language models make
them impractical to deploy for spatio-temporal applications in
resource-constrained environments such as mobile phones or
embedded systems. The trade-off between performance and efficiency of spatio-temporal foundation models is still a research
problem, requiring foundation models to retain high one-tomany performance without too intricate designs and too large a
size. Efficient deep learning methods such as distillation [244],
pruning [245], quantization [246], condensation [247], and deep
learning units with subquadratic complexity [69] can be utilized
in spatio-temporal foundation models in the future to make a
balance between computation demands and one-to-many performance, which can bridge the gap between scientific research
and industrial needs.

C. Generalization
Apart from using foundation models on the single spatiotemporal domain, extending foundation models for the spatiotemporal graph domain to other domains, such as the trajectory
and spatio-temporal grid domains, provides considerable opportunities for future research. Most spatio-temporal grid data is
generated by satellite images and spatio-temporal graph data is
recorded by sensors. The difference between them is that sensors
are irregularly distributed in the spatial dimension. Fortunately,
universal spatial patch methods for the grid and graph data are
proposed [69] and foundation models across these two domains
are expected to be designed. Moreover, trajectories can be seen as
univariate spatio-temporal graph data for integration into crossdomain foundation models [248], yet the irregular time interval
and the spatial correlations of the same sequence should be carefully considered in future research. Addressing these issues will
yield real universal spatio-temporal foundation models, which
are more versatile and applicable to a broader range of tasks.
Developing foundation models that effectively incorporate many
spatio-temporal domains will be essential for emerging LLMlike spatio-temporal intelligence and further reducing energy
consumption.

D. Lack of Benchmarks
Different from the diverse application-crossed tasks that
spatio-temporal foundation models were applied for, dedicated benchmarks are provided for the time series forecasting
task [249]. Therefore, systematic evaluation and comprehensive
benchmarks for all spatio-temporal domains need to be proposed
urgently for a fair comparison of spatio-temporal foundation
models. Proposing various and representative benchmarks that
encompass a wide range of spatio-temporal domains, including event tasks, video tasks, trajectory tasks, spatio-temporal
graph tasks, and spatio-temporal grid tasks, will offer a more
thorough evaluation of the performance of STFMs. Systematic
benchmarks will reflect the strengths and weaknesses of spatiotemporal foundation models in a fair comparison, promoting understanding and stimulating the improvement of spatio-temporal
foundation models.

E. Multi-Objective Training
While using a single self-supervised training objective for
primitive foundation models can achieve superior performance
on simple spatio-temporal tasks, their performance on complex
tasks is still limited, such as the task of predicting the future with
missing historical data, which is difficult when using only regression or masked modeling. However, through combining denoising diffusion with masked modeling, spatio-temporal foundation models can obtain powerful generative capabilities while
improving computational efficiency by masking. Moreover, incorporating different training objectives can capture complementary aspects of spatio-temporal data. For example, regression is good at learning effective temporal patterns and trends
while masked modeling encourages contextual understanding.
In addition, contrastive learning enhances feature discrimination
and robustness, and denoising diffusion enhances generative
capabilities. By combining these objectives, spatio-temporal
foundation models are expected to gain stronger representation
learning, better predictive capabilities, and improved robustness
across different downstream tasks.
F. Multi-Modal Foundation Models
Currently, most spatio-temporal foundation models are
learned from single modality data, e.g., time series, video, or
grid. However, such single modality data might fall short in
capturing important spatio-temporal context information and
increases the difficulty in learning spatio-temporal general
knowledge. Moreover, multi-modal knowledge from different
sources can make models more robust to missing or noisy
data. This may lead to better generalization, and enable various
downstream tasks, such as autonomous driving. Besides, recent
breakthroughs in foundation models (e.g., CLIP and VideoGPT)
highlight the power of multi-modal integration. In fact, the multimodal information can also be extracted from spatio-temporal
data, e.g., heatmap images for trajectory data and text descriptions for event data. Therefore, multi-modal spatio-temporal
foundation models are a feasible frontier research direction to
improve robustness and generalization.
VII. CONCLUSION
In this paper, we present a comprehensive survey of recent advancements in spatio-temporal foundation models, a growing research direction that solves various downstream spatio-temporal
tasks via a single model. We offer an innovative pipeline
perspective to categorize existing spatio-temporal foundation
models. We first give an introduction to data harmonization
for foundation models, providing researchers and practitioners
with a holistic understanding to enhance the assessment of
spatio-temporal data properties. Then primitive and transferred
foundation models are introduced, covering the model designation and training objectives of primitive methods, and the
model selection and transfer adaptation of transferred methods.
Finally, we underscore the restrictions of current spatio-temporal
foundation models, while highlighting the opportunities in efficiency, scalability, generalization, and benchmarks. We expect

FANG et al.: UNRAVELING SPATIO-TEMPORAL FOUNDATION MODELS VIA THE PIPELINE LENS: A COMPREHENSIVE REVIEW

that this survey not only explains the current state-of-the-art
but also inspires further innovations and breakthroughs in the
future.

REFERENCES
[1] G. Jin et al., “Spatio-temporal graph neural networks for predictive
learning in urban computing: A survey,” IEEE Trans. Knowl. Data Eng.,
vol. 36, no. 10, pp. 5388–5408, Oct. 2024.
[2] Z. Lv, J. Xu, K. Zheng, H. Yin, P. Zhao, and X. Zhou, “LC-RNN: A deep
learning model for traffic speed prediction,” in Proc. Int. Joint Conf. Artif.
Intell., 2018, pp. 3470–3476.
[3] Y. Fang, F. Zhao, Y. Qin, H. Luo, and C. Wang, “Learning all dynamics:
Traffic forecasting via locality-aware spatio-temporal joint transformer,”
IEEE Trans. Intell. Transp. Syst., vol. 23, no. 12, pp. 23433–23446,
Dec. 2022.
[4] K. He, G. Gkioxari, P. Dollár, and R. Girshick, “Mask R-CNN,” in Proc.
Int. Conf. Comput. Vis., 2017, pp. 2961–2969.
[5] X. Jiang, D. Zhuang, X. Zhang, H. Chen, J. Luo, and X. Gao, “Uncertainty
quantification via spatial-temporal tweedie model for zero-inflated and
long-tail travel demand prediction,” in Proc. 32nd ACM Int. Conf. Inf.
Knowl. Manage., 2023, pp. 3983–3987.
[6] J. Kaplan et al., “Scaling laws for neural language models,” 2020,
arXiv:2001.08361 .
[7] E. J. Hu et al., “LoRA: Low-rank adaptation of large language models,”
in Proc. Int. Conf. Learn. Representations, 2021, pp. 1–20.
[8] J. Wei et al., “Chain-of-thought prompting elicits reasoning in large
language models,” in Proc. 36th Int. Conf. Neural Inf. Process. Syst.,
2022, pp. 24824–24837.
[9] M. Jin et al., “Large models for time series and spatio-temporal data: A
survey and outlook,” 2023, arXiv:2310.10196 .
[10] Y. Liang et al., “Foundation models for time series analysis: A tutorial
and survey,” in Proc. 30th ACM SIGKDD Conf. Knowl. Discovery Data
Mining, 2024, pp. 6555–6565.
[11] W. Zhang, J. Han, Z. Xu, H. Ni, H. Liu, and H. Xiong, “Urban foundation
models: A survey,” in Proc. ACM SIGKDD Conf. Knowl. Discovery Data
Mining, 2024, pp. 6633–6643.
[12] A. Goodge, W. S. Ng, B. Hooi, and S. K. Ng, “Spatio-Temporal
foundation models: Vision, challenges, and opportunities,” 2025,
arXiv:2501.09045 .
[13] Y. Liang et al., “Foundation models for spatio-temporal data science: A
tutorial and survey,” in Proc. ACM SIGKDD Conf. Knowl. Discovery
Data Mining, 2025, pp. 1–14.
[14] L. Deng, Y. Zhao, J. Chen, S. Liu, Y. Xia, and K. Zheng, “Learning to
hash for trajectory similarity computation and search,” in Proc. IEEE
40th Int. Conf. Data Eng., 2024, pp. 4491–4503.
[15] D. Hu, L. Chen, H. Fang, Z. Fang, T. Li, and Y. Gao, “Spatio-Temporal
trajectory similarity measures: A comprehensive survey and quantitative
study,” IEEE Trans. Knowl. Data Eng., vol. 36, no. 5, pp. 2191–2212,
May 2024.
[16] Z. Fang, Y. Du, L. Chen, Y. Hu, Y. Gao, and G. Chen, “E2 DTC: An end
to end deep trajectory clustering framework via self-training,” in Proc.
IEEE 37th Int. Conf. Data Eng., 2021, pp. 696–707.
[17] Y. Zhu, J. J. Yu, X. Zhao, X. Wei, and Y. Liang, “UniTraj: Learning a universal trajectory foundation model from billion-scale worldwide traces,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2025,
pp. 1–38.
[18] T. Wei et al., “PTR: A pre-trained language model for trajectory recovery,”
2024, arXiv:2410.14281 .
[19] C. Yang and G. Gidofalvi, “Fast map matching, an algorithm integrating
hidden markov model with precomputation,” Int. J. Geographical Inf.
Sci., vol. 32, no. 3, pp. 547–570, 2018.
[20] J. Jiang, D. Pan, H. Ren, X. Jiang, C. Li, and J. Wang, “Self-supervised
trajectory representation learning with temporal regularities and travel
semantics,” in Proc. IEEE 39th Int. Conf. Data Eng., 2023, pp. 843–855.
[21] Z. Liu, H. Miao, Y. Zhao, C. Liu, K. Zheng, and H. Li, “LightTR: A
lightweight framework for federated trajectory recovery,” in Proc. IEEE
40th Int. Conf. Data Eng., 2024, pp. 4422–4434.
[22] B. Hofmann-Wellenhof, H. Lichtenegger, and E. Wasle, GNSS–Global
Navigation Satellite Systems: GPS, GLONASS, Galileo, and More.
Berlin, Germany: Springer, 2007.
[23] Z. Chen et al., “KGTS: Contrastive trajectory similarity learning over
prompt knowledge graph embedding,” in Proc. AAAI Conf. Artif. Intell.,
2024, pp. 8311–8319.

2057

[24] Y. Lin, H. Wan, S. Guo, J. Hu, C. S. Jensen, and Y. Lin, “Pre-training
general trajectory embeddings with maximum multi-view entropy coding,” IEEE Trans. Knowl. Data Eng., vol. 36, no. 12, pp. 9037–9050,
Dec. 2024.
[25] X. Wang, Z. Fang, C. Huang, D. Hu, L. Chen, and Y. Gao, “GTR: A
general, multi-view, and dynamic framework for trajectory representation
learning,” in Proc. Int. Conf. Mach. Learn., 2025, pp. 1–20.
[26] Y. Chen, G. Cong, and C. Anda, “TERI: An effective framework for trajectory recovery with irregular time intervals,” Proc. VLDB Endowment,
vol. 17, pp. 414–426, 2023.
[27] J. Su, M. Ahmed, Y. Lu, S. Pan, W. Bo, and Y. Liu, “Roformer: Enhanced
transformer with rotary position embedding,” Neurocomputing, vol. 568,
2024, Art. no. 127063.
[28] Y. Lin et al., “TrajMamba: An efficient and semantic-rich vehicle trajectory pre-training model,” in Proc. Int. Conf. Neural Inf. Process. Syst.,
2025, pp. 1–26.
[29] T.-Y. Fu and W.-C. Lee, “Trembr: Exploring road networks for trajectory
representation learning,” ACM Trans. Intell. Syst. Technol. vol. 11, no. 1,
pp. 1–25, 2020.
[30] Y. Zhu et al., “ControlTraj: Controllable trajectory generation with
topology-constrained diffusion model,” in Proc. ACM SIGKDD Conf.
Knowl. Discovery Data Mining, 2024, pp. 4676–4687.
[31] X. Yu, W. Sun, J. Li, K. Liu, C. Liu, and J. Tan, “ONSEP: A novel
online neural-symbolic framework for event prediction based on large
language model,” in Proc. Findings Assoc. Comput. Linguistics, 2024,
pp. 6335–6350.
[32] Y. Xia, D. Wang, Q. Liu, L. Wang, S. Wu, and X.-Y. Zhang, “Chain-ofhistory reasoning for temporal knowledge graph forecasting,” in Proc.
Findings Assoc. Comput. Linguistics, 2024, pp. 16144–16159.
[33] S. Deng, M. de Rijke, and Y. Ning, “Advances in human event modeling:
From graph neural networks to language models,” in Proc. ACM SIGKDD
Conf. Knowl. Discovery Data Mining, 2024, pp. 6459–6469.
[34] S. Deng, H. Rangwala, and Y. Ning, “Learning dynamic context graphs
for predicting social events,” in Proc. ACM SIGKDD Conf. Knowl.
Discovery Data Mining, 2019, pp. 1007–1016.
[35] T. Mikolov, I. Sutskever, K. Chen, G. S. Corrado, and J. Dean, “Distributed representations of words and phrases and their compositionality,”
in Proc. Int. Conf. Neural Inf. Process. Syst., 2013, pp. 1–9.
[36] C. Ye et al., “MIRAI: Evaluating LLM agents for event forecasting,”
2024, arXiv:2407.01231 .
[37] X. Shi et al., “Language models can improve event prediction by few-shot
abductive reasoning,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2024,
pp. 29532–29557.
[38] Z. Song, C. Yang, C. Wang, B. An, and S. Li, “Latent logic tree extraction
for event sequence explanation from LLMs,” in Proc. Int. Conf. Mach.
Learn., 2024, pp. 46238–46258.
[39] C. Yuan, Q. Xie, J. Huang, and S. Ananiadou, “Back to the future: Towards
explainable temporal reasoning with large language models,” in Proc.
ACM Web Conf., 2024, pp. 1963–1974.
[40] Y. Liu, Y. Ma, M. Hildebrandt, M. Joblin, and V. Tresp, “TLogic: Temporal logical rules for explainable link forecasting on temporal knowledge
graphs,” in Proc. AAAI Conf. Artif. Intell., 2022, pp. 4120–4127.
[41] S. Deng, H. Rangwala, and Y. Ning, “Robust event forecasting with spatiotemporal confounder learning,” in Proc. ACM SIGKDD Conf. Knowl.
Discovery Data Mining, 2022, pp. 294–304.
[42] Z. Chen and Y. Wang, “Civil unrest event forecasting using graphical and
sequential neural networks,”in Proc. Artif. Neural Netw. Mach. Learn.,
2021, pp. 192–203.
[43] T. Nguyen, J. Brandstetter, A. Kapoor, J. K. Gupta, and A. Grover,
“ClimaX: A foundation model for weather and climate,” in Proc. Int.
Conf. Mach. Learn., 2023, pp. 25904–25938.
[44] Y. Yuan, J. Ding, J. Feng, D. Jin, and Y. Li, “UniST: A prompt-empowered
universal model for urban spatio-temporal prediction,” in Proc. ACM
SIGKDD Conf. Knowl. Discovery Data Mining, 2024, pp. 4095–4106.
[45] K. Bi, L. Xie, H. Zhang, X. Chen, X. Gu, and Q. Tian, “Accurate
medium-range global weather forecasting with 3D neural networks,”
Nature, vol. 619, no. 7970, pp. 533–538, 2023.
[46] Y. Zheng et al., “DiffUFlow: Robust fine-grained urban flow inference
with denoising diffusion model,” in Proc. ACM Int. Conf. Inf. Knowl.
Manage., 2023, pp. 3505–3513.
[47] Y. Yuan, C. Han, J. Ding, D. Jin, and Y. Li, “UrbanDiT: A foundation
model for open-world urban spatio-temporal learning,” in Proc. Int. Conf.
Neural Inf. Process. Syst., 2025, pp. 1–29.
[48] C. J. Reed et al., “Scale-MAE: A scale-aware masked autoencoder
for multiscale geospatial representation learning,” in Proc. Int. Conf.
Comput. Vis., 2023, pp. 4088–4099.

2058

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 3, MARCH 2026

[49] X. Zhao et al., “WeatherGFM: Learning a weather generalist foundation
model via in-context learning,” in Proc. Int. Conf. Log. Program., 2025,
pp. 1–21.
[50] Z. Li et al., “UrbanGPT: Spatio-temporal large language models,” in
Proc. ACM SIGKDD Conf. Knowl. Discovery Data Mining, 2024,
pp. 5351–5362.
[51] G. Chen et al., “VideoLLM: Modeling video sequence with large language models,” 2023, arXiv:2305.13292 .
[52] A. Dosovitskiy, “An image is worth 16x16 words: Transformers for image
recognition at scale” in Proc. Int. Conf. Learn. Representations, 2020,
pp. 1–22.
[53] K. Li et al., “VideoChat: Chat-centric video understanding,” Sci. China
Inf. Sci., vol. 68, no. 10, 2025, Art. no. 200102.
[54] E. Song et al., “MovieChat: From dense token to sparse memory for long
video understanding,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., 2024, pp. 18221–18232.
[55] X. Chen et al., “SEINE: Short-to-long video diffusion model for generative transition and prediction,” in Proc. Int. Conf. Learn. Representations,
2024, pp. 1–15.
[56] X. Gu, C. Wen, W. Ye, J. Song, and Y. Gao, “Seer: Language instructed
video prediction with latent diffusion models,” in Proc. Int. Conf. Learn.
Representations, 2024, pp. 1–31.
[57] A. Radford et al., “Learning transferable visual models from natural language supervision,” in Proc. Int. Conf. Mach. Learn., 2021,
pp. 8748–8763.
[58] A. Yang, A. Miech, J. Sivic, I. Laptev, and C. Schmid, “Zero-shot video
question answering via frozen bidirectional language models,” in Proc.
Int. Conf. Neural Inf. Process. Syst., 2022, pp. 124–141.
[59] J. Pan et al., “Retrieving-to-answer: Zero-shot video question answering
with frozen large language models,” in Proc. Int. Conf. Comput. Vis.,
2023, pp. 272–283.
[60] J. Li, D. Li, S. Savarese, and S. Hoi, “BLIP-2: Bootstrapping language-image pre-training with frozen image encoders and
large language models,” in Proc. Int. Conf. Mach. Learn., 2023,
pp. 19730–19742.
[61] H. Zhang, X. Li, and L. Bing, “Video-LLaMA: An instruction-tuned
audio-visual language model for video understanding,” in Proc. Conf.
Empirical Methods Natural Lang. Process., Syst. Demonstrations, 2023,
pp. 543–553.
[62] J. Yang et al., “Generalized predictive model for autonomous driving,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2024,
pp. 14662–14672.
[63] S. Zhang, S. Wang, H. Miao, H. Chen, C. Fan, and J. Zhang, “ScoreCDM: Score-weighted convolutional diffusion model for multivariate
time series imputation,” in Proc. Int. Joint Conf. Artif. Intell., 2024,
pp. 2551–2560.
[64] X. Yang, Y. Sun, X. Yuan, and X. Chen, “Frequency-aware generative
models for multivariate time series imputation,” in Proc. Int. Conf. Neural
Inf. Process. Syst., 2024, pp. 52595–52623.
[65] D. Zhang, Z. Yuan, Y. Yang, J. Chen, J. Wang, and Y. Li, ”Brant:
Foundation model for intracranial neural signal,” in Proc. Int. Conf.
Neural Inf. Process. Syst., 2024, pp. 26304–26321.
[66] Z. Shao, Z. Zhang, F. Wang, and Y. Xu, “Pre-training enhanced spatialtemporal graph neural network for multivariate time series forecasting,”
in Proc. ACM SIGKDD Conf. Knowl. Discovery Data Mining, 2022,
pp. 1567–1577.
[67] Z. Li, L. Xia, Y. Xu, and C. Huang, “Generative pre-training of spatiotemporal graph neural networks,” in Proc. Int. Conf. Neural Inf. Process.
Syst., 2023, pp. 70229–70246.
[68] H. Gao, R. Jiang, Z. Dong, J. Deng, Y. Ma, and X. Song, “Spatialtemporal-decoupled masked pre-training for spatiotemporal forecasting,”
in Proc. Int. Joint Conf. Artif. Intell., 2024, pp. 3998–4006.
[69] Y. Fang et al., “Efficient large-scale traffic forecasting with transformers:
A spatial data management perspective,” in Proc. ACM SIGKDD Conf.
Knowl. Discovery Data Mining, 2025, pp. 1–11.
[70] Z. Li, L. Xia, Y. Xu, and C. Huang, “FlashST: A simple and universal
prompt-tuning framework for traffic prediction,” in Proc. Int. Conf. Mach.
Learn., 2024, pp. 28978–28988.
[71] Z. Li et al., “Open spatio-temporal foundation models for traffic prediction,” ACM Trans. Intell. Syst. Technol., 2025.
[72] Z. Yuan, D. Zhang, Y. Yang, J. Chen, and Y. Li, “PPi: Pretraining brain
signal model for patient-independent seizure detection,” in Proc. Int.
Conf. Neural Inf. Process. Syst., 2024, pp. 69586–69604.
[73] L. Wu et al., “G2PTL: A geography-graph pre-trained model,” in Proc.
ACM Int. Conf. Inf. Knowl. Manage., 2024, pp. 4991–4999.

[74] S. Tu, Y. Zhang, J. Zhang, and Y. Yang, “PowerPM: Foundation model
for power systems,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2024,
pp. 115233–115260.
[75] L. Wu et al., “LaDe: The first comprehensive last-mile delivery dataset
from industry,” in Proc. ACM SIGKDD Conf. Knowl. Discovery Data
Mining, 2024, pp. 1–23.
[76] D. Yang, D. Zhang, V. W. Zheng, and Z. Yu, “Modeling user activity
preference by leveraging user spatial temporal characteristics in LBSNs,”
IEEE Trans. Syst., Man, Cybern. Syst., vol. 45, no. 1, pp. 129–142,
Jan. 2015.
[77] E. Cho, S. A. Myers, and J. Leskovec, “Friendship and mobility: User
movement in location-based social networks,” in Proc. ACM SIGKDD
Conf. Knowl. Discovery Data Mining, 2011, pp. 1082–1090.
[78] Y. Zheng et al., “GeoLife: A collaborative social networking service
among user, location and trajectory,” IEEE Data Eng. Bull., vol. 33, no.
2, pp. 32–39, 2010.
[79] Z. Wang et al., “OpenForecast: A large-scale open-ended event forecasting dataset,” in Proc. 31st Int. Conf. Comput. Linguistics, 2025,
pp. 5273–5294.
[80] K. Leetaru and P. A. Schrodt, “GDELT: Global data on events, location,
and tone,” in Proc. ISA Annu. Conv., 2013, pp. 1–49.
[81] F. Zhang, Z. Zhang, X. Ao, F. Zhuang, Y. Xu, and Q. He, “Along the time:
Timeline-traced embedding for temporal knowledge graph completion,”
in Proc. ACM Int. Conf. Inf. Knowl. Manage., 2022, pp. 2529–2538.
[82] Z. Zhang et al., “PromptST: Prompt-enhanced spatio-temporal multiattribute prediction,” in Proc. ACM Int. Conf. Inf. Knowl. Manage., 2023,
pp. 3195–3205.
[83] A. E. Johnson et al., “MIMIC-III: A freely accessible critical care
database,” Sci. Data, vol. 3, 2016, Art. no. 160035.
[84] S. Rasp, P. D. Dueben, S. Scher, J. A. Weyn, S. Mouatadid, and
N. Thuerey, “WeatherBench: A benchmark data set for data-driven
weather forecasting,” J. Adv. Model. Earth Syst., vol. 12, no. 11, 2020,
Art. no. e2020MS002203.
[85] M. Veillette, S. Samsi, and C. Mattioli, “SEVIR: A storm event imagery dataset for deep learning applications in radar and satellite
meteorology,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2020,
pp. 22009–22019.
[86] S. Jamali, A. Ghorbanian, and A. M. Abdi, “Satellite-observed spatial
and temporal sea surface temperature trends of the baltic sea between
1982 and 2021,” Remote Sens., vol. 15, no. 1, 2022, Art. no. 102.
[87] Z. Li, C. Huang, L. Xia, Y. Xu, and J. Pei, “Spatial-temporal hypergraph
self-supervised learning for crime prediction,” in Proc. IEEE 38th Int.
Conf. Data Eng., 2022, pp. 2984–2996.
[88] S. Wang et al., “DiffCrime: A multimodal conditional diffusion model
for crime risk map inference,” in Proc. ACM SIGKDD Conf. Knowl.
Discovery Data Mining, 2024, pp. 3212–3221.
[89] A. Geiger, P. Lenz, and R. Urtasun, “Are we ready for autonomous
driving? The KITTI vision benchmark suite,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2012, pp. 3354–3361.
[90] C. Schuldt, I. Laptev, and B. Caputo, “Recognizing human actions: A
local SVM approach,” in Proc. 17th Int. Conf. Pattern Recognit., 2004,
pp. 32–36.
[91] K. Soomro, “UCF101: A dataset of 101 human actions classes from
videos in the wild,” 2012, arXiv:1212.0402 .
[92] C. Lu, J. Shi, and J. Jia, “Abnormal event detection at 150 fps in
MATLAB,” in Proc. Int. Conf. Comput. Vis., 2013, pp. 2720–2727.
[93] R. Goyal et al., “The ‘something something’ video database for learning
and evaluating visual common sense,” in Proc. Int. Conf. Comput. Vis.,
2017, pp. 5842–5850.
[94] M. Bain, A. Nagrani, G. Varol, and A. Zisserman, “Frozen in time: A
joint video and image encoder for end-to-end retrieval,” in Proc. Int.
Conf. Comput. Vis., 2021, pp. 1728–1738.
[95] Y. Li, R. Yu, C. Shahabi, and Y. Liu, “Diffusion convolutional recurrent
neural network: Data-driven traffic forecasting,” in Proc. Int. Conf. Learn.
Representations, 2017, pp. 1–16.
[96] C. Song, Y. Lin, S. Guo, and H. Wan, “Spatial-temporal synchronous
graph convolutional networks: A new framework for spatial-temporal
network data forecasting,” in Proc. AAAI Conf. Artif. Intell., 2020,
pp. 914–921.
[97] X. Liu et al., “LargeST: A benchmark dataset for large-scale traffic forecasting,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2023,
pp. 75354–75371.
[98] Y. Fang, R. Liu, H. Huang, P. Zhao, and Q. Wu, “A spatio-temporal
diffusion model for missing and real-time financial data inference,” in
Proc. ACM Int. Conf. Inf. Knowl. Manage., 2024, pp. 602–611.

FANG et al.: UNRAVELING SPATIO-TEMPORAL FOUNDATION MODELS VIA THE PIPELINE LENS: A COMPREHENSIVE REVIEW

[99] Z. Wu, S. Pan, G. Long, J. Jiang, X. Chang, and C. Zhang, “Connecting the
dots: Multivariate time series forecasting with graph neural networks,”
in Proc. ACM SIGKDD Conf. Knowl. Discovery Data Mining, 2020,
pp. 753–763.
[100] C. Wimmer and N. Rekabsaz, “Leveraging vision-language models for
granular market change prediction,” in Proc. AAAI Conf. Artif. Intell.
Muffin, 2023, pp. 1–11.
[101] X. Yi, J. Zhang, Z. Wang, T. Li, and Y. Zheng, “Deep distributed fusion
network for air quality prediction,” in Proc. ACM SIGKDD Conf. Knowl.
Discovery Data Mining, 2018, pp. 965–973.
[102] Y. Liang et al., “AirFormer: Predicting nationwide air quality in
China with transformers,” in Proc. AAAI Conf. Artif. Intell., 2023,
pp. 14329–14337.
[103] W.-L. Zheng and B.-L. Lu, “Investigating critical frequency bands and
channels for EEG-based emotion recognition with deep neural networks,” IEEE Trans. Auton. Mental Develop., vol. 7, no. 3, pp. 162–175,
Sep. 2015.
[104] B. Blankertz, G. Dornhege, M. Krauledat, K.-R. Müller, and G. Curio,
“The non-invasive berlin Brain–computer interface: Fast acquisition
of effective performance in untrained subjects,” NeuroImage, vol. 37,
pp. 539–550, 2007.
[105] A. L. Goldberger et al., “Physiobank, physiotoolkit, and physionet:
components of a new research resource for complex physiologic signals,”
Circulation, vol. 101, pp. e215–e220, 2000.
[106] Z. Shao et al., “Exploring progress in multivariate time series forecasting:
Comprehensive benchmarking and heterogeneity analysis,” IEEE Trans.
Knowl. Data Eng., vol. 37, no. 1, pp. 291–305, Jan. 2025.
[107] Y. Fang et al., “When spatio-temporal meet wavelets: Disentangled traffic
forecasting via efficient spectral graph attention networks,” in Proc. IEEE
39th Int. Conf. Data Eng., 2023, pp. 517–529.
[108] W. Shu, K. Cai, and N. N. Xiong, “A short-term traffic flow prediction model based on an improved gate recurrent unit neural network,”
IEEE Trans. Intell. Transp. Syst., vol. 23, no. 9, pp. 16654–16665,
Sep. 2022.
[109] T. Bogaerts, A. D. Masegosa, J. S. Angarita-Zapata, E. Onieva, and P.
Hellinckx, “A graph CNN-LSTM neural network for short and long-term
traffic forecasting based on trajectory data,” Transp. Res. Part C, Emerg.
Technol., vol. 112, pp. 62–77, 2020.
[110] L. Deng, Y. Zhao, Z. Fu, H. Sun, S. Liu, and K. Zheng, “Efficient trajectory
similarity computation with contrastive learning,” in Proc. ACM Int. Conf.
Inf. Knowl. Manage., 2022, pp. 365–374.
[111] Z. Ma et al., “More than routing: Joint GPS and route modeling for
refine trajectory representation learning,” in Proc. ACM Web Conf., 2024,
pp. 3064–3075.
[112] T. Zhou, Z. Ma, Q. Wen, X. Wang, L. Sun, and R. Jin, “FEDformer: Frequency enhanced decomposed transformer for longterm series forecasting,” in Proc. Int. Conf. Mach. Learn., 2022,
pp. 27268–27286.
[113] Y. Lin et al., “TrajFM: A vehicle trajectory foundation model for region
and task transferability,” 2024, arXiv:2408.15251 .
[114] T. Yue et al., “EEGPT: Unleashing the potential of EEG generalist foundation model by autoregressive pre-training,” 2024, arXiv:2410.19779
.
[115] W.-B. Jiang, L.-M. Zhao, and B.-L. Lu, “Large brain model for learning
generic representations with tremendous EEG data in BCI,” in Proc. Int.
Conf. Learn. Representations, 2024, pp. 1–22.
[116] V. Ekambaram et al., “Tiny time mixers (TTMS): Fast pretrained models for enhanced zero/few-shot forecasting of multivariate time series,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2024,
pp. 74147–74181.
[117] J. Ho, A. Jain, and P. Abbeel, “Denoising diffusion probabilistic models,”
in Proc. Int. Conf. Neural Inf. Process. Syst., 2020, pp. 6840–6851.
[118] Z. Wu, S. Pan, G. Long, J. Jiang, and C. Zhang, “Graph wavenet for deep
spatial-temporal graph modeling,” in Proc. Int. Joint Conf. Artif. Intell.,
2019, pp. 1907–1913.
[119] Q. Zhang, C. Huang, L. Xia, Z. Wang, Z. Li, and S. Yiu, “Automated
spatio-temporal graph contrastive learning,” in Proc. ACM Web Conf.,
2023, pp. 295–305.
[120] Q. Zhang, C. Huang, L. Xia, Z. Wang, S. M. Yiu, and R. Han, “Spatialtemporal graph learning with adversarial contrastive adaptation,” in Proc.
Int. Conf. Mach. Learn., 2023, pp. 41151–41163.
[121] Y. Chang, E. Tanin, X. Cao, and J. Qi, “Spatial structure-aware road
network embedding via graph contrastive learning,” in Proc. 26th Int.
Conf. Extending Database Technol., 2023, pp. 144–156.
[122] K. Chen et al., “FENGWU: Pushing the skillful global medium-range
weather forecast beyond 10 days lead,” 2023, arXiv:2304.02948 .

2059

[123] L. Yuan et al., “Contextualized spatio-temporal contrastive learning
with self-supervision,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., 2022, pp. 13977–13986.
[124] K. Bi, L. Xie, H. Zhang, X. Chen, X. Gu, and Q. Tian, “Pangu-weather: A
3D high-resolution model for fast and accurate global weather forecast,”
Nature, vol. 619, pp. 533–538, 2023.
[125] J. Pathak et al., “FOURCASTNET: A global data-driven high-resolution
weather model using adaptive fourier neural operators,” in Proc. Platform
Adv. Sci. Comput. Conf., 2023, pp. 1–11.
[126] Y. Zhu, Y. Ye, S. Zhang, X. Zhao, and J. Yu, “DiffTraj: Generating GPS
trajectory with diffusion probabilistic model,” in Proc. Int. Conf. Neural
Inf. Process. Syst., 2023, pp. 65168–65188.
[127] J. Ji et al., “Spatio-temporal self-supervised learning for traffic flow
prediction,” in Proc. AAAI Conf. Artif. Intell., 2023, pp. 4356–4364.
[128] J. Deng, R. Jiang, J. Zhang, and X. Song, “Multi-modality spatiotemporal forecasting via self-supervised learning,” in Proc. Int. Joint
Conf. Artif. Intell., 2024, pp. 2018–2026.
[129] Z. Gu et al., “MSTEM: Masked spatiotemporal event series modeling
for urban undisciplined events forecasting,” in Proc. ACM Int. Conf. Inf.
Knowl. Manage., 2024, pp. 685–694.
[130] H. Wen et al., “DiffSTG: Probabilistic spatio-temporal graph forecasting
with denoising diffusion models,” in Proc. 30th Int. Conf. Adv. Geographic Inf. Syst., 2023, pp. 1–12.
[131] J. Hu, X. Liu, Z. Fan, Y. Liang, and R. Zimmermann, “Towards unifying
diffusion models for probabilistic spatio-temporal graph learning,” in
Proc. 30th Int. Conf. Adv. Geographic Inf. Syst., 2024, pp. 135–146.
[132] H. Chen, Y. Jiang, S. Guo, X. Mao, Y. Lin, and H. Wan, “DiffLight:
A partial rewards conditioned diffusion model for traffic signal control
with missing data,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2024,
pp. 123353–123378.
[133] F. Du et al., “A survey of LLM datasets: From autoregressive model to
ai chatbot,” J. Comput. Sci. Technol., vol. 39, pp. 542–566, 2024.
[134] G. Chen, M. Wang, Y. Yang, K. Yu, L. Yuan, and Y. Yue, “PointGPT:
Auto-regressively generative pre-training from point clouds,” in Proc.
Int. Conf. Neural Inf. Process. Syst., 2024, pp. 29667–29679.
[135] Y. Lin et al., “UVTM: Universal vehicle trajectory modeling with ST
feature domain generation,” IEEE Trans. Knowl. Data Eng., pp. 1–14,
2025.
[136] W. Jiang, L. Zhao, and B.-l. Lu, “Large brain model for learning generic
representations with tremendous EEG data in BCI,” in Proc. Int. Conf.
Learn. Representations, 2024, pp. 1–22.
[137] J. Wu et al., “iVideoGPT: Interactive videoGPTs are scalable world models,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2024, pp. 68082–68119,
[138] G. T. Hudson et al., “Everything is a video: Unifying modalities through
next-frame prediction,” in Proc. Int. Conf. Comput. Vis., 2025, pp. 22004–
22013.
[139] K. Tian, Y. Jiang, Z. Yuan, B. Peng, and L. Wang, “Visual autoregressive
modeling: Scalable image generation via next-scale prediction,” in Proc.
Int. Conf. Neural Inf. Process. Syst., 2024, pp. 84839–84865.
[140] J. D.M.-W. C. Kenton and L. K. Toutanova, “BERT: Pre-training of deep
bidirectional transformers for language understanding,” in Proc. Conf.
North Amer. Chapter Assoc. Comput. Linguistics, Hum. Lang. Technol.,
Vol. 1 (Long Short Papers), 2019, pp. 4171–4186.
[141] K. He, X. Chen, S. Xie, Y. Li, P. Dollár, and R. Girshick, “Masked
autoencoders are scalable vision learners,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2022, pp. 16000–16009.
[142] C. Feichtenhofer et al., “Masked autoencoders as spatiotemporal learners,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2022, pp. 35946–35958.
[143] J. Sun, Y. Fan, C.-C. M. Yeh, W. Zhang, and G. Chowdhary, “Revealing
the power of masked autoencoders in traffic forecasting,” in Proc. ACM
Int. Conf. Inf. Knowl. Manage., 2024, pp. 4071–4075.
[144] Z. Tong, Y. Song, J. Wang, and L. Wang, “VideoMAE: Masked autoencoders are data-efficient learners for self-supervised video pre-training,”
in Proc. Int. Conf. Neural Inf. Process. Syst., pp. 10078–10093, 2022.
[145] Z. Cai et al., “MARLIN: Masked autoencoder for facial video representation learning,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.,
2023, pp. 1493–1504.
[146] Y. Pang, W. Wang, F. E. Tay, W. Liu, Y. Tian, and L. Yuan, “Masked
autoencoders for point cloud self-supervised learning,” in Proc. Eur. Conf.
Comput. Vis., 2022, pp. 604–621.
[147] Y. Fang, J. Xie, Y. Zhao, L. Chen, Y. Gao, and K. Zheng, “Temporalfrequency masked autoencoders for time series anomaly detection,” in
Proc. IEEE 40th Int. Conf. Data Eng., 2024, pp. 1228–1241.
[148] W. Yu, M. Huang, S. Wu, and Y. Zhang, “Ensembled masked graph
autoencoders for link anomaly detection in a road network considering
spatiotemporal features,” Inf. Sci., vol. 622, pp. 456–475, 2023.

2060

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 3, MARCH 2026

[149] P. Khosla et al., “Supervised contrastive learning,” in Proc. Int. Conf.
Neural Inf. Process. Syst., 2020, pp. 18661–18673.
[150] J. Yang et al., “Vision-language pre-training with triple contrastive learning,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2022,
pp. 15671–15680.
[151] A. Diba et al., “Vi2CLR: Video and image for visual contrastive learning
of representation,” in Proc. Int. Conf. Comput. Vis., 2021, pp. 1502–1512.
[152] Y. You, T. Chen, Y. Sui, T. Chen, Z. Wang, and Y. Shen, “Graph contrastive
learning with augmentations,” in Proc. Int. Conf. Neural Inf. Process.
Syst., 2020, pp. 5812–5823.
[153] S. Ding, R. Qian, and H. Xiong, “Dual contrastive learning for spatiotemporal representation,” in Proc. 30th ACM Int. Conf. Multimedia, 2022,
pp. 5649–5658.
[154] J. Tang, L. Xia, J. Hu, and C. Huang, “Spatio-temporal meta contrastive learning,” in Proc. ACM Int. Conf. Inf. Knowl. Manage., 2023,
pp. 2412–2421.
[155] X. Gao, Y. Yang, Y. Zhang, M. Li, J.-G. Yu, and S. Du, “Efficient spatiotemporal contrastive learning for skeleton-based 3-d action recognition,”
IEEE Trans. Multimedia, vol. 25, pp. 405–417, 2023.
[156] Y. Fang, Y. Qin, H. Luo, F. Zhao, and K. Zheng, “STWave+ : A multiscale efficient spectral graph attention network with long-term trends for
disentangled traffic flow forecasting,” IEEE Trans. Knowl. Data Eng.,
vol. 3, no. 6, pp. 2671–2685, Jun. 2024.
[157] X. Liu, Y. Liang, C. Huang, Y. Zheng, B. Hooi, and R. Zimmermann,
“When do contrastive learning signals help spatio-temporal graph forecasting?” in Proc. 30th Int. Conf. Adv. Geographic Inf. Syst., 2022,
pp. 1–12.
[158] R. Li, T. Zhong, X. Jiang, G. Trajcevski, J. Wu, and F. Zhou, “Mining spatio-temporal relations via self-paced graph contrastive learning,”
in Proc. ACM SIGKDD Conf. Knowl. Discovery Data Mining, 2022,
pp. 936–944.
[159] Y. Chang, J. Qi, Y. Liang, and E. Tanin, “Contrastive trajectory similarity
learning with dual-feature attention,” in Proc. IEEE 39th Int. Conf. Data
Eng., 2023, pp. 2933–2945.
[160] Y. Yan et al., “UrbanCLIP: Learning text-enhanced urban region profiling
with contrastive language-image pretraining from the web,” in Proc. ACM
Web Conf., 2024, pp. 4006–4017.
[161] R. Xu et al., “MM-path: Multi-modal, multi-granularity path representation learning,” in Proc. ACM SIGKDD Conf. Knowl. Discovery Data
Mining, 2025, pp. 1703–1714.
[162] R. Rombach, A. Blattmann, D. Lorenz, P. Esser, and B. Ommer, “High-resolution image synthesis with latent diffusion models,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2022,
pp. 10684–10695.
[163] W. Peebles and S. Xie, “Scalable diffusion models with transformers,” in
Proc. Int. Conf. Comput. Vis., 2023, pp. 4195–4205.
[164] X. Xu, Y. Wei, P. Wang, X. Luo, F. Zhou, and G. Trajcevski, “Diffusion
probabilistic modeling for fine-grained urban traffic flow inference with
relaxed structural constraint,” in Proc. IEEE Int. Conf. Acoust., Speech
Signal Process., 2023, pp. 1–5.
[165] S. Rühling Cachay, B. Zhao, H. Joren, and R. Yu, “DYffusion: A
dynamics-informed diffusion model for spatiotemporal forecasting,” in
Proc. Int. Conf. Neural Inf. Process. Syst., 2024, pp. 45259–45287.
[166] D. Daiya, M. Yadav, and H. S. Rao, “DiffSTOCK: Probabilistic relational
stock market predictions using diffusion models,” in Proc. IEEE Int. Conf.
Acoust., Speech Signal Process., 2024, pp. 7335–7339.
[167] Y. Duan et al., “Causal deciphering and inpainting in spatio-temporal
dynamics via diffusion model,” in Proc. Int. Conf. Neural Inf. Process.
Syst., 2024, pp. 107604–107632.
[168] H. Chen, J. Ding, Y. Li, Y. Wang, and X.-P. Zhang, “Social physics
informed diffusion model for crowd simulation,” in Proc. AAAI Conf.
Artif. Intell., 2024, pp. 474–482.
[169] Y. Yuan, J. Ding, C. Shao, D. Jin, and Y. Li, “Spatio-temporal diffusion
point processes,” in Proc. ACM SIGKDD Conf. Knowl. Discovery Data
Mining, 2023, pp. 3173–3184.
[170] M. Liu, H. Huang, H. Feng, L. Sun, B. Du, and Y. Fu, “PriSTI: A
conditional diffusion framework for spatiotemporal imputation,” in Proc.
IEEE 39th Int. Conf. Data Eng., 2023, pp. 1927–1939.
[171] S. Zhang, S. Wang, X. Tan, R. Liu, J. Zhang, and J. Wang, “SASDIM:
Self-adaptive noise scaling diffusion model for spatial time series imputation,” in Proc. Int. Joint Conf. Artif. Intell., 2024, pp. 2561–2569.
[172] H. Wang, J. Han, W. Fan, W. Zhang, and H. Liu, “PhyDA: Physics-guided
diffusion models for data assimilation in atmospheric systems,” 2025,
arXiv:2505.12882 .

[173] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for image
recognition,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.,
2016, pp. 770–778.
[174] D. Alexey, “An image is worth 16x16 words: Transformers for image
recognition at scale,” in Proc. Int. Conf. Learn. Representations, 2021,
pp. 1–22.
[175] D. Tran, H. Wang, L. Torresani, J. Ray, Y. LeCun, and M. Paluri, “A closer
look at spatiotemporal convolutions for action recognition,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2018, pp. 6450–6459.
[176] H. Qu, Y. Cai, and J. Liu, “LLMs are good action recognizers,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2024,
pp. 18395–18406.
[177] Q. Sun, Y. Fang, L. Wu, X. Wang, and Y. Cao, “EVA-CLIP: Improved
training techniques for clip at scale,” 2023, arXiv:2303.15389 .
[178] P. P. Ray, “ChatGPT: A comprehensive review on background, applications, key challenges, bias, ethics, limitations and future scope,” in Proc.
Internet Things Cyber- Phys. Syst., pp. 121–154, 2023.
[179] J. Bai et al., “Qwen technical report,” 2023, arXiv:2309.16609 .
[180] T. GLM et al., “ChatGLM: A family of large language models from
GLM-130b to GLM-4 all tools,” 2024, arXiv:2406.12793 .
[181] Y. Wu, Y. Peng, J. Yu, and R. S. Lee, “MAS4POI: A multi-agents collaboration system for next POI recommendation,” in Proc. Pacific-Asia
Conf. Knowl. Discovery Data Mining, 2025, pp. 356–367.
[182] J. Wang et al., “Large language models as urban residents: An LLM agent
framework for personal mobility generation,” in Proc. Int. Conf. Neural
Inf. Process. Syst., 2024, pp. 124547–124574.
[183] L. Zheng et al., “Extracting spatiotemporal data from gradients with large
language models,” 2024, arXiv:2410.16121 .
[184] A. Q. Jiang et al., “Mixtral of experts,” 2024, arXiv:2401.04088 ,
[185] X. Yang et al., “A large language model for electronic health records,”
npj Digit. Med., vol. 5, 2022, Art. no. 194.
[186] Z. Li, J. Kim, Y.-Y. Chiang, and M. Chen, “SpaBERT: A pretrained
language model from geographic data for geo-entity representation,” in
Proc. Findings Assoc. Comput. Linguistics, 2022, pp. 2757–2769.
[187] Y. Chen, X. Wang, and G. Xu, “GATGPT: A pre-trained large language
model with graph attention network for spatiotemporal imputation,”
2023, arXiv:2311.14332 .
[188] Y. Ren, Y. Chen, S. Liu, B. Wang, H. Yu, and Z. Cui, “TPLLM: A traffic
prediction framework based on pretrained large language models,” 2024,
arXiv:2403.02221 .
[189] L. Liu, S. Yu, R. Wang, Z. Ma, and Y. Shen, “How can large language
models understand spatial-temporal data?” 2024, arXiv:2401.14192 .
[190] H. Wang, J. Han, W. Fan, and H. Liu, “Empowering pre-trained language
models for spatio-temporal forecasting via decoupling enhanced discrete
reprogramming,” in Proc. Int. Joint Conf. Artif. Intell., 2025, pp. 1–7.
[191] H. Xue, B. P. Voutharoja, and F. D. Salim, “Leveraging language foundation models for human mobility forecasting,” in Proc. 30th Int. Conf.
Adv. Geographic Inf. Syst., 2022, pp. 1–9.
[192] H. Touvron et al., “LLaMA: Open and efficient foundation language
models,” 2023, arXiv:2302.13971 .
[193] C. Liu et al., “Spatial-temporal large language model for traffic prediction,” in Proc. 25th IEEE Int. Conf. Mobile Data Manage., 2024,
pp. 31–40.
[194] P. Li, M. de Rijke, H. Xue, S. Ao, Y. Song, and F. D. Salim, “Large language models for next point-of-interest recommendation,” in Proc. 47th
Int. ACM SIGIR Conf. Res. Develop. Inf. Retrieval, 2024, pp. 1463–1472.
[195] M. Chen, Z. Li, W. Huang, Y. Gong, and Y. Yin, “Profiling urban streets:
A semi-supervised prediction model based on street view imagery and
spatial topology,” in Proc. ACM SIGKDD Conf. Knowl. Discovery Data
Mining, 2024, pp. 319–328.
[196] X. Hao et al., “UrbanVLP: A multi-granularity vision-language pretrained foundation model for urban indicator prediction,” in Proc. AAAI
Conf. Artif. Intell., 2025, pp. 1–17.
[197] P. Gao et al., “LLaMA-Adapter V2: Parameter-efficient visual instruction
model,” 2023, arXiv:2304.15010 .
[198] Z. Lin et al., “SPHINX: The joint mixing of weights, tasks, and visual
embeddings for multi-modal large language models,” in Proc. 18th Eur.
Conf. Comput. Vis., 2024, pp. 1–24.
[199] R. Schumann, W. Zhu, W. Feng, T.-J. Fu, S. Riezler, and W. Y. Wang,
“VELMA: Verbalization embodiment of LLM agents for vision and
language navigation in street view,” in Proc. AAAI Conf. Artif. Intell.,
2024, pp. 18924–18933.
[200] L. Giray, “Prompt engineering with ChatGPT: A guide for academic
writers,” Ann. Biomed. Eng., vol. 51, pp. 2629–2633, 2023.

FANG et al.: UNRAVELING SPATIO-TEMPORAL FOUNDATION MODELS VIA THE PIPELINE LENS: A COMPREHENSIVE REVIEW

[201] H. Xue and F. D. Salim, “PromptCast: A new prompt-based learning
paradigm for time series forecasting,” IEEE Trans. Knowl. Data Eng.,
vol. 36, no. 11, pp. 6851–6864, Nov. 2024.
[202] X. Wang, M. Fang, Z. Zeng, and T. Cheng, “Where would I go next? Large
language models as human mobility predictors,” 2023, arXiv:2308.15197
.
[203] X. Yu, Z. Chen, Y. Ling, S. Dong, Z. Liu, and Y. Lu, “Harnessing LLMs for
temporal data-a study on explainable financial time series forecasting,”
in Proc. Empirical Methods Natural Lang. Process., 2023, pp. 739–753.
[204] C. Sun, H. Li, Y. Li, and S. Hong, “TEST: Text prototype aligned
embedding to activate LLM’s ability for time series,” in Proc. Int. Conf.
Learn. Representations, 2024, pp. 1–28.
[205] M. Jin et al., “Time-LLM: Time series forecasting by reprogramming
large language models,” in Proc. Int. Conf. Learn. Representations, 2023,
pp. 1–24.
[206] X. Liu et al., “Large language models are few-shot health learners,” 2023,
arXiv:2305.15525 .
[207] B. Li, Y. Ge, Y. Chen, Y. Ge, R. Zhang, and Y. Shan, “Seed-bench-2-plus:
Benchmarking multimodal large language models with text-rich visual
comprehension,” 2024, arXiv:2404.16790 .
[208] Z. Chen, L. N. Zheng, C. Lu, J. Yuan, and D. Zhu, “ChatGPT informed graph neural network for stock movement prediction,” in Proc.
ACM SIGKDD Conf. Knowl. Discovery Data Mining RobustFin, 2023,
pp. 1–10.
[209] P. Li et al., “RealTCD: Temporal causal discovery from interventional
data with large language model,” in Proc. ACM Int. Conf. Inf. Knowl.
Manage., 2024, pp. 4669–4677.
[210] H. Xu, Y. Gao, Z. Hui, J. Li, and X. Gao, “Language knowledge-assisted
representation learning for skeleton-based action recognition,” 2023,
arXiv:2305.12398 .
[211] L. Da, M. Gao, H. Mei, and H. Wei, “Prompt to transfer: Sim-to-real
transfer for traffic signal control with prompt learning,” in Proc. AAAI
Conf. Artif. Intell., 2024, pp. 82–90.
[212] Z. Li et al., “Ocean significant wave height estimation with spatiotemporally aware large language models,” in Proc. ACM Int. Conf. Inf.
Knowl. Manage., 2024, pp. 3892–3896.
[213] Y. Liu, C. Kuai, X. Liao, H. Ma, B. Y. He, and J. Ma, “Semantic trajectory
data mining with LLM-informed POI classification,” in IEEE 27th Int.
Conf. Intell. Transp. Syst., 2024, pp. 207–213.
[214] Y. Ning and H. Liu, “UrbanKGent: A unified large language model agent
framework for urban knowledge graph construction,” in Proc. Int. Conf.
Neural Inf. Process. Syst., 2024, pp. 1–28.
[215] L. Zhong, L. Wang, X. Yang, and Q. Liao, “Comapoi: A collaborative
multi-agent framework for next poi prediction bridging the gap between
trajectory and language,” in Proc. 48th Int. ACM SIGIR Conf. Res.
Develop. Inf. Retrieva, 2025, pp. 1768–1778.
[216] A. Van Den et al., “Neural discrete representation learning,” in Proc. Int.
Conf. Neural Inf. Process. Syst., 2017, pp. 6309–6318.
[217] S. T. Piantadosi, “Zipf’s word frequency law in natural language: A
critical review and future directions,” Psychon. Bull. Rev., vol. 21,
pp. 1112–1130, 2014.
[218] D. Kondratyuk et al., “VideoPoet: A large language model for zeroshot video generation,” in Proc. Int. Conf. Mach. Learn., 2024,
pp. 25105–25124.
[219] Y. Wei, Y. Lin, H. Gao, R. Xu, S. B. Yang, and J. Hu, “PathLLM: A multi-modal path representation learning by aligning and
fusing with large language models,” in Proc. ACM Web Conf., 2025,
pp. 2289–2298.
[220] C. Liu et al., “TimeCMA: Towards LLM-empowered time series forecasting via cross-modality alignment,” in Proc. AAAI Conf. Artif. Intell.,
2025, pp. 1–9.
[221] Z. Li, W. Zhou, Y.-Y. Chiang, and M. Chen, “GeoLM: Empowering
language models for geospatially grounded language understanding,” in
Proc. Conf. Empirical Methods Natural Lang., 2023, pp. 5227–5240.
[222] W. Shao, Z. Fang, L. Chen, and Y. Gao, “Towards trajectory anomaly
detection: A fine-grained and noise-resilient framework,” in Proc. ACM
SIGKDD Conf. Knowl. Discovery Data Mining, 2025, pp. 2490–2501.
[223] Y. Fan et al., “Spatio-temporal denoising graph autoencoders with data
augmentation for photovoltaic data imputation,” in Proc. ACM Manage.
Data, 2023, pp. 1–19.
[224] Z. Ma et al., “FusionSF: Fuse heterogeneous modalities in a vector
quantized framework for robust solar power forecasting,” in Proc. ACM
SIGKDD Conf. Knowl. Discovery Data Mining, 2024, pp. 5532–5543.
[225] L. Deng, T. Wang, Y. Zhao, and K. Zheng, “MILLION: A general multiobjective framework with controllable risk for portfolio management,”
Proc. VLDB, vol. 18, no. 2, 2025, pp. 1–9, 2025.

2061

[226] Y. Duan et al., “CaT-GNN: Enhancing credit card fraud detection
via causal temporal graph neural networks,” in Proc. COLING, 2024,
pp. 1–10.
[227] B. Hui, Y. Fang, T. Xia, S. Aykent, and W.-S. Ku, “Constrained market
share maximization by signal-guided optimization,” in Proc. AAAI Conf.
Artif. Intell., 2023, pp. 4330–4338.
[228] J. Luo et al., “Timeseries suppliers allocation risk optimization via
deep black litterman model,” in Proc. AAAI Conf. Artif. Intell., 2025,
pp. 1–14.
[229] Y. Tong, J. She, B. Ding, L. Wang, and L. Chen, “Online mobile microtask allocation in spatial crowdsourcing,” in Proc. IEEE 32nd Int. Conf.
Data Eng., 2016, pp. 49–60.
[230] Z. Chen, P. Cheng, L. Chen, X. Lin, and C. Shahabi, “Fair task assignment in spatial crowdsourcing,” Proc. VLDB Endowment„ vol. 13,
pp. 2479–2492, 2020.
[231] M. Grunde-McLaughlin, M. S. Lam, R. Krishna, D. S. Weld, and J. Heer,
“Designing LLM chains by adapting techniques from crowdsourcing
workflows,” ACM Trans. Comput.- Hum. Interaction, vol. 32, no. 3,
pp. 1–57, 2025.
[232] G. I. Yussif, M. Abdelatti, and A. Hendawi, “Harnessing crowdsourced
mobile data and LLM for dynamic and accessible pedestrian routing,” in Proc. 26th IEEE Int. Conf. Mobile Data Manage., 2025,
pp. 109–112.
[233] Y. Xu et al., “ProtoMix: Augmenting health status representation learning via prototype-based mixup,” in Proc. ACM SIGKDD Conf. Knowl.
Discovery Data Mining, 2024, pp. 3633–3644.
[234] L. Y. Jiang et al., “Health system-scale language models are all-purpose
prediction engines,” Nature, vol. 619, pp. 357–362, 2023.
[235] X. Jiang et al., “Hykge: A hypothesis knowledge graph enhanced RAG
framework for accurate and reliable medical LLMS responses,” in Proc.
Assoc. Comput. Linguistics, 2025, pp. 11836–11856.
[236] S. Lai, Z. Xu, W. Zhang, H. Liu, and H. Xiong, “Large language
models as traffic signal control agents: Capacity and opportunity,”
in Proc. ACM SIGKDD Conf. Knowl. Discovery Data Mining, 2025,
pp. 1–13.
[237] A. Seff et al., “MotionLM: Multi-agent motion forecasting as language
modeling,” in Proc. Int. Conf. Comput. Vis., 2023, pp. 8579–8590.
[238] X. Zheng et al., “Large language models powered context-aware motion
prediction in autonomous driving,” in Proc. IEEE/RSJ Int. Conf. Intell.
Robots Syst., 2024, pp. 980–985.
[239] Q. Xu, Y. Shi, J. L. Bamber, C. Ouyang, and X. X. Zhu, “Large-scale
flood modeling and forecasting with floodcast,” Water Res., vol. 264,
2024, Art. no. 122162.
[240] X. Si, X. Wu, Z. Li, S. Wang, and J. Zhu, “An all-in-one seismic
phase picking, location, and association network for multi-task multistation earthquake monitoring,” Commun. Earth Environ., vol. 5, 2024,
Art. no. 22.
[241] Z. Wu, F. Liu, J. Han, Y. Liang, and H. Liu, “Spatial-temporal mixture-ofgraph-experts for multi-type crime prediction,” 2024, arXiv:2409.15764
.
[242] Z. Guo, X. Wu, L. Liang, H. Sheng, N. Chen, and Z. Bi, “Cross-domain
foundation model adaptation: Pioneering computer vision models for
geophysical data analysis,” J. Geophys. Res., Mach. Learn. Comput.,
vol. 2, no. 1, 2025, Art. no. e2025JH000601.
[243] X. Si, X. Wu, H. Sheng, J. Zhu, and Z. Li, “SeisCLIP: A seismology
foundation model pre-trained by multi-modal data for multi-purpose
seismic feature extraction,” IEEE Trans. Geosci. Remote Sens., vol. 62,
2024, Art. no. 5903713.
[244] H. Zhang, F. Zhao, C. Wang, H. Luo, H. Xiong, and Y. Fang, “Knowledge
distillation for travel time estimation,” IEEE Trans. Intell. Transp. Syst.,
vol. 25, no. 8, pp. 9631–9642, Aug. 2024.
[245] X. Ma, G. Fang, and X. Wang, “LLM-Pruner: On the structural pruning
of large language models,” in Proc. Int. Conf. Neural Inf. Process. Syst.,
2023, pp. 21702–21720.
[246] K. Egashira, M. Vero, R. Staab, J. He, and M. Vechev, “Exploiting
LLM quantization,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2024,
pp. 1–17.
[247] H. Miao et al., “Less is more: Efficient time series dataset condensation
via two-fold modal matching,” in Proc. VLDB Endowment, vol. 18, 2025,
pp. 226–238.
[248] X. Yu, J. Wang, Y. Yang, Q. Huang, and K. Qu, “BIGCity: A universal
spatiotemporal model for unified trajectory and traffic state data analysis,”
in Proc. IEEE 41st Int. Conf. Data Eng., 2025, pp. 4455–4469.
[249] X. Qiu et al., “TFB: Towards comprehensive and fair benchmarking of
time series forecasting methods,” in Proc. VLDB Endowment, vol. 18,
pp. 226–238, 2024.

2062

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 3, MARCH 2026

Yuchen Fang is currently working toward the PhD
degree with the University of Electronic Science and
Technology of China. He has authored or coauthored
several papers in top journals and conference proceedings, such as SIGKDD, ICDE, SIGIR, IEEE Transactions on Intelligent Transportation Systems, and IEEE
Transactions on Knowledge and Data Engineering.
His research interests include spatio-temporal data
mining, time series analysis, and urban computing,
with a special focus on traffic forecasting.

Hao Miao received the PhD degree in computer
science from Aalborg University, Denmark. He is
currently a research assistant professor with the Department of Computing, Hong Kong Polytechnic University. His research interests include spatio-temporal
data analytics, trajectory computing, and large language models.

Yuxuan Liang (Member, IEEE) received the PhD
degree from the School of Computing, National University of Singapore. He is currently an assistant professor with The Hong Kong University of Science and
Technology (Guangzhou), working on the research,
development, and innovation of spatio-temporal data
mining and urban computing. He has authored or
coauthored more than 100 papers in refereed journals and conferences with more than 10,000 citations on Google Scholar and was recognized as Stanford/Elsevier Top 2% Scientists in 2024. He is an
associate editor for Neurocomputing (IF=6.0) and area chair/senior PC of
prestigious conferences such as KDD, NeurIPS, IJCAI, MM, and ICASSP. He
is the tutorial co-chair of SSTD’25 and workshop co-chair for PAKDD’26. He
was the recipient of ACM SIGSPATIAL China Chapter Rising Star Award, 23 rd
China Patent Excellence Award, and SDSC Dissertation Research Fellowship.

Liwei Deng received the PhD degree in computer
science from the University of Electronic Science and
Technology of China, China, in 2025. He is currently
a postdoc of computer science with Aalborg University. His research interests include spatio-temporal
data mining and vector approximate nearest neighbor
search.

Yue Cui received the bachelor’s degree from the
University of Electronic Science and Technology of
China, in 2020. She is currently working toward
the PhD degree with the Hong Kong University of
Science and Technology (HKUST). Her research
interests include the interdisciplinary study of data
science and social science, including reliability and
governance and developing responsible and efficient
solutions to identify, evaluate, mitigate/control, the
effect of data on societal consequences across its lifecycle, prioritizing aspects such as efficacy, equality,
equity, and privacy.

Ximu Zeng (Graduate Student Member, IEEE) received the bachelor’s degree in data science and Big
Data technology from the Chongqing University of
Posts and Telecommunications, in 2022. She is currently working toward the PhD degree with the School
of Computer Science and Technology, University of
Electronic Science and Technology of China. Her
research interests include spatial-temporal data mining, spatial crowdsourcing, and vector approximate
nearest neighbor search.

Yuyang Xia received the bachelor’s degree in computer science and technology from the Chongqing
University of Posts and Telecommunications, in
2021. He is currently working toward the PhD degree with the University of Electronic Science and
Technology of China. His research interests include
autonomous driving and spatio-temporal data mining.

Yan Zhao (Senior Member, IEEE) received the doctoral degree in computer science from Soochow
University, China, in 2020. She is currently a professor with the Shenzhen Institute for Advanced
Study, University of Electronic Science and Technology of China. Her research interests include spatial
databases and trajectory computing.

Torben Bach Pedersen (Senior Member, IEEE)
received the honorary doctorate degree from TU
Dresden, Dresden, Germany. He is currently a professor with the Center for Data-Intensive Systems
(Daisy), Aalborg University, Aalborg, Denmark. His
research interests include predictive, prescriptive, and
extreme-scale data analytics with digital energy as the
main application area. He is an ACM distinguished
scientist, IEEE Computer Society distinguished contributor, member of the Danish Academy of Technical
Sciences.

Christian S. Jensen (Fellow, IEEE) is currently a
professor of computer science with Aalborg University, Denmark. His research interests include data
management and analytics and temporal and spatiotemporal data. He is a member of Academia Europaea, Royal Danish Academy of Sciences and Letters, and Danish Academy of Technical Sciences. He
is a fellow of ACM.

FANG et al.: UNRAVELING SPATIO-TEMPORAL FOUNDATION MODELS VIA THE PIPELINE LENS: A COMPREHENSIVE REVIEW

Xiaofang Zhou (Fellow, IEEE) is currently the Otto
Poon professor of engineering and chair professor
of computer science and engineering with the Hong
Kong University of Science and Technology. He is
also the head of the Department of Computer Science
and Engineering. His research focuses on finding effective and efficient solutions to managing integrating
and analyzing very large amounts of complex data.

2063

Kai Zheng (Senior Member, IEEE) received the PhD
degree in computer science from The University of
Queensland, in 2012. He is currently a professor with
the University of Electronic Science and Technology of China. His research interest includes spatiotemporal data management, spatial crowdsourcing,
intelligent database systems and vector data management.
PAPER_TEXT
