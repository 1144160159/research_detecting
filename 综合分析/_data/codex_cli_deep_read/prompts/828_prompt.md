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
# [828] Towards Semantic-aware Aerial Video Anomaly Detection by Exploiting Multimodal Large Language Model
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
编号：828
题名：Towards Semantic-aware Aerial Video Anomaly Detection by Exploiting Multimodal Large Language Model
年份：2026
DOI：10.1109/tcsvt.2026.3686230
来源：IEEE Transactions on Circuits and Systems for Video Technology
PDF：paper/10.1109_TCSVT.2026.3686230.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：入侵检测与网络异常检测、其他AI安全与跨域异常检测
相关性：中相关，分数 5
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\828.txt
- 原始字符数：100911
- 本次发送字符数：100911
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. X, NO. X, X 2025

1

Towards Semantic-aware Aerial Video Anomaly
Detection by Exploiting Multimodal Large
Language Model
Ruoheng Li, Xuhui Liu, Yutao Hu, Xi Zhu, and Xianbin Cao, Senior Member, IEEE

Abstract—Drones have become increasingly widely applied
in surveillance systems due to their mobility, making aerial
video anomaly detection methods more crucial. Anomalies
in aerial videos often present as semantic conflicts, such
as the presence of unexpected objects or unusual behaviors
that do not align with the context. Previous approaches
often relied on manually crafted knowledge graphs to detect
such conflicts, which suffer from poor scalability. Recently,
owing to their sufficient alignment training, multimodal large
language models (MLLMs) have emerged as a generalized
solution for semantic understanding. However, the direct
application of MLLMs does not yield satisfactory anomaly
detection performance in aerial videos. First, aerial videos
often manifest platform-induced pseudo-motion, which obscures the true motion of objects and exacerbates detection
errors. Second, without sufficient labeled data for fine-tuning,
generic MLLMs often lack scene-level semantic guidance to
reliably distinguish abnormal events that include contextually
inappropriate behaviors. To address these challenges, we
propose SemAero, an MLLM-based framework to address
these challenges by: 1) designing an ego-motion reduction
module to enhance model perception on object movement,
2) generating scene-specific prompts adaptively with step-bystep guidance for reasonable output, and 3) refining scores
with dual-stream consistent feature for better domain-specific
anomaly detection. Evaluated across 8 diverse aerial scenes
and 73 sub-datasets, SemAero achieves a 3.09% improvement
in AUC-ROC over the second-best model, demonstrating its
ability in aerial video anomaly detection.
Index Terms—Aerial video, Anomaly detection, Multimodal
large language model, Anomaly understanding

GT: Abnormal (1)
Q: Is there any vehicle stopped on the road
and blocking the traffic?
A: No, all vehicles
Output: Normal (0).

are

moving

smoothly.

(a) Challenges in motion perception due to platforminduced motion

GT: Abnormal (1)
Q: Is there an anomaly in this video?
A: The traffic flow appears normal, and there are
no unusual events observed. Output: Normal (0).

(b) Detection failures caused by insufficient domain
knowledge
Fig. 1. Challenges in aerial video anomaly detection using multimodal
large language models: InternVL2-8B [5] (a) failed to detect stopped
vehicles due to platform-induced motion in aerial videos, and (b) were
unable to identify a bus in a non-motor vehicle area due to insufficient
logical guidance in system prompt design.

I. I NTRODUCTION

V

Ideo anomaly detection identifies behaviors or events
that deviate from the norm, such as unauthorized
access, unusual parking, or illegal activities, with essential
applications in intelligent surveillance systems [1], [2].
Traditional surveillance systems typically rely on groundbased cameras, which offer fixed viewpoints and limited
Manuscript received xx xx 2025; revised xx xx xxxx; accepted xx
xx xxxx. This work is supported by National Key Research and Development Program of China under Grant No. 2024YFE0217600 and
National Natural Science Foundation of China under Grant No.62501140.
(Corresponding author: Xi Zhu.)
Ruoheng Li, Xi Zhu, and Xianbin Cao are with the School of Electronic and Information Engineering, Beihang University, Beijing 100191,
China, and also with the MIIT Key Laboratory of Aerospace Mobile
Communications, Beijing 100191, China (e-mail: ruohengli@buaa.edu.cn,
zhuxi@buaa.edu.cn, xbcao@buaa.edu.cn).
Xuhui Liu is with the School of Automation Science and Electrical Engineering, Beihang University, Beijing 100191, China(e-mail:
xhliu.comp@gmail.com).
Yutao Hu is with the School of Computer Science and Engineering,
Southeast University, Nanjing 210096, China, and also with the Key
Laboratory of New Generation Artificial Intelligence Technology and Its
Interdisciplinary Applications, Ministry of Education, Southeast University, Nanjing 210096, China (e-mail: huyutao@seu.edu.cn).

flexibility for large-scale monitoring. Drones, with their
mobility and maneuverability, provide a valuable complement to modern surveillance systems [3] [4].
Most existing aerial video anomaly detection methods
follow a self-supervised paradigm [4], [6], [7], where
anomalies are identified as deviations from learned normal
patterns [8], [9], [10]. However, such methods are often
less capable of handling anomalies with semantic conflicts,
such as a complete object appearing in an inappropriate
region [11], [12]. Some earlier studies attempted to encode
semantics through knowledge graphs to detect anomalies
[11], [13], [14], which are effective but labor-intensive to
generalize across diverse aerial scenarios.
Recent Multimodal Large Language Models (MLLMs)
and Vision-Language Models (VLMs) provide powerful
semantic reasoning capabilities, and have recently been
introduced into video anomaly detection tasks through
knowledge graph [12], knowledge sharing [15], and semantic alignment mechanisms [16]. However, these advances
are not directly applicable to aerial anomaly detection,

Copyright © 2026 IEEE. Personal use of this material is permitted.
However, permission to use this material for any other purposes must be obtained
from
the IEEE
by text
sending
anmining
emailand
to training
pubs-permissions@ieee.org.
© 2026 IEEE. All rights reserved,
including
rights for
and data
of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

2

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. X, NO. X, X 2025

since most existing methods are developed under relatively
stable viewpoints and do not explicitly address the pseudomotion caused by moving aerial platforms. As shown in
Figure 1(a), camera motion may cause stationary vehicles to appear as moving, which can mislead MLLMs to
misinterpret congested traffic as normal flow. In addition,
aerial anomaly detection is highly scene-dependent and
often requires domain-specific reasoning ability. As is
illustrated in Figure 1(b), an abnormal event such as a bus
appearing in a non-vehicle area may be overlooked without
explicit contextual guidance. Although approaches such as
Parameter-Efficient Fine-Tuning (PEFT) [17] can partially
address this issue, they typically rely on large annotated
datasets, which are expensive and difficult to obtain.
To address these challenges, we propose SemAero, an
MLLM-based framework for aerial video anomaly detection without task-specific fine-tuning. Unlike conventional
baselines that primarily detect appearance deviations, SemAero integrates semantic reasoning with motion-aware
anomaly discrimination in a unified framework. It is also
distinct from existing VLM- and MLLM-based methods in
that it does not rely on task-specific fine-tuning to acquire
domain-specific knowledge, empowered by scene-specific
prompts and normal motion anchors to obtain the contextual awareness. Specifically, SemAero incorporates an
adaptive ego-motion reduction module to suppress camerainduced motion and reveal true object dynamics. It further
employs scene-specific prompt generation with Chain-ofThought reasoning to provide contextual semantic guidance
without fine-tuning. Finally, a dual-stream consistencyguided module leverages normal feature anchors to refine
anomaly discrimination. Through this design, SemAero
enables more reliable detection of semantic anomalies in
dynamic aerial scenes.
Our contributions are summarized as follows:
1) We propose SemAero, a MLLM-based framework
for semantic-aware aerial video anomaly detection
without further fine-tuning. SemAero achieves good
domain-specific detection performance without reliance on large annotated datasets.
2) We introduce an ego-motion reduction module to
dynamically estimate and mitigate platform-induced
motion, ensuring the model has more accurate perception of object behaviors in aerial videos.
3) We develop a scene-adaptive prompts generation
mechanism using GPT-4o, with Chain-of-thought
(CoT) reasoning to ensure consistent and robust
anomaly detection across diverse contexts.
4) We validate SemAero through extensive experiments
across eight diverse scenes and 73 sub-datasets,
achieving an average performance improvement of
3.09% in anomaly detection accuracy compared to
the state-of-the-art methods.
The rest of this paper is organized as follows. We review
related work in Section II and introduce the proposed
SemAero in Section III. We present the experiments results
to demonstrate the effectiveness of SemAero in Section IV,
and conclude with limitation and future work in Section V.

II. R ELATED W ORK
A. Research on Video Anomaly Detection
Video anomaly detection methods can generally be categorized into unsupervised, weakly supervised, and fully
supervised settings. In particular, self-supervised learning has become an important paradigm for unsupervised
video anomaly detection. These methods typically learn
normality-aware representations from anomaly-free data
through auxiliary tasks, such as prediction or reconstruction
[18]. During inference, samples that deviate from the
learned normal patterns are regarded as anomalies. Selfsupervised methods are particularly valuable when anomalous samples are scarce or unavailable. To strengthen normality modeling in this setting, Chang et al. [19] introduced
an elegant clustering-driven framework together with a
highly effective spatio-temporal dissociation strategy [20],
substantially enhancing the pattern representation capacity
of self-supervised methods.
Weakly-supervised methods utilize video-level anomaly
labels, often formulated as the Multiple Instance Learning
(MIL) problem [21], [22]. By maximizing the confidence
difference between normal and abnormal instances, these
approaches enhance detection performance while requiring less precise annotations than fully-supervised methods. Fully-supervised methods rely on precise frame-level
anomaly labels for training, achieving high accuracy when
abnormal behaviors are well-defined [14]. However, their
dependence on high-quality labeled data poses a significant
challenge in real-world applications.
Beyond conventional experimental settings, recent research has increasingly turned to open-set video anomaly
detection to address unseen anomaly categories in complex
real-world scenes [23]. To support semantic understanding,
some recent approaches incorporate VLMs and LLMs to
exploit rich language priors [24], [25]. With text-driven
prompts and reasoning capabilities, these methods provide
a promising direction for zero-shot detection.
B. Research on Aerial Video Anomaly Detection
Current research on aerial video anomaly detection predominantly employs self-supervised learning approaches
[7], formulating the task as prediction [6], [4], reconstruction [8], or one-class learning [9], [10]. These methods
identify anomalies by detecting frames that significantly
deviate from a learned normal pattern. However, they often
fail to capture scene context, limiting their ability to detect
anomalies involving semantic conflicts, such as unexpected
objects or behaviors in specific scenarios.
To address this limitation, subsequent studies [11], [14],
[8] have integrated knowledge-based or ontology-driven
approaches with object detection to identify semantically
conflicting anomalies. Despite these advancements, such
methods rely heavily on rule-based frameworks, which
struggle to generalize across diverse scenes due to their
inherent rigidity. Biswas et al. pioneered the use of visionlanguage models for aerial video anomaly detection [27],
leveraging multimodal capabilities to enhance performance.
However, their approach, MMVAD, falls short in addressing platform-induced dynamic motion and depends on
coarse labels for contrastive training. These shortcomings

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

LI et al.:TOWARDS SEMANTIC-AWARE AERIAL VIDEO ANOMALY DETECTION BY EXPLOITING MULTIMODAL LARGE LANGUAGE MODEL

Initial score 𝒔𝑰𝒊

Stabilized frames and prompt

Pretrained
MLLM

…

Prompts for user prompts generation
{Scene}-Specific Prompts Generation

Farmland

❄

