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
# [635] Corner Case Detection and Generation for Autonomous Driving: An Overview
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
编号：635
题名：Corner Case Detection and Generation for Autonomous Driving: An Overview
年份：2026
DOI：10.1109/tits.2026.3688488
来源：IEEE Transactions on Intelligent Transportation Systems
PDF：paper/10.1109_TITS.2026.3688488.pdf
已有粗分类：数据集、基准、综述与开源工具
二级关联：无
相关性：弱相关，分数 2
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\635.txt
- 原始字符数：154177
- 本次发送字符数：140041
- 是否截断：True

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

1

Corner Case Detection and Generation for
Autonomous Driving: An Overview
Yunji Liang , Junteng Liu , Xiaokai Yan, Xiaolong Zheng , Member, IEEE, Lei Tang , Member, IEEE,
Luwen Huangfu, Sagar Samtani , Member, IEEE, and Zhiwen Yu , Senior Member, IEEE

Abstract—Safety concerns remain one of the most significant
obstacles to the large-scale deployment and continued advancement of autonomous driving (AD) systems. A major underlying
cause of many safety-related incidents in AD systems is suboptimal or erroneous decision-making when the vehicle encounters
corner cases (CCs)—rare, unexpected, or extreme situations
that fall outside typical operating conditions. Although recent
advances in artificial intelligence have driven substantial progress
in both autonomous driving and corner-case research, the field
still lacks a coherent conceptual foundation and a systematic,
widely accepted categorization of CCs. In this survey, we address
this gap by offering a structured review of the existing corner-case
literature along three key dimensions: understanding, detection,
and generation. The key contribution is a three-level classification
of corner cases—spanning data-level, model-level, and semanticlevel CCs—that clarifies and disambiguates competing definitions
and perspectives on AD corner cases. Building on this framework,
we examine simulator-based methods for corner-case selection
and data generation, and we identify open challenges, promising
directions, and potential solutions to more effectively handle
corner cases in autonomous driving systems.
Index Terms—Corner case, autonomous driving, out-ofdistribution, generated data set.

I. I NTRODUCTION

W

ITH advances in artificial intelligence, significant
progress has been made in autonomous vehicles,
enhancing perception capabilities and refining decisionmaking algorithms. However, safety concerns surrounding autonomous driving have garnered growing attention
amid the widespread deployment of AI-powered algorithms
Received 20 May 2024; revised 28 December 2025 and 30 March 2026;
accepted 25 April 2026. This work was supported by the Natural Science
Foundation of China under Grant 62372378, Grant 72225011, and Grant
72434005. The Associate Editor for this article was S. Sacone. (Corresponding
author: Yunji Liang.)
Yunji Liang, Junteng Liu, Xiaokai Yan, and Zhiwen Yu are with the School
of Computer Science, Northwestern Polytechnical University, Xi’an 710072,
China (e-mail: liangyunji@nwpu.edu.cn).
Xiaolong Zheng is with the State Key Laboratory of Multimodal Artificial
Intelligence Systems and the State Key Laboratory of Management and
Control for Complex Systems, Institute of Automation, Chinese Academy
of Sciences, Beijing 100190, China, and also with the School of Artificial
Intelligence, University of Chinese Academy of Sciences, Beijing 100049,
China (e-mail: xiaolong.zheng@ia.ac.cn).
Lei Tang is with the College of Transportation Engineering, Chang’an
University, Xi’an 710064, China (e-mail: tanglei24@chd.edu.cn).
Luwen Huangfu is with the Fowler College of Business, San Diego
State University, San Diego, CA 92182 USA (e-mail: lhuangfu@sdsu.edu).
Sagar Samtani is with the Kelley School of Business, Indiana University,
Bloomington, IN 47405 USA (e-mail: ssamtani@iu.edu).
Digital Object Identifier 10.1109/TITS.2026.3688488

in real-world traffic environments [1], [2], [3], [4], [5],
[6]—particularly in safety-critical scenarios such as adverse
weather conditions [7], [8], adversarial attacks [9], [10], [11],
and unseen driving situations [12], [13], [14], [15], [16], [17].
Among the core safety challenges for autonomous driving,
rare and safety-critical incidents in the perception stage are of
paramount importance: failures in environmental sensing and
scene understanding can directly propagate to the downstream
planning and control module. This survey, therefore, focuses
on corner cases in the perception subsystem of autonomous
driving architectures, specifically investigating how in-vehicle
sensors acquire, preprocess, and analyze environmental information under rare, unexpected, and hard-to-handle operating
conditions.
Existing literature on autonomous driving surveys have
already underscored the significance of simulation, diverse
data distributions, and safety-critical scenario validation,
including autonomous driving policy learning [18], [19],
open-source simulators [20], [21], virtual testing tools (encompassing simulators, datasets, and competitive benchmarks)
[22], [23], data-driven traffic simulation [24], and foundationmodel-based scenario generation and analysis [25]. These
works provide valuable contextual insights for autonomous
driving validation and long-tail scenario analysis. Nevertheless, they primarily focus on policy learning, simulation
platforms, testing pipelines, traffic evolution, or scenario generation/analysis in a broad sense, and do not offer a dedicated
survey that makes perception-stage corner cases its primary
research focus. This research gap highlights the need for
a clearer and more focused synthesis of the literature on
perception-oriented corner cases in autonomous driving.
A. Importance of Corner Case for Driving Safety
In autonomous driving research, corner cases (CC) refer
to rare and unexpected situations that fall outside normal
operating conditions and the usual parameters of perception systems. They are crucial for validating the safety of
autonomous vehicle perception modules, which can fail in scenarios not represented in their training data, potentially leading
to accidents due to object misclassification, missed obstacles,
or inaccurate distance estimation. Typical examples include
pedestrians abruptly stepping into the roadway, headlight glare
impairing camera visibility, and unusual road hazards such as
fallen tree branches. Analyzing these cases enables researchers

1558-0016 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
2

to design methods that reduce their negative impact on sensor
interpretation and environment modeling.
Nowadays, there is no consensus on the definition of
the term corner case, and existing descriptive definitions
often implicitly focus on perception-related scenarios. Initially,
numerous descriptive definitions of corner cases are proposed.
For example, Bolte et al. [26] defined a corner case as a
non-predictable relevant object/class in a relevant location.
Breitenstein et al. [27] emphasized that a known object in
an unusual location is a corner case. For example, in a
traffic scene, if the relationships among participants do not
conform to prior knowledge or common sense, the object that
violates the rules is defined as a corner case. Li et al. [28]
considered the spatial relationship of objects and deemed
objects that are about to block a potential path of the selfdriving vehicle as the corner case. However, these descriptive
definitions of CCs are task-specific. In general, outliers,
anomalies, OOD samples, adversary samples, and corner cases
are used interchangeably in perception-related research. For
example, Heidecker et al. [29] associated corner cases with
outliers, novelty, and anomaly samples, and defined sensordriven corner cases for LiDAR, RADAR, and cameras. In
contrast, numerous definitions of corner cases have been
developed based on the complexity of the anomalies [27]. The
diversity of what may constitute the corner case has, to some
extent, shaped the solutions to detect these samples. On the
other hand, OOD samples are treated as corner cases to assess
the trained perception models’ generalization to unseen or
novel objects. Zhou et al. [30] provided systematic overviews
of the detection of out-of-distribution samples. In addition,
adversarial samples that can mislead the perception model to
induce incorrect decisions are also treated as corner cases [11],
[31], [32].
B. Our Contributions
There are numerous survey studies associated with anomaly
examples [33], [34], out-of-distribution samples [30], [35],
adversary samples [36], policy learning [18], simulators
and virtual testing [20], [22], traffic simulation [24], and
foundation-model-based scenario generation and analysis [25].
None of these works, however, takes perception-stage corner
cases as their central research object, nor do they offer a
unified discussion of how such cases ought to be defined,
detected, generated, and evaluated—alongside the supporting
role of dedicated datasets and simulators—in the context of
autonomous driving.
Unlike previous studies, this survey provides a comprehensive examination of perception-oriented corner cases that
are crucial for maintaining the operational reliability of
autonomous driving systems. As shown in Fig. 1, the integrated use of heterogeneous sensors (cameras, LiDARs, and
RADARs) establishes the core data basis for detecting and
analyzing these critical scenarios. Despite this technological
foundation and recent progress in sensing and anomaly-aware
perception that have advanced real-time corner-case detection, there is still no dedicated, comprehensive survey that
systematically organizes research on perception-stage corner
cases within a unified framework. This study addresses this

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

gap by offering the first unified survey and taxonomy, thereby
clarifying the scope of existing research, improving the effectiveness of anomaly management strategies, identifying open
research challenges, and shedding light on their implications
for ensuring the safety of autonomous driving. The principal
contributions of this work are as follows.
• We conduct a systematical literature overview of studies
associated with perception-stage corner cases and provide
a multigranularity taxonomy of the existing solutions
for the detection of these corner cases. Specifically, we
provide the problem definitions of corner cases from three
levels, including the data level, the model level, and the
semantic level, and formulate these problems mathematically. Meanwhile, a comprehensive literature overview is
presented to investigate the existing detection solutions at
these three levels in the context of autonomous driving
perception.
• As data collection from the real world is time-consuming
and expensive, synthesizing large-scale corner cases for
model training is a promising solution. In this paper, we
also provide an overview of generating corner cases from
scene simulators and generation algorithms. In contrast
to prior simulator- or scenario-centric reviews [20], [22],
[24], [25], our discussion is explicitly organized around
how these tools and methods facilitate the study of
perception-stage corner cases. In addition, we outline the
challenges and research opportunities.
As illustrated in Fig. 2, the remainder of this paper
is organized as follows. Section II refines the definitions
of perception-stage CCs from three perspectives related to
sensors and perception tasks. Sections III and IV then summarize the main approaches for detecting and generating
perception-oriented CCs, respectively. Sections V and VI
introduce commonly used performance evaluation metrics,
large-scale public datasets, and non-commercial simulators tailored to perception-stage corner cases in autonomous driving.
Section VII discusses current limitations and outlines challenges for future work on perception-related corner case
research. Finally, Section VIII concludes the paper by summarizing key contributions and highlighting future research
directions.
II. D EFINITIONS OF C ORNER C ASES
Understanding corner cases is central to the safety assurance
of autonomous driving systems, yet a unified and rigorous
definition remains absent. To fill this gap, we propose a
three-level framework grounded in the end-to-end perception
pipeline that spans input, processing, and output. Specifically,
the framework is structured along three orthogonal dimensions: data level, model level, and semantic level. Together,
these dimensions provide a complete and non-overlapping
characterization of CCs. The data level captures abnormalities
in raw sensory input, including noise, corruption, and distributional shifts. The model level concerns failures arising from
the processing stage, such as limited robustness and unreliable
algorithmic behavior. The semantic level addresses deviations
in scene meaning, contextual consistency, and safety-critical

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIANG et al.: CORNER CASE DETECTION AND GENERATION FOR AUTONOMOUS DRIVING: AN OVERVIEW

3

Fig. 1. An overview of the autonomous driving system (ADS). In ADS, a wide variety of sensors, including LiDAR, RADAR, and vision cameras, are
integrated for perception tasks such as semantic segmentation, object detection, and instance segmentation. In the decision-making component, numerous
automated driving algorithms are employed for surrounding environmental sensing, motion planning, and vehicle control.

interpretation. Since each dimension corresponds to a distinct aspect of the perception chain, the proposed framework
ensures both comprehensive coverage and conceptual separation. For cases spanning multiple levels, classification is
assigned based on the dominant factor in terms of safety
impact. This framework also forms the basis for the CC
detection methods introduced in Section III, where the analysis
is organized according to the formalization of each level.
In the following, we detail the conceptual and mathematical
formulations of each dimension and further demonstrate the
completeness of the proposed framework.
A. Definition 1: Data-Level Corner Case
Data-level corner cases (CCs) in autonomous driving systems target input-layer anomalies, specifically defined by
statistical deviations in raw sensor data that violate preestablished normal measurement ranges—these deviations
directly induce inference failures in deployed machine learning
models. Notably, such anomalies arise independently of model
processing logic or scene semantics; their root causes instead
lie in sensor hardware defects or environmental interference.
For instance, a camera capturing an image with 90% of pixels
saturated to the maximum intensity value due to overexposure,
or a LiDAR unit generating point cloud data exceeding its
rated maximum effective detection range, both qualify as datalevel CCs. In such scenarios, the machine learning model
fails to process the input data accurately, primarily due to the
novelty and anomalous nature of the sensor measurements.
Mathematically, let the input raw sensor data be denoted as
X ∈ Rn , where the dimension n is determined by the sensor
type: for example, n = H ∗ W ∗ 3 for RGB images (with H
and W representing the image height and width, respectively),
and n = N ∗ 3 for LiDAR point clouds (with N denoting the
number of points in the point cloud). The detection of datalevel CCs is formulated as a binary classification task, with the

objective of determining whether a given input sample constitutes a data-level CC. Formally, we aim to learn a mapping
function y = f (x), where the output label y ∈ Y = {0, 1}—here,
y = 1 indicates that the input x is a data-level CC, while
y = 0 indicates normal sensor data. A critical criterion for this
classification is: y = 1 if and only if the statistical features of
x deviate from a pre-defined normal data distribution Pnormal .
This deviation is quantified using a statistical distance metric,
expressed as D (x, Pnormal ) > τ, where D(·) denotes a statistical distance metric (e.g., Euclidean distance for evaluating
pixel intensity deviations, Mahalanobis distance for measuring
LiDAR point coordinate anomalies relative to Pnormal ), and τ
represents a pre-determined deviation threshold. For practical
clarity, consider 8-bit grayscale images: Pnormal encompasses
pixel intensities within the valid range [0,255]; if x contains
any pixels with intensity values outside this range (i.e.,> 255
or < 0), the distance D (x, Pnormal ) will exceed τ, leading to
the classification result y = 1.
This definition aligns with the sensor-driven CC categorization proposed in [29], which explicitly confirms that
input-layer data anomalies are independent of model-specific
behaviors and high-level scene semantics—thus solidifying the
role of data-level CCs as the foundational layer of our tri-level
CC definition framework.
B. Definition 2: Model-Level Corner Case
Model-level corner cases (CCs) capture failures at the
processing stage of autonomous driving perception models.
They refer to scenarios in which the input data remain statistically normal, i.e., free of data-level anomalies, yet the
model nonetheless fails to generate accurate outputs due to
deficiencies in its internal representations or decision-making
mechanisms. This definition characterizes model robustness
along three key dimensions: sensitivity to perturbation, consistency across domains, and completeness of topological
representation. In contrast to data-level CCs, such failures

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
4

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

and Ptest denote training/test distributions; if the Wasserstein
distance (a standard distributional divergence metric) between
Ptrain and Ptest exceeds threshold γ (i.e., Wasserstein distance
(Ptrain , Ptest ) > γ), any xtest ∈ Ptest is a model-level CC
[30]. Topological defects-related CCs, by contrast, stem from
insufficient model neuron activation during inference: let D =
all neuron units, g(x, D) = neuron coverage (activated neurons/
|D|, with “activation” = output > 0.1); if g(x, D) < δ(δ =
minimum coverage threshold from normal dataset validation),
x is a model-level CC.
Collectively, a model-level CC is formally defined by two
conditions: (1) the model’s output deviates from ground truth
( f (x) , y∗ , where y∗ ∈ Y is the true label for x), and (2) the
input has no data-level anomalies (∃
 data-level anomaly in x.
This dual-condition framework ensures model-level CCs are
orthogonal to both data-level and semantic-level CCs in our
tri-level system.
C. Definition 3: Semantic-Level Corner Case

Fig. 2. Overall organization of this paper, including the refined definition
of perception-stage corner cases, methods for their detection and generation,
evaluation metrics, public datasets, simulation platforms, current limitations,
and future research challenges.

cannot be attributed to degraded sensor quality or highlevel semantic complexity. Instead, they arise from intrinsic
limitations of the model itself, primarily including vulnerability to adversarial perturbations, inadequate generalization
under domain shift, and defects in topological structure. The
validity of this formulation is further supported by the domain
generalization theory established in [30].
Concretely, adversarial perturbations denote small, humanimperceptible modifications to the input that can mislead
the model while leaving the underlying semantic content
unchanged. For example, a visually normal stop sign with a
small adversarial sticker may be incorrectly recognized as a
speed limit sign. Mathematically, let f : X →
− Y denote the
target perceptual model, x ∈ X represent normal input data, and
δ denote a perturbation vector with kδk p < ( = perceptibility
threshold ensuring δ is human-undetectable); an adversarial
example qualifies as a model-level CC if f (x + δ) , f (x).
Domain shift-induced CCs occur when test data distribution
deviates significantly from training data—for example, a clearweather-trained semantic segmentation model failing at object
boundary detection in fog or heavy snow. Formally, let Ptrain

Semantic-level corner cases (CCs) refer to failures in scene
understanding of autonomous driving systems. They describe
scenarios in which the input is statistically normal, with no
data-level anomaly, and the model processes the data correctly,
with no model-level failure, yet the resulting semantic interpretation of the scene conflicts with driving common sense or
prior knowledge. Unlike lower-level CCs, these cases directly
affect safety-critical decisions such as trajectory planning and
emergency braking and therefore represent the highest level of
safety risk, consistent with the observation in [26]. In general,
they arise in two forms: out-of-distribution (OOD) objects and
OOD spatial relations, both of which violate the expected
semantic structure of typical driving scenes.
Concretely, OOD objects are novel or otherwise unusual
objects not seen during model training, such as a pet dog
suddenly appearing in front of the ego vehicle, an overturned
truck blocking a lane, a pedestrian dressed as a doll in
the road, or a deer straying onto a highway. OOD spatial
relations, by contrast, involve illogical positional relationships
between objects that contradict common sense or prior driving
knowledge—examples include a chair falling from a moving
truck, a phantom pedestrian (e.g., a misdetected or unrealistic
pedestrian) “passing through” the middle of the ego vehicle, or
a pedestrian walking outside sidewalks and directly crossing
the vehicle’s trajectory. These scenarios pose inherent safety
risks because they disrupt the model’s expected understanding
of reasonable scene dynamics.
Mathematically, let the scene semantic representation generated by the perceptual model be S (x) = {O, R}, where
O = {o1 , o2 , . . . , ok } denotes the set of detected objects in the
scene, and R = {r(oi , o j )|1 ≤ i, j ≤ k} denotes the set of spatial
relations between objects (e.g., “in front of the ego vehicle”,
“crossing the trajectory of”). A semantic-level CC is formally
defined by two conditions:(S (x) < Scommon ) and there is no
data/model-level anomaly in x. Here, Scommon represents the set
of semantically reasonable driving scenes (e.g., “pedestrians
on sidewalks”, “cars traveling in lanes”, “traffic signs above
intersections”). For its two specific forms: 1) OOD objects:
There exists at least one object o ∈ O such that o < Otrain ,

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIANG et al.: CORNER CASE DETECTION AND GENERATION FOR AUTONOMOUS DRIVING: AN OVERVIEW

where Otrain is the set of all objects the model encountered
during training; 2) OOD relations: There exists at least one
spatial relation r(oi , o j ) ∈ R such that r(oi , o j ) < Rcommon , where
Rcommon is the set of logically reasonable spatial relations in
driving scenarios. This definition aligns with [26]’s emphasis
on semantic-level CCs as the top of the CC hierarchy—their
direct link to collision avoidance and driving safety makes
them the most critical category in our tri-level framework.
D. Handling Multi-level Corner Cases
In practical autonomous driving environments, corner cases
often manifest with hierarchical overlaps, where a single scenario may concurrently exhibit multiple levels of anomalies.
For example, an overexposed sensor capture constitutes a datalevel anomaly, while an unexpected pedestrian crossing event
occurring in the same scene reflects a semantic-level deviation.
To systematically address such compound anomalies, we formalize a prioritization framework informed by the scene safety
axioms established in [26]. This hierarchical resolution model
adheres to a strict precedence order: semantic-level > modellevel > data-level, which is derived from the direct impact on
operational safety. Semantic-level corner cases pose immediate
existential risks to vehicular autonomy, as they disrupt critical
path-planning algorithms by introducing contradictory scene
interpretations. Model-level anomalies, while less immediately
hazardous, undermine system integrity by causing algorithmic
failures that lead to misclassification or missed detections.
Data-level irregularities, by contrast, represent lower-order disturbances that can be mitigated via preprocessing techniques,
such as noise filtering or sensor calibration.
We define categorical decision rules consistent with the
following schema: any scenario that exhibits semanticlevel discrepancies—regardless of data quality or model
performance—is labeled a semantic-level corner case, for
example, an overexposed image in which a cyclist unexpectedly appears. If no semantic anomaly is present but
the model demonstrably fails on valid input data, the case
is classified as model-level, such as misidentifying a traffic
cone as a road marker in a clear camera feed. Finally,
scenarios that manifest only data-level variations, without
degrading model behavior or semantic correctness, are designated as data-level corner cases, such as an overexposed
image of an otherwise unobstructed highway. This tri-level
(data–model–semantic) framework exhaustively characterizes
all CCs in autonomous driving perception systems. Data-level
CCs address raw sensor irregularities, consistent with the
taxonomy of [29]; model-level CCs capture model failures
such as adversarial perturbations, supported by the theory
in [30]; and semantic-level CCs encode scene-level safety
conflicts, in line with the framework of [26]. Because all CCs
arise from these three system components, no additional levels
are required. For example, a LiDAR malfunction that triggers
both misdetection and misplanning is still a data-level CC,
underscoring the framework’s completeness.
III. C ORNER C ASE D ETECTION
We characterize existing solutions for corner-case detection
at the data, model, and semantic levels, respectively.

5

A. Detecting Data-level Corner Cases
In general, existing solutions for detecting data-level corner
cases can be categorized into the following two groups.
1) Statistical Learning Solutions: A plethora of studies
have applied statistical learning algorithms to recognize corner
cases at the data level. For example, Liu et al. [37] extracted
multidimensional features (e.g., weather, time, location, speed,
and surrounding vehicles) from videos recorded by the frontfacing camera and applied a random forest algorithm to
classify the complexity of driving scenes in a hierarchical
manner. Ryan et al. [38] used Gaussian process regression
to quantify the uncertainty (confidence interval) of the model
prediction. Measurement of risky scenarios in autonomous
driving can also be achieved by comparing autonomous and
safe driving behaviors [38]. Due to the heavy-tailed distribution of corner cases, the aforementioned solutions exhibit
biased performance. To address this problem, a one-class
support vector machine (OCSVM) is employed to detect
corner cases. The main idea of OCSVM is to map the data
into a high-dimensional feature space induced by a kernel
function, construct a hyperplane that separates the data from
the origin, and maximize the margin between the hyperplane
and the origin. This yields a binary function that determines
whether a new data point is similar to the training data. The
optimization objective function of OCSVM is shown in Eq. 1,
where w is the normal vector of the hyperplane, ρ is the
distance from the hyperplane to the origin, ζi is the slack
variable, and ν ∈ (0, 1) controls the proportion of outliers and
the proportion of support vectors. φ(xi ) is the kernel function.
n

1 X
1
ζi − ρ
min ||w||2 +
w,ζi ,ρ 2
νn
i=1

s.t. (wT φ(xi )) ≥ ρ − ζi , i = 1, . . . , n
ζi ≥ 0

(1)

Unlike in classification tasks, corner cases are often treated
as anomalies. Therefore, clustering algorithms are widely used
to detect data-level corner cases, offering a more intuitive
approach: they group samples into homogeneous categories
and flag outliers that deviate from the cluster centers. Given
the input samples {x1 , x2 , . . ., xm }, where x ∈ Rn , randomly
select the centroid of each category as µ1 , µ2 , . . ., µk ∈ Rn . For
each sample xi , it should belong to c = argminkxi − µi k2 .
As the sample size increases, the centers of the sample
categories tend to remain stable. For example, Lee et al. [39]
estimated the cluster centers and covariances of each class and
used the Mahalanobis distance to detect OOD samples, while
Deng et al. [40] used relative feature displacement to describe
the sample as the feature centroids and displacement.
Leino et al. [41] introduced the concept of global robustness
of the classification model, and the classifier keeps samples of
different categories in a certain width interval in the feature
space to ensure the difference between categories. This method
leverages the Lipschitz condition to measure neural network
robustness. However, such methods perform reliably only on
samples with minor perturbations and fail to generalize to data
from open environments. Furthermore, samples far from the

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
6

centers of their class labels’ clusters tend to be misclassified
[38], [39], [42].
2) Deep Learning Methods: Over the past two decades,
deep neural networks have made substantial progress in
autonomous driving. For corner case detection, domain adaptation methods are useful for assessing the normality of samples
that remain semantically similar to the source domain but
differ in distribution. Such domain shifts arise from changes in
statistical properties across training, validation, and test data
and are commonly grouped into three types: distribution shift,
covariate shift, and label shift. “Distribution shift” refers to
differences in overall data distributions, “covariate shift” to
changes in input features, and “label shift” to changes in label
distributions across domains.
However, most existing solutions primarily focus on mapping from a single source domain to a single target domain,
resulting in poor generalization. To enhance robustness across
multiple source and target domains, a novel Open-Scenario
Domain Adaptive Object Detection (OSDA) [43] has been
proposed. It utilizes a contrastive vision-language pretraining strategy to distinguish foreground from background and
introduces a cross-reconstruction framework across multiple domains to learn domain invariances. Kim et al. [44]
extended the domain adaptation theory to LiDAR sensors
to enhance performance. They introduced sparsity-invariant
feature consistency and semantic correlation consistency to
learn generalizable LiDAR representations across the source
domain and unseen domains. Moreover, real-world datasets
often exhibit class imbalance with a long-tailed distribution.
To detect corner cases from unbalanced datasets, Liu et al. [45]
proposed OLTR to associate head categories with tail categories by mapping images in space. To address the limitations
of the aforementioned methods in handling large-scale, highresolution image data, Hendrycks et al. [46] introduced the
Maxlogit detector to improve performance on multi-label
datasets in complex scenes and on anomaly segmentation tasks
in driving environments.
Most existing corner-case detection techniques at the data
level require the incorporation of additional corner-case
datasets to regularize the decision boundaries of the model.
Because these auxiliary datasets typically follow a probability
distribution that differs from that of the primary training data,
the resulting classification boundaries are often insufficiently
strict or poorly calibrated. Moreover, the applicability of such
methods is generally restricted to relatively simple scenarios,
and they do not directly generalize to complex, real-world
environments.
B. Detecting Model-Level Corner Cases
To detect model-level corner cases, numerous studies investigated the effects of the input on topological patterns and
model behavior.
1) Solutions Based on Software Testing: In software development, rigorous testing is paramount for ensuring robustness.
This principle has been applied to evaluate the robustness
of deep neural networks. Inspired by the concept of code
coverage (i.e., the ratio of code statements executed by a test
case to all statements), DeepXplore [47] introduced neuron

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

coverage to measure the proportion of activated neurons by
test input. This approach leverages multiple DL models as
cross-referencing oracles to identify test inputs that trigger
differential behavior and achieve high neuron coverage. Following this paradigm, DeepTest [48], an automated testing
framework for autonomous cars driven by DNNs, uses generated test samples across diverse weather conditions to identify
extreme behaviors produced by DNNs in extreme scenarios by
maximizing neuron coverage. On the contrary, Wu et al. [49]
posited that a meaningful corner case detector should be sceneagnostic, inferring that the corner case should be beyond the
effective input domain range of the DNN model. Based on
this premise, Deep Validation was proposed to evaluate test
samples that could cause system errors by examining whether
the model’s intermediate states exceed predefined thresholds.
However, these solutions are computationally intensive. To
mitigate this problem, DeepEvolution [50] proposed a searchbased solution that significantly enhances the diversity and
neuron coverage of generated test cases.
2) Solutions Based on Network Similarity: Compared with
neuron coverage, we can extract sample representations from
the model’s middle layer in a more fine-grained manner to
explore corner cases. Dauphin et al. [51] observed that training
the same neural network with different random initializations
might yield similar performance. Given an in-distribution
dataset Dbase and a corner case dataset Dcc , for a neural
network f (·), fi (·) represents the i-th layer of the neural
network. If S imilarity( fi (x), fi (y)) < ε, the input sample is
taken as a corner case, where x ∈ Dbase , y ∈ Dcc , and
Dbase ∩ Dcc = ∅.
To quantify the similarity of latent representations in neural
networks, Wang et al. [52] characterized the structure of
matches between neuron activation subspaces. Furthermore,
canonical correlation analysis (CCA) [53] is used to quantify
the association among multiple high-dimensional variables.
Raghu et al. [54] proposed the SVCCA, combining singular
value decomposition and CCA, to efficiently compare invariant
neural representations and affine transformations. To extend
this solution to high-dimensional neural representations, centered kernel alignment (CKA) [55] was proposed to measure
the similarity between neural representations derived from
different initialization weights.
Inspired by CKA, [56], [57] measured the functional similarity of different models through model stitching. These
works primarily examine whether the network can replace the
representations of other networks via an affine transformation
while preserving functional integrity.
Similar to neuron coverage, Ouyang et al. [58] proposed
surprise sufficiency to formally quantify how deep learning
(DL) systems respond to given inputs. Intuitively, the more
surprising an input is to the test DNN, the more likely the
system is to behave unexpectedly. First, the activation trace is
defined as the pattern of neuron activations triggered by data in
the DL system. For a neuron N in the DL system, the activation
trace aN (x) of a given test input x with respect to N is defined
as in Eq. 2, where αi (x) denotes the activation value of x for
an individual neuron ni . Accordingly, the surprise adequacy
(SA) for testing a DL system can be formulated based on the

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIANG et al.: CORNER CASE DETECTION AND GENERATION FOR AUTONOMOUS DRIVING: AN OVERVIEW

7

Fig. 3. Understanding corner case from data level, model level and semantic level, respectively: (a) For the data-level CCs, they can be formulated as a
binary classification problem; (b) for the model-level CCs, they aim to investigate the model robustness by quantifying the network behaviors under the given
samples; and (c) for semantic-level CCs, they focus on unseen objects or scenarios where the spatial relation of objects is rare.

similarity of activation traces between samples.
αN (x) = [α1 (x), α2 (x), . . . , αN (x)]

T

(2)

In practical scenarios, there exist outlier instances in which
the test and training data are highly similar but differ in their
labels. In response to this phenomenon, Ouyang et al. [59]
proposed DSA to measure the discrepancy between a single
sample and the local descriptor of its class according to Eq. 3,
where αN denotes the activation value (Eq. 2); xa represents the
nearest neighbor in class x ; and then, taking xa as the reference
point and finding its nearest neighbor xb in a class different
from class xa .
kαN (x) − αN (xa )k
DS A(x) =
(3)
kαN (xa ) − αN (xb )k
Model-level corner-case detection offers a distinct way to
quantify corner cases. Inspired by software testing methodologies, these approaches analyze variations in samples at
intermediate network layers using neuron coverage to assess
whether a given input elicits abnormal neuron behavior. Unlike
other post-processing algorithms, model-level methods are
inherently grounded in the model’s internal representations,
enabling the development of novel strategies for measuring
corner cases. However, these methods have poor interpretability, and are difficult to be applied to large-scale datasets
directly.
C. Detecting Semantic-level Corner Cases
Unlike the data-level and model-level ones, CCs at the
semantic level focus on detecting unseen objects and understanding the abnormal spatial relations of objects. To detect

semantic-level CCs, as shown in Fig. 4, four types of methodologies are studied.
1) Uncertainty-Aware Solutions: For uncertainty-aware
solutions, they first employ an object detection or segmentation
network g(·) to obtain the set of objects {ob j1 , ob j2 , . . ., ob jn }
or region proposals in the scene. Then, the confidence score
for each object or proposal is quantified using an uncertainty estimator. Finally, objects with higher uncertainty are
recognized as corner cases. As shown in Fig. 4, numerous
studies followed this paradigm to produce confidence scores or
uncertainty scores for objects, regions, or instances [60], [61],
[62]. This method is simple and effective, without modifying
the structure of the classification model or training an OOD
sample classifier.
Similar to the confidence score, numerous studies [63],
[64], [65] have detected abnormal regions in images by outputting their uncertainty. DUQ [63] used a deterministic deep
neural network for uncertainty estimation, using a trainable
kernel function to reject data points outside the distribution.
Kendall et al. [64] used Monte Carlo sampling and Bayesian
inference to estimate the uncertainty of each pixel. However,
none of them can guarantee real-time uncertainty prediction.
Huang et al. [65] attempted to use video sequences as input
and leverage temporal information to aggregate and disperse
the uncertainty of each pixel. In general, video sequences
contain more semantic information and are more consistent
with data from autonomous vehicle sensors. Joseph et al.
[66] performed contrastive clustering on features generated by
the residual module in the ROI head, and used energy-based

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
8

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