- Reasoning: Buses are not
supposed to be in the bike
roundabout.
- Conclusion: Yes, there is an
object (bus) illegally using
the bike roundabout.
Class Label:
Based on the observations, the
class label is 1.

❄

…

𝒔𝒔𝒊 =∑𝒋∈𝒕𝒐𝒑𝒌𝒔 𝐬𝐢𝐦𝒔𝒊𝒋 & 𝒔𝑰𝒋
𝒊

-

-

…

Motion feature deviation
from normal anchors

𝒎
𝒔𝒎
𝒊 = ∑𝒂∈𝒕𝒐𝒑𝒌𝒎 𝒅𝒊,𝒂
𝒊

3) Temporal-consistent score aggregation
Gaussian kernel
𝒇

𝒔𝒊 = 𝒔𝒔𝒊 + 𝒔𝒎
𝒊

Original data

Temporal smoothing

Patches

…

(1) Semantic feature

Optical features

…

…

Dual-steam feature extraction:

Smoothed data

RAFT

…

…

𝒅𝒎
𝒊,𝟏
𝒅𝒎
𝒊,𝟐
𝒅𝒎
𝒊,𝟑
𝒎
𝒅𝒊,𝒌

Euclidean

❄

…

Imagebind

Semantic feature
between test frames

𝒔𝒊𝒎𝟏𝒔
𝒔𝒊𝒎𝟐𝒔
𝒔𝒊𝒎𝟑𝒔
𝒔𝒊𝒎𝒔𝒌

e

2) Motion-consistent score refinement

Aggregated score

User prompt with CoT guidance

…

sin
co

…

Vehicle roundabout

❄

Answer to prompts, e.g.
- Observation: The red bus is
seen moving...

…

Bike roundabout

Text encoder

Scenario labels

(ii) Prompt Generation and Formalization

(iv) Dual-stream Consistencyguided Score Refinement
1) Semantic-consistency score aggregation

Large Language Model

Motion compensation

❄

Visual encoder

Motion smoothing

Frame Sampling

Motion estimation

(iii) Anomaly Inference

…

(i) Ego-motion Reduction

Video frames

3

Hierarchical
statistics

(2) Hierarchical motion feature

Fig. 2. The overall model framework of SemAero. Raw frames are first stabilized and sampled through the (i) ego-motion reduction module. With
prompts generated by the (ii) prompt generation and formalization module, the MLLM produces the anomaly inference and initial anomaly score sI .
f
The initial scores are then refined by the semantics consistency simsij and distance with normal motion features dm
i,a , resulting in the fused score si ,
which is then smoothed by a Gaussian kernel to ensure temporal consistency [26].

underscore the need for a more generalized approach that
effectively handles semantic-aware conflict detection while
mitigating the challenges posed by platform motion.
C. Research on Semantic-aware Anomaly Detection and
Video Understanding
Early semantic-aware video anomaly detection methods
often relied on rule-based approaches to identify anomalies
[28], [29], which relied heavily on labeled data and suffered
from limited scalability. Recently, the emergence of visionlanguage models [30] and large language models, has
opened a new stage for semantic-aware anomaly analysis [31], [32], [33]. Such pre-trained models leverage
large-scale aligned image-text data to learn shared embeddings [34], enabling textual descriptions to directly support
anomaly detection [35], [24]. However, these approaches
often still require labeled data to achieve sufficiently discriminative capability, which limits their applicability in
data-scarce scenarios.
Some semantic-aware methods adopt a staged pipeline
that separates visual observation from anomaly reasoning.
For example, LAVAD [25] first uses a captioning model
[36] to convert video content into textual descriptions, and
then relies on a large language model to infer whether
anomalies are present based on the generated texts [37],
[31], [27]. This design has shown promising results in
anomaly detection settings. However, missing details or
descriptions in the first stage may directly affect the
reasoning in the second stage. In contrast, MLLMs, such
as Video-LLaVA and InternVL, integrates observation and
reasoning in a end-to-end manner [17], [26], [38]. For
example, VERA [26] leverages MLLM to produce anomaly
scores and interpretable explanations for video segments in

an integrated way through verbalized learning.
Beyond anomaly detection, cross-modal modeling has
evolved into a highly versatile paradigm for complex
visual understanding. Notably, recent extensions to 3D
scene understanding [39] and autonomous-driving navigation [40] are particularly impressive, as they push crossmodal reasoning into structurally rich and safety-critical
environments. A series of downstream studies also report
strong and consistent gains in few-shot action recognition
[41], [42], event localization [43], zero-shot generalization
[44], and robust gaze estimation [45], highlighting both the
breadth and robustness of cross-modal transfer.
In summary, video anomaly detection has gradually
evolved from coarse anomaly localization toward more
comprehensive anomaly understanding [33]. Unlike conventional anomaly detection, anomaly understanding requires not only identifying whether an event is abnormal, but also explaining why it is abnormal in a scene
context. Nevertheless, research on aerial video anomaly
detection remains limited. Compared with ground-view
videos, aerial videos present unique challenges, including
platform-induced pseudo-motion, complex scene dynamics,
and subtle object behaviors. These characteristics often lead
existing MLLMs to produce hallucinated or overly generic
responses and weaken their ability to identify motionrelated anomalies. Therefore, there remains a strong need
for specialized semantic-aware frameworks tailored to the
unique characteristics of aerial videos.
III. M ETHOD
A. Problem Formulation and Model Framework
Let V = {It }Tt=1 denote a video sequence of T frames.
We consider an offline video anomaly detection setting,

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

4

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. X, NO. X, X 2025

Video frames

Homography matrix

Inliers
sufficient?

Initialize the reference frame

Yes

Scene
change?

Yes

Change the
reference frame

Matrix
decomposition

No

Identity
matrix

Smoothed matrix

Apply homography
transformation
Crop region calculation

No

Feature matching with SIFT
Homography matrix estimation
with RANSAC

Kalman Filter
Smoothed matrix

Motion estimation

Fig. 3.

Motion smoothing

Crop image
Resize image
Motion compensation

Procedure of ego-motion reduction.

where the full video is accessible during inference. The
video is divided into overlapping temporal windows of
fixed length w with stride δ, with window centers defined
as C = {δ, 2δ, . . . , ⌊T /δ⌋ · δ}. For each center c ∈ C, the
corresponding temporal window is denoted by Wc . Our
goal is to generate frame-level anomaly scores for the input
video. Specifically, a pretrained MLLM first produces an
initial anomaly score ScI associated with the center frame c,
which are subsequently refined by the temporal smoothing
module to obtain the final frame-level anomaly scores.
As illustrated in Figure 2, the proposed framework consists of four components: Ego-motion Reduction, Prompt
Generation and Formalization, Anomaly Inference, and
Dual-stream Consistency-guided Score Refinement. For
each detection window, the raw video frames are first stabilized to mitigate platform-induced camera motion. A scenespecific prompt is then constructed, and CoT reasoning
is incorporated to guide inference. The stabilized video
frames together with the generated prompts are fed into a
frozen pre-trained MLLM to produce initial anomaly scores
and textual rationales. The initial scores are subsequently
refined by a dual-stream consistency-guided module using
semantic and motion cues, followed by Gaussian temporal
smoothing to obtain temporally stable anomaly estimates.
The proposed framework does not perform task-specific
fine-tuning on the MLLM backbone. Instead, it uses normal
training videos for motion-anchor construction and scenecategory information for scene-specific prompt generation
({SCENE}). These inputs are used only for inference-time
support and do not update any model parameters.
B. Ego-motion Reduction
Videos captured from moving aerial platforms suffer
from undesired platform-induced motion, which confounds
the real motion of objects. We therefore design an egomotion reduction module to eliminate the induced effect.
The procedure of Ego-motion Reduction module is illustrated in Figure 3, consisting of three steps include motion
estimation, motion smoothing, and motion reduction.
1) Motion Estimation: A reference frame Ir should
be selected and updated adaptively for motion reduction.
To determine whether an update of the reference frame
is required, the normalized mean absolute difference of
grayscale intensity between the current frame It and the
reference frame Ir is computed:
dt =

W X
H
X

| I˜r (x, y) − I˜t (x, y) |
1
,
H · W x=1 y=1
255

(1)

where I˜r (x, y) and I˜t (x, y) denote the grayscale versions
of the reference and current frames, and H and W are the
frame height and width. The reference frame is updated
from Ir to It whenever dt > τs , with τs being a predefined
threshold for scene change.
Given the reference frame Ir and current frame It , Scale
Invariant Feature Transform (SIFT) keypoints are extracted
and matched [46]. Random Sample Consensus (RANSAC)
is then applied to robustly estimate the homography transformation from current frame to the reference frame:
X
2
Ht,r = arg min
∥H · pt,n − pr,n ∥ ,
(2)
H

n∈I

where pt,n ∈ R3 , pr,n ∈ R3 are matched keypoints in homogeneous coordinates and I denotes the RANSAC inlier
set. The ego-motion correction for frame It is discarded if
the proportion of matched points that are outliers exceeds
a reliability threshold ζ.
2) Motion Smoothing: Homography matrices estimated
from keypoint matching often exhibit noise due to mismatches or environmental factors. To address this issue, a
Kalman filter is used to smooth the homography parameters
over time, under the assumption of limited acceleration
of the platform. The homography matrix from frame t to
reference frame r is given by:


h11 h12 h13


(3)
Ht,r = h21 h22 h23  ,
h31 h32
1
where (h13 , h23 ) denote translation, and the linear terms
h11 , h12 , h21 , h22 , h31 , h32 jointly encode rotation, scaling,
shear, and perspective.
The homography matrix can then be divided into a
measurement vector of eight parameters:
Ẑt = [h13,t , h23,t , at , sx,t , sy,t , sht , px,t , py,t ]⊤ ,

(4)

with at = arctan 2(h21 , hp
11 ) denoting the rotation, sx,t =
p
h211 + h221 and sy,t = h212 + h222 denoting the scales,
sht = arctan 2(h12 , h11 ) denoting the shear, and px,t =
h31 , py,t = h32 denoting the perspective terms. Ẑt serves
as the noisy observation of the latent state Zt . Assuming
that the platform is moving with a constant velocity, the
state vector Zt can be defined as
Zt = [ h13,t , h23,t , at , sx,t , sy,t , sht , px,t , py,t , vh13 ,t ,
vh23 ,t , va,t , vsx ,t , vsy ,t , vsh,t , vpx ,t , vpy ,t ]⊤
(5)
where the first eight entries represent translation, rotation,
scales, shear, and perspective, and the latter eight denote
their velocities. Assuming that the state transition follows
a constant-velocity model, the predict state vector Ztp can
be formulated as:
"
#
I8 ∆tI8
p
k
Zt = AZt−1 ,
A=
,
(6)
0
I8
where A denotes the state transition matrix, and ∆t is the
frame interval. Prediction uncertainty Ptp is updated as
k
Ptp = APt−1
A⊤ + Q,

(7)

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

LI et al.:TOWARDS SEMANTIC-AWARE AERIAL VIDEO ANOMALY DETECTION BY EXPLOITING MULTIMODAL LARGE LANGUAGE MODEL

where Q is the process noise covariance controlling the
trade-off between smoothness and responsiveness. Given
the observation Ẑt , we use the observation model
Ẑt = HZt + rt ,

H = [I8 08×8 ],

TABLE I
S UMMARY OF H IERARCHICAL M OTION F EATURES .
Level

(8)
Local

with rt ∼ N (0, R) measuring noise and H denotes the
observation matrix. The Kalman gain is then
Kt = Ptp H ⊤ (HPtp H ⊤ + R)−1 ,

(9)

where R is the measurement noise covariance that reflects
the reliability of the homography estimate.
The smoothed state and covariance can be updated:

5

Global

Feature
a,b
µa,b
mag , σmag
a,b
Mmax
a,b
µa,b
u , µv
a,b
σu , σva,b
h̃ a,b ∈ RB
µmag , σmag
Mmax
M75

Description
Mean and std of magnitude in each cell
Maximum magnitude in each cell
Mean of flow components in each cell
Std of flow in each cell
Histogram of oriented flow in each cell
Mean and std of magnitude for the frame
Maximum flow magnitude for the frame
75th percentile of magnitude for the frame

Note: Local features are computed per patch Ca,b within the optical
flow field, while global features are computed over the entire frame. B
represents the number of bins in the HOF.

Ztk = Ztp + Kt (Ẑt − HZtp ),

Ptk = (I − Kt H)Ptp ,
(10) task-aligned questions to enhance context-aware ability of
The filtered homography Hkt,r is reconstructed from the the model. In the heuristic setting, they are automatically
smoothed parameters in Ztk as :
generated by GPT-4o using a prompt-generation template,
 k
 as shown in Figure 4(b). Given a scene category, GPTk
k
k
k
k
k
k
sx,t cos at sy,t (sin at cos sht − cos at sin sht ) h13,t
 k
 4o generates a set of general questions. These questions
 sx,t sin akt sky,t (cos akt cos shkt + sin akt sin shkt ) hk23,t  . are then instantiated and incorporated into the prompt
pkx,t
pky,t
1
presented to the MLLM to guide structured reasoning
(11) during inference. In our implementation, prompt generation
3) Motion Compensation: Once the smoothed homog- is performed via the GPT-4o API with temperature set as
raphy matrix Hkt,r is obtained, each frame It can be 0.8 and a maximum output length set as 300 tokens.
geometrically aligned to the reference frame Ir by inverse
2) Deterministic Scene-specific Prompt: While the
warping. Formally, for each target coordinate (x′ , y ′ ), the heuristic prompt strategy provides flexible scene-adaptive
corresponding source coordinate is recovered as
guidance, it relies on an external model to generate prompt.
 
 ′
To provide a more controllable and reproducible alternax
x
 
k −1  ′ 
(12) tive, we further introduce a deterministic prompt variant.
 y  = (Ht,r ) y  ,
In this setting, a more fixed scene-conditioned user prompt
w
1
template is employed: “The video frames are captured in
and the pixel value at (x′ , y ′ ) is interpolated from It {SCENE}. What is this environment intended for? Are there
using bilinear sampling. By warping frame It with the any anomalies in the video?”, where {SCENE} denotes the
transformation matrix Hkt,r , we map it to the coordinate scene category of specific scenario. This variant contributes
system of the reference frame Ir , thereby improving the to contextual awareness, enabling a more controlled evalalignment of background regions. Homography warping uation on the reasoning capability of MLLM.
inevitably introduces invalid border areas where mapped
pixels fall outside the image domain. To remove these D. Anomaly Inference and Dual-stream Consistencyartifacts, we identify the valid pixel set Ωvalid , which con- guided Score Refinement
tains all pixels whose mapped coordinates remain inside the
1) Initial Anomaly Inference: We adopt uniform samimage domain. We then compute the axis-aligned cropping
pling within each detection window to reduce redundancy
box using the set of valid pixel coordinates Ωvalid , which
caused by the high frame rate. Specifically, for each
is then used to crop the output region.
detection window, we select Tk frames at approximately
equal intervals. Given the sampled stabilized video frames
C. Prompt Generation and Formalization
and the scene-specific prompts, the pretrained MLLM
1) Heuristic Scene-specific Prompt: In aerial videos, an produces an initial judgment for each detection window
event is considered anomalous not merely because of its Wc , including textual responses to the prompted questions
visual appearance, but also because it violates the expected and an initial anomaly score sIc ∈ {0, 1}.
Since the initial window-level predictions may be locally
functional of the scene. Effective anomaly detection therefore requires the MLLM to capture scene semantics and unstable and general MLLMs often show limited sensitivity
contextual expectations. To explicitly introduce such scene- to motion-related anomalies, we introduce a Dual-stream
specific semantic priors into the inference process, we de- Consistency-guided Score Refinement module. It refines
sign a structured prompt generation mechanism that guides the initial scores from both semantic and motion perspectives. Specifically, it aggregates semantically related scores
the MLLM toward context-aware anomaly reasoning.
The overall prompt design is illustrated in Figure 4. to regularize prediction consistency and leverages motion
The system prompt (Figure 4 (a)) defines the task and similarity with normal anchor samples to better identify
constrains the output format. It incorporates a structured behavioral anomalies under limited training samples.
2) Dual-stream Feature Extraction: To support the subreasoning paradigm consisting of observation, reasoning,
and conclusion, encouraging the MLLM to ground its judg- sequent score refinement, both semantic and motion feament in visual evidence before producing a final decision. tures are extracted. For each center frame c in the test set,
The user prompts are scene-adaptive and formulated as we extract a semantic embedding fcs ∈ RDs using a frozen

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

6

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. X, NO. X, X 2025

User Prompt Generation Template

System Prompt Template

Developer Prompt

You are designed to do binary classification. The
input is a sequence of videos frames for identifying
whether there is an anomaly in the video. You need
to output the class label, i.e., an integer in the
set {0, 1}. 0 represents normal video, and 1
represents abnormal video.

You are an expert in aerial video anomaly detection.
Your task is to generate concise questions that can help
a multimodal large language model identify anomalies in
aerial video scenes.
User Prompt

Data :{VIDEO_FRAMES}

We assume that anomalies often present as semantic
conflicts. Please generate five user prompts for
multimodal large language models to assist in their aerial
video anomaly detection task in {SCENE) scenarios.
Please formulate each prompt as concise general questions
and provide the prompts in a JSON format.

Prompt Questions : {SCENE_SPECIFIC_QUESTIONS}
Answer Format : For each question, describe the
reasoning behind your observation on the video
frames, and provide a clear conclusion.
Final Decision: Based on the above answers, give the
integer class label: [ 0 for for normal video, 1 for
abnormal video.]

Generation Setting:

Model: GPT-4o, Temperature: 0.8, Max output tokens: 300

(b) Generation template for user prompts used in MLLM

(a) System prompt template for MLLM inference

Fig. 4. Prompt design for aerial video anomaly detection, including system and user prompt design. {VIDEO FRAMES} denotes the input video
frames, {SCENE SPECIFIC QUESTIONS} denotes the generated user prompts, and {SCENE} denotes the scene category of specific scenario.

vision encoder (ImageBind [47] in our implementation),
where Ds denotes the feature dimension.
For motion representation, we compute optical flow
between frames i and i + ∆t to construct hierarchical
motion features {fim }Ti=1 . Specifically, dense optical flow
is estimated using RAFT [48], yielding a flow map Oi ∈
RH×W ×2 with per-pixel vectors

⊤
Oi (x, y) = ui (x, y), vi (x, y) , i = 1, . . . , T − ∆t,
(13)
where ui (x, y) and vi (x, y) denote the horizontal and vertical components, respectively, and ∆t is the frame interval.
To handle missing flows near the temporal boundaries, the
optical flow of the nearest valid frame is replicated for the
initial and final ∆t frames, ensuring temporal alignment.
Based on the estimated flow field, we further construct
hierarchical motion descriptors. Specifically, the flow field
is divided into L×L non-overlapping patches {Ca,b }L
a,b=1 ,
from which we extract statistics of flow magnitudes and
components, together with histograms of oriented flow
(HOF). In addition, global motion statistics are computed
over the entire frame. These local and global descriptors together form the hierarchical motion representation
2
{fim } ∈ RL (7+B)+4 , where B denotes the number of
HOF bins. A detailed summary of the extracted hierarchical
motion features is provided in Table I.
3) Semantic Consistency Score Aggregation: To stabilize the initial output, we refine initial scores by aggregating
information from semantic-similar neighboring segments.
Specifically, for each center frame c ∈ C, we compute the
pairwise cosine similarity between its semantic embedding
fcs and those of the other center frames c′ ∈ C:
simsc,c′ =

fcs⊤ fcs′
,
∥fcs ∥2 ∥fcs′ ∥2

′

c, c ∈ C.

(14)

For each center frame c, we then construct its semantic
neighborhood Ncs by selecting its top-K s semantic similar
center frames, including c itself. The similarities of these

neighbors are normalized into non-negative aggregation
weights:
s

max(simsc,c′ , 0)
,
s
c′ ∈Ncs max(simc,c′ , 0) + ϵ

simc,c′ = P

(15)

with ϵ > 0. Using these weights, we obtain a semanticaggregated refined score for frame c that refined by its
semantically related contexts:
X
s
Scs =
simc,c′ ScI′ .
(16)
c′ ∈Ncs

4) Motion Consistency Score Refinement: Motion anchors A are constructed exclusively from normal training
videos and serve as reference patterns of normal motion
behavior during inference. They are used only for motion
consistency comparison and are not obtained through parameter learning or optimization:
anc
A = {fam }N
a=1 ,

(17)

Motion anchors are similar with the idea of memorybank that used in self-supervised learning, while feature
representations in our framework are maintained as a fixed
reference set. The motion anchor does not involve any
parameter learning or optimization, serving as reference
for measuring motion consistency during inference.
For a test frame i with motion feature fim , we measure
its deviation from normal motion by summing the L2
distances to its K m nearest anchors in A:
X
dm
∥fim − fam ∥2 ,
(18)
i =
fam ∈Nim

where Nim ⊂ A contains the K m closest anchors. The
motion deviation score is then normalized across the video:
Sim =

m
dm
i − minj dj
,
m
maxj dm
j − minj dj + ϵ

(19)

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

LI et al.:TOWARDS SEMANTIC-AWARE AERIAL VIDEO ANOMALY DETECTION BY EXPLOITING MULTIMODAL LARGE LANGUAGE MODEL

with ϵ > 0 for numerical stability. A higher Sim indicates
greater deviation from normal motion patterns.
For test frames lacking matched normal anchors, a
sparsity-based method inspired by Local Outlier Factor
(LOF) is employed. The average L2 distance from fim to
its K m nearest neighbors among other test frames can be
computed as anomaly indicator.
5) Temporal Smoothing: We interpolate both the Semantic consistency and motion consistency scores to the
frame level and fuse them additively to produce the integrated anomaly score.
Sif = Sis + Sim ,

(20)

where Sif represents the integrated anomaly score for frame
i. To mitigate temporal noise and ensure smooth anomaly
trajectories, we apply Gaussian smoothing to the fused
scores:
Pn
f
τ2
=−n exp(− 2σ 2 ) Si+τ
,
(21)
S̃if = τP
n
τ2
exp(−
)
2
τ =−n
2σ
where the smoothing window spans 2n + 1 frames. Boundary effects are mitigated using reflection padding. The
standard deviation is adaptively set as σ = αT to scale
with video duration.
IV. E XPERIMENTS
We conducted a series of experiments to answer the
following questions about our model: Q1. Accuracy. How
accurately does our model detect anomalies compared
to other baselines? Q2. Explainability. Can our model
provides reasonable explanations for detected anomalies?
Q3. Effectiveness. How does each module contribute to
the model performance? Q4. Robustness. How does the
performance vary under different parameter configurations?
A. Experimental Details
Below are the details of our experimental setup, including dataset configurations, baselines for comparison, key
parameters settings, and evaluation metrics.
1) Dataset Setup: For evaluation, we utilize two aerial
video anomaly detection datasets, comprising 73 subdatasets across various detection scenarios. The Drone
Anomaly dataset [6] includes 7 scenarios with 22 subdatasets, while UIT-ADrone [49] provides 51 sub-datasets
for various roundabout scenarios. We strictly follow the
original self-supervised evaluation protocol for all 73 subdatasets. For each sub-dataset, motion anchors are constructed only from the normal videos in its training split.
Validation and test videos are not used in anchor construction. During inference, each test video is evaluated
only against anchors derived from the training split of
the same sub-dataset. No anchors are shared across subdatasets, thereby preventing both cross-split and crossdataset information leakage.
2) Baselines: We evaluate SemAero against 21
state-of-the-art baselines, spanning self-supervised,
weakly-supervised, open-set supervised, and training-free
paradigms. These are summarized below by category.
Self-Supervised Methods: These approaches learn normality patterns on training data. DSN [50] is a predictionbased method that uses spatial and motion features.