Fig. 4. An overview of detecting semantic-level corner cases. For corner-case detection at the semantic level, we divide it into four types in the figure:
Uncertainty-Aware Methods, Data Distribution Methods, Prediction-Difference-based Methods, and Reconstruction-Based Methods. We summarize four
methods that prior research collectively regard as the paradigm.

models to learn experience categories and identify possible
location types in the test set.
To encapsulate such methodologies, uncertainty and confidence measures are typically implemented as post-processing.
This can include either outputting the softmax posterior probability or computing the distance between the sample and
the prototype. In essence, most methods are evaluated by
comparing the score to a fixed threshold to determine whether
the sample is a corner case. Unlike data-level detection methods, this type of method generally does not require additional
auxiliary data. Instead, it conducts supervised training directly
through standard training samples.
2) Solutions Based on Prediction Difference: Predictionbased methods typically utilize video sequences as input to
the model, which can be formulated as dt+1 = st+1 − f (st ),
where dt+1 is the prediction error, st+1 is the ground truth,
st is the input scene and f (·) is a complex-valued function
that predicts the next scene. A salient characteristic of corner
cases is that they are difficult for general detection models to
recognize and process correctly. By comparing the difference
between the predicted scene s0t+1 and the ground truth st+1 ,
the detection of the corner case object in the scene is achieved.
Therefore, unlike the aforementioned methods based on confidence scores, the difference between the prediction result and
the ground truth is used to locate the object in the corner
case [26], [28], [67]. As illustrated in Figure 4, the method
predicated on the prediction difference diverges from other
methods that use a single-frame image as input. It requires
a video sequence as ground truth to determine whether the
model has accurately discerned the object’s intention in the
scene at the subsequent moment.
Bolte et al. [26] designed an image prediction module that
computes the prediction error for each input frame, performs
semantic segmentation on the input frames to identify and
locate objects in the scene, and devises a detection system
that fuses the information from image prediction and semantic
segmentation. This framework verified whether the predictable
objects/classes/instances are in the expected locations and output a binarized score of the corner-case probability. Compared
to the method proposed in [26], Liu et al. [67] use GAN to

assist in the prediction of new frames. Through adversarial
training of GAN, to ensure the accuracy and authenticity of
the prediction, and then improve the performance of frame
prediction. In [28], multiple modalities, including point clouds
and images, were utilized to bolster corner case detection
robustness. In autonomous driving scenarios, the vehicle’s
sensors are typically multimodal, including cameras, radars,
and lidars. In addition to using single-modal camera data for
corner case detection, Bogdoll et al. [68] proposed a method
to detect anomaly data based on multimodal data.
3) Reconstructed-Based Solutions: The underlying assumption of reconstruction-based solutions is that normal scenes
tend to have smaller reconstruction errors than corner cases.
By comparing the reconstructed image with the original image,
the corner case can be identified and localized. As shown in
Fig. 4, it first feeds the raw image into a neural network to
learn the intermediate representations. Then, a reconstruction
task is introduced to generate images based on the intermediate
representations. If the discrepancy between the reconstructed
output and the original input exceeds a certain threshold, the
object can be classified as a corner case.
In general, autoencoders are widely used for a range of
reconstruction tasks [69], [70]. For example, Hasan et al. [69]
used autoencoders to capture the distributions of normal
motion patterns from video sequences and detect abnormal
behaviors based on reconstruction errors. Xia et al. [71] introduced a discriminative autoencoder that can identify abnormal
images by incorporating discriminative information during
training. However, these methods are not feasible for corner
cases that are rare or unseen. For the unseen samples, [70]
developed a category-conditioned autoencoder that first trains
an encoder on a closed set of categories and then trains
a decoder conditioned on the category labels to reconstruct
the input. The reconstruction error is then used to determine
whether the input belongs to a known or unknown category.
On the other hand, semantic and instance segmentation
models are also widely used for reconstructive tasks. For
semantic segmentation, the goal is to assign each pixel in
an image to a class or object label. Accordingly, numerous
studies use the output of a semantic segmentation network

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIANG et al.: CORNER CASE DETECTION AND GENERATION FOR AUTONOMOUS DRIVING: AN OVERVIEW

as an intermediate representation to reconstruct images and
explore corner-case objects in autonomous driving scenes
[72], [73], [74]. For example, Yan et al. [75] used a pretrained image segmentation model to produce a segmentation
map, and then used the segmentation masks as input to a
conditional GAN for image generation. They then used the
dissimilarity network to detect differences between the two
images and localize uncertain objects in the scene. To enhance
robustness, Di Biase et al. [73] combined multiple information
sources, including semantic maps, softMax entropy, softMax
distance, regenerated images, and perceptual differences, into
a difference network to recognize abnormal objects in images.
In addition, depth information can play an auxiliary role in
corner-case detection. Furthermore, Lis et al. [76] detected
and identified road obstacles by erasing instance objects. The
model first uses a general method for filling, relying on
adversarial methods to ensure that the erased instances in
the filled image are partially realistic. Secondly, a separate
network is trained to compare the two images and detect
abnormal road objects. In essence, the reconstruction method
is based on learning intermediate representations of images
and on the reconstruction discrepancy. This leads to an overreliance on feature extraction, semantic segmentation, and
related techniques. This will directly influence the subsequent
reconstruction effect, thereby affecting our judgment of cornercase objects.
4) Solutions Based on Data Distributions: Corner cases
(CCs) typically follow distributions in latent representation
space that differ from those of normal samples. Building on
this observation, data distribution-based methods map input
images into a shared latent space via learnable functions,
where distributional discrepancies are measured using kernel functions or random feature mappings, typically using
maximum divergence criteria. In this framework, deep neural networks first extract features from the input, which
are then either processed further by downstream methods
or used directly for classification. Unlike uncertainty-based
approaches, this class of methods either directly identifies
sample types or performs post hoc classification based on
the extracted latent features. For example, two additional
constraints are enforced in DaCUP [77] for representation
learning: not belonging to a modelable category and not being
visually similar to non-anomalous objects in the image. Based
on these assumptions, the authors propose a novel embedding bottleneck to effectively capture the visual variations
in unknown, multimodal scenes. Reference [78] integrated
both greedy search and confidence intervals to determine the
boundaries of abnormal regions in multivariate spatio-temporal
time series. Reference [79] presented a CROSR open-set
classification framework, which consists of two components:
a closed-set classifier and an unknown detector. The closedset classifier uses common supervised learning methods to
learn label representations. The unknown detector uses the
reconstructed potential representations and labeled data for
training.
Semantic-level corner-case detection allows us to pinpoint
specific objects or instances within an image, thereby improving both interpretability and practical utility. By operating at

9

this finer granularity, we can focus on specific regions or
objects exhibiting unusual behavior, rather than treating the
entire image as an outlier. Addressing corner cases at the
semantic level can therefore enhance the robustness and safety
of ADS. However, in contrast to image-level classification,
which considers the entire scene as a single entity, semantic
detection works at the object level, substantially increasing
task complexity and demanding more sophisticated models
and stronger regularization. Moreover, current datasets primarily focus on common objects and scenes, leading to degraded
performance in corner cases.
IV. G ENERATION OF C ORNER C ASES FOR S AFETY
T ESTING
Autonomous driving systems (ADSs) rely extensively on
large-scale, real-world driving datasets for perception, prediction, planning, and validation. However, exclusive dependence
on such datasets is both economically prohibitive and
intrinsically limited. First, the collection and annotation of
autonomous driving data are time-consuming, labor-intensive,
and costly [80], [81]. Second, the inherently dynamic nature
of environmental and traffic conditions makes exhaustive coverage of all possible scenarios infeasible, which in turn leads
to degraded model performance under distributional shifts and
weak generalization to previously unseen situations [13], [82].
Third, real-world data predominantly reflect routine operating conditions rather than rare or challenging corner cases,
making such data inefficient for safety-critical stress testing.
Consequently, corner-case generation should be regarded not
merely as a data synthesis task, but as a systematic mechanism
for enhancing model adaptiveness and robustness in long-tail
and safety-critical scenarios. Existing studies provide preliminary empirical support for this perspective. For instance,
Bewley et al. [83] demonstrated that a self-driving vehicle
trained exclusively on simulated data could operate on real
roads, indicating that synthetic data can effectively support
downstream driving performance. More broadly, synthetic data
has been shown to accelerate the development of generalizable
learning-based algorithms [84]. Therefore, the generation of
corner cases is pivotal for the safety testing of ADSs. In this
section, we review corner-case generation methods from three
perspectives: data transformation-based, knowledge-based, and
scene-based (Fig. 5).
A. Data Transformation-Based Corner Case Generation
Image transformation-based corner case (CC) generation
typically applies targeted augmentation operators to derive new
samples from existing datasets. This approach leverages specialized image processing techniques, including sharpening,
rotation, scaling, and noise injection, to generate scenariospecific samples that mimic adverse conditions such as rain,
fog, and low light, which are common sources of corner cases
in autonomous driving [8], [48]. For example, DeepTest [48]
applied affine transformations to original scenes to evaluate
ADS robustness under variable weather conditions. DeepXplore [47] generated transformed inputs to maximize neuron
coverage, while DeepRoad [85] adopted a metamorphic testing

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
10

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

Fig. 5. An overview of corner case generation methods. For data-augmentation-based tasks, transformation operations encompass both linear and affine
transformations. Knowledge-based methods can be categorized into three types: text, scene graphs, and layouts. Scene-based generation methods can be
categorized into physical models, style transfer, and event-based approaches.

framework to expand test coverage through transformation
functions that produced new samples with different characteristics.
A principal advantage of these methods lies in their capacity to enhance the robustness of ADS to nuisance factors
and domain shifts encountered in adverse environments. By
introducing controlled perturbations while preserving the core
scene semantics, they mitigate dependence on spurious correlations typically learned under standard conditions and
improve robustness to variations in weather, illumination,
and visual appearance. This property is particularly beneficial
in scenarios where real-world corner-case data are scarce.
Nonetheless, these approaches primarily address appearancelevel corner cases, and the generated samples often inherit
biases from the original dataset. Furthermore, the perturbations
applied are generally restricted to relatively simple or limited
scenarios.
B. Knowledge-Based Corner Case Generation
To address the limitation of transformation-based
methods—their inability to capture the semantic complexity of
real traffic scenes—knowledge-based corner case generation
incorporates external knowledge (e.g., text descriptions,
scene graphs, layouts) to guide image synthesis with richer
structural and semantic constraints. By integrating metadata
such as object orientation, size, color, and spatial relations,
these methods enable the construction of rare scenarios that
are not readily obtainable from routine driving logs.
1) Text-Guided Generation: As a natural and flexible form
of scene description, text provides an intuitive source of
semantic guidance for image generation. Reed et al. [86]
proposed the classic model to generate images based on
descriptive text input, and StackGAN [87] was applied to
improve the image resolution from 64 × 64 to 256 × 256.
Since then, numerous GAN-based text-to-image generation
models have been proposed [88], [89], [90]. In addition, the
attention mechanism was integrated into the GANs to align
the same objects in text sequence and visual semantics [91],
[92]. Quan et al. [93] combined the attention regularization
module and the region proposal network (RPN) to efficiently
locate keywords. With the popularity of Transformer [94],
autoregressive syntactic models employ Transformer-based
sequence-to-sequence architectures to learn the relationship
between linguistic input and visual output. Autoregressive
models were usually combined with variational autoencoders

(VAEs) [95] and CLIP [96]. For example, Ramesh et al. [97]
trained VAE to acquire image tokens. The text and image
tokens were concatenated and then fed into the Transformer.
Similarly, CogView [98] and UMT (Unifying Multimodal
Transformer) [99] conducted large-scale joint generative pretraining on text and image tokens obtained from VQ-VAE.
Recently, denoising diffusion models have gained increasing
attention and have demonstrated outstanding performance in
image generation [100], [101]. It is a parameterized Markov
chain that transforms Gaussian noise into samples. The model
is meticulously trained through variational inference, enabling
it to generate samples that match the data distribution. The
mathematical representation of the forward process (diffusion
process) is shown in Eq. 4, where xt and xt−1 √
are random
variables, N represents the normal distribution, 1 − βt xt−1
is the mean, βt I is the covariance matrix, and I is the identity
matrix. The input to the forward process is the original image,
which follows a specific distribution, and the output is a noisy
image that follows a Gaussian distribution.

 p
q(xt | xt−1 ) = N xt ; 1 − βt xt−1 , βt I
q(x1:T | x0 ) : =

T
Y

q(xt | xt−1 )

(4)

t=1

The mathematical representation of the backward process
(reverse process) is shown in Eq. 5, where pθ (x0:T ) represents the probability density function of the random variable
sequence from xQ
0 to xT ; pθ (x0:T ) is the probability density
function of xT ; Tt=1 represents the product of t from 1 to
T . pθ (xt−1 | xt ) is the conditional probability density function
between xt−1 and xt under given conditions. With a parameter
θ, µθ (xt , t) is the mean function, and Σθ (xt , t) is the covariance
matrix function.
pθ (x0:T ) = p(xT )

T
Y

pθ (xt−1 | xt )

t=1

pθ (xt−1 | xt ) = N (xt−1 ; µθ (xt , t), Σθ (xt , t))

(5)

To reduce training costs and substantial computational load,
Rombach et al. [102] introduced the latent diffusion model,
which demonstrated robustness in generating high-resolution
images, including some corner cases.
Text-guided generation’s key advantage is explicit specification of rare semantic scenarios absent from the original dataset:
researchers can directly describe such cases in language and

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIANG et al.: CORNER CASE DETECTION AND GENERATION FOR AUTONOMOUS DRIVING: AN OVERVIEW

11

Fig. 6. Overview of Sg2im. The input scene graph specifies objects and their
relationships, which are then processed using a graph convolutional network.
After computing embedding vectors for all objects, they are used to predict
bounding boxes and segmentation masks, then combined to form a scene
layout. The layout is converted to an image using a cascaded refinement
network (CRN).

Fig. 7. Image generation from layout. Given the coarse layout (bounding
boxes and object categories), the Layout2Im model simplifies the process
by sampling each object’s appearance from a normal distribution. They are
then transformed into a real image by a series of components. This figure is
inspired by [110].

synthesize corresponding scenes, rather than waiting for them
to emerge naturally in real-world data. This makes it ideal for
constructing long-tail scenarios, offering semantic controllability at low data-collection cost.
2) Scene Graph-Guided Generation: Scene graph (SG) is
a widely used data structure in computer vision for scene
understanding. In a scene graph, nodes correspond to objects
or entities, while edges represent their relationships or interactions [103]. Mathematically, given a set of objects Co and
a set of relations E, a scene graph is a tuple (O, E), where
E ⊆ O × R × O is a set of directed edges of the form
(oi , r, o j ) and oi , o j ∈ Co , r ∈ E. Therefore, precise control
over the semantic position of traffic elements plays a vital
role in corner case generation. Sg2im [104] was the first
to use graph convolution for SG processing, learning layout
information by predicting the bounding boxes and segmentation masks of objects (Fig. 6), which the cascade refinement
network then converts into images. Following this paradigm,
Mittal et al. [105] subsequently proposed a sequential
incremental approach. In contrast, Ashual and Wolf [106]
distinguished objects by adding attributes such as types and
appearance embeddings, employing dual encoding for each
object. Attention mechanisms [107] and external knowledge
bases [108] have been further employed to enhance the
model’s understanding of objects. Scene graphs are useful data structures for describing traffic scenes. To bridge
the gap between real-world traffic images and generated
images, Savkin et al. [109] proposed a method based on
domain-invariant scene representation to directly generate traffic imagery. The model extracted the SG from the virtual
environment and then generated traffic scenes in the real
environment. Compared with previous methods that relied on
manually crafted SG representations, the images produced by
this method appeared more realistic and compliant.
SG-guided generation is particularly effective for explicitly
encoding inter-object relationships and atypical interactions,
which constitute the core of most safety-critical driving scenarios. In contrast to appearance-level augmentation, SG-based
approaches enable the systematic construction of corner cases
characterized by abnormal object configurations, complex
agent interactions, and traffic-rule–related semantic violations.
Consequently, these methods increase both visual variability and semantic representativeness, which are crucial for
rigorously assessing and improving model performance in
interaction-intensive driving environments.

3) Layout-Guided Generation: Layout has historically
functioned as an intermediate representation for processing
textual and other multimodal inputs. In particular, its capacity
to encode object locations—an aspect that is crucial in traffic
scenes—has motivated researchers to employ layout information directly as an input modality to constrain the spatial distribution of scene objects. Consequently, layout-guided image
generation methods leverage explicit positional information
of scene elements to condition and structure the synthesis
process. In general, layout representations are commonly
instantiated as “bounding box + category,” semantic layout
maps, and related variants. For example, Zhao et al. [110]
proposed a classic layout-to-image model, as shown in Fig. 7,
where the input consisted of bounding boxes and object
categories. It constructed feature maps for individual objects
and applied a convolutional LSTM to generate a hidden
feature map. Subsequently, it decoded the entire map into
a set of output images. LostGan [111] focused on reconfigurable layout and style, and also learned about object
instance-specific layout-aware feature normalization (ISLA) in
generators. ISLA was extended to Attr-ISLA with additional
control over the attributes in [112]. Furthermore, [113], [114],
[115], [116] optimized the architecture to produce images with
more robust object appearance in complex layouts. Zheng et al.
[117] utilized structural image patches with region information
and a diffusion model to design an end-to-end controllable
model.
In addition to bounding boxes, the semantic layout offers
a flexible description. Park et al. [118] introduced spatially
adaptive normalization, which uses the layout to modulate
activations in normalization layers. Following this paradigm,
Zhu et al. [119] further conditioned on segmentation masks
that described semantic regions in the output images. Additionally, [120], [121] used semantic operations to modify
local objects in images. The generated traffic scenarios could
produce more reasonable and distinctive results for finegrained objects. Using a multiscale guided diffusion model,
Zeng et al. [122] leveraged a precision-encoded mask pyramid
and combined text features by accuracy level.
Layout-guided generation is well-suited to synthesizing rare,
safety-critical spatial configurations underrepresented in routine driving data (e.g., unusual object placement, constrained
road occupancy, anomalous spatial proximity). Layout control
enables a more direct specification of such configurations
than standard augmentation, providing a practical way to

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
12

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

model atypical spatial arrangements that challenge the ADS
perception and planning modules.
C. Scene-based Corner Case Generation
For robustness of the ADS model, the data pipeline must
incorporate diverse driving scenes, and scene-based cornercase generation methods address this by moving beyond
image-level modifications to directly create safety-relevant
scene-level variations—either by generating scenarios with
real-world-like distributions or by collecting samples under
targeted conditions. These methods are primarily categorized
into physical-model-based, style-transfer-based, and eventbased approaches.
1) Scene Generation Based on Physical Models: Physicsbased approaches rely on explicit physical models, including
atmospheric scattering models [123], [124], rain photometric
modeling [125] and pulse propagation models in the presence
of scattering particles [126], [127], [128] to generate samples
under foggy, rainy, or snowy conditions [8]. Physics-based
generation solutions are efficient and interpretable. However,
the model parameters are predefined under ideal assumptions
and only apply to specific scenes. For example, in the atmospheric scattering model, the atmosphere condition is assumed
to be homogeneous and overlooks the impacts of texture
density and scene depth on light [129]. To ensure that the predefined parameters adapt to varying conditions, it is essential
to adjust them within a specified range. This enables control
over specific attributes of generated scenes. Physical-modelbased approaches are particularly useful for generating adverse
environmental conditions in a controllable and interpretable
manner, as such conditions are a major source of distribution
shift for perception systems. Given that weather-related corner
cases are costly and challenging to capture exhaustively in
real-world driving datasets, physics-based models provide a
principled framework for assessing ADS performance under
environmental degradation while maintaining precise control
over relevant scene parameters and attributes.
2) Scene Generation Based on Image Style Transfer: Image
style transfer has been applied in autonomous driving to
improve robustness to target domains, such as adverse weather
conditions and day-to-night image translation [131]. Applying
style transfer to existing driving images can streamline cornercase generation and reduce the time and resources required to
construct domain-diverse samples.
Traditional style transfer methods rely on manually crafted
low-level features to align patches between the content and
style images [132], aiming to achieve a harmonious fusion of
their visual characteristics. In recent years, deep learning methods have demonstrated strong capabilities for feature extraction, offering a promising approach to capture intricate style
patterns [133], [134]. Arbitrary style transfer methods used
unified models with feedforward architectures to efficiently
handle diverse inputs [135], [136], [137]. Liu et al. [138]
used an adaptive attention normalization module to acquire
spatial attention scores from both shallow and deep features. However, image reconstruction errors can corrupt image
content after several rounds of stylization. An et al. [139] mitigated content leakage employing reversible neural flows and an

Fig. 8. Overview of StyleDiffusion. Initially, the content image Ic and the
style image I s are processed by a diffusion-based style removal module to
extract domain-aligned content information. Subsequently, the content of Ic
is utilized in a diffusion-based style transfer module to produce the stylized
result Ics . This figure is inspired by [130].

unbiased feature transfer module. It performed unbiased style
transfer on deep features and reconstructed the stylized images
through reversed feature inference. Zhang et al. [140] applied
contrastive learning to directly learn style representations from
image features, improving arbitrary style transfer in different
domains.
In addition, visual transformers were incorporated into style
transfer tasks. Park and Kim [141] performed global style
composition guided by content through a transformer-driven
style composition module. They used self-attention mechanisms to capture long-range dependencies and subsequently
merged Styleformer with StyleGAN2 to generate compositional scenes. The model could utilize the Cityscapes dataset to
produce high-resolution samples depicting traffic and vehicle
conditions. Reference [142] proposed a transformer-based
method to alleviate biased content representation in style
transfer by accounting for long-range dependencies of input
images. In diffusion-based style transfer, [143] proposed an
inversion-based method for stylization. Furthermore, [130]
explored the problem of content–style disentanglement, as
shown in Fig 8. The diffusion-based style removal and transfer
modules first separated style information from both content
and style images to reveal domain-aligned content, and then
transferred the disentangled style representation to the target
image.
Style-transfer-based data generation constitutes an effective
strategy for exposing models to cross-domain appearance variations while preserving the underlying scene semantics. This
is particularly pertinent in the context of autonomous driving,
where an identical physical traffic configuration may exhibit
substantial variability across different weather conditions,
illumination regimes, or sensing modalities. By augmenting
domain diversity around fixed scene semantics, style transfer
facilitates model adaptation to target conditions that are infrequently represented or entirely absent in the original source
domain.
3) Scene Generation Based On Events: Among scenebased approaches, event-based corner-case generation is most
directly tied to safety validation, as it focuses on algorithmically identifying safety-critical corner cases (e.g., traffic

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIANG et al.: CORNER CASE DETECTION AND GENERATION FOR AUTONOMOUS DRIVING: AN OVERVIEW

13

TABLE I
S UMMARY OF V IRTUAL E NVIRONMENT S IMULATORS

TABLE II
E VALUATION M ETRICS

violations, collisions) that pose unsafe outcomes prior to realworld deployment [144]. Rather than generating only visually
distinct scenes, these methods search the action space to
pinpoint behaviors that trigger such safety risks. The sensory
outputs associated with these trigger events are then used as
corner cases. This formulation makes event-based generation
particularly meaningful because it targets the conditions under
which model failure is most consequential.
Inspired by parallel system theory [150], as shown in
Table I, numerous simulators have been developed, including
CARLA [145], VISTA data-driven simulation engine [149],
[151], urban mobility simulation (SUMO) [148], InterSim
[152], TrafficBots [153], and HMIway-env [154]. Leveraging
these simulators, numerous search algorithms are employed
to efficiently identify rare safety-critical events in a large
search space. Reinforcement learning (RL) and its variants are

widely used to control agents’ intentional behavior, simulate
scenarios, and identify dangerous actions that violate them.
For example, Sun et al. [155] used reinforcement learning
to generate corner-case scenarios in the simulator’s virtual
environment. Kishore et al. [156] first selected failure cases,
such as false-positive and false-negative samples, and used
imitation training to learn an optimal policy for generating data with domain randomization. Due to the rarity of
safety-critical events, Feng et al. [1] proposed a dense deep
reinforcement learning approach (D2RL) to find critical states
(dangerous events) from a large number of vehicle behavior
plans, and reconnect these critical states for information densification through augmented reality to accelerate model training
in potentially unsafe situations. To improve the efficiency
of model training and robustness under unseen ‘long tail’
scenarios, Cao et al. [157] presented a dynamic confidenceaware reinforcement learning (DCARL) framework to generate
vehicle potential trajectories, evaluate the dynamic confidence
value of each trajectory, and update the policy with the high
confidence value for continuous performance improvement.
Event-based generation goes beyond improving sample
realism; more importantly, it offers a direct mechanism for
uncovering failure-inducing states and safety-critical interactions that are difficult to encounter naturally. Compared with
other generation strategies, event-based methods are more
tightly coupled to ADS failure modes because they explicitly
search the regions of the scenario space where robustness
is most severely challenged. This makes them particularly
valuable for safety-oriented testing, long-tail validation, and
the iterative improvement of model behavior under rare but
hazardous conditions.
V. E VALUATION M ETRICS
Well-designed evaluation metrics are essential for determining whether AVs are truly ready for deployment, especially
in rare but safety-critical edge cases [1], [157], [158]. In

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
14

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

TABLE III
A C OMPARATIVE S TUDY OF E XISTING DATASETS FOR AUTONOMOUS D RIVING

this section, we summarize three principal categories of
metrics—data-level, model-level, and semantic-level—which
collectively constitute a systematic framework to quantify the
safety of automated vehicles.
A. Data-Level Metrics
In data-level corner case detection, which aims to identify
anomalous inputs not covered by standard training data, most
methods treat the task as binary classification by separating
rare, safety-critical corner cases from normal samples. The
most common evaluation metrics are AUC and AP, which
capture complementary aspects of detection performance and
together provide a more complete assessment. AUC is a
standard metric for evaluating a model’s overall discriminative ability. It is computed from the receiver operating
characteristic (ROC) curve, which characterizes performance
across all possible classification thresholds by plotting the
true positive rate (TPR), namely the proportion of correctly
identified corner cases, against the false positive rate (FPR),
namely the proportion of normal samples incorrectly classified as corner cases. AUC aggregates this tradeoff into a
single score: a value of 1 reflects perfect discrimination (all
corner cases are caught, no normal samples are flagged),
while 0.5 indicates random guessing. Crucially, AUC is

threshold-invariant, meaning it evaluates performance across
all possible decision boundaries—vital for real-world deployment, where threshold tuning directly affects false-alarm rates
and safety.
However, AUC’s strengths also limit its usefulness for
corner-case detection, where positive samples (corner cases)
are extremely rare. Unlike AUC, which aggregates performance across all thresholds, Average Precision (AP) focuses
on the Precision–Recall (PR) curve, which emphasizes the
positive class. AP summarizes this curve as a weighted mean
of precision values across thresholds, with weights proportional to the increase in recall at each step. This makes AP
particularly well-suited for corner-case detection: it directly
measures how well a model balances capturing rare risks (high
recall) with avoiding false alarms (high precision)—a critical
trade-off for deploying safe, reliable systems.

B. Model-Level Metrics
Neuron coverage was first proposed in a white-box differential test algorithm to identify inputs that cause inconsistent
outputs across multiple DNNs by applying an affine transformation to the image [47]. Mathematically, N = n1 , n2 , . . .
indicates all neurons of a DNN and T = x1 , x2 , . . . represents

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIANG et al.: CORNER CASE DETECTION AND GENERATION FOR AUTONOMOUS DRIVING: AN OVERVIEW

the test input. The out(n, x) function returns the output of the
neuron n. Thus, the coverage of neurons defined is as follows:
NCov(T , x) =

|n|∀x ∈ T , out(n, x) > t|
|N|

(6)

Neuron coverage quantifies the testing of a DNN’s internal
logic. DeepGauge proposed multi-granularity testing criteria
[159], which provide test coverage standards for deep learning
systems at two levels: the neuron and layer levels. Accordingly,
neurons are divided into two states: the major function region
and the corner-case region. For a neuron n, low and high are
the upper and lower boundary output values of the activation
function range, and if the neuron output is within a reasonable
range, this is identified as the major function region. It can be
defined as follows:
∀n ∈ N : φ(x, n) ∈ [lown , highn ]

(7)

15

Wilderness Impact (WI) was proposed in [66] as an evaluation index of the corner case. Because unknown objects are
prone to misclassification into known categories, WI quantifies
the impact of unknown categories on the model’s accuracy.
Ideally, the smaller the WI value, the less the unknown class
interferes with the accuracy.
WI =

PK
−1
PK∪U

(11)

where PK represents the accuracy of the known class in the
validation set, and PK∪U represents the accuracy of the model
on the validation set of the known class and the unknown
class.
VI. DATASETS
In this section, we summarize publicly available datasets for
robust safety-critical corner-case detection.

If it exceeds this range, it is considered a corner-case region.
∃n ∈ N : φ(x, n) ∈ (−∞, lown ) ∪ (highn , +∞)

(8)

Combinatorial testing (CT) is an effective technique for
inspecting traditional software systems, as it balances the
trade-off between test coverage and fault detection. DeepCT
[160] extends this idea to deep learning systems and proposes
a combinatorial testing criterion for DL systems. It introduces
the concept of tomography, which treats the DNN as a
multilayer (multiscale) function and tests it layer by layer to
explore its potential feature space.
C. Semantic-Level Metrics
Semantic-level corner-case detection is predominantly
investigated along four principal dimensions: predictive uncertainty, reconstruction error, semantic distance, and distributional shift between datasets. Accordingly, the effectiveness
of a given model can be quantitatively assessed using the
following metrics.
Structural similarity (SSIM) quantifies the degree of distortion in an image or the resemblance between two images.
SSIM is a perceptual model that quantifies the perceptual
discrepancy between the original and predicted images. It
relies on the image’s visible structure and is more consistent
with human intuition. The mathematical definition of SSIM is
shown in Eq. 9, where µ x denotes the average gray-scale for
measuring brightness, and σ xy denotes the standard deviation
of gray-scale for measuring contrast.


2µ x µy + c1 2σ xy + c2


(9)
SSIM(x, y) = 2
µ x + µ2y + c1 σ2x + σ2y + c2
In general, mIoU is used to evaluate the performance of
semantic segmentation models. Similarly, to detect corner
cases at the semantic level, mIoU defined in Eq. 10 is used
to quantify the segmentation mask’s accuracy. Here T Pt , FPt ,
and FNt are the numbers of true positive, false positive, and
false negative pixels in frame t, respectively.
IoUt =

T Pt
T Pt + FPt + FNt

(10)

A. Real-World Datasets
To evaluate the model’s performance across various scenarios, extensive real-world data collection has been conducted.
As one of the most popular datasets in autonomous driving,
KITTI (Karlsruhe Institute of Technology and Toyota Technological Institute) consists of sensory outputs recorded with a
variety of sensor modalities, including high-resolution RGB,
grayscale stereo cameras, and a 3D laser scanner, and provides
15,000 frames of data around locations in Karlsruhe, Germany.
The KITTI dataset is widely used to assess depth prediction,
depth completion, and object recognition. Recently, numerous
large-scale datasets including nuScenes [161],1 Cityscapes
[177], Waymo [163],2 Audi Autonomous Driving Dataset
(A2D2) [164]3 and the ONCE (One millioN sCenEs) dataset
for 3D object detection [178] have been collected under
various scenarios.
Apart from these general-purpose datasets, a few datasets
(such as RoadAnomaly [72], RoadAnomaly21 [179], Lost and
Found Dataset [180], Fishyscapes [181]) focus on abnormal
or dangerous scenes. For example, RoadAnomaly [72] and
RoadAnomaly21 [179] are datasets for anomaly segmentation
and can be used to identify regions containing unusual objects
(such as animals, rocks, and obstacles) that were never seen
during training. DADA [182] can be used to localize video
accidents. Although these benchmarks can detect anomalies or
predict risky attributes in safety-critical settings, they cannot
improve the model’s robustness in

[...正文过长，此处由批处理脚本仅做上下文截断；请在结论中说明该限制...]

in a future issue of this journal. Content is final as presented, with the exception of pagination.
18

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