7

CVAE [51] regularizes the feature in latent space for robust
representation. GANomaly [52] and its extension SkipGANomaly [53] use reconstruction error with adversarial
training and skip connections, respectively. adVAE [54]
models anomalies as deviations from normal Gaussian
distributions through a self-adversarial VAE. MemAE [55]
and MNAD [56] leverage memory banks, with the latter
introducing compactness and separateness losses for better generalization. STD [20] jointly exploits spatial and
motion streams. MKD [57] applies knowledge distillation
for feature discrimination. SSPCAB [58] enhances prediction with convolutional attention blocks. Aerial-specific
models include ANDT [6] and ASTT [4], predicting future frames using vision transformers and cross-attention,
respectively. DAD-FSM [59] employs a spatio-temporal
relational cross-transformer for frame prediction.
Weakly-Supervised Methods: These approaches leverage sparse or noisy labels for training. TEVAD [31]
integrates captioning with cross-modal enhancement.
MGFN [60] captures contextual and temporal dependencies. VadCLIP [61] adapts CLIP via learnable prompts
and a local-global temporal adapter. MMVAD [27] uses
attention fusion and saliency-aware contrastive learning.
Open-Set Supervised Methods: These handle limited
known anomalies in training. MLEP [62] applies margin
learning on rare events. HolmesVAU [17] fine-tunes an
LLM on HIVAU-70k with multi-granular annotations and
anomaly-focused sampling. VERA [26] uses verbalized
learning to optimize MLLM prompts.
Training-Free Methods: LAVAD [25] generates framelevel scores and interpretations using captioning and LLMs.
3) Experimental Setting: All experiments were conducted on a server running Ubuntu 20.04.5 LTS, equipped
with an Intel Xeon Gold 6242R CPU @ 3.10 GHz, 192
GB of RAM, and an NVIDIA GeForce RTX 4090 GPU.
The MLLM used in the main experiments is InternVL28B. In the comparative study, we set the detection window
to ω = 2 seconds, corresponding to 60 frames in DroneAnomaly (30 fps) [6] and 12 frames in UIT-ADrone
(6 fps) [49]. Center frames are sampled every δ = 16
frames, and Tk = 8 frames are uniformly extracted within
each window to form the input. All main experiments
were conducted using shared parameters setting across all
scenes. The parameters are categorized and set as follows:
1) Stabilization-related parameters include the Kalman
filter parameters (P0 = 1000I16 , Q = 0.01I16 ,
R = 0.1I8 ) and the motion-related thresholds (outlier
proportion threshold ζ = 0.8, scene-change threshold
τs = 0.17). These parameters were determined on a
separate development set to ensure broad engineering
feasibility.
2) Feature representation parameters include the semantic feature dimension Ds = 1024, patch level L = 2,
and frame interval ∆t = 1, which control the spatial
and temporal granularity of motion features. Further
parameter analysis suggests that scenes with more
complex motion may benefit from a larger ∆t.
3) Score refinement parameters are used to stabilize
frame-level anomaly scores, including neighborhood
sizes K s = K m = 5 for consistency aggregation,
and Gaussian temporal smoothing with half-window

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

8

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. X, NO. X, X 2025

TABLE II
D ETAILED S CENE -S PECIFIC U SER P ROMPTS FOR VARIOUS A ERIAL S CENARIOS
Scene Scenario
Bike Roundabout

Crossroads

Farmland Inspection

Highway

Railway Inspection

Solar Panel Inspection

Vehicle Roundabout

UIT-ADrone (Roundabout)

Generated Prompts
1. Is there any vehicle in the bike roundabout area that is not a bicycle?
2. Do any objects appear to be moving in the wrong direction inside the bike roundabout?
3. Are there pedestrians or animals obstructing the flow of bicycles in the roundabout?
4. Do you notice any stalled or fallen bikes creating blockage in the roundabout?
5. Are motorized vehicles (e.g., motorcycles, cars) illegally using the bike roundabout path?
1. Do any vehicles in the intersection violate traffic rules?
2. Is there any vehicle stopped or parked in a location that creates a hazard in the intersection area?
3. Are there any near-collision incidents or unusually close interactions between vehicles and pedestrians?
4. Are there any objects not on the right position and posing threat to the normal function of the crossroad?
5. Is the overall traffic behavior in the intersection inconsistent with normal flow patterns?
1. Are there unauthorized vehicles or people present in the farmland area?
2. Do you notice any damage or destruction to the crops or irrigation infrastructure?
3. Are drones or aircraft flying unusually close to or landing on the farmland?
4. Is there any smoke, fire, or machinery operating abnormally within the farmland?
5. Are animals intruding into the crop fields from surrounding areas?
1. Are there any pedestrians on the highway that may cause danger?
2. Do you observe any objects (e.g., barriers, cargo, animals) on the road that could interfere with traffic flow?
3. Are vehicles moving against traffic, making U-turns, or otherwise behaving abnormally?
4. Are there any signs of accidents, damage, or road degradation that affect the highway’s normal use?
5. Is there any unauthorized activity (e.g., people walking, selling, or filming) taking place on the highway?
1. Are there any objects or people present on or near the railway tracks that should not be there?
2. Do the tracks, bridges, or nearby equipment appear damaged or disrupted in any way?
3. Are there any vehicles or machinery obstructing the railway path?
4. Do you observe smoke, fire, water, or structural instability that could endanger train operations?
5. Are there any signs of illegal activity or unauthorized construction near the railway?
1. Are there any broken, missing, or visibly damaged solar panels in the inspection area?
2. Is there any foreign object, such as debris or vegetation, obstructing the surface of the solar panels?
3. Do all solar panels appear to be uniformly aligned and securely mounted in the expected formation?
4. Is there any unauthorized person, animal, or vehicle present near the solar panel installation area?
5. Are there any signs of fire, discoloration, or hotspots that could indicate overheating or electrical malfunction?
1. Are there any vehicles that are violating the roundabout’s traffic rules?
2. Is there any unexpected congestion or traffic jam forming at the roundabout?
3. Are there pedestrians or cyclists that should not appear in the vehicle roundabout?
4. Do you observe signs of accidents or collisions that interrupt the roundabout’s operation?
5. Is there any vehicle entering the roundabout causing disruption to other vehicles?
1. Are any vehicles in the scene performing illegal or dangerous maneuvers that violate traffic rules?
2. Is there any unusual congestion, blockage, or disruption in the normal flow of traffic?
3. Are there any objects or people in inappropriate locations that could pose a risk to traffic safety?
4. Are there any vehicles or pedestrians exhibiting unusual, erratic, or dangerous behavior?
5. Is there any damage, obstruction, or abnormal situation affecting the infrastructure visible in the scene?

size n = 7 and standard deviation σ = T /16, where
T is the total video length in frames.
The heuristic scene-specific user prompts are generated
through the GPT-4o API, with the temperature set to 0.8
and the maximum output length set to 300 tokens. The
scene-specific prompts used in the comparative study are
listed in Table II. The robustness of heuristic user prompts
generation is further evaluated in the following study.
Following [27], [4], [6], we use frame-level AUC-ROC
as the primary evaluation metric. Model performance was
evaluated using the heuristic variant as the default, except
for the metric comparison in the comparative study.

TABLE III
C OMPARISON OF THE F RAME - LEVEL AUC-ROC P ERFORMANCE (%)
ON THE D RONE -A NOMALY DATASET WITH P REVIOUS M ETHODS
Categories

Weakly-Supervised

Open-set Supervised

Self-supervised

B. Comparative Study
1) Metric Comparison: Table III presents the model
performance, measured by AUC-ROC, on the DroneAnomaly dataset [6]. SemAero with hubristic prompts
achieved an average AUC-ROC of 77.99% across the seven
detection scenarios, while that with deterministic prompts
achieved an average AUC-ROC of 76.97%, surpassing
the leading weakly-supervised multimodal model MMVAD (71.22%). Other weakly-supervised methods leveraging cross-modal information, including MGFN (68.92%),
VadCLIP (68.11%), and TEVAD (67.35%), demonstrated
competitive performance. However, these models struggled
to detect behavioral anomalies due to limited training

MLLM/LLM-based

Method
TEVAD [31]
MGFN [60]
VadCLIP [63]
MMVAD-RNet50 [27]
MMVAD-CSPDNet53 [27]
MLEP [62]
DSN [50]
CVAE [51]
GANomaly [52]
Skip-GANomaly [53]
adVAE [54]
MemAE [55]
MNAD [56]
STD [20]
MKD [57]
SSPCAB [58]
ANDT [6]
ASTT [4]
LAVAD [25]
HolmesVAU [17]
VERA [26]
SemAero (Deterministic)
SemAero (Heuristic)

AUC-ROC
67.35
68.92
68.11
70.78
71.22
53.55
53.36
64.74
63.69
66.21
66.34
67.67
66.30
52.49
68.13
68.91
60.35
67.80
49.35
56.07
53.17
76.97
77.99

samples, resulting in lower performance compared to SemAero. Self-supervised methods, such as DSN (53.36%),
ASTT (67.80%) , ANDT (60.35%) , and CVAE (64.74%),

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

LI et al.:TOWARDS SEMANTIC-AWARE AERIAL VIDEO ANOMALY DETECTION BY EXPLOITING MULTIMODAL LARGE LANGUAGE MODEL

9

TABLE IV
C OMPARISON OF THE F RAME - LEVEL AUC-ROC P ERFORMANCE
(%) ON THE UIT-AD RONE DATASET WITH P REVIOUS M ETHODS
Frame 0

Frame 400

Frame 900

Frame 1000

Frame 1200

Frame 1400

Categories

Weakly-Supervised

Open-set Supervised

(a) Bike roundabout 03

Frame 0

Frame 100

Frame 200

Frame 300

Frame 400

Frame 500

Self-supervised

(b) Solar Panel Inspection 03
Frame 0

Frame 210

Frame 40

(c) UIT-Adrone (DJI_065)

Frame 100

Frame 5

Frame 200

(d) UIT-Adrone (DJI_081)

Fig. 5. Visualization of anomaly score rated by SemAero: (a) Bike
roundabout, (b) Solar panel inspection, (c) UIT-ADrone (DJI 065), and
(d) UIT-ADrone (DJI 081).

(a) Bike roundabout 03

(b) Solar Panel Inspection 03

(c) UIT-Adrone (DJI_065)

(d) UIT-Adrone (DJI_081)

Fig. 6.
Confusion matrices corresponding to the detection results
in Figure 5, illustrating the classification performance across the four
scenarios.

MLLM/LLM-based

Method
TEVAD [31]
MGFN [60]
VadCLIP [63]
MMVAD-RNet50[27]
MMVAD-CSPDNet53[27]
MLEP [62]
DSN [50]
CVAE [51]
MemAE [55]
MNAD [56]
STD [20]
ANDT [6]
ASTT [4]
DAD-FSM [59]
LAVAD[25]
HolmesVAU[17]
VERA [26]
SemAero (Deterministic)
SemAero (Heuristic)