remains a key issue to be addressed in photorealistic corner
case generation research.
E. Large Language Models for CC Understanding
With the remarkable advancements of large language
models (LLMs) across diverse domains, their integration
into autonomous driving systems has garnered significant
traction—enriching human-machine interaction [235], [236],
[237], enhancing environmental perception capabilities [238],
[239], and enabling a paradigm shift from data-driven to
knowledge-driven end-to-end pipelines [240], [241], [242],
[243]. For instance, Cui et al. [244] and Yang et al.
[245] have presented comprehensive literature reviews on the
application of LLMs in autonomous driving, synthesizing
existing progress in this rapidly evolving field. However,
leveraging LLMs to effectively understand and address corner
cases—a critical bottleneck for safe and reliable autonomous
navigation—remains in its nascent stages, plagued by several
unresolved challenges.
First, while a plethora of visual language models (VLMs,
e.g., VisionLLM [246]) and multimodal LLMs (MLLMs,
e.g., LLaVa [247]) have been developed, these models are
inherently general-purpose and lack specialized optimization for autonomous driving scenarios, particularly extreme
cornering contexts. To address this, Chen et al. proposed
CODA-LM [248], leveraging a hierarchical data structure
and LLM prompting to generate high-quality pre-annotations
for complex scenes. CODA-REC [249] augmented with textual descriptions to facilitate MLLM-based comprehension
of multimodal semantic information—addressing the inherent
limitation of general-purpose models in interpreting domainspecific corner scenarios. Second, while existing studies have
sought to integrate VLMs for automated decision-making in
autonomous driving, they rarely prioritize robustness and interpretability. Mo et al. [250] fine-tuned InternVL-2.0 for driving
scenarios by enhancing spatial correlation with position and
depth information, incorporating chain-of-thought reasoning to
improve accuracy, and developing context-aware learning via
scenario-based retrieval. However, it still highlights the need
for further refinement to fully address corner-case complexity.
Furthermore, integrating LLMs and VLMs into autonomous
driving systems remains challenging due to hallucination risk
and real-time performance limitations.

multiple dimensions to deepen understanding of corner cases.
First, large-scale corner-case datasets, either collected in the
real world via crowdsourcing or generated by deep generative neural networks, are prerequisites. Second, how to fuse
multimodal outputs for corner-case detection in the mixed
driving system is promising for improving model performance, especially in complex scenarios. Third, the current
data-driven paradigm has substantial performance limitations,
including low robustness, limited interpretability, and poor
fault tolerance. With the popularity of LLMs, leveraging prior
knowledge to improve corner-case understanding and building
a knowledge-based decision-making system are promising
approaches for the safety of autonomous driving.
R EFERENCES
[1]

[2]

[3]
[4]

[5]

[6]

[7]

[8]

[9]

[10]

[11]

[12]

VIII. C ONCLUSION
Understanding corner cases is critical for decision-making
in safety-critical scenarios. However, research on corner cases
in autonomous driving has received comparatively less attention, overshadowed by topics like OOD learning, anomaly
detection, and adversarial examples. In this survey, we conduct
a taxonomic analysis of data samples and their relationships
to decision boundaries. We observe that corner cases remain
understudied due to three key gaps: limited consensus in
their definition, a scarcity of dedicated datasets, and diverged
research priorities.
To accelerate the development of autonomous driving, both
academia and industry should make greater efforts across

[13]

[14]

[15]

[16]

S. Feng et al., “Dense reinforcement learning for safety validation of
autonomous vehicles,” Nature, vol. 615, no. 7953, pp. 620–627, Mar.
2023.
D. Lee and D. J. Hess, “Public concerns and connected and automated
vehicles: Safety, privacy, and data security,” Humanities Social Sci.
Commun., vol. 9, no. 1, p. 90, Mar. 2022.
G. Falco et al., “Governing AI safety through independent audits,”
Nature Mach. Intell., vol. 3, no. 7, pp. 566–571, Jul. 2021.
J. Guo, U. Kurup, and M. Shah, “Is it safe to drive? An overview
of factors, metrics, and datasets for driveability assessment in
autonomous driving,” IEEE Trans. Intell. Transp. Syst., vol. 21, no. 8,
pp. 3135–3151, Aug. 2020.
A. Nunes, B. Reimer, and J. F. Coughlin, “People must retain control of
autonomous vehicles,” Nature, vol. 556, no. 7700, pp. 169–171, Apr.
2018.
C. Pek, S. Manzinger, M. Koschi, and M. Althoff, “Using online
verification to prevent autonomous vehicles from causing accidents,”
Nature Mach. Intell., vol. 2, no. 9, pp. 518–528, Sep. 2020.
Y. Almalioglu, M. Turan, N. Trigoni, and A. Markham, “Deep learningbased robust positioning for all-weather autonomous driving,” Nature
Mach. Intell., vol. 4, no. 9, pp. 749–760, Sep. 2022.
Y. Liang et al., “An interpretable image denoising framework via
dual disentangled representation learning,” IEEE Trans. Intell. Vehicles,
vol. 9, no. 1, pp. 2016–2030, Jan. 2024.
Y. Deng, T. Zhang, G. Lou, X. Zheng, J. Jin, and Q.-L. Han, “Deep
learning-based autonomous driving systems: A survey of attacks and
defenses,” IEEE Trans. Ind. Informat., vol. 17, no. 12, pp. 7897–7912,
Dec. 2021.
J. Sun, Y. Cao, Q. A. Chen, and Z. M. Mao, “Towards robust LiDARbased perception in autonomous driving: General black-box adversarial
sensor attack and countermeasures,” in Proc. 29th USENIX Conf. Secur.
Symp., 2020, pp. 1–11.
R. Song, M. O. Ozmen, H. Kim, R. Müller, Z. B. Celik, and
A. Bianchi, “Discovering adversarial driving maneuvers against
autonomous vehicles,” in Proc. 32nd USENIX Secur. Symp. (USENIX
Secur. 23), Aug. 2023, pp. 2957–2974.
A. Filos, P. Tigkas, R. Mcallister, N. Rhinehart, S. Levine, and
Y. Gal, “Can autonomous vehicles identify, recover from, and adapt
to distribution shifts?” in Proc. 37th Int. Conf. Mach. Learn., vol. 119,
2020, pp. 3145–3153.
Z. Ma, Y. Yang, G. Wang, X. Xu, H. T. Shen, and M. Zhang,
“Rethinking open-world object detection in autonomous driving
scenarios,” in Proc. 30th ACM Int. Conf. Multimedia, Oct. 2022,
pp. 1279–1288.
K. Wang, L. Pu, J. Zhang, and J. Lu, “Gated adversarial network
based environmental enhancement method for driving safety under
adverse weather conditions,” IEEE Trans. Intell. Vehicles, vol. 8, no. 2,
pp. 1934–1943, Feb. 2023.
Y. Liu, M. Wang, P. Lasang, and Q. Sun, “Importance biased traffic
scene segmentation in diverse weather conditions,” IEEE Trans. Intell.
Vehicles, vol. 9, no. 1, pp. 2753–2765, Jan. 2024.
J. Shen, J. Y. Won, Z. Chen, and Q. A. Chen, “Drift with devil: Security
of multi-sensor fusion based localization in high-level autonomous
driving under GPS spoofing,” in Proc. 29th USENIX Secur. Symp.
(USENIX Security), 2020, pp. 931–948.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIANG et al.: CORNER CASE DETECTION AND GENERATION FOR AUTONOMOUS DRIVING: AN OVERVIEW

[17]

[18]
[19]
[20]
[21]
[22]
[23]
[24]
[25]
[26]
[27]

[28]
[29]
[30]
[31]
[32]
[33]
[34]
[35]
[36]
[37]
[38]
[39]
[40]
[41]

X. Ren, M. Li, Z. Li, W. Wu, L. Bai, and W. Zhang, “Curiosity-driven
attention for anomaly road obstacles segmentation in autonomous
driving,” IEEE Trans. Intell. Vehicles, vol. 8, no. 3, pp. 2233–2243,
Mar. 2023.
Z. Zhu and H. Zhao, “A survey of deep RL and IL for autonomous
driving policy learning,” IEEE Trans. Intell. Transp. Syst., vol. 23,
no. 9, pp. 14043–14065, Sep. 2022.
S. Grigorescu, B. Trasnea, T. Cocias, and G. Macesanu, “A survey
of deep learning techniques for autonomous driving,” J. Field Robot.,
vol. 37, no. 3, pp. 362–386, Apr. 2020.
Y. Li et al., “Choose your simulator wisely: A review on open-source
simulators for autonomous driving,” IEEE Trans. Intell. Vehicles,
vol. 9, no. 5, pp. 4861–4876, May 2024.
H. Zhao, M. Meng, X. Li, J. Xu, L. Li, and S. Galland, “A survey of
autonomous driving frameworks and simulators,” Adv. Eng. Informat.,
vol. 62, Oct. 2024, Art. no. 102850.
T. Zhang, H. Liu, W. Wang, and X. Wang, “Virtual tools for testing
autonomous driving: A survey and benchmark of simulators, datasets,
and competitions,” Electronics, vol. 13, no. 17, p. 3486, Sep. 2024.
S. Tang et al., “A survey on automated driving system testing:
Landscapes and trends,” ACM Trans. Softw. Eng. Methodology, vol. 32,
no. 5, pp. 1–62, Sep. 2023.
D. Chen, M. Zhu, H. Yang, X. Wang, and Y. Wang, “Data-driven traffic
simulation: A comprehensive review,” IEEE Trans. Intell. Vehicles,
vol. 9, no. 4, pp. 4730–4748, Apr. 2024.
Y. Gao et al., “Foundation models in autonomous driving: A survey on
scenario generation and scenario analysis,” IEEE Open J. Intell. Transp.
Syst., early access, Feb. 3, 2026, doi: 10.1109/OJITS.2026.3660686.
J.-A. Bolte, A. Bar, D. Lipinski, and T. Fingscheidt, “Towards corner
case detection for autonomous driving,” in Proc. IEEE Intell. Vehicles
Symp. (IV), Jun. 2019, pp. 438–445.
J. Breitenstein, J.-A. Termöhlen, D. Lipinski, and T. Fingscheidt,
“Systematization of corner cases for visual perception in automated
driving,” in Proc. IEEE Intell. Vehicles Symp. (IV), Oct. 2020,
pp. 1257–1264.
K. Li et al., “CODA: A real-world road corner case dataset for object
detection in autonomous driving,” in Proc. Eur. Conf. Comput. Vis.ECCV, 2022, pp. 406–423.
F. Heidecker et al., “An application-driven conceptualization of corner
cases for perception in highly automated driving,” in Proc. IEEE Intell.
Vehicles Symp. (IV), Jul. 2021, pp. 644–651.
K. Zhou, Z. Liu, Y. Qiao, T. Xiang, and C. C. Loy, “Domain
generalization: A survey,” IEEE Trans. Pattern Anal. Mach. Intell.,
vol. 45, no. 4, pp. 4396–4415, Apr. 2023.
H. Nichols, M. Jimenez, Z. Goddard, M. Sparapany, B. Boots, and
A. Mazumdar, “Adversarial sampling-based motion planning,” IEEE
Robot. Autom. Lett., vol. 7, no. 2, pp. 4267–4274, Apr. 2022.
P. Jing et al., “Too good to be safe: Tricking lane detection in
autonomous driving with crafted perturbations,” in Proc. 30th USENIX
Secur. Symp. (USENIX Security), 2021, pp. 3237–3254.
T. Fernando, H. Gammulle, S. Denman, S. Sridharan, and C. Fookes,
“Deep learning for medical anomaly detection—A survey,” ACM
Comput. Surv., vol. 54, no. 7, pp. 1–37, Jul. 2021.
S. Calderon-Ramirez, S. Yang, and D. Elizondo, “Semisupervised deep
learning for image classification with distribution mismatch: A survey,”
IEEE Trans. Artif. Intell., vol. 3, no. 6, pp. 1015–1029, Dec. 2022.
J. Wang et al., “Generalizing to unseen domains: A survey on
domain generalization,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 8,
pp. 8052–8072, Aug. 2023.
N. Akhtar, A. Mian, N. Kardan, and M. Shah, “Advances in adversarial
attacks and defenses in computer vision: A survey,” IEEE Access,
vol. 9, pp. 155161–155196, 2021.
Y. Liu and J. H. L. Hansen, “Towards complexity level classification
of driving scenarios using environmental information,” in Proc. IEEE
Intell. Transp. Syst. Conf. (ITSC), Oct. 2019, pp. 810–815.
C. Ryan, F. Murphy, and M. Mullins, “End-to-end autonomous driving
risk analysis: A behavioural anomaly detection approach,” IEEE Trans.
Intell. Transp. Syst., vol. 22, no. 3, pp. 1650–1662, Mar. 2021.
K. Lee, K. Lee, H. Lee, and J. Shin, “A simple unified framework for
detecting out-of-distribution samples and adversarial attacks,” in Proc.
Adv. Neural Inf. Process. Syst., vol. 31, 2018, pp. 1–10.
S. Deng, J.-G. Yu, Z. Wu, H. Gao, Y. Li, and Y. Yang, “Learning
relative feature displacement for few-shot open-set recognition,” IEEE
Trans. Multimedia, vol. 25, pp. 5763–5774, 2023.
K. Leino, Z. Wang, and M. Fredrikson, “Globally-robust neural
networks,” in Proc. Int. Conf. Mach. Learn. (ICML), Jul. 2021,
pp. 6212–6222.

[42]

[43]

[44]

[45]

[46]

[47]

[48]

[49]

[50]

[51]

[52]

[53]

[54]

[55]

[56]

[57]

[58]

[59]

[60]

[61]

[62]

[63]

[64]

19

J. Kim, R. Feldt, and S. Yoo, “Guiding deep learning system testing
using surprise adequacy,” in Proc. IEEE/ACM 41st Int. Conf. Softw.
Eng. (ICSE), May 2019, pp. 1039–1049.
Z. Ma, Z. Zheng, J. Wei, X. Wei, Y. Yang, and H. T. Shen, “Openscenario domain adaptive object detection in autonomous driving,”
in Proc. 31st ACM Int. Conf. Multimedia. New York, NY, USA:
Association for Computing Machinery, Oct. 2023, pp. 8453–8462.
H. Kim, Y. Kang, C. Oh, and K.-J. Yoon, “Single domain generalization
for LiDAR semantic segmentation,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit. (CVPR), Jun. 2023, pp. 17587–17598.
Z. Liu, Z. Miao, X. Zhan, J. Wang, B. Gong, and S. X. Yu, “Large-scale
long-tailed recognition in an open world,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2019, pp. 2537–2546.
D. Hendrycks et al., “Scaling out-of-distribution detection for realworld settings,” in Proc. 39th Int. Conf. Mach. Learn. (ICML), 2022,
pp. 8759–8773.
K. Pei, Y. Cao, J. Yang, and S. Jana, “DeepXplore: Automated
whitebox testing of deep learning systems,” Commun. ACM, vol. 62,
no. 11, pp. 137–145, Oct. 2019.
Y. Tian, K. Pei, S. Jana, and B. Ray, “DeepTest: Automated testing
of deep-neural-network-driven autonomous cars,” in Proc. IEEE/ACM
40th Int. Conf. Softw. Eng. (ICSE), May 2018, pp. 303–314.
W. Wu, H. Xu, S. Zhong, M. R. Lyu, and I. King, “Deep validation:
Toward detecting real-world corner cases for deep neural networks,” in
Proc. 49th Annu. IEEE/IFIP Int. Conf. Dependable Syst. Netw. (DSN),
Jun. 2019, pp. 125–137.
H. Ben Braiek and F. Khomh, “DeepEvolution: A search-based testing
approach for deep neural networks,” in Proc. IEEE Int. Conf. Softw.
Maintenance Evol. (ICSME), Sep. 2019, pp. 454–458.
Y. N. Dauphin, R. Pascanu, C. Gulcehre, K. Cho, S. Ganguli, and
Y. Bengio, “Identifying and attacking the saddle point problem in highdimensional non-convex optimization,” in Proc. 27th Int. Conf. Neural
Inf. Process. Syst., vol. 2, Dec. 2014, pp. 2933–2941.
L. Wang et al., “Towards understanding learning representations:
To what extent do different neural networks learn the same
representation,” in Proc. 32nd Int. Conf. Neural Inf. Process. Syst.,
2018, pp. 9607–9616.
D. R. Hardoon, S. Szedmak, and J. Shawe-Taylor, “Canonical correlation analysis: An overview with application to learning methods,”
Neural Comput., vol. 16, no. 12, pp. 2639–2664, Dec. 2004.
M. Raghu, J. Gilmer, J. Yosinski, and J. Sohl-Dickstein, “SVCCA: Singular vector canonical correlation analysis for deep learning dynamics
and interpretability,” in Proc. 31st Int. Conf. Neural Inf. Process. Syst.,
2017, pp. 6078–6087.
S. Kornblith, M. Norouzi, H. Lee, and G. Hinton, “Similarity of neural
network representations revisited,” in Proc. Int. Conf. Mach. Learn.,
2019, pp. 3519–3529.
K. Lenc and A. Vedaldi, “Understanding image representations by
measuring their equivariance and equivalence,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2015, pp. 991–999.
A. Csiszárik, P. Kőrösi-Szabó, A. Matszangosz, G. Papp, and D. Varga,
“Similarity and matching of neural network representations,” in Proc.
Adv. Neural Inf. Process. Syst., vol. 34, 2021, pp. 5656–5668.
T. Ouyang, V. S. Marco, Y. Isobe, H. Asoh, Y. Oiwa, and Y. Seo,
“Corner case data description and detection,” in Proc. IEEE/ACM 1st
Workshop AI Eng., Softw. Eng. AI (WAIN), May 2021, pp. 19–26.
T. Ouyang, Y. Isobe, V. S. Marco, J. Ogata, Y. Seo, and Y. Oiwa, “AI
robustness analysis with consideration of corner cases,” in Proc. IEEE
Int. Conf. Artif. Intell. Test. (AITest), Aug. 2021, pp. 29–36.
R. Chan, M. Rottmann, and H. Gottschalk, “Entropy maximization
and meta classification for out-of-distribution detection in semantic
segmentation,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV),
Oct. 2021, pp. 5108–5117.
D. Hendrycks and K. Gimpel, “A baseline for detecting misclassified
and out-of-distribution examples in neural networks,” in Proc. Int.
Conf. Learn. Represent., 2017, pp. 1–11.
S. Liang, Y. Li, and R. Srikant, “Enhancing the reliability of out-ofdistribution image detection in neural networks,” in Proc. Int. Conf.
Learn. Represent., 2018, pp. 1–8.
J. Van Amersfoort, L. Smith, Y. W. Teh, and Y. Gal, “Uncertainty
estimation using a single deep deterministic neural network,” in Proc.
Int. Conf. Mach. Learn., 2020, pp. 9690–9700.
A. Kendall, V. Badrinarayanan, and R. Cipolla, “Bayesian SegNet:
Model uncertainty in deep convolutional encoder–decoder architectures
for scene understanding,” in Proc. Brit. Mach. Vis. Conf., 2017,
pp. 1–7.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
20

[65]

[66]

[67]

[68]

[69]

[70]

[71]

[72]

[73]

[74]

[75]

[76]

[77]

[78]

[79]

[80]
[81]

[82]

[83]

[84]

[85]

[86]

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

P.-Y. Huang, W.-T. Hsu, C.-Y. Chiu, T.-F. Wu, and M. Sun, “Efficient
uncertainty estimation for semantic segmentation in videos,” in Proc.
Eur. Conf. Comput. Vis. (ECCV), 2018, pp. 520–535.
K. J. Joseph, S. Khan, F. S. Khan, and V. N. Balasubramanian,
“Towards open world object detection,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021, pp. 5826–5836.
W. Liu, W. Luo, D. Lian, and S. Gao, “Future frame prediction
for anomaly detection—A new baseline,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., Jun. 2018, pp. 6536–6545.
D. Bogdoll, E. Eisen, M. Nitsche, C. Scheib, and J. M. Zöllner,
“Multimodal detection of unknown objects on roads for autonomous
driving,” in Proc. IEEE Int. Conf. Syst., Man, Cybern. (SMC), Oct.
2022, pp. 325–332.
M. Hasan, J. Choi, J. Neumann, A. K. Roy-Chowdhury, and
L. S. Davis, “Learning temporal regularity in video sequences,” in
Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2016,
pp. 733–742.
P. Oza and V. M. Patel, “C2AE: Class conditioned auto-encoder for
open-set recognition,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2019, pp. 2307–2316.
Y. Xia, X. Cao, F. Wen, G. Hua, and J. Sun, “Learning discriminative
reconstructions for unsupervised outlier removal,” in Proc. IEEE Int.
Conf. Comput. Vis. (ICCV), Dec. 2015, pp. 1511–1519.
K. Lis, K. K. Nakka, P. Fua, and M. Salzmann, “Detecting the
unexpected via image resynthesis,” in Proc. IEEE/CVF Int. Conf.
Comput. Vis. (ICCV), Oct. 2019, pp. 2152–2161.
G. Di Biase, H. Blum, R. Siegwart, and C. Cadena, “Pixelwise anomaly detection in complex driving scenes,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021,
pp. 16918–16927.
T. Vojir, T. Šipka, R. Aljundi, N. Chumerin, D. O. Reino, and
J. Matas, “Road anomaly detection by partial image reconstruction
with segmentation coupling,” in Proc. IEEE/CVF Int. Conf. Comput.
Vis. (ICCV), Oct. 2021, pp. 15651–15660.
S. Yan, L. Chen, C. Wang, Y. Liu, P. Zhai, and L. Zhang, “Re-synthesis
anomaly detection framework for driving scenes guided by uncertain
metrics,” in Proc. 8th Int. Conf. Comput. Artif. Intell., Mar. 2022,
pp. 579–584.
K. Lis, S. Honari, P. Fua, and M. Salzmann, “Detecting road obstacles
by erasing them,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 46,
no. 4, pp. 2450–2460, Apr. 2024.
T. Vojı́r and J. Matas, “Image-consistent detection of road anomalies as
unpredictable patches,” in Proc. IEEE/CVF Winter Conf. Appl. Comput.
Vis. (WACV), Jan. 2023, pp. 5480–5489.
B. Barz, E. Rodner, Y. G. Garcia, and J. Denzler, “Detecting regions
of maximal divergence for spatio-temporal anomaly detection,” IEEE
Trans. Pattern Anal. Mach. Intell., vol. 41, no. 5, pp. 1088–1101, May
2019.
R. Yoshihashi, W. Shao, R. Kawakami, S. You, M. Iida, and T. Naemura, “Classification-reconstruction learning for open-set recognition,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2019, pp. 4011–4020.
Z. Song et al., “Synthetic datasets for autonomous driving: A survey,”
IEEE Trans. Intell. Vehicles, vol. 9, no. 1, pp. 1847–1864, Jan. 2024.
X. Bai et al., “Bridging the domain gap between synthetic and realworld data for autonomous driving,” ACM J. Auto. Transp. Syst., vol. 1,
no. 2, pp. 1–15, Jun. 2024, doi: 10.1145/3633463.
Y. Fu, S. Liu, Y. Xia, F. Guo, and K. Zheng, “Cross-scenario maneuver
decision with adaptive perception for autonomous driving,” in Proc.
32nd ACM Int. Conf. Inf. Knowl. Manage., Oct. 2023, pp. 535–544,
doi: 10.1145/3583780.3614831.
A. Bewley et al., “Learning to drive from simulation without real
world labels,” in Proc. Int. Conf. Robot. Autom. (ICRA), May 2019,
pp. 4818–4824.
C. Gao et al., “Synthetic data accelerates the development of generalizable learning-based algorithms for X-ray image analysis,” Nature
Mach. Intell., vol. 5, no. 3, pp. 294–308, 2023.
M. Zhang, Y. Zhang, L. Zhang, C. Liu, and S. Khurshid, “DeepRoad:
GAN-based metamorphic testing and input validation framework for
autonomous driving systems,” in Proc. 33rd IEEE/ACM Int. Conf.
Automated Softw. Eng. (ASE), Sep. 2018, pp. 132–142, doi: 10.1145/
3238147.3238187.
S. Reed, Z. Akata, X. Yan, L. Logeswaran, B. Schiele, and H. Lee,
“Generative adversarial text to image synthesis,” in Proc. 33rd Int.
Conf. Mach. Learn., vol. 48, Jun. 2016, pp. 1060–1069.

[87]

H. Zhang et al., “StackGAN: Text to photo-realistic image synthesis
with stacked generative adversarial networks,” in Proc. IEEE Int. Conf.
Comput. Vis. (ICCV), Oct. 2017, pp. 5908–5916.
[88] Z. Zhang, Y. Xie, and L. Yang, “Photographic text-to-image synthesis
with a hierarchically-nested adversarial network,” in Proc. IEEE/CVF
Conf. Comput. Vis. Pattern Recognit., Jun. 2018, pp. 6199–6208.
[89] M. Cha, Y. L. Gwon, and H. T. Kung, “Adversarial learning of semantic
relevance in text to image synthesis,” in Proc. 33rd AAAI Conf. Artif.
Intell., 2019, pp. 1–11, doi: 10.1609/AAAI.v33i01.33013272.
[90] Z. Deng, X. He, and Y. Peng, “LFR-GAN: Local feature refinement
based generative adversarial network for text-to-image generation,”
ACM Trans. Multimedia Comput., Commun., Appl., vol. 19, no. 6,
pp. 1–18, Jul. 2023, doi: 10.1145/3589002.
[91] T. Xu et al., “AttnGAN: Fine-grained text to image generation with
attentional generative adversarial networks,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., Jun. 2018, pp. 1316–1324.
[92] H. Zhang, H. Zhu, S. Yang, and W. Li, “DGattGAN: Cooperative
up-sampling based dual generator attentional GAN on text-to-image
synthesis,” IEEE Access, vol. 9, pp. 29584–29598, 2021.
[93] F. Quan, B. Lang, and Y. Liu, “ARRPNGAN: Text-to-image GAN
with attention regularization and region proposal networks,” Signal
Process., Image Commun., vol. 106, Jan. 2022, Art. no. 116728.
[Online]. Available: https://www.sciencedirect.com/science/article/pii/
S0923596522000601
[94] A. Vaswani et al., “Attention is all you need,” in Proc. Adv.
Neural Inf. Process. Syst., vol. 30, 2017, pp. 1–14. [Online].
Available:
https://proceedings.neurips.cc/paperfiles/paper/2017/file/
3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf
[95] D. P. Kingma and M. Welling, “Auto-encoding variational Bayes,”
2013, arXiv:1312.6114.
[96] A. Radford et al., “Learning transferable visual models from natural
language supervision,” in Proc. Int. Conf. Mach. Learn., vol. 139,
2021, pp. 8748–8763.
[97] A. Ramesh et al., “Zero-shot text-to-image generation,” in Proc.
Int. Conf. Mach. Learn. (ICML), Jul. 2021, pp. 8821–8831. [Online].
Available: https://proceedings.mlr.press/v139/ramesh21a.html
[98] M.
Ding
et
al.,
“Cogview:
Mastering
text-to-image
generation via transformers,” in Proc. Adv. Neural Inf.
Process. Syst. (NIPS), 2021, pp. 19822–19835. [Online].
Available:
https://proceedings.neurips.cc/paperfiles/paper/2021/file/
a4d92e2cd541fca87e4620aba658316d-Paper.pdf
[99] Y. Huang, H. Xue, B. Liu, and Y. Lu, “Unifying multimodal transformer for bi-directional image and text generation,” in Proc. 29th
ACM Int. Conf. Multimedia, Oct. 2021, pp. 1138–1147, doi: 10.1145/
3474085.3481540.
[100] I. Kapelyukh, V. Vosylius, and E. Johns, “DALL-E-bot: Introducing
Web-scale diffusion models to robotics,” IEEE Robot. Autom. Lett.,
vol. 8, no. 7, pp. 3956–3963, Jul. 2023.
[101] L. Zhang and M. Agrawala, “Adding conditional control to text-toimage diffusion models,” in Proc. IEEE/CVF Int. Conf. Comput. Vis.,
Oct. 2023, pp. 3836–3847.
[102] R. Rombach, A. Blattmann, D. Lorenz, P. Esser, and B. Ommer, “Highresolution image synthesis with latent diffusion models,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022,
pp. 10674–10685.
[103] J. Johnson et al., “Image retrieval using scene graphs,” in Proc.
IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2015,
pp. 3668–3678.
[104] J. Johnson, A. Gupta, and L. Fei-Fei, “Image generation from scene
graphs,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun.
2018, pp. 1219–1228.
[105] G. Mittal, S. Agrawal, A. Agarwal, S. Mehta, and T. Marwah,
“Interactive image generation using scene graphs,” in Proc. Int. Conf.
Learn. Represent., Mar. 2019, pp. 1–14.
[106] O. Ashual and L. Wolf, “Specifying object attributes and relations in
interactive scene generation,” in Proc. IEEE/CVF Int. Conf. Comput.
Vis. (ICCV), Oct. 2019, pp. 4560–4568.
[107] Y. Li, T. Ma, Y. Bai, N. Duan, S. Wei, and X. Wang, “PasteGAN: A
semi-parametric method to generate image from scene graph,” in Proc.
Adv. Neural Inf. Process. Syst., 2019, pp. 1–8.
[108] J. Gu, H. Zhao, Z. Lin, S. Li, J. Cai, and M. Ling, “Scene graph
generation with external knowledge and image reconstruction,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2019,
pp. 1969–1978.
[109] A. Savkin, R. Ellouze, N. Navab, and F. Tombari, “Unsupervised traffic
scene generation with synthetic 3D scene graphs,” in Proc. IEEE/RSJ
Int. Conf. Intell. Robots Syst. (IROS), Sep. 2021, pp. 1229–1235.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIANG et al.: CORNER CASE DETECTION AND GENERATION FOR AUTONOMOUS DRIVING: AN OVERVIEW

[110] B. Zhao, L. Meng, W. Yin, and L. Sigal, “Image generation from
layout,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2019, pp. 8576–8585.
[111] W. Sun and T. Wu, “Image synthesis from reconfigurable layout and
style,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2019,
pp. 10530–10539.
[112] S. Frolov, A. Sharma, J. Hees, T. Karayil, F. Raue, and A. Dengel,
“AttrLostGAN: Attribute controlled image synthesis from reconfigurable layout and style,” in Proc. 43rd DAGM German Conf. Pattern
Recognit., 2021, pp. 361–375, doi: 10.1007/978-3-030-92659-5 23.
[113] Y. Li, Y. Cheng, Z. Gan, L. Yu, L. Wang, and J. Liu, “BachGAN:
High-resolution image synthesis from salient object layout,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2020,
pp. 8362–8371.
[114] S. He et al., “Context-aware layout to image generation with enhanced
object appearance,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2021, pp. 15044–15053.
[115] Z. Yang, D. Liu, C. Wang, J. Yang, and D. Tao, “Modeling image
composition for complex scene generation,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022, pp. 7754–7763.
[116] B. Wang, T. Wu, M. Zhu, and P. Du, “Interactive image synthesis with
panoptic layout generation,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit. (CVPR), Jun. 2022, pp. 7773–7782.
[117] G. Zheng, X. Zhou, X. Li, Z. Qi, Y. Shan, and X. Li, “LayoutDiffusion:
Controllable diffusion model for layout-to-image generation,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2023,
pp. 22490–22499.
[118] T. Park, M.-Y. Liu, T.-C. Wang, and J.-Y. Zhu, “Semantic image synthesis with spatially-adaptive normalization,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2019, pp. 2332–2341.
[119] P. Zhu, R. Abdal, Y. Qin, and P. Wonka, “SEAN: Image synthesis with
semantic region-adaptive normalization,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), CA. Los Alamitos, CA, USA:
IEEE Computer Society, Jun. 2020, pp. 5103–5112.
[120] D. Bau et al., “Semantic photo manipulation with a generative image
prior,” ACM Trans. Graph., vol. 38, no. 4, pp. 1–11, Jul. 2019, doi:
10.1145/3306346.3323023.
[121] T.-C. Wang, M.-Y. Liu, J.-Y. Zhu, A. Tao, J. Kautz, and B. Catanzaro,
“High-resolution image synthesis and semantic manipulation with
conditional GANs,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., Jun. 2018, pp. 8798–8807.
[122] Y. Zeng et al., “SceneComposer: Any-level semantic image synthesis,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2023, pp. 22468–22478.
[123] S. Hong, M. Kim, and M. G. Kang, “Single image dehazing via
atmospheric scattering model-based image fusion,” Signal Process.,
vol. 178, Jan. 2021, Art. no. 107798.
[124] C. Dai, M. Lin, X. Wu, and D. Zhang, “Single hazy image restoration
using robust atmospheric scattering model,” Signal Process., vol. 166,
Jan. 2020, Art. no. 107257.
[125] M. Tremblay, S. S. Halder, R. de Charette, and J.-F. Lalonde, “Rain
rendering for evaluating and improving robustness to bad weather,” Int.
J. Comput. Vis., vol. 129, no. 2, pp. 341–360, Feb. 2021.
[126] M. Hahner et al., “LiDAR snowfall simulation for robust 3D object
detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2022, pp. 16343–16353.
[127] H. Yang et al., “Synthesizing realistic snow effects in driving images
using GANs and real data with semantic guidance,” in Proc. IEEE
Intell. Vehicles Symp. (IV), Jun. 2023, pp. 1–6.
[128] N. Mann and S. Hughes, “Soliton pulse propagation in the presence of
disorder-induced multiple scattering in photonic crystal waveguides,”
Phys. Rev. Lett., vol. 118, no. 25, Jun. 2017, Art. no. 253901.
[129] M. Ju, C. Ding, W. Ren, Y. Yang, D. Zhang, and Y. J. Guo, “IDE:
Image dehazing and exposure using an enhanced atmospheric scattering model,” IEEE Trans. Image Process., vol. 30, pp. 2180–2192,
2021.
[130] Z. Wang, L. Zhao, and W. Xing, “StyleDiffusion: Controllable disentangled style transfer via diffusion models,” in Proc. IEEE/CVF Int.
Conf. Comput. Vis. (ICCV), Oct. 2023, pp. 7643–7655.
[131] C.-T. Lin, S.-W. Huang, Y.-Y. Wu, and S.-H. Lai, “GAN-based
day-to-night image style transfer for nighttime vehicle detection,”
IEEE Trans. Intell. Transp. Syst., vol. 22, no. 2, pp. 951–963,
Feb. 2021.
[132] B. Wang, W. Wang, H. Yang, and J. Sun, “Efficient example-based
painting and synthesis of 2D directional texture,” IEEE Trans. Vis.
Comput. Graphics, vol. 10, no. 3, pp. 266–277, May 2004.