AUC-ROC
63.46
64.25
66.32
67.40
69.56
53.55
57.94
56.39
59.07
52.34
57.05
60.50
65.45
68.13
51.32
55.32
51.69
68.22
71.07

also underperformed SemAero, primarily due to their
limited semantic-awareness capabilities. The incorporation
of memory module, such as MemAE and MNAD, can
improve the performance slightly by enforcing the reconstructed frames closing to the normality space.
The fine-tuned multimodal large language model,
HolmesVAU (56.07%), exhibited suboptimal performance,
likely because its training dataset (HIVAU-70k) consists
primarily of CCTV videos, which do not align well with
the characteristics of aerial videos. Similarly, LAVAD
(49.35%), a zero-shot approach relying on captioning and
LLM for anomaly reasoning, struggled with motion understanding due to platform-induced motion.
The UIT-ADrone dataset [49] presents greater challenges, as its anomalies are subtle and primarily motionbased. Model performance comparisons are shown in Table IV. Despite these challenges, SemAero with hubristic prompts achieved the highest AUC-ROC of 71.07%,
outperforming the leading weakly-supervised models
MMVAD-CSPDNet53 (69.56%) and MMVAD-RNet50
(67.40%). The performance with deterministic prompts was
slightly worse, with the mean AUC-ROC reaching 68.22%.
Other cross-modal methods, including TEVAD (63.46%),
MGFN (64.25%), and VadCLIP (66.32%) , outperformed
single-modal self-supervised models like ASTT (65.45%)
and ANDT (60.50%) , underscoring the importance of
semantic understanding in aerial video anomaly detection.
HolmesVAU (55.32%) and LAVAD (51.32%) continued to
perform poorly, reflecting their limitations in addressing the
complex motion dynamics and semantic nuances of aerial
videos. SemAero effectively integrates semantic-aware reasoning and motion compensation through its dual-stream
consistency refinement module and ego-motion reduction,
tailored specifically for aerial video challenges.
2) Visualization of Results: We visualize the anomaly
scores generated by SemAero on four distinct scenarios:
(a) Bike Roundabout, (b) Solar Panel Inspection, and
more challenging traffic roundabout scenes from the UITADrone dataset (Figure 5 (c) and (d)). To further illustrate
the model’s performance, we also present their corresponding confusion matrices in Figure 6. Anomalies in the

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

10

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. X, NO. X, X 2025

Frame 0

Frame 500

Frame 1200

Frame 800

Frame 1600

Frame 1800

Frame 2200

(a) Ground Truth
A large field with a path running through
it.

LAVAD

(b) Scores rated by LAVAD

The video depicts a serene and peaceful
scene of a rice field, with no unusual or
out-of-the-ordinary
events
occurring
throughout.

HolmesVAU

(c) Scores rated by HolmesVAU

The video frames show motorcycles on the
farmland,
which
are
not
typically
authorized vehicles for such areas. Based
on
the
above
question
answers,
the
condition is met for an abnormal video
Therefore, the class Label is 1.

(d) Scores rated by SemAero

SemAero

Fig. 7. Comparison of semantic-aware anomaly detection models: Anomaly scoring and video understanding on the Farmland Inspection dataset.
Green-marked text represents the correct video or anomaly understanding, while the red-marked text represent the incorrect one.
TABLE V
A BLATION S TUDY FOR D IFFERENT M ODULES OF S EM A ERO ( HEURISTIC VARIANT )
Method

S

Vanilla MLLM
VERA
w/S
w/S,G
w/S,G,M
w/S,G,M,O
SemAero(w/all)

✓
✓
✓
✓
✓

G

✓
✓
✓
✓

M

✓
✓
✓

O

✓
✓

C

✓

Bike
Round
52.52
51.99
53.17
72.52
80.34
80.34
85.69

Crossroads
49.30
50.00
50.00
50.00
52.88
64.97
74.00

Farmland

Highway

Railway

44.45
50.91
99.90
99.80
99.80
99.60
99.86

66.60
61.10
60.79
66.47
66.47
80.48
81.45

50.00
50.00
50.00
50.00
50.00
50.33
50.33

Solar
Panel
50.00
58.21
59.70
54.68
62.09
70.79
78.80

Vehicle
Round
50.00
50.00
50.00
54.31
57.24
73.26
75.80

Mean
51.84
53.17
60.50 (+7.33%)
63.97 (+3.47%)
66.97 (+3.00%)
74.25 (+7.28%)
77.99 (+3.74%)

Note: S is the abbreviation for Scene-specific prompts module, G for CoT guidance module, M is for Motion reduction module, O is for motion
consistency refinement module, and C is for the whole consistency refinement module that includes semantic consistency measurement. ✓denotes
the module is included in testing.

Bike Roundabout and Solar Panel Inspection scenes are
mainly associated with semantic conflicts. For instance, a
white car appearing on a road that designed for non-motor
vehicles (Figure 5(a)) and sheep intruding into the solar
panel area (Figure 5(b)) are semantic anomalies. SemAero
correctly identified these anomalies, with the anomaly
scores aligning well with the ground truth. The confusion
matrices in Figure 6(a) and (b) further confirm this, with
SemAero achieving high F1 scores of 0.85 and 0.97
on corresponding dataset. Anomalies in the UIT-ADrone
dataset are mostly related to object behaviors and often
occupy only a small portion of the frame. SemAero is also
capable of detecting such subtle anomalies, largely owing
to the motion-consistency refinement modules. As shown in
Figure 5(c), between frames 20 and 70, a pedestrian failed
to cross the street at the designated crosswalk. Between
frames 180 and 280, a motorcycle illegally made a U-turn
at the pedestrian crossing. Similar anomalies occurred in
Figure 5(d), with an illegal U-turn between frames 5 and 40
and dangerous pedestrian behavior between frames 190 and
250. SemAero assigned high anomaly scores when such
events occurred, achieving F1 scores of 0.92 and 0.77 on

corresponding dataset (Figure 6(c) and Figure 6(d)).
3) Visualization Comparison: We present a comparative analysis of our model, SemAero, against two video
anomaly understanding models that leverages Large Language Models for video understanding: LAVAD and
HolmesVAU. The evaluation focuses on two key aspects:
frame-level anomaly scoring and semantic anomaly understanding. Results on Farmland datasets were visualized in Figure 7. SemAero outperformed both LAVAD
and HolmesVAU in anomaly detection and semantic understanding. The frame-level anomaly scores rated by
SemAero is aligned with the ground truth, have clear
distinctive ability between normal and abnormal samples.
SemAero demonstrated superior robustness and semantic
awareness, accurately identifying anomalies such as a vehicle on the farmland (Figure 7).
In contrast, LAVAD, which generates captions for video
segments to perform anomaly detection, exhibited significant limitations in anomaly localization. LAVAD misinterpreted the scene as a ‘large field with a path running
through it,’ which is likely due to misinterpreting water
reflections as a path. This hallucination led to unstable

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

LI et al.:TOWARDS SEMANTIC-AWARE AERIAL VIDEO ANOMALY DETECTION BY EXPLOITING MULTIMODAL LARGE LANGUAGE MODEL

11

TABLE VI
A BLATION STUDY FOR QUANTIFYING THE CONTRIBUTION OF MLLM REASONING AND REFINEMENT MODULES IN S EM A ERO
Method

Modules

Vanilla MLLM (generic prompt)
Refinement-only, w/O,C
Heuristic prompt, w/S
Heuristic prompt, w/S,G
Heuristic prompt, w/S,G,M
Heuristic prompt, w/all
Deterministic prompt, w/S
Deterministic prompt, w/S,G
Deterministic prompt, w/S,G,M
Deterministic prompt, w/all

–
O+C
S
S+G
S+G+M
All
S
S+G
S+G+M
All

Bike
Round
52.52
52.08
53.17
72.52
80.34
85.69
60.00
61.07
64.76
65.12

Crossroads
49.30
70.90
50.00
50.00
52.88
74.00
50.47
63.64
72.79
82.50

Farmland

Highway

Railway

44.45
97.54
99.90
99.80
99.80
99.86
50.00
82.44
82.44
98.10

66.60
65.42
60.79
66.47
66.47
81.45
80.76
61.67
64.27
82.33

50.00
50.33
50.00
50.00
50.00
50.33
50.00
50.00
50.00
50.33

Solar
Panel
50.00
66.52
59.70
54.68
62.09
78.80
50.43
65.02
66.67
83.82

Vehicle
Round
50.00
73.06
50.00
54.31
57.24
75.80
43.27
50.00
61.77
76.58

Mean
51.84
67.98
60.50
63.97
66.97
77.99
54.99
61.98
66.10
76.97

Note: Vanilla MLLM (generic prompt) denotes direct MLLM inference without scene-specific prompting or refinement. Refinement-only baseline
denotes anomaly scoring using only the refinement branch without scene-aware MLLM reasoning. S denotes scene-specific prompting, G denotes CoT
guidance, M denotes motion reduction, O denotes motion consistency refinement, and C denotes the full consistency refinement module including
semantic consistency. All indicates that all corresponding modules are enabled. This table is designed to distinguish the contribution of scene-aware
MLLM reasoning from that of the downstream refinement modules.

anomaly awareness and poor discriminative performance,
as evidenced by the frame-level scores.
HolmesVAU, designed to provide semantic interpretations at the video level, struggled with anomaly detection
in aerial contexts despite its training on multi-granular
datasets. It failed to detect unauthorized vehicles and
viewed the scene as peaceful, which is likely due to the
anomalous feature in the trained datasets are much different
from that in aerial videos, resulting in poor scalability.
C. Ablation Study
1) Ablation Study of Core Modules: We evaluated the
contribution of each module in SemAero through an ablation study using various module combinations, including
scene-specific prompts (S), CoT guidance (G), motion
reduction (M), and consistency refinement (C). The results
of this ablation study are summarized in Table V. We
included two simplified baselines for comparison. The first
uses the vanilla MLLM with a generic static prompt:
“Is there any anomaly in this video? Output exactly:
Class label: < 0, 1 >. 0 means normal, and 1 means
abnormal.” This baseline is intended to directly evaluate
the performance of the chosen MLLM without the any
wrapper. The second baseline uses the prompt design from
VERA [26], which serves as an existing prompt-based
reference. Both baselines perform substantially worse than
the full SemAero framework, with average AUC-ROC
scores of 51.84% and 53.17 %, respectively. The results
reveal the limited ability of MLLM under insufficient
reasoning guidance. Introducing scene-specific prompting
alone improves the mean AUC-ROC by 7.33% over the
VERA baseline, indicating the importance of semantic
contextualization for anomaly reasoning. This effect is
particularly pronounced on the Farmland dataset, which
achieves a gain of +48.99%. Adding CoT guidance further
improves the mean AUC-ROC by 3.47%, suggesting that
explicit reasoning guidance benefits scene-aware anomaly
judgment. Incorporating motion reduction brings an additional improvement of 3.00%, indicating that motioncompensated visual input benefits subsequent reasoning.
We further compare the variant with motion-consistency
only (O) with the full consistency refinement variant (C),
where C includes both motion and semantic consistency
aggregation. As shown in Table V, extending O to C

(a) Frame 122 (Crossroad dataset)

Fig. 8.

(b) Frame 1008 (Highway dataset)

Effectiveness of video reduction with flow analysis

(a) Drone-Anomaly
(Highway)

(b) Drone-Anomaly
(Solar Inspection)

(c) UIT-ADrone
(DJI_065)

(d) UIT-ADrone
(DJI_067)

Fig. 9. Distribution of Hierarchical Motion Feature Distances to Normal
Anchors: Normal vs. Anomalous Samples