21

[133] L. A. Gatys, A. S. Ecker, M. Bethge, A. Hertzmann, and E. Shechtman, “Controlling perceptual factors in neural style transfer,” in
Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR), Jul. 2017,
pp. 3730–3738.
[134] N. Kolkin, J. Salavon, and G. Shakhnarovich, “Style transfer by
relaxed optimal transport and self-similarity,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2019, pp. 10043–10052.
[135] D. Y. Park and K. H. Lee, “Arbitrary style transfer with style-attentional
networks,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2019, pp. 5873–5881.
[136] X. Wu, Z. Hu, L. Sheng, and D. Xu, “StyleFormer: Real-time arbitrary
style transfer via parametric style composition,” in Proc. IEEE/CVF Int.
Conf. Comput. Vis. (ICCV), Oct. 2021, pp. 14598–14607.
[137] Y. Zhang, M. Li, R. Li, K. Jia, and L. Zhang, “Exact feature distribution
matching for arbitrary style transfer and domain generalization,” in
Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2022, pp. 8025–8035.
[138] S. Liu et al., “AdaAttN: Revisit attention mechanism in arbitrary neural
style transfer,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct.
2021, pp. 6629–6638.
[139] J. An, S. Huang, Y. Song, D. Dou, W. Liu, and J. Luo, “ArtFlow:
Unbiased image style transfer via reversible neural flows,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021,
pp. 862–871.
[140] Y. Zhang et al., “Domain enhanced arbitrary image style transfer
via contrastive learning,” in Proc. Special Interest Group Comput.
Graph. Interact. Techn. Conf., Aug. 2022, pp. 1–8, doi: 10.1145/
3528233.3530736.
[141] J. Park and Y. Kim, “Styleformer: Transformer based generative adversarial networks with style vector,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit. (CVPR), Jun. 2022, pp. 8973–8982.
[142] Y. Deng et al., “StyTr2: Image style transfer with transformers,” in
Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2022, pp. 11316–11326.
[143] Y. Zhang et al., “Inversion-based style transfer with diffusion models,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2023, pp. 10146–10156.
[144] G. Chou, Y. E. Sahin, L. Yang, K. J. Rutledge, P. Nilsson, and
N. Ozay, “Using control synthesis to generate corner cases: A case
study on autonomous driving,” IEEE Trans. Comput.-Aided Design
Integr. Circuits Syst., vol. 37, no. 11, pp. 2906–2917, Nov. 2018.
[145] A. Dosovitskiy, G. Ros, F. Codevilla, A. Lopez, and V. Koltun,
“CARLA: An open urban driving simulator,” in Proc. 1st Annu. Conf.
Robot Learn., 2017, pp. 1–16.
[146] Q. Li, Z. Peng, L. Feng, Q. Zhang, Z. Xue, and B. Zhou, “MetaDrive:
Composing diverse driving scenarios for generalizable reinforcement
learning,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 45, no. 3,
pp. 3461–3475, Mar. 2023.
[147] S. Shah, D. Dey, C. Lovett, and A. Kapoor, “AirSim: High-fidelity
visual and physical simulation for autonomous vehicles,” in Proc. 11th
Int. Conf. Field Service Robot., 2018, pp. 621–635.
[148] P. A. Lopez et al., “Microscopic traffic simulation using SUMO,”
in Proc. 21st Int. Conf. Intell. Transp. Syst. (ITSC), Nov. 2018,
pp. 2575–2582.
[149] T.-H. Wang, A. Amini, W. Schwarting, I. Gilitschenski, S. Karaman,
and D. Rus, “Learning interactive driving policies via data-driven
simulation,” in Proc. Int. Conf. Robot. Autom. (ICRA), May 2022,
pp. 7745–7752.
[150] F.-Y. Wang, “Parallel control and management for intelligent transportation systems: Concepts, architectures, and applications,” IEEE
Trans. Intell. Transp. Syst., vol. 11, no. 3, pp. 630–638, Sep. 2010.
[151] A. Amini et al., “VISTA 2.0: An open, data-driven simulator for
multimodal sensing and policy learning for autonomous vehicles,” in
Proc. Int. Conf. Robot. Autom. (ICRA), May 2022, pp. 2419–2426.
[152] Q. Sun, X. Huang, B. C. Williams, and H. Zhao, “InterSim: Interactive
traffic simulation via explicit relation modeling,” in Proc. IEEE/RSJ Int.
Conf. Intell. Robots Syst. (IROS), Oct. 2022, pp. 11416–11423.
[153] Z. Zhang, A. Liniger, D. Dai, F. Yu, and L. Van Gool, “TrafficBots:
Towards world models for autonomous driving simulation and motion
prediction,” in Proc. IEEE Int. Conf. Robot. Autom. (ICRA), May 2023,
pp. 1522–1529.
[154] D. Gopinath et al., “HMIway-env: A framework for simulating behaviors and preferences to support human-AI teaming in driving,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. Workshops (CVPRW),
Jun. 2022, pp. 4341–4349.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
22

[155] H. Sun, S. Feng, X. Yan, and H. X. Liu, “Corner case generation and
analysis for safety assessment of autonomous vehicles,” Transp. Res.
Rec., J. Transp. Res. Board, vol. 2675, no. 11, pp. 587–600, Nov. 2021.
[156] A. Kishore, T. E. Choe, J. Kwon, M. Park, P. Hao, and A. Mittel, “Synthetic data generation using imitation training,” in Proc.
IEEE/CVF Int. Conf. Comput. Vis. Workshops (ICCVW), Oct. 2021,
pp. 3071–3079.
[157] Z. Cao, K. Jiang, W. Zhou, S. Xu, H. Peng, and D. Yang, “Continuous
improvement of self-driving cars using dynamic confidence-aware reinforcement learning,” Nature Mach. Intell., vol. 5, no. 2, pp. 145–158,
Feb. 2023.
[158] H. Niu, J. Hu, Z. Cui, and Y. Zhang, “DR2L: Surfacing corner cases to
robustify autonomous driving via domain randomization reinforcement
learning,” in Proc. 5th Int. Conf. Comput. Sci. Appl. Eng., Oct. 2021,
pp. 1–8.
[159] L. Ma et al., “DeepGauge: Multi-granularity testing criteria for deep
learning systems,” in Proc. 33rd IEEE/ACM Int. Conf. Automated Softw.
Eng. (ASE), Sep. 2018, pp. 120–131.
[160] L. Ma et al., “DeepCT: Tomographic combinatorial testing for deep
learning systems,” in Proc. IEEE 26th Int. Conf. Softw. Anal., Evol.
Reengineering (SANER), Feb. 2019, pp. 614–618.
[161] H. Caesar et al., “NuScenes: A multimodal dataset for autonomous
driving,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2020, pp. 11618–11628.
[162] A. Geiger, P. Lenz, C. Stiller, and R. Urtasun, “Vision meets robotics:
The KITTI dataset,” Int. J. Robot. Res., vol. 32, no. 11, pp. 1231–1237,
Sep. 2013.
[163] P. Sun et al., “Scalability in perception for autonomous driving: Waymo
open dataset,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2020, pp. 2443–2451.
[164] J. Geyer et al., “A2D2: Audi autonomous driving dataset,” 2020,
arXiv:2004.06320.
[165] F. Yu et al., “BDD100K: A diverse driving dataset for heterogeneous
multitask learning,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2020, pp. 2636–2645.
[166] G. J. Brostow, J. Shotton, J. Fauqueur, and R. Cipolla, “Segmentation
and recognition using structure from motion point clouds,” in Proc.
Eur. Conf. Comput. Vis., 2008, pp. 44–57.
[167] D. Arya, H. Maeda, S. K. Ghosh, D. Toshniwal, and Y. Sekimoto,
“RDD2020: An annotated image dataset for automatic road damage
detection using deep learning,” Data Brief, vol. 36, Jun. 2021, Art. no.
107133.
[168] S. Malla, C. Choi, I. Dwivedi, J. Hee Choi, and J. Li, “DRAMA: Joint
risk localization and captioning in driving,” in Proc. IEEE/CVF Winter
Conf. Appl. Comput. Vis. (WACV), Jan. 2023, pp. 1043–1052.
[169] G. Neuhold, T. Ollmann, S. R. Bulo, and P. Kontschieder, “The
mapillary vistas dataset for semantic understanding of street scenes,” in
Proc. IEEE Int. Conf. Comput. Vis. (ICCV), Oct. 2017, pp. 5000–5009.
[170] G. Ros, L. Sellart, J. Materzynska, D. Vazquez, and A. M. Lopez,
“The SYNTHIA dataset: A large collection of synthetic images for
semantic segmentation of urban scenes,” in Proc. IEEE Conf. Comput.
Vis. Pattern Recognit. (CVPR), Jun. 2016, pp. 3234–3243.
[171] S. R. Richter, Z. Hayder, and V. Koltun, “Playing for benchmarks,” in
Proc. IEEE Int. Conf. Comput. Vis. (ICCV), Oct. 2017, pp. 2232–2241.
[172] X. Weng, Y. Man, D. Cheng, J. Park, M. O’Toole, and K. Kitani,
“All-in-one drive: A large-scale comprehensive perception
dataset with high-density long-range point clouds,” 2020,
doi: 10.13140/RG.2.2.21621.81122. [Online]. Available: https://
openreview.net/forum?id=yl9aThYT9W
[173] S. R. Richter, V. Vineet, S. Roth, and V. Koltun, “Playing for data:
Ground truth from computer games,” in Proc. Eur. Conf. Comput. Vis.,
2016, pp. 102–118.
[174] T. Sun et al., “SHIFT: A synthetic driving dataset for continuous multitask domain adaptation,” in Proc. IEEE Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2022, pp. 21371–21382.
[175] G. Franchi et al., “MUAD: Multiple uncertainties for autonomous
driving, a benchmark for multiple uncertainty types and tasks,” in Proc.
33rd Brit. Mach. Vis. Conf., 2022, pp. 1–11.
[176] W. Lu, Y. Zhou, G. Wan, S. Hou, and S. Song, “L3-Net: Towards
learning based LiDAR localization for autonomous driving,” in
Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun. 2019,
pp. 6389–6398.
[177] M. Cordts et al., “The cityscapes dataset for semantic urban scene
understanding,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2016, pp. 3213–3223.

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

[178] J. Mao et al., “One million scenes for autonomous driving: Once
dataset,” in Proc. Adv. Neural Inf. Process. Syst., vol. 1, 2021,
pp. 1–12.
[179] R. Chan et al., “SegmentMeIfYouCan: A benchmark for anomaly
segmentation,” in Proc. Adv. Neural Inf. Process. Syst., vol. 1, 2021,
pp. 1–8.
[180] P. Pinggera, S. Ramos, S. Gehrig, U. Franke, C. Rother, and R. Mester,
“Lost and found: Detecting small road hazards for self-driving
vehicles,” in Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS),
Oct. 2016, pp. 1099–1106.
[181] H. Blum, P.-E. Sarlin, J. Nieto, R. Siegwart, and C. Cadena,
“The fishyscapes benchmark: Measuring blind spots in semantic
segmentation,” Int. J. Comput. Vis., vol. 129, no. 11, pp. 3119–3135,
Nov. 2021.
[182] J. Fang, D. Yan, J. Qiao, J. Xue, and H. Yu, “DADA: Driver attention
prediction in driving accident scenarios,” IEEE Trans. Intell. Transp.
Syst., vol. 23, no. 6, pp. 4959–4971, Jun. 2022.
[183] A. Kerim, F. C. Chamone, W. L. S. Ramos, L. S. Marcolino,
E. R. Nascimento, and R. Jiang, “Semantic segmentation under
adverse conditions: A weather and nighttime-aware synthetic databased approach,” in Proc. 33rd Brit. Mach. Vis. Conf., 2022, pp. 1–12.
[184] T. Stauner et al., “SynPeDS: A synthetic dataset for pedestrian detection
in urban traffic scenes,” in Proc. 6th ACM Comput. Sci. Cars Symp.,
2022, pp. 1–7.
[185] G. Li, Z. Ji, X. Qu, R. Zhou, and D. Cao, “Cross-domain object
detection for autonomous driving: A stepwise domain adaptative YOLO
approach,” IEEE Trans. Intell. Vehicles, vol. 7, no. 3, pp. 603–615,
Sep. 2022.
[186] X. Hu, S. Li, T. Huang, B. Tang, R. Huai, and L. Chen, “How
simulation helps autonomous driving: A survey of sim2real, digital
twins, and parallel intelligence,” IEEE Trans. Intell. Vehicles, vol. 9,
no. 1, pp. 1–20, Jan. 2024.
[187] L. Gong et al., “SDAC: A multimodal synthetic dataset for anomaly
and corner case detection in autonomous driving,” in Proc. AAAI Conf.
Artif. Intell., 2024, vol. 38, no. 3, pp. 1914–1922.
[188] P. Ball, “Crowd-sourcing: Strength in numbers,” Nature, vol. 506,
no. 7489, pp. 422–423, Feb. 2014.
[189] Y. Liu, Z. Yu, B. Guo, Q. Han, J. Su, and J. Liao, “CrowdOS:
A ubiquitous operating system for crowdsourcing and mobile crowd
sensing,” IEEE Trans. Mobile Comput., vol. 21, no. 3, pp. 878–894,
Mar. 2022.
[190] V. Patil, W. Van Gansbeke, D. Dai, and L. Van Gool, “Don’t forget the
past: Recurrent depth estimation from monocular video,” IEEE Robot.
Autom. Lett., vol. 5, no. 4, pp. 6813–6820, Oct. 2020.
[191] K. Wang et al., “Regularizing nighttime weirdness: Efficient selfsupervised monocular depth estimation in the dark,” in Proc. IEEE/CVF
Int. Conf. Comput. Vis. (ICCV), Oct. 2021, pp. 16035–16044.
[192] F. Bao et al., “Heat-assisted detection and ranging,” Nature, vol. 619,
no. 7971, pp. 743–748, Jul. 2023.
[193] A. Seppänen, R. Ojala, and K. Tammi, “4DenoiseNet: Adverse weather
denoising from adjacent point clouds,” IEEE Robot. Autom. Lett.,
vol. 8, no. 1, pp. 456–463, Jan. 2023.
[194] R. Heinzler, F. Piewak, P. Schindler, and W. Stork, “CNN-based LiDAR
point cloud de-noising in adverse weather,” IEEE Robot. Autom. Lett.,
vol. 5, no. 2, pp. 2514–2521, Apr. 2020.
[195] X. Cheng, P. Wang, G. Chenye, and R. Yang, “CSPN++: Learning
context and resource aware convolutional spatial propagation networks
for depth completion,” in Proc. AAAI Conf. Artif. Intell., vol. 34, Apr.
2020, pp. 10615–10622.
[196] Y. Lin, T. Cheng, Q. Zhong, W. Zhou, and H. Yang, “Dynamic spatial
propagation network for depth completion,” in Proc. AAAI Conf. Artif.
Intell. (AAAI), 2022, pp. 1638–1646.
[197] J. Li, J. Chen, J. Liu, and H. Ma, “Learning a graph neural network
with cross modality interaction for image fusion,” in Proc. 31st ACM
Int. Conf. Multimedia, Oct. 2023, pp. 4471–4479.
[198] J. Nie, H. Sun, X. Sun, L. Ni, and L. Gao, “Cross-modal feature fusion
and interaction strategy for CNN-transformer-based object detection in
visual and infrared remote sensing imagery,” IEEE Geosci. Remote
Sens. Lett., vol. 21, pp. 1–5, 2024.
[199] Z. Xie et al., “Cross-modality double bidirectional interaction and
fusion network for RGB-T salient object detection,” IEEE Trans.
Circuits Syst. Video Technol., vol. 33, no. 8, pp. 4149–4163, Aug.
2023.
[200] Y. Tian et al., “ACF-Net: Asymmetric cascade fusion for 3D detection
with LiDAR point clouds and images,” IEEE Trans. Intell. Vehicles,
vol. 9, no. 2, pp. 3360–3371, Feb. 2024.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIANG et al.: CORNER CASE DETECTION AND GENERATION FOR AUTONOMOUS DRIVING: AN OVERVIEW

[201] A. Prakash, K. Chitta, and A. Geiger, “Multi-modal fusion transformer
for end-to-end autonomous driving,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit. (CVPR), Jun. 2021, pp. 7073–7083.
[202] Y. Liang et al., “Learning cross-modality interaction for robust depth
perception of autonomous driving,” ACM Trans. Intell. Syst. Technol.,
vol. 15, no. 3, pp. 1–26, Jun. 2024, doi: 10.1145/3650039.
[203] Y. Man, L.-Y. Gui, and Y.-X. Wang, “BEV-guided multi-modality
fusion for driving perception,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit. (CVPR), Jun. 2023, pp. 21960–21969.
[204] Z. Liu et al., “BEVFusion: Multi-task multi-sensor fusion with unified
bird’s-eye view representation,” in Proc. IEEE Int. Conf. Robot. Autom.
(ICRA), May 2023, pp. 2774–2781.
[205] A. W. Harley, Z. Fang, J. Li, R. Ambrus, and K. Fragkiadaki,
“Simple-BEV: What really matters for multi-sensor BEV perception?”
in Proc. IEEE Int. Conf. Robot. Autom. (ICRA), May 2023,
pp. 2759–2765.
[206] Z. Li et al., “Bevformer: Learning bird’s-eye-view representation from
multi-camera images via spatiotemporal transformers,” in Proc. 17th
Eur. Conf. Comput. Vis. (ECCV), 2022, pp. 1–18.
[207] Z. Xue, M. Guo, H. Fan, S. Zhang, and Z. Zhang, “CorrBEV: Multiview 3D object detection by correlation learning with multi-modal
prototypes,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2025, pp. 27413–27423.
[208] P. Hu et al., “T-READi: Transformer-powered robust and efficient
multimodal inference for autonomous driving,” IEEE Trans. Mobile
Comput., vol. 24, no. 1, pp. 135–149, Jan. 2025.
[209] Y. Liu, D. Liao, M. Qi, L. Liu, and H. Ma, “RoboFormer: A
robust multi-modal transformer for 3D object detection in autonomous
driving,” in Proc. 6th ACM Int. Conf. Multimedia Asia, Dec. 2024,
pp. 1–7.
[210] X. Chen, S. Zhang, J. Li, and J. Yang, “Pedestrian crossing intention
prediction based on cross-modal transformer and uncertainty-aware
multi-task learning for autonomous driving,” IEEE Trans. Intell.
Transp. Syst., vol. 25, no. 9, pp. 12538–12549, Sep. 2024.
[211] R. Chen, W. Shao, B. Zhang, S. Shi, L. Jiang, and P. Luo, “JiSAM:
Alleviate labeling burden and corner case problems in autonomous
driving via minimal real-world data,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2025, pp. 6792–6801.
[212] G. Bernardino et al., “Reinforcement learning for active modality
selection during diagnosis,” in Proc. Int. Conf. Med. Image Comput.
Comput.-Assist. Intervent., 2022, pp. 592–601.
[213] M. Yang, Y. Chen, and H.-S. Kim, “Efficient deep visual and inertial
odometry with adaptive visual modality selection,” in Proc. Eur. Conf.
Comput. Vis. (ECCV), 2022, pp. 233–250.
[214] B. Xu et al., “Different data, different modalities! Reinforced data
splitting for effective multimodal information extraction from social
media posts,” in Proc. 29th Int. Conf. Comput. Linguistics, Oct. 2022,
pp. 1855–1864.
[215] S. He, K. Shi, C. Liu, B. Guo, J. Chen, and Z. Shi, “Collaborative sensing in Internet of Things: A comprehensive survey,” IEEE Commun.
Surveys Tuts., vol. 24, no. 3, pp. 1435–1474, Jul. 2022.
[216] Y. Liang, X. Wang, Z. Yu, B. Guo, X. Zheng, and S. Samtani,
“Energy-efficient collaborative sensing: Learning the latent correlations
of heterogeneous sensors,” ACM Trans. Sensor Netw., vol. 17, no. 3,
pp. 1–28, Jun. 2021.
[217] S. Ansari, F. Naghdy, and H. Du, “Human-machine shared driving:
Challenges and future directions,” IEEE Trans. Intell. Vehicles, vol. 7,
no. 3, pp. 499–519, Sep. 2022.
[218] G. Kaljavesi, X. Su, and F. Diermeyer, “Integrating end-to-end and
modular driving approaches for online corner case detection in
autonomous driving,” in Proc. IEEE Int. Conf. Syst., Man, Cybern.
(SMC), Oct. 2024, pp. 1017–1023.
[219] Z. Yang et al., “A vision chip with complementary pathways for
open-world sensing,” Nature, vol. 629, no. 8014, pp. 1027–1033,
May 2024.
[220] C. Schicktanz and K. Gimm, “Detection and analysis of corner case
scenarios at a signalized urban intersection,” Accident Anal. Prevention,
vol. 210, Feb. 2025, Art. no. 107838.
[221] B. Fan, Z. Su, Y. Chen, Y. Wu, C. Xu, and T. Q. S. Quek, “Ubiquitous
control over heterogeneous vehicles: A digital twin empowered edge
AI approach,” IEEE Wireless Commun., vol. 30, no. 1, pp. 166–173,
Feb. 2023.
[222] T. Zheng, A. Li, Z. Chen, H. Wang, and J. Luo, “AutoFed:
Heterogeneity-aware federated multimodal learning for robust
autonomous driving,” in Proc. 29th Annu. Int. Conf. Mobile Comput.
Netw., 2023, pp. 1–11.

23

[223] F. Mohseni, E. Frisk, and L. Nielsen, “Distributed cooperative MPC for
autonomous driving in different traffic scenarios,” IEEE Trans. Intell.
Vehicles, vol. 6, no. 2, pp. 299–309, Jun. 2021.
[224] P. Hang, C. Lv, C. Huang, Y. Xing, and Z. Hu, “Cooperative decision
making of connected automated vehicles at multi-lane merging zone: A
coalitional game approach,” IEEE Trans. Intell. Transp. Syst., vol. 23,
no. 4, pp. 3829–3841, Apr. 2022.
[225] H. Bilal et al., “Hybrid TrafficAI: A generative AI framework for
real-time traffic simulation and adaptive behavior modeling,” IEEE
Trans. Intell. Transp. Syst., early access, Jun. 2, 2025, doi: 10.1109/
TITS.2025.3571041.
[226] S. Lee, J. Yoon, H. Kim, J. Kim, and B. Kim, “Ego vehicle speed
estimation with automotive corner radar under velocity ambiguity using
optimized MobileNetV3,” IEEE Access, vol. 13, pp. 117404–117419,
2025.
[227] R. Ding, J. Yang, L. Jiang, and X. Qi, “DODA: Data-oriented sim-toreal domain adaptation for 3D semantic segmentation,” in Proc. 17th
Eur. Conf. Comput. Vis. (ECCV), Oct. 2022, pp. 284–303.
[228] E. Alberti, A. Tavera, C. Masone, and B. Caputo, “IDDA: A large-scale
multi-domain dataset for autonomous driving,” IEEE Robot. Autom.
Lett., vol. 5, no. 4, pp. 5526–5533, Oct. 2020.
[229] X. Yang et al., “DriveArena: A closed-loop generative simulation
platform for autonomous driving,” in Proc. IEEE/CVF Int. Conf.
Comput. Vis., Sep. 2025, pp. 26933–26943.
[230] O. Gafni, A. Polyak, O. Ashual, S. Sheynin, D. Parikh, and Y. Taigman,
“Make-a-scene: Scene-based text-to-image generation with human
priors,” in Proc. 17th Eur. Conf. Comput. Vis., 2022, pp. 89–106.
[231] Y. Li et al., “GLIGEN: Open-set grounded text-to-image generation,”
in Proc. IEEE Comput. Soc. Conf. Comput. Vis. Pattern Recognit., Jan.
2023, pp. 22511–22521.
[232] L. Zhou, M. Jiang, and D. Wang, “HumanSim: Human-like multi-agent
novel driving simulation for corner case generation,” in Proc. Eur. Conf.
Comput. Vis., 2024, pp. 287–304.
[233] K. Arndt, M. Hazara, A. Ghadirzadeh, and V. Kyrki, “Meta reinforcement learning for sim-to-real domain adaptation,” in Proc. IEEE Int.
Conf. Robot. Autom. (ICRA), May 2020, pp. 2725–2731.
[234] J. Xu et al., “Regressing simulation to real: Unsupervised domain
adaptation for automated quality assessment in transoesophageal
echocardiography,” in Proc. Int. Conf. Med. Image Comput. Comput.Assist. Intervent., 2023, pp. 154–164.
[235] J. Roh, C. Paxton, A. Pronobis, A. Farhadi, and D. Fox, “Conditional
driving from natural language instructions,” in Proc. Conf. Robot
Learn., vol. 100, Nov. 2020, pp. 540–551.
[236] C. Cui, Y. Ma, X. Cao, W. Ye, and Z. Wang, “Drive as you
speak: Enabling human-like interaction with large language models in
autonomous vehicles,” in Proc. IEEE/CVF Winter Conf. Appl. Comput.
Vis. Workshops (WACVW), Jan. 2024, pp. 902–909.
[237] Y. Yang, Q. Zhang, C. Li, D. S. Marta, N. Batool, and J. Folkesson,
“Human-centric autonomous systems with LLMs for user command
reasoning,” in Proc. IEEE/CVF Winter Conf. Appl. Comput. Vis.
Workshops (WACVW), Jan. 2024, pp. 988–994.
[238] Y. Cui et al., “DriveLLM: Charting the path toward full autonomous
driving with large language models,” IEEE Trans. Intell. Vehicles,
vol. 9, no. 1, pp. 1450–1464, Jan. 2024.
[239] E. Aasi, P. Nguyen, S. Sreeram, G. Rosman, S. Karaman, and
D. Rus, “Generating out-of-distribution scenarios using language
models,” in Proc. IEEE Int. Conf. Robot. Autom. (ICRA), May 2025,
pp. 10616–10623.
[240] L. Wen et al., “DiLu: A knowledge-driven approach to autonomous
driving with large language models,” in Proc. 11th Int. Conf. Learn.
Represent., 2024, pp. 1–12.
[241] D. Fu et al., “Drive like a human: Rethinking autonomous driving with
large language models,” 2023, arXiv:2307.07162.
[242] Y. Deng et al., “TARGET: Traffic rule-based test generation for
autonomous driving systems,” IEEE Trans. Softw. Eng., vol. 51, no. 7,
pp. 1950–1968, Jul. 2025.
[243] D. Pei et al., “Methodology and benchmark for automated driving
theory test of large language models,” IEEE Trans. Intell. Transp. Syst.,
vol. 26, no. 10, pp. 17013–17026, Oct. 2025.
[244] C. Cui et al., “A survey on multimodal large language models for
autonomous driving,” in Proc. IEEE/CVF Winter Conf. Appl. Comput.
Vis. (WACV) Workshops, Jan. 2024, pp. 958–979.
[245] Z. Yang, X. Jia, H. Li, and J. Yan, “LLM4Drive: A survey of large
language models for autonomous driving,” 2023, arXiv:2311.01043.
[246] W. Wang et al., “VisionLLM: Large language model is also an openended decoder for vision-centric tasks,” 2023, arXiv:2305.11175.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
24

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

[247] H. Liu, C. Li, Q. Wu, and Y. J. Lee, “Visual instruction tuning,” in
Proc. Adv. Neural Inf. Process. Syst., vol. 36, 2023, pp. 34892–34916.
[248] K. Chen et al., “Automated evaluation of large vision-language models
on self-driving corner cases,” in Proc. IEEE/CVF Winter Conf. Appl.
Comput. Vis. (WACV), Feb. 2025, pp. 7817–7826.
[249] T. Liu, Y. Qin, S. Zhang, and X. Tao, “Empowering corner case
detection in autonomous vehicles with multimodal large language
models,” IEEE Signal Process. Lett., vol. 32, pp. 51–55, 2025.
[250] M. Mo et al., “NexusAD: Exploring the Nexus for multimodal perception and comprehension of corner cases in autonomous driving,” in
Proc. Eur. Conf. Comput. Vis., 2024, pp. 1–17.

Yunji Liang received the Ph.D. degree in computer
science from Northwestern Polytechnical University,
Xi’an, China, in 2016. From 2012 to 2017, he was
with The University of Arizona, Tucson, AZ, USA,
as a Visiting Scholar and a Post-Doctoral Researcher,
respectively. He is currently an Associate Professor with Northwestern Polytechnical University. His
research interests include pervasive computing, the
Internet of Things, and mobile computing.

Junteng Liu is currently pursuing the master’s
degree with Northwestern Polytechnical University, Xi’an, China. His research interests include
autonomous driving and the Internet of Things.

Xiaokai Yan is currently pursuing the master’s
degree with Northwestern Polytechnical University,
Xi’an, China. His research interests include pervasive computing, social computing, and data mining.

Xiaolong Zheng (Member, IEEE) received the B.S.
degree from China Jiliang University in 2003, the
M.S. degree from Beijing Jiaotong University in
2006, and the Ph.D. degree from the Institute of
Automation, Chinese Academy of Sciences, in 2009.
He is currently a Professor with the Institute of
Automation, Chinese Academy of Sciences. He
has published more than 120 peer-to-peer academic
papers in journals/magazines and conferences. His
research interests include social computing, big data
analytics, knowledge graphs, financial technologies,
and complex system intelligence. He has served as the program co-chair for
six international conferences and a technical program committee member for
more than 40 international conferences.

Lei Tang (Member, IEEE) received the Ph.D. degree
in computer science and technology from Northwestern Polytechnical University in 2012. From
2009 to 2010, she was a Visiting Researcher with
the Chair of Information Systems, Mannheim University, Germany. She is currently working with
the School of Information Engineering, Chang’an
University, China. Her research interests include
the area of intelligent transportation systems and
network representation. She is a member of ACM,
China Computer Federation (CCF), and Pervasive
Computing Technical Committee. She received the Distinguished Young
Scholars Award from the Universities of Shaanxi.

Luwen Huangfu received the B.S. degree in
software engineering from Chongqing University,
Chongqing, China, the M.S. degree in computer
science from Chinese Academy of Sciences, Beijing,
China, and the Ph.D. degree in management information systems from The University of Arizona,
Tucson, AZ, USA. She is currently an Assistant
Professor with the Fowler College of Business, San
Diego State University, San Diego, CA, USA, where
she is also with the Center for Human Dynamics
in the Mobile Age. Her research interests include
business analytics, text mining, data mining, software management, computer
vision, artificial intelligence, and healthcare management.

Sagar Samtani (Member, IEEE) received the Ph.D.
degree from The University of Arizona. He is currently an Assistant Professor in information systems
and a Weimer Faculty Fellow with the Kelley School
of Business. He is also the Executive Founding
Director of the Kelley’s Data Science and Artificial
Intelligence Laboratory. He has published over 85
papers on topics related to cyber threat intelligence,
cybersecurity, artificial intelligence, health informatics, and business intelligence.

Zhiwen Yu (Senior Member, IEEE) received the
Ph.D. degree from Northwestern Polytechnical University, Xi’an, China, in 2005. He is currently a Professor with Northwestern Polytechnical University.
His current research interests include the Internet
of Things, pervasive computing, human–machine
systems, mobile computing, and crowd sensing. He
is also an Associate Editor or an Editorial Board
Member of IEEE T RANSACTIONS ON H UMAN M ACHINE S YSTEMS, IEEE Communications Magazine, and Personal and Ubiquitous Computing
(ACM/Springer).
PAPER_TEXT