improves the mean AUC-ROC from 74.25% to 77.99%
across all evaluated scenarios. This result suggests that
semantic aggregation is overall beneficial on the evaluated
datasets. Overall, these results verify that all core modules
contribute positively to the final performance, with the full
SemAero framework achieving the best overall result.
2) Analysis of MLLM Contribution: To clarify the contribution of MLLM reasoning, we conduct a targeted
ablation, with results recorded in Table VI. A vanilla

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

12

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. X, NO. X, X 2025

(a) Model performance

(c) Inference time

AUC-ROC (%)

(a) Bike roundabout (03)

(b) Farmland inspection

AUC-ROC (%)

MLLM with generic static prompts yields only 51.84%
mean AUC-ROC. Introducing scene-specific prompts consistently boosts performance by 3.15–8.66%, highlighting
the importance of providing contextual information. Further adding CoT guidance (G) and motion reduction (M)
raises the score to 66.97% (heuristic) and 66.10% (deterministic), demonstrating the benefit of reasoning guidance
and motion compensation. Meanwhile, the refinement-only
baseline reaches 67.98%, which is promising but still lags
behind the full SemAero framework (77.99% for heuristic
and 76.97% for deterministic). These results indicate that
MLLM reasoning and refinement modules are complementary. The former supplies semantically anomaly cues, while
the latter further refines their effectiveness by incorporating
motion awareness.

AUC-ROC (%)

Quantitative evaluation of prompt robustness, inference time, and cost across five repeated generations.

AUC-ROC (%)

Fig. 10.

(b) Averaged cost

(c) Solar panel inspection (02)

(d) Vehicle roundabout (02)

Fig. 11. Model detection performance with varying patch number (L)
and time interval (∆t) for hierarchical motion features extraction.

D. Module Analysis
1) Effectiveness of Ego-motion Reduction Module: To
assess the effectiveness of ego-motion reduction, we visualized a comparison of the original and stabilized frames
(Figure 8), along with their corresponding optical flow
maps relative to previous frames. Frames were selected
from the Crossroads (Figure 8(a)) and Highway datasets
(Figures 8(b)). As shown in the images, the original optical
flow displays significant platform motion, which interferes
with the motion of foreground objects. In contrast, the
motion of foreground objects in the optical flow of the
stabilized frames becomes more apparent.
2) Effectiveness of the Motion-consistency Score Refinement Module: We visualize the distribution of the top-k
hierarchical motion feature distances from test samples to
normal anchor samples in Figure 9. As shown, anomalous
frames consistently result in larger distances with minimal
overlap to the normal distribution. This clear separation
in distance distributions validates the effectiveness of our
hierarchical motion features in discriminating abnormal
events from normal behavior.
E. Analysis of Prompt Robustness and Inference Cost
We evaluate the robustness of the heuristic scene-specific
prompts by repeating prompt generation five times for each
detection scene and recording the corresponding model performance, estimated cost, and inference time. The results is
shown in Figure 10. The left panel shows the mean AUCROC (%) across repetitions, with shaded areas representing
±1 standard deviation. For most scenes, performance remains relatively stable, with limited variation in Railway

(0.00%), Farmland (0.63%), Solar (2.06%), and Highway
(2.31%). Larger variability is observed in more complex
traffic scenes such as Crossroads (7.64%) and Vehicle
(8.03%), suggesting that performance is more sensitive to
prompt variation when the scene contains richer semantic
interactions. The middle and right panels report the mean
estimated cost (USD) and mean inference time (s), respectively, together with ±1 standard deviation. These results
indicate that the prompt generation and inference process
incurs low monetary cost and moderate runtime overhead
in practice.
F. Parameter Study
We tested how our model perform under different parameters setting, including the parameters for hierarchical
motion feature extraction, size of detection window size,
and the number of user prompts.
1) Parameters for Hierarchical Motion Features: In this
experiment, we evaluate the model detection performance
under different patch numbers (L) and time intervals (∆t)
on four sub-datasets: Bike Roundabout 03, Farmland Inspection, Solar Panel Inspection 01, and Vehicle Roundabout 02. L controls the spatial partition factor, and ∆t
control the temporal interval for motion feature extraction.
As illustrated in Figure 11, the impact of these parameters is highly scene-dependent. Generally, the roundabout
datasets exhibit greater sensitivity to parameter variations
compared to the inspection datasets, with ∆t having a more
pronounced influence on performance than L.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

0.40
0.35
0.30

(a) Bike roundabout (03)

(b) Farmland inspection

0.20
0.15

2.5

5.0

7.5

10.0

Delta t

12.5

15.0

AUC-ROC (%)

0.25
AUC-ROC (%)

Spectral entropy

0.45

13

AUC-ROC (%)

Bike roundabout (03)
Farmland inspection
Solar panel inspection (02)
Vehicle roundabout (02)

0.50

AUC-ROC (%)

LI et al.:TOWARDS SEMANTIC-AWARE AERIAL VIDEO ANOMALY DETECTION BY EXPLOITING MULTIMODAL LARGE LANGUAGE MODEL

Fig. 12. Spectral entropy of different dataset under different time interval.
(c) Solar panel inspection (02)

(d) Vehicle roundabout (02)

80

77.99

78

AUC-ROC (%)

Fig. 14. Model performance under varying threshold for outlier (ζ) and
scene change (τs ).

78.96

79

78.36
77.21

77
76
75

74.21

74

1

Fig. 13.
Km .

5

10

K s and K m

15

20

Overall model performance under various setting of Ks and

To further investigate this phenomenon, we quantified
the motion complexity of each dataset using spectral
entropy (Figure 12). The results indicate that the two
roundabout datasets involve more intricate motions, increasing the temporal interval helps stabilize motion patterns and resulting in superior performance. Specifically,
Bike and Vehicle Roundabout reaches its peak performance
at ∆t = 12 and ∆t = 16, respectively. In contrast,
the two inspection datasets demonstrate higher robustness
across different t settings. These observations suggest that
complex scenes favor longer temporal intervals to establish
stable motion representations. L mainly impacts the granularity of hierarchical motion features, which is also scene
dependent, but a moderate value can balance computation
efficiency and performance. Overall, these results indicate
that moderate values of L and ∆t provide a practical and
reproducible compromise for unseen scenes, although they
do not eliminate the need for more adaptive parameter
selection in future work.
2) Parameters for Consistency Refinement: We further
investigate the sensitivity of our model to the number of
semantic and motion neighbors, Ks and Km (Figure 13).
For simplicity, we set Ks = Km = K in this experiment.
The results exhibit a rise-then-fall trend as K increases.
Initially, increasing K from 1 to 15 yields a steady performance gain, suggesting that a broader context helps
mitigate local noise and promotes model performance. The
performance reaches its peak at K = 15. However, a slight
degradation is observed when K exceeds this threshold,
which is likely because an excessively large K introduces
irrelevant neighbors, leading to reduced discriminative ability between normal and anomalous patterns.
3) Parameters for Motion Reduction: To evaluate the
robustness of the stabilization module, we conducted a
sensitivity analysis on the outlier proportion threshold ζ ∈
[0.7, 0.9] with step 0.05 and scene-change threshold τs ∈
[0.07, 0.47] with step 0.05 across four representative subdatasets. As shown in Figure 14, the AUC-ROC remains
highly stable across the entire tested range. Specifically,
Vehicle Roundabout 02 exhibits completely constant performance, while Farmland Inspection shows only negligible
variation, smaller than 0.008%. Bike Roundabout 03 and
Solar Panel Inspection 02 exhibit relatively larger but still
minor fluctuations, with maximum variation within 1.07%,
respectively. Overall, the ego-motion reduction module
benefits most from retaining more reliable inliers (high ζ)
while keeping the reference frame fresh (low τs ). These
results demonstrate that the module is highly robust within
typical operating ranges, primarily due to the built-in
RANSAC rejection mechanism and the Kalman filter.
4) Detection Window Size and Number of Prompts: As
shown in Table VII, performance varies with the window
size ω. At ω = 1s, the model achieves an AUC-ROC
of 75.86%. Increasing the window size to 2s improves
performance to 77.99%. However, further expansion to 4s
or 6s yields no additional gain, with performance slightly
declining to 77.39% and 77.14%, respectively. The peak
performance (80.05%) occurs at ω = 10s, suggesting that
longer temporal contexts enhance model stability.
Regarding the number of prompts, a single prompt yields
a relatively low AUC-ROC of 68.69%, likely due to limited
semantic guidance. Performance consistently improves as
the number of prompts increases from 2 to 5, peaking at
77.99%. This trend suggests that a higher prompt diversity
enhances semantic coverage and contextual understanding.
However, increasing the count to 6 causes a drop to
71.11%, likely due to redundancy from excessive prompts
that confuses the model’s decision-making. These results
highlight that a balance between prompt diversity and
conciseness is crucial for maximizing detection efficacy.
5) Model Robustness under Various MLLM Models:
Table VIII presents the detection performance and memory
usage of different MLLMs on the Drone-Anomaly dataset.
Within the InternVL2 series, the AUC-ROC score consis-

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

14

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. X, NO. X, X 2025

TABLE VII
M ODEL D ETECTION P ERFORMANCE ON D RONE -A NOMALY DATASET
UNDER D IFFERENT S ETTINGS OF D ETECTION W INDOW S IZE ω ( S )
AND N UMBER OF P ROMPTS
ω (s)
1
2
4
6
8
10

AUC-ROC (%)
75.86
77.99
77.39
77.14
78.67
80.05

Prompts numbers
1
2
3
4
5
6

AUC-ROC (%)
68.69
76.85
75.76
77.82
77.99
71.11

TABLE VIII
M ODEL D ETECTION P ERFORMANCE OF D IFFERENT MLLM M ODELS
ON D RONE -A NOMALY DATASET
Model
InternVL2-1B
InternVL2-2B
InternVL2-4B
InternVL2-8B
Qwen3-VL-2B-Instruct
Qwen3-VL-2B-Thinking

Memory usage
5716 MiB
7944 MiB
12160 MiB
20248 MiB
20034 MiB
23478 MiB

AUC-ROC
62.06 %
63.09 %
76.06 %
77.99 %
60.97 %
61.96%

Note:The reported memory usage corresponds to the peak value
observed during the inference phase.

tently improves with model size, increasing from 62.06 %
(1B) to 77.99 % (8B). This indicates that enlarging the
visual–language capacity significantly enhances the ability
of model to capture subtle motion and contextual cues in
aerial scenes. Meanwhile, the GPU memory usage grows
nearly linearly with model parameters, from 5.7 GB to 20.2
GB, showing good scalability for inference deployment.
In contrast, both Qwen3-VL-2B variants require substantially more memory than InternVL2-2B, reaching
20.0–23.5 GB, owing to their deeper cross-modal attention.
However, their detection performance does not surpass InternVL2 models, with the Qwen3-VL-2B-Thinking variant
achieving only 61.96% AUC-ROC.
V. C ONCLUSION AND F UTURE W ORK
In this paper, we introduce SemAero, a novel framework
that explores MLLMs for aerial video anomaly detection.
SemAero can detect both behavior-related and semantic
anomalies, while providing not only frame-level anomaly
scores but also natural language explanations. We acknowledge that the current framework does not automatically
determine the scene-wise optimal values for completely
unseen scenes. A possible solution is to use unsupervised
scene statistics to guide the selection.
Although this work is evaluated on aerial video anomaly
detection benchmarks, several design elements of SemAero
may also be useful for broader video understanding tasks.
In particular, the ego-motion reduction module may generalize to moving-platform settings, while the scene-specific
prompting strategy and dual-stream consistency refinement
may benefit video analysis tasks that require joint semantic
and motion modeling under limited annotations. Recent
advances in few-shot action recognition [41], audio-visual
event localization [43], compositional zero-shot learning
[44], and robust gaze estimation [45] further suggest the
broader value of structured semantic modeling and crossmodal reasoning. Exploring such broader applicability beyond aerial anomaly detection will be an important direction for future work.

Nevertheless, several limitations of the current framework should be acknowledged. First, the current framework
remains computationally expensive due to the combined
cost of ego-motion reduction MLLM inference. Runtime
analysis shows that the dual-stream refinement module
introduces negligible overhead, whereas the dominant latency arises from MLLM inference, followed by egomotion reduction. As a result, the present implementation is more suitable for offline analysis or near-online
monitoring than for strict real-time onboard deployment
on edge devices. Future work will investigate lightweight
motion estimation, more efficient multimodal models, and
edge-cloud collaborative deployment to improve practical efficiency. Second, the proposed framework does not
fundamentally resolve hallucinations caused by imperfect
alignment between visual evidence and linguistic priors
[64]. Although the semantic score aggregation strategy improves anomaly discrimination ability overall, it may also
propagate erroneously high scores to semantically related
normal clips. Future work will explore more principled
approaches to improving the reliability of MLLM-based
anomaly reasoning, including reinforcement learning [65],
and confidence-aware fine-tuning [66].
R EFERENCES
[1] Y. Zhong, R. Zhu, G. Yan, P. Gan, X. Shen, and D. Zhu, “Inter-clip
feature similarity based weakly supervised video anomaly detection
via multi-scale temporal mlp,” IEEE Transactions on Circuits and
Systems for Video Technology, vol. 35, no. 2, pp. 1961–1970, 2025.
[2] Y. Fan, Y. Yu, W. Lu, and Y. Han, “Weakly-supervised video
anomaly detection with snippet anomalous attention,” IEEE Transactions on Circuits and Systems for Video Technology, vol. 34, no. 7,
pp. 5480–5492, 2024.
[3] J. Chen, X. Cao, P. Yang, M. Xiao, S. Ren, Z. Zhao, and D. O. Wu,
“Deep reinforcement learning based resource allocation in multiuav-aided mec networks,” IEEE Transactions on Communications,
vol. 71, no. 1, pp. 296–309, 2023.
[4] T. M. Tran, D. C. Bui, T. V. Nguyen, and K. Nguyen, “TransformerBased Spatio-Temporal Unsupervised Traffic Anomaly Detection
in Aerial Videos,” IEEE Transactions on Circuits and Systems for
Video Technology, vol. 34, no. 9, pp. 8292–8309, 2024.
[5] Z. Chen, J. Wu, W. Wang, W. Su, G. Chen, S. Xing, M. Zhong,
Q. Zhang, X. Zhu, L. Lu, et al., “Internvl: Scaling up vision
foundation models and aligning for generic visual-linguistic tasks,”
in Proceedings of the IEEE/CVF Conference on Computer Vision
and Pattern Recognition, 2024, pp. 24 185–24 198.
[6] P. Jin, L. Mou, G.-S. Xia, and X. X. Zhu, “Anomaly Detection
in Aerial Videos With Transformers,” IEEE Transactions on Geoscience and Remote Sensing, vol. 60, pp. 1–13, 2022.
[7] X. Liu, Y. Liu, H. Sui, C. Qin, Y. Che, and Z. Guo, “Anomaly detection in cropland monitoring using multiple view vision transformer,”
Scientific Reports, vol. 15, no. 1, p. 14147, Apr. 2025.
[8] I. Bozcan and E. Kayacan, “Context-dependent anomaly detection
for low altitude traffic surveillance,” in 2021 IEEE International
Conference on Robotics and Automation (ICRA), May 2021, pp.
224–230.
[9] S. Hamdi, S. Bouindour, H. Snoussi, T. Wang, and M. Abid, “Endto-end deep one-class learning for anomaly detection in UAV video
stream,” Journal of Imaging, vol. 7, no. 5, p. 90, May 2021.
[10] D. Avola, L. Cinque, A. Di Mambro, A. Diko, A. Fagioli, G. L.
Foresti, M. R. Marini, A. Mecca, and D. Pannone, “Low-altitude
aerial video surveillance via one-class SVM anomaly detection from
textural features in UAV images,” Information, vol. 13, no. 1, p. 2,
Jan. 2022.
[11] D. Cavaliere, A. Saggese, S. Senatore, M. Vento, and V. Loia,
“Empowering UAV scene perception by semantic spatio-temporal
features,” in 2018 IEEE International Conference on Environmental
Engineering (EE), Mar. 2018, pp. 1–6.
[12] C. Chen, X. Liu, M. Song, L. Li, S. Yuan, X. Yu, and S. Pang,
“Unveiling context-related anomalies: Knowledge graph empowered
decoupling of scene and action for human-related video anomaly
detection,” IEEE Transactions on Circuits and Systems for Video
Technology, vol. 35, no. 8, pp. 8071–8085, 2025.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

LI et al.:TOWARDS SEMANTIC-AWARE AERIAL VIDEO ANOMALY DETECTION BY EXPLOITING MULTIMODAL LARGE LANGUAGE MODEL

[13] D. Cavaliere, V. Loia, A. Saggese, S. Senatore, and M. Vento, “A
human-like description of scene events for a proper UAV-based
video content analysis,” Knowledge-Based Systems, vol. 178, pp.
163–175, Aug. 2019.
[14] G. S., M. P. M.M., U. Verma, and R. M. Pai, “Semantic segmentation
of UAV aerial videos using convolutional neural networks,” in 2019
IEEE Second International Conference on Artificial Intelligence and
Knowledge Engineering (AIKE), June 2019, pp. 21–27.
[15] X. Cai, Y. Qian, C. Wang, X. Peng, Y. Qian, and J. Wu, “Semantic
boosting via knowledge sharing and feedback for video anomaly
detection,” IEEE Transactions on Circuits and Systems for Video
Technology, pp. 1–1, 2026.
[16] C. Xu, K. Xu, X. Jiang, and T. Sun, “Plovad: Prompting visionlanguage models for open vocabulary video anomaly detection,”
IEEE Transactions on Circuits and Systems for Video Technology,
vol. 35, no. 6, pp. 5925–5938, 2025.
[17] H. Zhang, X. Xu, X. Wang, J. Zuo, X. Huang, C. Gao, S. Zhang,
L. Yu, and N. Sang, “Holmes-vau: Towards long-term video
anomaly understanding at any granularity,” in Proceedings of the
Computer Vision and Pattern Recognition Conference, 2025, pp.
13 843–13 853.
[18] Y. Zhong, G. Yan, Y. Hu, D. Zhu, and R. Zhu, “A two-stage framework with memory for anomaly detection via video decomposition
and bidirectional consistency,” IEEE Transactions on Circuits and
Systems for Video Technology, 2025.
[19] Y. Chang, Z. Tu, W. Xie, and J. Yuan, “Clustering driven deep
autoencoder for video anomaly detection,” in Computer Vision –
ECCV 2020: 16th European Conference, Glasgow, UK, August
23–28, 2020, Proceedings, Part XV. Berlin, Heidelberg: SpringerVerlag, 2020, p. 329–345.
[20] Y. Chang, Z. Tu, W. Xie, B. Luo, S. Zhang, H. Sui, and J. Yuan,
“Video anomaly detection with spatio-temporal dissociation,” Pattern Recognition, vol. 122, p. 108213, 2022.
[21] S. Sun, J. Hua, J. Feng, D. Wei, B. Lai, and X. Gong, “Delving into
instance modeling for weakly supervised video anomaly detection,”
IEEE Transactions on Circuits and Systems for Video Technology,
2025.
[22] Z. Yang, Y. Guo, J. Wang, D. Huang, X. Bao, and Y. Wang,
“Towards video anomaly detection in the real world: A binarization embedded weakly-supervised network,” IEEE Transactions on
Circuits and Systems for Video Technology, vol. 34, no. 5, pp. 4135–
4140, 2023.
[23] A. Acsintoae, A. Florescu, M.-I. Georgescu, T. Mare, P. Sumedrea,
R. T. Ionescu, F. S. Khan, and M. Shah, “Ubnormal: New benchmark for supervised open-set video anomaly detection,” in 2022
IEEE/CVF Conference on Computer Vision and Pattern Recognition
(CVPR), June 2022, pp. 20 111–20 121.
[24] P. Wu, X. Zhou, G. Pang, Y. Sun, J. Liu, P. Wang, and Y. Zhang,
“Open-vocabulary video anomaly detection,” in Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern Recognition,
2024, pp. 18 297–18 307.
[25] L. Zanella, W. Menapace, M. Mancini, Y. Wang, and E. Ricci,
“Harnessing large language models for training-free video anomaly
detection,” in 2024 IEEE/CVF Conference on Computer Vision and
Pattern Recognition (CVPR). Seattle, WA, USA: IEEE, June 2024,
pp. 18 527–18 536.
[26] M. Ye, W. Liu, and P. He, “Vera: Explainable video anomaly
detection via verbalized learning of vision-language models,” in
Proceedings of the Computer Vision and Pattern Recognition Conference, 2025, pp. 8679–8688.
[27] D. Biswas and J. Tesic, “Mmvad: A vision–language model for
cross-domain video anomaly detection with contrastive learning and
scale-adaptive frame segmentation,” Expert Systems with Applications, vol. 285, p. 127857, 2025.
[28] A. Singh, M. J. Jones, and E. G. Learned-Miller, “EVAL: Explainable video anomaly localization,” in 2023 IEEE/CVF Conference
on Computer Vision and Pattern Recognition (CVPR). Vancouver,
BC, Canada: IEEE, June 2023, pp. 18 717–18 726.
[29] A. Singh, M. J. Jones, and E. G. Learned-Miller, “Tracklet-based
explainable video anomaly localization,” in 2024 IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops
(CVPRW), 2024, pp. 3992–4001.
[30] F. Liu, D. Chen, Z. Guan, X. Zhou, J. Zhu, Q. Ye, L. Fu, and
J. Zhou, “RemoteCLIP: A vision language foundation model for
remote sensing,” IEEE Transactions on Geoscience and Remote
Sensing, vol. 62, pp. 1–16, 2024.
[31] W. Chen, K. T. Ma, Z. Jian Yew, M. Hur, and D. A.-A. Khoo,
“TEVAD: Improved video anomaly detection with captions,” in 2023
IEEE/CVF Conference on Computer Vision and Pattern Recognition
Workshops (CVPRW). Vancouver, BC, Canada: IEEE, June 2023,
pp. 5549–5559.

15

[32] T. Yuan, X. Zhang, B. Liu, K. Liu, J. Jin, and Z. Jiao, “Surveillance
Video-and-Language Understanding: From Small to Large Multimodal Models,” IEEE Transactions on Circuits and Systems for
Video Technology, vol. 35, no. 1, pp. 300–314, Jan. 2025.
[33] H. Du, S. Zhang, B. Xie, G. Nan, J. Zhang, J. Xu, H. Liu,
S. Leng, J. Liu, H. Fan, et al., “Uncovering what why and how:
A comprehensive benchmark for causation understanding of video
anomaly,” in Proceedings of the IEEE/CVF Conference on Computer
Vision and Pattern Recognition, 2024, pp. 18 793–18 803.
[34] Y. Pu, X. Wu, L. Yang, and S. Wang, “Learning prompt-enhanced
context features for weakly-supervised video anomaly detection,”
IEEE Transactions on Image Processing, vol. 33, pp. 4923–4936,
2024.
[35] R. Liang, Y. Li, J. Zhou, and X. Li, “Text-driven traffic anomaly
detection with temporal high-frequency modeling in driving videos,”
IEEE Transactions on Circuits and Systems for Video Technology,
vol. 34, no. 9, pp. 8684–8697, 2024.
[36] K. Lin, L. Li, C.-C. Lin, F. Ahmed, Z. Gan, Z. Liu, Y. Lu,
and L. Wang, “SwinBERT: End-to-end transformers with sparse
attention for video captioning,” in 2022 IEEE/CVF Conference on
Computer Vision and Pattern Recognition (CVPR). New Orleans,
LA, USA: IEEE, June 2022, pp. 17 928–17 937.
[37] J. Xie, G. Wang, T. Zhang, Y. Sun, H. Chen, Y. Zhuang, and J. Li,
“LLaMA-Unidetector: An LLaMA-Based Universal Framework for
Open-Vocabulary Object Detection in Remote Sensing Imagery,”
IEEE Transactions on Geoscience and Remote Sensing, vol. 63, pp.
1–18, 2025.
[38] Y. Tang, J. Bi, S. Xu, L. Song, S. Liang, T. Wang, D. Zhang, J. An,
J. Lin, R. Zhu, A. Vosoughi, C. Huang, Z. Zhang, P. Liu, M. Feng,
F. Zheng, J. Zhang, P. Luo, J. Luo, and C. Xu, “Video understanding
with large language models: A survey,” IEEE Transactions on
Circuits and Systems for Video Technology, pp. 1–1, 2025.
[39] Q. Peng, B. Planche, Z. Gao, M. Zheng, A. Choudhuri, T. Chen,
C. Chen, and Z. Wu, “3d vision-language gaussian splatting,” in
International Conference on Learning Representations, Y. Yue,
A. Garg, N. Peng, F. Sha, and R. Yu, Eds., vol. 2025, 2025, pp.
61 008–61 031.
[40] Q. Peng, C. Bai, G. Zhang, B. Xu, X. Liu, X. Zheng, C. Chen, and
C. Lu, “Navigscene: Bridging local perception and global navigation
for beyond-visual-range autonomous driving,” in Proceedings of the
33rd ACM International Conference on Multimedia, ser. MM ’25.
New York, NY, USA: Association for Computing Machinery, 2025,
p. 4193–4202.
[41] H. Qu, X. Shu, R. Yan, H. Gao, W. Wang, and J. Tang, “Spatiotemporal decoupled knowledge compensator for few-shot action
recognition,” IEEE Transactions on Pattern Analysis and Machine
Intelligence, pp. 1–15, 2026.
[42] H. Qu, R. Yan, X. Shu, H. Gao, P. Huang, and G. Xie, “Mvp-shot:
Multi-velocity progressive-alignment framework for few-shot action
recognition,” IEEE Transactions on Multimedia, vol. 27, pp. 6593–
6605, 2025.
[43] L. Xing, H. Qu, R. Yan, X. Shu, and J. Tang, “Locality-aware
cross-modal correspondence learning for dense audio-visual events
detection,” IEEE Transactions on Circuits and Systems for Video
Technology, pp. 1–1, 2025.
[44] H. Qu, J. Wei, X. Shu, and W. Wang, “Learning clustering-based
prototypes for compositional zero-shot learning,” in The Thirteenth
International Conference on Learning Representations, 2025.
[45] H. Qu, J. Wei, X. Shu, Y. Yao, W. Wang, and J. Tang, “Omnigaze:
Reward-inspired generalizable gaze estimation in the wild,” in The
Thirty-ninth Annual Conference on Neural Information Processing
Systems, 2025.
[46] D. G. Lowe, “Distinctive image features from scale-invariant keypoints,” International journal of computer vision, vol. 60, no. 2, pp.
91–110, 2004.
[47] R. Girdhar, A. El-Nouby, Z. Liu, M. Singh, K. V. Alwala, A. Joulin,
and I. Misra, “Imagebind: One embedding space to bind them all,”
in CVPR, 2023.
[48] Z. Teed and J. Deng, “Raft: Recurrent all-pairs field transforms for
optical flow,” in European conference on computer vision. Springer,
2020, pp. 402–419.
[49] T. M. Tran, T. N. Vu, T. V. Nguyen, and K. Nguyen, “UIT-ADrone:
A novel drone dataset for traffic anomaly detection,” IEEE Journal
of Selected Topics in Applied Earth Observations and Remote
Sensing, vol. 16, pp. 5590–5601, 2023.
[50] W. Liu, W. Luo, D. Lian, and S. Gao, “Future frame prediction for
anomaly detection - a new baseline,” in 2018 IEEE/CVF Conference
on Computer Vision and Pattern Recognition, 2018, pp. 6536–6545.
[51] D. T. Nguyen, Z. Lou, M. Klar, and T. Brox, “Anomaly detection
with multiple-hypotheses predictions,” in International Conference
on Machine Learning. PMLR, 2019, pp. 4800–4809.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2026.3686230

16

IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY, VOL. X, NO. X, X 2025

[52] S. Akcay, A. Atapour-Abarghouei, and T. P. Breckon, “Ganomaly:
Semi-supervised anomaly detection via adversarial training,” in
Asian conference on computer vision. Springer, 2018, pp. 622–
637.
[53] S. Akçay, A. Atapour-Abarghouei, and T. P. Breckon, “Skipganomaly: Skip connected and adversarially trained encoder-decoder
anomaly detection,” in 2019 international joint conference on neural
networks (IJCNN). IEEE, 2019, pp. 1–8.
[54] X. Wang, Y. Du, S. Lin, P. Cui, Y. Shen, and Y. Yang, “advae: A
self-adversarial variational autoencoder with gaussian anomaly prior
knowledge for anomaly detection,” Knowledge-Based Systems, vol.
190, p. 105187, 2020.
[55] D. Gong, L. Liu, V. Le, B. Saha, M. R. Mansour, S. Venkatesh,
and A. Van Den Hengel, “Memorizing normality to detect anomaly:
Memory-augmented deep autoencoder for unsupervised anomaly detection,” in 2019 IEEE/CVF International Conference on Computer
Vision (ICCV), 2019, pp. 1705–1714.
[56] H. Park, J. Noh, and B. Ham, “Learning memory-guided normality
for anomaly detection,” in 2020 IEEE/CVF Conference on Computer
Vision and Pattern Recognition (CVPR), 2020, pp. 14 360–14 369.
[57] M. Salehi, N. Sadjadi, S. Baselizadeh, M. H. Rohban, and H. R. Rabiee, “Multiresolution knowledge distillation for anomaly detection,”
in 2021 IEEE/CVF Conference on Computer Vision and Pattern
Recognition (CVPR), 2021, pp. 14 897–14 907.
[58] N.-C. Ristea, N. Madan, R. T. Ionescu, K. Nasrollahi, F. S. Khan,
T. B. Moeslund, and M. Shah, “Self-supervised predictive convolutional attentive block for anomaly detection,” in Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern Recognition,
2022.
[59] A. Fakhry, J. Lee, and J. Taek Lee, “Drone video anomaly detection
by future segmentation prediction and spatio- temporal relational
modeling,” IEEE Access, vol. 13, pp. 22 395–22 406, 2025.
[60] Y. CHEN, Z. LIU, B. ZHANG, W. FOK, X. QI, and Y.-C.
WU, “Mgfn: Magnitude-contrastive glance-and-focus network for
weakly-supervised video anomaly detection,” in Proceedings of the
37th AAAI Conference on Artificial Intelligence, AAAI 2023, ser.
Proceedings of the AAAI Conference on Artificial Intelligence,
B. WILLIAMS, Y. CHEN, and J. NEVILLE, Eds., no. 1. AAAI
press, June 2023, pp. 387–395.
[61] P. Wu, X. Zhou, G. Pang, L. Zhou, Q. Yan, P. Wang, and Y. Zhang,
“Vadclip: Adapting vision-language models for weakly supervised
video anomaly detection,” in Proceedings of the AAAI Conference
on Artificial Intelligence, vol. 38, no. 6, 2024, pp. 6074–6082.
[62] W. Liu, W. Luo, Z. Li, P. Zhao, and S. Gao, “Margin learning embedded prediction for video anomaly detection with a few anomalies,”
in Proceedings of the Twenty-Eighth International Joint Conference
on Artificial Intelligence, IJCAI-19. International Joint Conferences
on Artificial Intelligence Organization, 7 2019, pp. 3023–3030.
[63] P. Wu, W. Su, G. Pang, Y. Sun, Q. Yan, P. Wang, and Y. Zhang,
“Avadclip: Audio-visual collaboration for robust video anomaly
detection,” arXiv preprint arXiv:2504.04495, 2025.
[64] X. Lyu, B. Chen, L. Gao, J. Song, and H. T. Shen, “Alleviating hallucinations in large vision-language models through hallucinationinduced optimization,” in Advances in Neural Information Processing Systems, A. Globerson, L. Mackey, D. Belgrave, A. Fan,
U. Paquet, J. Tomczak, and C. Zhang, Eds., vol. 37.
Curran
Associates, Inc., 2024, pp. 122 811–122 832.
[65] X. Zhu, K. Zhao, L. Yi, S. Wang, Z. Wang, B. Zhu, H. Zhang, and
X. He, “Look carefully: Adaptive visual reinforcements in multimodal large language models for hallucination mitigation,” in The
Fourteenth International Conference on Learning Representations,
2026.
[66] Z. Zhang, W. Zhou, J. Zhao, and H. Li, “Robust multimodal
large language models against modality conflict,” in Proceedings
of the 42nd International Conference on Machine Learning, ser.
Proceedings of Machine Learning Research, A. Singh, M. Fazel,
D. Hsu, S. Lacoste-Julien, F. Berkenkamp, T. Maharaj, K. Wagstaff,
and J. Zhu, Eds., vol. 267. PMLR, 13-19 Jul 2025, pp. 77 233–
77 253.

Ruoheng Li received the B.S. degrees from
Nanjing University of Aeronautics and Astronautics, Nanjing, China, and the Royal Melbourne Institute of Technology University, Melbourne, VIC, Australia, both in 2020, and the
M.S. degree from Nanjing University of Aeronautics and Astronautics in 2023. She is currently pursuing the Ph.D. degree with Beihang
University, Beijing, China. Her research interests
include data science and intelligent transportation.

Xuhui Liu is now pursuing his Ph.D. degree
in Beihang University, and received his B.S. degree and M.S. degree from Beihang University,
Beijing, China in 2018 and 2021, respectively.
His research interests include machine learning
and computer vision.

Yutao Hu received his B.S. and Ph.D. degree
in the National Key Laboratory of CNS/ATM,
School of Electronics and Information Engineering, Beihang University, Beijing, China in
2017 and 2022, respectively. From 2022 to 2024,
he worked as a postdoctoral research fellow in
HKU-MMLab, The University of Hong Kong.
He is currently an Associate Professor in the
school of computer science and engineering,
Southeast University. His research interests include machine learning, computer vision and
multimodal learning.

Xi Zhu received the B.E. degree in electronic
and information engineering in 2010, and the
M.E. degree in control science and engineering
in 2013, both from Beijing University of Technology, Beijing, China, and the Ph.D. degree in
signal and information processing from Beihang
University, Beijing, in 2018. He is currently
an Associate Researcher with the School of
Electronic and Information Engineering, Beihang University. His research interests include
multivariate time series analysis, spatiotemporal
data mining, and target behavior cognition.

Xianbin Cao (Senior Member, IEEE) received
the B.E. and M.E. degrees in computer applications and information science from Anhui
University, Hefei, China, in 1990 and 1993,
respectively, and the Ph.D. degree in information
science from the University of Science and
Technology of China, Hefei, in 1996. He is
currently a Professor with the School of Electronic and Information Engineering, Beihang
University, Beijing, China. His current research
interests include intelligent transportation systems, air traffic management, and intelligent computation.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.
PAPER_TEXT
