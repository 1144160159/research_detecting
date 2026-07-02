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
# [495] Multimodal Evidential Learning for Open-World Weakly-Supervised Video Anomaly Detection
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
编号：495
题名：Multimodal Evidential Learning for Open-World Weakly-Supervised Video Anomaly Detection
年份：2025
DOI：10.1109/tmm.2025.3557682
来源：IEEE Transactions on Multimedia
PDF：paper/10.1109_TMM.2025.3557682.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：入侵检测与网络异常检测、其他AI安全与跨域异常检测
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\495.txt
- 原始字符数：56009
- 本次发送字符数：56009
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
3132

IEEE TRANSACTIONS ON MULTIMEDIA, VOL. 27, 2025

Multimodal Evidential Learning for Open-World
Weakly-Supervised Video Anomaly Detection
Chao Huang , Member, IEEE, Weiliang Huang, Qiuping Jiang , Senior Member, IEEE, Wei Wang ,
Jie Wen , Senior Member, IEEE, and Bob Zhang , Senior Member, IEEE

Abstract—Efforts in weakly-supervised video anomaly detection
center on detecting abnormal events within videos by coarsegrained labels, which has been successfully applied to many
real-world applications. However, a significant limitation of most
existing methods is that they are only effective for specific objects
in specific scenarios, which makes them prone to misclassification
or omission when confronted with previously unseen anomalies.
Relative to conventional anomaly detection tasks, Open-world
Weakly-supervised Video Anomaly Detection (OWVAD) poses
greater challenges due to the absence of labels and fine-grained
annotations for unknown anomalies. To address the above problem,
we propose a multi-scale evidential vision-language model to
achieve open-world video anomaly detection. Specifically, we
leverage generalized visual-language associations derived from
CLIP to harness the full potential of large pre-trained models
in addressing the OWVAD task. Subsequently, we integrate a
multi-scale temporal modeling module with a multimodal evidence
collector to achieve precise frame-level detection of both seen and
unseen anomalies. Extensive experiments on two widely-utilized
benchmarks have conclusively validated the effectiveness of our
method. The code will be made publicly available.
Index Terms—Video anomaly detection, vision-language model,
evidential learning.

I. INTRODUCTION
IDEO anomaly detection (VAD), which aims to identify
the anomaly events that diverge from normal ones, has
become an increasingly critical field because of its promising

V

Received 24 August 2024; revised 16 December 2024 and 23 January 2025;
accepted 5 February 2025. Date of publication 3 April 2025; date of current
version 28 May 2025. This work was supported in part by the National Natural Science Foundation of China under Grant 62301621, in part by Shenzhen
Science and Technology Program under Grant 20231121172359002, in part by
Shenzhen General Research Project under Grant JCYJ20241202125904007, in
part by Guangdong Basic and Applied Basic Research Foundation under Grant
2025A1515011398, and in part by the Science and Technology Development
Fund of Macao S.A.R (FDCT) under Grant 0028/2023/RIA1. The guest editor
coordinating the review of this article and approving it for publication was Prof.
Xiankai Lu. (Corresponding author: Qiuping Jiang.)
Chao Huang and Wei Wang are with the School of Cyber Science and Technology, Shenzhen Campus of Sun Yat-sen University, Shenzhen 518000, China
(e-mail: huangch253@mail.sysu.edu.cn; wangwei29@mail.sysu.edu.cn).
Weiliang Huang and Bob Zhang are with the PAMI Research Group, Department of Computer and Information Science, University of Macau, Macau
999078, China (e-mail: yc47492@um.edu.mo; bobzhang@um.edu.mo).
Qiuping Jiang is with the Faculty of Information Science and Engineering,
Ningbo University, Ningbo 315211, China (e-mail: jiangqiuping@nbu.edu.cn).
Jie Wen is with the Shenzhen Key Laboratory of Visual Object Detection and
Recognition, Harbin Institute of Technology, Shenzhen 518055, China (e-mail:
jiewen_pr@126.com).
Digital Object Identifier 10.1109/TMM.2025.3557682

Fig. 1. Illustration of the train and test phases of (a) Unsupervised, (b) Weaklysupervised and (c) Open-world Weakly-supervised VAD task.

application prospects. Due to the unavailability of substantial
fine-grained anomaly annotation, most existing VAD methods
focus on unsupervised learning and weakly-supervised learning
to detect those deviated samples as anomalies. The main difference between them is inherent in the availability of annotated
training samples. As shown in Fig. 1(a) and (b), unsupervised
VAD methods [1], [2], [3], [4] focus on how to detect unseen
anomaly events by mining the intrinsic structural information
and correlation of data, while Weakly-supervised VAD (WVAD)
methods [5], [6], [7], [8], [9], [10] focus on how to detect seen
anomaly events by limited annotated training samples. From the
perspective of supervised mode and model performance, neither
method is entirely satisfactory for real-world VAD. On the one
hand, though unsupervised methods are convenient for detecting a wide variety of unseen anomaly events in the real world,

1520-9210 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

HUANG et al.: MULTIMODAL EVIDENTIAL LEARNING FOR OPEN-WORLD WEAKLY-SUPERVISED VIDEO ANOMALY DETECTION

the performance is often unsatisfactory. On the other hand, while
WVAD methods exhibit superior performance in closed-set scenarios, they manifest a susceptibility to misclassification or oversight when confronted with unanticipated anomaly events. Some
recent works [11], [12], [13], [14], [15], [16] have attempted to
solve this problem by means of image enhancement, which improves its performance in the real world to some extent, but still
does not completely solve this problem.
The essential reason for this situation is that, as the dynamically changing real world continues to evolve, never-before-seen
anomalies consistently emerge. Therefore, to meet the requirements of VAD tasks in the real world, it is necessary to explore
the Open-world WVAD (OWVAD) methods, which can achieve
content performance in detecting anomaly events from videos
with assorted seen and unseen anomaly.
Divergent from the traditional VAD methods, as shown in
Fig. 1(c), OWVAD methods can detect temporal boundaries accurately of the anomaly events in the testing phase, which have
never occurred in the training phase. There is no doubt that OWVAD tasks are more complicated than WVAD tasks based on
closed sets. We argue that the following two aspects are key
limiting factors for OWVAD performance:
r Complexity of scenarios and diversity of anomaly categories in the real world: Unlike the closed-set WVAD task,
the OWVAD task is expected to detect anomaly events from
a variety of real-world scenarios. However, the limited scenario information in the training set makes it difficult for the
model to have a generic visual representation. Moreover,
a single scenario usually contains a series of associated
anomaly events, which is difficult to detect accurately in
the absence of information about the internal correlation
of these associated events.
r Ambiguity of training sample annotations: Under the conditions of OWVAD, not only are annotations unavailable
for the unseen anomaly, but also the temporal boundaries
for both seen and unseen anomaly can only be ambiguously inferred from the video and its coarse-grained annotation. This ambiguity brings confusion between seen
anomaly, unseen anomaly, and background. Furthermore,
the duration of anomalous events is often unpredictable and
exhibits considerable variability in the real world, which
increases the difficulty of accurately identifying their temporal boundaries.
To alleviate the above limitations of OWVAD, we propose a Multi-scale Evidential Learning method based on the
Vision-Language Pre-trained model (MEL-VLP) for OWVAD.
Guided by the introduced visual-textual associated knowledge,
MEL-VLP detects both seen and unseen anomalies by collecting multi-scale temporal contexts, text-associated information, and joint-modal features as evidence. To be specific, we
first extract visual features and textual features from the encoders of vision-language pre-trained model and constructed
a joint discriminative framework to detect anomalies by both
visual-textual features and their associated relationship. Recently, large vision-language pre-trained model has exhibited remarkable success across a diverse array of downstream tasks, attributed to its acquired cross-modal prior knowledge and robust

3133

transfer learning capabilities. Some recent VLP-based WVAD
methods [17], [18] have demonstrated the feasibility and superiority of VLP(e.g. Contrastive Language-Image Pre-training
(CLIP [19])) in VAD task.
Second, to address the problem of ambiguity of training sample annotations, we design a multimodal evidence collector,
under Subjective Logic Theory (SLT [20]), to better distinguish between background and anomalies by jointly leveraging single-modal and multimodal features. We argue that, for
abnormal events in a scenario, visual features should provide
sufficient evidence of the seen anomalies, while textual features
can provide not only supplementary evidence information for
seen anomalies but also correlation evidence for unseen anomalies, thereby enhancing the model’s ability to detect various
anomalies in the real world. To combine multimodal evidence to
dynamically calibrate the temporal boundaries of anomaly, we
propose a multimodal evidential collaborative learning method
that allows single and joint modal evidence information to be
calibrated against each other according to their respective confidence and uncertainty.
Finally, for the unpredictability and variability of anomaly duration, a Multi-scale Temporal Visual Modeling (MTVM) module is designed to empower single snippet features with the capacity to perceive multi-scale contextual video segments. By
capturing and aggregating local and global visual information
across video segments that traverse distinct temporal scales, our
MTVM facilitates the acquisition of features at both fine-grained
and coarse-grained levels, thereby augmenting the capability to
characterize anomalies with varied durations.
Therefore, our potential contributions can be summarized as
follows.
r We propose a novel multi-scale evidential learning framework for open-world weakly-supervised video anomaly
detection, which is driven by vision-language pre-trained
model and under the guidance of subjective logic theory.
r We jointly leverage the multi-scale temporal visual modeling (MTVM) module and multimodal evidential collaborative learning (MECL) module to address the limitation
of ambiguity of training sample annotations.
r We conduct extensive experiments on two popular benchmarks, XD-Violence and UCF-Crime. And the experimental results demonstrate significant superiority to several
state-of-the-art weakly supervised approaches.
II. RELATIVE WORK
A. Weakly Supervised Video Anomaly Detection
Recent weakly supervised anomaly detection methods are
mainly based on the multi-instance learning (MIL) framework [21], which regards the anomaly and normal segments as
positive and negative samples respectively. Among them, most
of the methods can be classified into three categories, namely,
erasing-based methods [22], [23], [24], [25], attention-based
methods [17], [26], [27], [28], [29] and uncertainty-based methods [30], [31], [32]. Erasure-based methods mainly erase outstanding areas by setting a threshold and then mining less obvious areas. For example, DE-Net [22] devises a dynamic erasing

3134

strategy that dynamically evaluates the completeness of the detected anomalies and erases the prominent anomaly segments in
order to motivate the model to discover milder anomaly segments in the video. Attention-based methods suppress background components by assessing foreground attention scores
mainly through the attention mechanism. RTFM [33] employs
self-attention mechanisms and dilation convolutions to capture
both long-range and short-range temporal dependencies for better feature learning.
As an emerging sort of approach, uncertainty-based methods primarily decompose model classification probabilities into
confidence and uncertainty through uncertainty estimation, and
optimization is conducted based on this uncertainty. Although
this paradigm has been successful in many fields [34], [35], it
has only been little studied in the field of anomaly detection.
For example, CELL [36] proposes a Cascade Evidential Learning framework at an evidence level, which jointly leverages
multi-scale temporal contexts and knowledge-guided prototype
information to achieve temporal action localization. For video
anomaly detection, Zhu et al. [30] use evidential deep learning
to instantiate MIL and use the predicted evidence to help select
anomaly instances with high cleanness for robust MIL training.
In this paper, by collecting multimodal anomaly evidence, we
propose a novel multimodal evidence collaboration framework
driven by vision-language pre-trained model to effectively mitigate the background ambiguity problem in WVAD.
B. Vision-Language Pre-Training Model
Over the past few years, vision-language pre-trained models [37], [38], [39], [40] have achieved substantial success, attributed to their pre-training on large-scale visual-textual pairs.
Pre-training based on large amounts of data allows the model to
learn more general and efficient visual and textual feature representations. Of greater significance is the assistance rendered by
the inherent associative information between visual and textual
modalities learned during the pre-training process, facilitating
application to diverse multi-modal downstream tasks [41], [42],
[43]. Llama [44] extends the scope of modeling in multimodal
domains such as image and video by integrating visual inputs
with the capabilities of LLMs. DoraemonGPT [38] achieves better processing of video tasks by combining LLM with dynamic
scene understanding to reason and predict objects and scenes in
videos.
For the VAD task, some recent works achieved significant performance gains by introducing the encoders of vision-language
pre-trained models. For instance, CLIP-TSA [17] acquires more
discriminative visual features using visual coders from CLIP
and models temporal dependence using a self-attention mechanism. Nevertheless, existing works have not delved deeply into
the exploration of associative information from vision-language
pre-training model for the OWVAD task. In this paper, we introduce visual encoders and textual encoders from vision-language
pre-train model to learn more generalized feature representations. At the same time, we enhance the performance of the
model in the open world by learning the intrinsic correlation
information between visual and textual modalities.

IEEE TRANSACTIONS ON MULTIMEDIA, VOL. 27, 2025

C. Evidential Deep Learning
Grounded in subjective logic theory [20], evidence-based
deep learning involves the collection of scalar evidence for each
category and models the probability distribution of the collected
evidence, enabling uncertainty estimation in a single forward
pass. Specifically, subjective logic is a logical framework for
dealing with and reasoning about uncertainty and trust, which is
particularly well suited for modeling and analyzing subjective
opinions or beliefs. It combines ideas from probabilistic and
multi-valued logic to be able to deal with the complexity of uncertainty, incomplete information, and inter-subjective trust. In
contrast to traditional probabilistic logic, subjective logic theory formalizes the cognitive uncertainty of a model in the face
of incomplete information by assigning belief measures to potential categories to characterize assertions of truthfulness and
explicitly incorporating uncertainty measures. As an emerging
method for uncertainty assessment, it holds a significant position across numerous applications. For video anomaly detection,
Zhu et al. [30] use evidential deep learning to instantiate MIL
and use the predicted evidence to help select anomaly instances
with high cleanness for robust MIL training. Huang et al. [45]
propose a model called Uncertainty-Aware Prototypical Transformer (UPformer), which is specialized for visual anomaly detection at the pixel level. In this work, the authors specifically
emphasize two challenges in the anomaly detection task: the diversity of anomalies and the blurred boundaries between them
and normal regions. To address these challenges, the authors
design a novel approach that takes into account not only the
diversity of anomalies but also the uncertainty in the anomaly
detection process.
However, evidence collected under single-modality conditions is limited by the constraints of modality-specific
information. Current methods used for VAD tasks overlook the
correlation and collaboration of evidence in a multi-modal context. Therefore, we propose a multi-modal evidence collaboration method aimed at endowing the model with the capability to
dynamically calibrate anomaly temporal boundaries.
III. METHOD
A. Overall Architecture
Problem Definition: OWVAD aims to detect seen and unseen abnormal instances in videos. Given a set of weakly|V |
labeled training videos V = {X (k) , y (k) }k=1 , where X (k) ∈
Nk ×H×W
represents a video with Nk frames with H × W pixR
els, and y (k) ∈ RC is its multi-hot label indicating the anomaly
categories that the abnormal instances in this video belong to,
where C is the number of seen anomaly categories. During the
testing phase, the model is used to predict frame-level anomaly
scores for the test video. It is worth noting that in the OWVAD
task, the training data contains several unknown anomaly categories, which are labeled as unknown categories.
Overview: We firstly leverage the most popular visuallanguage pre-trained models, such as CLIP, utilizing their visual
encoders and text encoders to extract visual and textual features,
which possess greater generality and discriminability. As shown

HUANG et al.: MULTIMODAL EVIDENTIAL LEARNING FOR OPEN-WORLD WEAKLY-SUPERVISED VIDEO ANOMALY DETECTION

3135

Fig. 2. The whole framework of our proposed method, in which the solid line box is divided into the main novel part of this paper. First, we perform feature
extraction on the video and labeled text with CLIP’s image encoders and text encoders to learn the more general and discriminative features. We then propose the
(a) Multi-scale Temporal Visual Modeling (MTVM) module for sensing different ranges of temporal contexts and capturing useful information. Finally, we design
the (b) Multimodal Evidence Collaborative Learning (MECL) module to dynamically calibrate the temporal boundaries of anomaly events.

in Fig. 2, for a given training video V , we input it into the visual
encoders of CLIP to obtain visual features X V ∈ RN ×D , where
N is the number of video frames, D is the dimension of visual feature. Similarly, we input category labels into the text encoders to
obtain textual features X T ∈ R(C+2)×D , where C is the number
of anomaly classes. Specifically, we code ‘normal’ and anomaly
categorries as text here. On the one hand, visual features X V employ the multi-scale temporal visual modeling (MTVM) module to perceive temporal context and derive anomaly probabilV
∈ R1×N through the classifier. Subsequently, we can
ity XN
get frame-level anomaly scores through the Tok-k algorithm.
V− attn
∈ R1×D (the proOn the other hand, visual attention XN
V
duction between visual features X and anomaly probabilV
) and textual features are aggregated together through
ity XN
the Visual Language Aggregation (VLA) module to get aggregated featuresXna ∈ RN ×D , and then a fine-grained aggregation
mappingXnA ∈ RN ×(C+2) is obtained through the product with
the visual features.
Besides, we use the multimodal evidential collaborative learning (MECL) module to dynamically calibrate the temporal
boundaries of anomaly. Specifically, we collect evidence from
V
, textual features X T and aggregaanomaly probability XN
A
tion mapping XN , respectively. The corresponding Dirichlet
distributions are obtained from the collected evidence and the
learned evidence is dynamically corrected by a joint-modal

discrimination (JMD) strategy. Specifically, the training process
and inference process are shown in Algorithms 1 and 2.
B. Multi-Scale Temporal Visual Modeling
Despite the potent feature representation capabilities of CLIP,
it is trained on a large-scale dataset of image-text pairs, which
implies that it faces challenges in extracting temporal dependencies within video data. Nevertheless, temporal dependencies
play a crucial role in video anomaly detection. Therefore, inspired by [46], [47], [48], we employ a Local and Global Temporal (LGT) adapter to model the long and short-term temporal
dependencies in videos. Then we design a multi-scale temporal visual modeling (MTVM) module to empower single snippet features with the capacity to perceive multi-scale contextual
video segments.
Local and Global Temporal Adapter: To capture the local temporal dependencies, we first compute the internal self-attention
of each video segment by Transformer. Then to capture the
global temporal dependency, we model the global temporal dependency in terms of feature similarity and relative distance
using GCN. These two processes can be expressed by the following formulas:
Xl = [T ransf ormer (xsegi ) , . . ., T ransf ormer (xsegj )] ,
(1)

3136

IEEE TRANSACTIONS ON MULTIMEDIA, VOL. 27, 2025

Xg = gelu ([Softmax (Hsim ) ; Softmax (Hdis )] Xl W ) , (2)

Algorithm 1: Training Process of Our Method.

where segi and segj denote the serial numbers of different video
segments respectively. Xl is the frame-level video feature extracted from the local module. Hsim is the adjacency matrix
computed by cosine similarity of each frame. Hdis is the adjacency matrix computed by the relative positions between each
two frames.
Multi-scale Temporal Visual Modeling: In MTVM, each
frame is assigned a series of multiscale video segments centered around it, and the contextual awareness properties of these
video segments contribute to the expansion of perceptual scope.
When a series of video segments centered around t are given,
our process of averaging this series of multiscale video frames
can be expressed as follows:

1
xi ,
(3)
fm
n = m
en − s m
n + 1 sm ≤i≤em
n

n

where m is the length of the predetermined temporal range,
m
and (sm
n , en ) indicate the start time and end time of the video
segment.
To enhance the perceptual capabilities of frame n regarding
abnormal events within the temporal context, feature enhancement is conducted through the fusion of xn and fnm . We argue that frame-level visual features can assimilate informative
contextual details from extended video segments highly correlated with them. Therefore, the fusion of xn and fnm to obtain
frame-level features with context awareness can be expressed as:

x̃n = (1 − β) xn + β
ωnm f m
(4)
n,

Algorithm 2: Inference Process of Our Method.

m∈M

where M is the total number of fused fragments, β is a hyperparameter for fusion weight of the cosine similarities ωnm
m
between xn and f m
n . And ωn can be calculated by:
ωnm =

xn f m
n
.
xn 2 · f m
n 2

(5)

C. Multimodal Evidential Collaborative Learning
We design a novel multimodal evidential collaboration learning approach for open-world WVAD task using the Evidential
Deep Learning (EDL) mechanism based on subjective logic
theory. In contrast to conventional classifiers that lack awareness of confidence in their predictions, EDL collects evidence
through uncertainty perception. It treats the classification output as a point estimate of the classification distribution, placing
priors on the distribution across all possible classification outputs. For the OWVAD task, the assessment of confidence and
uncertainty regarding unknown anomalies is significantly more
effective through evidence collection and the construction of an
uncertainty perception framework. Optimization of prediction
results based on this approach proves to be more efficient in many
fields compared to traditional classifier learning methods. Therefore, we devise a Multimodal Evidential Collaborative Learning
(MECL) module for the OWVAD task. By collecting evidence
from visual modality, textual modality, and joint modality, we

optimize prediction results based on the confidence and uncertainty associated with different modalities. For the features of
T
modality m ∈ (vsion, language, aggregated), (xm
n )n=1 , the
evidence of the c-th anomaly category is a scalar and can be
calculated by:
m
em
n,c = g (fc (xn ; θ)) ,

(6)

where fc (·) is the DNN evidential collector parameterized by
θ for c-th category. In order to keep the collected evidence

HUANG et al.: MULTIMODAL EVIDENTIAL LEARNING FOR OPEN-WORLD WEAKLY-SUPERVISED VIDEO ANOMALY DETECTION

non-negative, the evidence function g(·) usually consists of
RELU, SoftPus or Exp function. For simplicity, we simplify
the process of constructing the distribution of evidence for each
modality as follow:
Distribution (xc ; αc ) =
B (αc ) =

Γ



1
C
c=1 αc



C

1
xαc −1 ,
B (αc ) c=1 c
C


Γ(αc ),

(7)

(8)

c=1

where xc the predicted results of model, αc = em
n,c + 1, and Γ is
the Gama function. Based on this we can obtain the confidence
and uncertainty as follow:
αc
c
, u c = C
.
(9)
pc = C
c=1 αc
c=1 αc
To make the evidence for different modalities effective for
joint learning, we jointly optimize using the prediction uncertainty of the different modalities as a correction factor. At first,
to prioritise the model to focus on the more reliable modality,
uni
we calculate {uuni
c , pc } as follow, which represents the confidence of category c in the most representative modality:

 uni uni 

= δ(c) {uvc , pvc } + (1 − δ(c)) utc , ptc , (10)
u c , pc
where δ(c) = 1 if pvc > ptc , otherwise the reverse is true.
Then, our multimodal collaborative learning strategy can be
expressed as:

uni
Ljmd =
(1 − mean(uagg
c )) 1 − uc
c
uni
,
∗l s (pagg
c ) , pc

3137

anomaly types from the XD-Violence and UCF-Crime training
datasets to simulate the real world with different proportions of
unseen anomalies. On this basis, we follow previous works and
use frame-level Average Precision (AP) and frame-level Area
under the operating Characteristic curve (AUC) as the metrics for
XD-Violence and UCF-Crime, respectively, on coarse-grained
predictions. For fine-grained predictions, we use the mean Average Precision (mAP) under different intersection over union
(IoU) thresholds as the evaluation metric.
Implementation Details: For the setting of unseen anomalies
in the training set, we train the model with 1, 2, 3, and 4 categories of seen anomaly videos together with normal videos in the
XD-Violence dataset, which has a total of 6 anomaly categories
in this dataset. Similarly, we train the model with 1, 3, 6, and 9
categories of seen anomaly videos together with normal videos
in the UCF-Crime dataset, which has a total of 13 anomaly categories in this dataset. Specifically, we randomly remove a certain
number of training anomaly classes each time and repeat them
three times to reduce the evaluation bias of the seen anomaly.
For the setting of vision-language pre-trained model, we use
the Contrastive Language-Image Pre-training (CLIP) to extract
both visual and textual features by their corresponding frozen
encoders. For the setting of hyperparameters, we set the fusion
weight β as 0.2, the weight of Ljmd as 1 × 10−2 , and the temporal context-aware range m as 3. Our model is implemented
with Python 3.8 and Pytorch 1.12, and we employ AdamW [53]
optimizer with a learning rate of 1 × 10−5 for optimization. All
experiments are conducted on a single RTX 3090 GPU.

B. Comparison With State-of-The-Arts
(11)

where l(·) is a distrance metrics function, e.g. L2-norm, and s(·)
the gradient truncation operation on the input.
IV. EXPERIMENTS
A. Experimental Settings.
Datasets:We perform experiments on the two most popular
anomaly detection datasets: (1) XD-Violence. The XD-Violence
dataset comprises 3954 training videos annotated at the video
level and 800 testing videos annotated at the frame level, encompassing 6 categories of violent anomalies. Additionally, it
stands out as one of the most challenging datasets due to the
frequent occurrence of camera movement and scene transitions
within the videos. (2) UCF-Crime. The UCF-Crime dataset is a
large-scale collection of real-world videos captured by surveillance cameras. Comprising 1,610 training videos annotated
with video-level labels and 290 testing videos annotated with
frame-level labels for performance evaluation. These surveillance videos are derived from a variety of complex real-world
scenarios, covering 13 classes of abnormal events.
Evaluation Metrics: Following the prior work [30], in order
to make the testing set contain previously unseen anomalies,
we train the model by altering the distribution of labels in the
training set. Specifically, we removed different proportions of

Comparison on XD-Violence: As shown in Table I, our proposed method outperforms previous weakly supervised methods in terms of AP metrics under different conditions of seen
anomaly categories. Specifically, compared to the SOTA method
VadCLIP [46], our method achieves superior performance under
different seen anomaly category conditions, achieving performance gains of 0.35%, 1.39%, 2.03%, and 1.86%, respectively.
Compared to other methods, our method also achieves varying
degrees of performance gain under different open set conditions.
This reflects the superiority of our approach in the open world.
As shown in Table III, compared to the performance of other
methods under closed-set conditions, our method achieves comparable performance even in the absence of partial seen anomaly
data, which reflects its robustness in the face of real-world complexity.
Comparison on UCF-Crime: As shown in Table II, our proposed method outperforms previous weakly supervised methods in terms of AUC metrics under different conditions of seen
anomaly categories. Specifically, compared to the SOTA method
VadCLIP [46], our method achieves superior performance under
different seen anomaly category conditions, achieving performance gains of 0.95%, 0.1%, 0.48%, and 0.34%, respectively.
As shown in Table III, we also achieved comparable performance
with VadCLIP under closed-set conditions. Similarly, compared
to other methods, our method also achieves varying degrees of

3138

IEEE TRANSACTIONS ON MULTIMEDIA, VOL. 27, 2025

TABLE I
COMPARISONS UNDER DIFFERENT SEEN ANOMALY IN XD-VIOLENCE

TABLE II
COMPARISONS UNDER DIFFERENT SEEN ANOMALY IN UCF-CRIME

TABLE III
COMPARISONS UNDER CLOSE-SET SETTING ON XD-VIOLENCE AND
UCF-CRIME DATASETS

performance gain under different open set conditions. This reflects the superiority of our approach in the open world.
In addition, We find that the standard deviation in XDViolence is much larger than that in UCF-Crime, implying that
the selection of different unseen anomalies in XD-Violence has
a greater impact on the model. This is particularly severe when

the number of unseen anomalies is 1. We believe that this is
mainly due to differences in the video sources of the dataset.
The videos in XD-Violence are mainly derived from movies and
web videos, which often contain numerous scene changes and
complex action behaviors. In contrast, UCF-Crime’s videos are
mainly derived from surveillance cameras, which have relatively
homogeneous scenes and shooting angles.
Performance in Seen and Unseen Categories: In addition, in
order to prove that the proposed method has stronger detection
ability for the unseen category, we conduct experiments on the
seen and unseen categories separately. Specifically, we set Seen
Category Set to {Fighting, Shooting, Riot, Abuse} and Unseen
Category Set to {Car Accident, Explosion} on XD Violance
dataset, while we set Seen Category Set to {Abuse, Arrest, Arson, Assault, Burglary, Explosion, Fighting, Road Accidents,
Robbery} and Unseen Category Set to {Shooting, Shoplifting, Stealing, Vandalism} on UCF-Crime dataset. As shown in
Tables IV and V, our proposed method achieves better performance than other SOTA methods in both seen and unseen categories. More importantly, the performance improvement of our
method on the unseen categories is significantly greater than
that on the seen categories, which proves the effectiveness of
our method on the unseen category.
Comparison of different methods on each category: In order
to explore in more detail the performance of different methods
for specific categories in open scenarios, we further conducted

HUANG et al.: MULTIMODAL EVIDENTIAL LEARNING FOR OPEN-WORLD WEAKLY-SUPERVISED VIDEO ANOMALY DETECTION

TABLE IV
COMPARISONS BETWEEN SEEN AND UNSEEN CATEGORY IN XD-VIOLENCE

TABLE V
COMPARISONS BETWEEN SEEN AND UNSEEN CATEGORY IN UCF-CRIME.

Fig. 3.

Comparison of different methods on seen and unseen categories.

experiments for each Base category and Novel category. Specifically, we set Seen Category Set to {Fighting, Shooting} and Unseen Category Set to {Riot, Abuse, Car Accident, Explosion} on
XD Violance dataset. As shown in Fig. 3, our method achieves
the best performance under open-set conditions in almost all
Base and Novel categories, which reflects the effectiveness and
superiority of our proposed method. Meanwhile, for the Novel
category, the performance under the open-set condition is still
quite different from that under the closed-set condition, which
means that there is still a lot of scope for improvement in the
current open-world video anomaly detection methods.
C. Ablation Study
In this section, ablation experiments are performed under the
condition of 4 seen anomaly categories and closed-set to verify
the effectiveness of the different modules. Specifically, we investigate the model performance gain of the proposed MTVM and
MECL by adding different module combinations in the network.
The results of the ablation study are illustrated in Table VI. The
MTVM and MECL are independent of each other, and each can
achieve better results compared to the baseline. Among them,
two modules have achieved performance gains of 0.41% and
1.7% in the 4 seen anomaly category condition, while they have
achieved performance gains of 0.43% and 1.67% in the closed set
condition. Therefore, we can conclude both MTVM and MECL

3139

TABLE VI
ABLATION STUDY OF MODULES

contribute to the performance gain. Moreover, the final result
of the ablation study demonstrates that the joint application of
proposed modules can further bring a great performance improvement, which proves the effectiveness and rationality of our
modules.
It is noteworthy that the proposed MTVM module needs to
compute the contextual details of each frame, which imposes a
certain computational burden. Specifically, the resulting complexity is mainly related to the video length and feature dimension. Assuming the length of the video is lv , the feature dimension is dv , and the number of fused segments is M. Then the
computational complexity is lv ∗ M ∗ d2v . Thus, the computational complexity is directly proportional to the length of the
video, the longer the video, the more computation is required.
It is also proportional to the square of the feature dimension,
which means that an increase in the feature dimension leads to a
significant increase in the computation. In addition, the number
of fused segments M also affects the computational complexity,
with more fused segments implying a more complex computational process. In practical applications, a combination of these
factors may need to be considered to balance computational efficiency and model performance. This can ensure that the model
can efficiently sense contextual information without putting too
much pressure on the computational resources.
Furthermore, the overall performance on close-set is better
when the MECL module is used individually. This is due to the
fact that the model under the closed-set condition is able to learn
wealthier features and patterns from seen anomalous events, thus
providing more accurate predictions in most cases. However,
the open-set condition brings larger performance gains than the
closed-set condition. This indicates that the MECL module is
more effective in identifying and distinguishing between normal and unseen abnormal events. This may be associated with
the MECL module’s ability to better capture the distributional
characteristics of the data under open-set conditions, as well as
to more accurately evaluate uncertainty.
D. Qualitative Results
In Fig. 4, we show the qualitative results of our proposed
method and the baseline (without MTVM and MECL) on unseen
and seen anomalies for the XD-Violence dataset. For continuous
unseen anomalous events, like riot and shooting, our method
produces high confidence in the anomalous region with precise
time boundaries, which reflects good detection performance for
unseen continuous anomaly. However, the anomalous events are
often complex and discontinuous in the real world. As shown in
fighting and car accident, it is easy to see that our model still has
difficulty in predicting time boundaries of unseen discontinuity

3140

IEEE TRANSACTIONS ON MULTIMEDIA, VOL. 27, 2025

Fig. 4. The qualitative results of our proposed method and the baseline without (MTVM and MECL) on unseen and seen anomalies for the XD-Violence dataset.
The light blue range represents abnormal ground truth.

events accurately. And it’s worth paying attention to the fact
that, for continuous seen anomalous events (like explosion and
abuse), our method produces high confidence in the anomalous
region with precise time boundaries. These results reflect its
similarly positive effect on the categories of seen anomaly.
In conclusion, our method achieves the detection of unseen
anomalies under open-world conditions to a certain extent.
However, there are still significant challenges in the complex
real-world because of the discontinuity and unpredictability of
unseen anomalies.
E. Sensitivity Analysis of Parameters
In this section, we discuss the parameters that are critical
to model performance. In addition to the hyperparameters

needed for the training process and the learnable parameters
in the network, the fusion weight of β plays a significant role
in controlling the fusion quality of multi-scale temporal visual
modeling features. Therefore, it is essential to explore the
appropriate range of β.
As shown in Fig. 5, we investigate the parameter sensitivity regarding the percentage of β for the XD-Violence dataset
and UCF-Crime dataset. Specifically, as the weight parameter
β increases, the evaluation metrics generally exhibit an initial
increase, followed by an decrease, and then another increase.
Regarding the performance in XD-Violence, the optimal
model performance is typically achieved when β is approximately 0.1. Regarding the performance in UCF-Crime, the optimal model performance is typically achieved when β is approximately 0.2. Ideally, useful information within the range of

HUANG et al.: MULTIMODAL EVIDENTIAL LEARNING FOR OPEN-WORLD WEAKLY-SUPERVISED VIDEO ANOMALY DETECTION

Fig. 5.

The changing trend of fusion weight β.

temporal context perception is transferred to the current frame
so that it can capture a certain range of temporal context information without affecting the representation of the current frame.
V. CONCLUSION
In this paper, we propose a multi-scale evidential learning
method for open-world weakly supervised anomaly detection,
which is driven by vision-language pre-trained model. Specifically, we commence by extracting features from both the video
and label text using the encoders of the pre-trained model.
Specifically, we learn generalized visual and textual feature representation from vision-language pre-trained model and capture
useful information in temporal context through multi-scale temporal visual modeling module. We then collect and jointly leverage multimodal evidence to achieve weakly-supervised video
anomaly detection in the open world. Extensive experimental
results demonstrate the effectiveness of components in our proposed framework, which also show that our method outperforms
those existing methods on XD-Violence and UCF-Crime for
open-world weakly-supervised video anomaly detection.
REFERENCES
[1] A. O. Tur, N. Dall’Asen, C. Beyan, and E. Ricci, “Exploring diffusion
models for unsupervised video anomaly detection,” in Proc. 2023 IEEE
Int. Conf. Image Process., 2023, pp. 2540–2544.
[2] Y. Liu, Z. Guo, J. Liu, C. Li, and L. Song, “OSIN: Object-centric scene inference network for unsupervised video anomaly detection,” IEEE Signal
Process. Lett., vol. 30, pp. 359–363, 2023.
[3] C. Tao et al., “Feature reconstruction with disruption for unsupervised video anomaly detection,” IEEE Trans. Multimedia, vol. 26,
pp. 10160–10173, 2024.
[4] T. M. Tran, D. C. Bui, T. V. Nguyen, and K. Nguyen, “Transformer-based
spatio-temporal unsupervised traffic anomaly detection in aerial videos,”
IEEE Trans. Circuits Syst. Video Technol., vol. 34, no. 9, pp. 8292–8309,
Sep. 2024.
[5] C. Zhang et al., “Exploiting completeness and uncertainty of pseudo labels
for weakly supervised video anomaly detection,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2023, pp. 16271–16280.
[6] M. Cho et al., “Look around for anomalies: Weakly-supervised anomaly
detection via context-motion relational learning,” in Proc. IEEE/CVF
Conf. Comput. Vis. pattern Recognit., 2023, pp. 12137–12146.
[7] Z. Yang, J. Liu, and P. Wu, “Text prompt with normality guidance for
weakly supervised video anomaly detection,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2024, pp. 18899–18908.

3141

[8] S. Sun et al., “TDSD: Text-driven scene-decoupled weakly supervised
video anomaly detection,” in Proc. ACM Int. Conf. Multimedia, 2024,
pp. 5055–5064.
[9] J. Chen, L. Li, L. Su, Z.-j. Zha, and Q. Huang, “Prompt-enhanced
multiple instance learning for weakly supervised video anomaly detection,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2024,
pp. 18319–18329.
[10] Y. Fan, Y. Yu, W. Lu, and Y. Han, “Weakly-supervised video anomaly
detection with snippet anomalous attention,” IEEE Trans. Circuits Syst.
Video Technol., vol. 34, no. 7, pp. 5480–5492, Jul. 2024.
[11] Q. Jiang et al., “Unsupervised decomposition and correction network for
low-light image enhancement,” IEEE Trans. Intell. Transp. Syst., vol. 23,
no. 10, pp. 19440–19455, Oct. 2022.
[12] J. Hu, Q. Jiang, R. Cong, W. Gao, and F. Shao, “Two-branch deep neural
network for underwater image enhancement in HSV color space,” IEEE
Signal Process. Lett., vol. 28, pp. 2152–2156, 2021.
[13] Q. Jiang, Y. Kang, Z. Wang, W. Ren, and C. Li, “Perception-driven deep
underwater image enhancement without paired supervision,” IEEE Trans.
Multimedia, vol. 26, pp. 4884–4897, 2024.
[14] Y. Kang et al., “A perception-aware decomposition and fusion framework
for underwater image enhancement,” IEEE Trans. Circuits Syst. Video
Technol., vol. 33, no. 3, pp. 988–1002, Mar. 2023.
[15] Q. Jiang, Y. Gu, C. Li, R. Cong, and F. Shao, “Underwater image enhancement quality evaluation: Benchmark dataset and objective metric,”
IEEE Trans. Circuits Syst. Video Technol., vol. 32, no. 9, pp. 5959–5974,
Sep. 2022.
[16] Q. Jiang et al., “Single image super-resolution quality assessment: A realworld dataset, subjective studies, and an objective metric,” IEEE Trans.
Image Process., vol. 31, pp. 2279–2294, 2022.
[17] H. K. Joo, K. Vo, K. Yamazaki, and N. Le, “CLIP-TSA: Clip-assisted
temporal self-attention for weakly-supervised video anomaly detection,”
in Proc. 2023 IEEE Int. Conf. Image Process., 2023, pp. 3230–3234.
[18] P. Wu et al., “Open-vocabulary video anomaly detection,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2024, pp. 18297–18307.
[19] A. Radford et al., “Learning transferable visual models from natural language supervision,” in Proc. Int. Conf. Mach. Learn., 2021, pp. 8748–8763.
[20] A. Jsang, Subjective Logic: A Formalism for Reasoning Under Uncertainty. Cham, Switzerland: Springer, 2018.
[21] W. Sultani, C. Chen, and M. Shah, “Real-world anomaly detection in
surveillance videos,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.,
2018, pp. 6479–6488.
[22] C. Zhang et al., “Dynamic erasing network based on multi-scale temporal features for weakly supervised video anomaly detection,” 2023,
arXiv:2312.01764.
[23] Y. Dang et al., “Discriminative action snippet propagation network for
weakly supervised temporal action localization,” ACM Trans. Multimedia
Comput., Commun. Appl., vol. 20, no. 6, pp. 1–21, 2024.
[24] X. Xie et al., “Attention erasing and instance sampling for weakly supervised object detection,” IEEE Trans. Geosci. Remote Sens., vol. 62, 2024,
Art. no. 5600910.
[25] F. Ye et al., “Attribute restoration framework for anomaly detection,” IEEE
Trans. Multimedia, vol. 24, pp. 116–127, 2020.
[26] F.-T. Hong, J.-C. Feng, D. Xu, Y. Shan, and W.-S. Zheng, “Cross-modal
consensus network for weakly supervised temporal action localization,”
in Proc. 29th ACM Int. Conf. Multimedia, 2021, pp. 1591–1599.
[27] M. Baradaran and R. Bergevin, “Multi-task learning based video anomaly
detection with attention,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., 2023, pp. 2886–2896.
[28] Z. Yang, J. Liu, Z. Wu, P. Wu, and X. Liu, “Video event restoration based
on keyframes for video anomaly detection,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2023, pp. 14592–14601.
[29] Z. Ye et al., “Unsupervised video anomaly detection with self-attention
based feature aggregating,” in Proc. 2023 IEEE 26th Int. Conf. Intell.
Transp. Syst., 2023, pp. 3551–3556.
[30] Y. Zhu, W. Bao, and Q. Yu, “Towards open set video anomaly detection,”
in Proc. Eur. Conf. Comput. Vis., 2022, pp. 395–412.
[31] H. Zhou, J. Yu, and W. Yang, “Dual memory units with uncertainty regulation for weakly supervised video anomaly detection,” in Proc. AAAI
Conf. Artif. Intell., 2023, pp. 3769–3777.
[32] M. Siemon, T. B. Moeslund, B. Norton, and K. Nasrollahi, “Bounding
boxes and probabilistic graphical models: Video anomaly detection simplified,” 2024, arXiv:2407.06000.
[33] Y. Tian et al., “Weakly-supervised video anomaly detection with robust
temporal feature magnitude learning,” in Proc. IEEE/CVF Int. Conf. Comput. Vis., 2021, pp. 4975–4986.

3142

[34] M. Chen, J. Gao, and C. Xu, “Uncertainty-aware dual-evidential learning
for weakly-supervised temporal action localization,” IEEE Trans. Pattern
Anal. Mach. Intell., vol. 45, no. 12, pp. 15896–15911, Dec. 2023.
[35] J. Gao, M. Chen, and C. Xu, “Collecting cross-modal presence-absence
evidence for weakly-supervised audio-visual event perception,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2023, pp. 18827–18836.
[36] M. Chen, J. Gao, and C. Xu, “Cascade evidential learning for open-world
weakly-supervised temporal action localization,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2023, pp. 14741–14750.
[37] W. Wang, Y. Yang, and Y. Pan, “Visual knowledge in the big model era:
Retrospect and prospect,” Frontiers Inf. Technol. Electron. Eng., vol. 26,
no. 1, pp. 1–19, 2025.
[38] Z. Yang, G. Chen, X. Li, W. Wang, and Y. Yang, “DoraemonGPT: Toward
understanding dynamic scenes with large language models,” in Proc. 41st
Int. Conf. Mach. Learn., 2024, pp. 55976–55997.
[39] H. Fang, P. Wu, Y. Li, X. Zhang, and X. Lu, “Unified embedding alignment
for open-vocabulary video instance segmentation,” in Proc. Eur. Conf.
Comput. Vis., 2024, pp. 225–241.
[40] X. Zhang, P. Zhao, J. Ji, X. Lu, and Y. Yin, “Video corpus moment retrieval
via deformable multigranularity feature fusion and adversarial training,”
IEEE Trans. Circuits Syst. Video Technol., vol. 34, no. 8, pp. 6686–6698,
Aug. 2024.
[41] R. Mokady, A. Hertz, and A. H. Bermano, “ClipCap: Clip prefix for image
captioning,” 2021, arXiv:2111.09734.
[42] W. Yu et al., “Turning a clip model into a scene text detector,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2023, pp. 6978–6988.
[43] H. Luo et al., “CLIP4Clip: An empirical study of CLIP for end to end video
clip retrieval and captioning,” Neurocomputing, vol. 508, pp. 293–304,
2022.
[44] A. Dubey et al., “The Llama 3 herd of models,” 2024, arXiv:2407.21783.
[45] C. Huang et al., “Pixel-level anomaly detection via uncertainty-aware prototypical transformer,” in Proc. 30th ACM Int. Conf. Multimedia, 2022,
pp. 521–530.
[46] P. Wu et al., “VadCLIP: Adapting vision-language models for weakly
supervised video anomaly detection,” in Proc. AAAI Conf. Artif. Intell.,
2024, vol. 38, no. 6, pp. 6074–6082.
[47] C. Huang et al., “Weakly supervised video anomaly detection via
self-guided temporal discriminative transformer,” IEEE Trans. Cybern.,
vol. 54, no. 5, pp. 3197–3210, May 2024.
[48] C. Huang et al., “Hierarchical graph embedded pose regularity learning
via spatio-temporal transformer for abnormal behavior detection,” in Proc.
30th ACM Int. Conf. Multimedia, 2022, pp. 307–315.
[49] P. Wu et al., “Not only look, but also listen: Learning multimodal violence
detection under weak supervision,” in Proc. 16th Eur. Conf. Comput. Vis.,
2020, pp. 322–339.
[50] J.-C. Wu, H.-Y. Hsieh, D.-J. Chen, C.-S. Fuh, and T.-L. Liu, “Selfsupervised sparse representation for video anomaly detection,” in Proc.
Eur. Conf. Comput. Vis., 2022, pp. 729–745.
[51] X. Zhou et al., “Learning weakly supervised audio-visual violence
detection in hyperbolic space,” Image Vis. Comput., vol. 151, 2024,
Art. no. 105286.
[52] Y. Pu, X. Wu, L. Yang, and S. Wang, “Learning prompt-enhanced context
features for weakly-supervised video anomaly detection,” IEEE Trans.
Image Process., vol. 33, pp. 4923–4936, 2024.
[53] I. Loshchilov and F. Hutter, “Decoupled weight decay regularization,”
2017, arXiv:1711.05101.
[54] J.-C. Feng, F.-T. Hong, and W.-S. Zheng, “MIST: Multiple instance
self-training framework for video anomaly detection,” in Proc. IEEE/CVF
Conf. Comput. Vis. pattern Recognit., 2021, pp. 14009–14018.
[55] S. Li, F. Liu, and L. Jiao, “Self-training multi-sequence learning with transformer for weakly supervised video anomaly detection,” in Proc. AAAI
Conf. Artif. Intell., 2022, vol. 36, no. 2, pp. 1395–1403.
[56] Y. Chen et al., “MGFN: Magnitude-contrastive glance-and-focus network
for weakly-supervised video anomaly detection,” in Proc. AAAI Conf. Artif. Intell., 2023, vol. 37, no. 1, pp. 387–395.
[57] R. Girdhar et al., “Imagebind: One embedding space to bind them
all,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2023,
pp. 15180–15190.
[58] H. Liu, C. Li, Y. Li, and Y. J. Lee, “Improved baselines with visual instruction tuning,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.,
2024, pp. 26296–26306.
[59] L. Zanella, W. Menapace, M. Mancini, Y. Wang, and E. Ricci, “Harnessing
large language models for training-free video anomaly detection,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2024, pp. 18527–18536.
[60] P. Wu et al., “Open-vocabulary video anomaly detection,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2024, pp. 18297–18307.

IEEE TRANSACTIONS ON MULTIMEDIA, VOL. 27, 2025

Chao Huang (Member, IEEE) received the Ph.D. degree in computer science and technology from the
Harbin Institute of Technology, Shenzhen, China, in
2022. From 2019 to 2022, he was a Visiting Scholar
with Peng Cheng Laboratory, Shenzhen. He is currently an Assistant Professor with the School of Cyber Science and Technology, Sun Yat-sen University,
Shenzhen. He has authored or coauthored more than
40 technical papers in prestigious international journals and conferences. His research interests include
anomaly detection, multimedia analysis, object detection, image/video compression, and deep learning. Dr. Huang was the recipient of the Distinguished Paper Award of AAAI 2023, and his dissertation
was nominated for the Harbin Institute of Technology’s Outstanding Dissertation Award. He is also an Associate Editor for Pattern Recognition and is/was
the Reviewer/PC Member for several top-tier journals and conferences, including IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE,
IEEE TRANSACTIONS ON IMAGE PROCESSING, IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, ACM CSUR, CVPR, ICCV, ECCV, ICML,
NeurIPS, ICLR, AAAI, IJCAI, and ACM Multimedia.

Weiliang Huang received the B.E. and M.E. degree
in electronic information engineering from the School
of Shantou University, Shantou, China, in 2020 and
2024, respectively. He is currently working toward
the Ph.D. degree in computer and information science with the University of Macau, Taipa, Macau. His
research interests include anomaly detection, image
segmentation, vision-language model, and prompt
learning.

Qiuping Jiang (Senior Member, IEEE) is currently a
Full Professor with the School of Information Science
and Engineering, Ningbo University, Ningbo, China.
His research interests include image quality assessment, visual perception modeling, and underwater visual information processing. He is also an Associate
Editor for several SCI-indexed journals such as Displays, Journal of Visual Communication and Image
Representation, IET Image Processing, and Journal
of Electronic Imaging.

Wei Wang received the B.S. degree from the School
of Science, Anhui Agricultural University, Hefei,
China, in 2015, the M.S. degree from the School
of Computer Science and Technology, Anhui University, Hefei, China, in 2018, and the Ph.D. degree
from the School of Software Technology, Dalian University of Technology, Dalian, China, in 2022. He is
currently a Postdoctoral researcher with the School
of Cyber Science and Technology, Shenzhen Campus, Sun Yat-Sen University, Shenzhen, China. His
research interests include transfer learning, zero-shot
learning, and deep learning.

HUANG et al.: MULTIMODAL EVIDENTIAL LEARNING FOR OPEN-WORLD WEAKLY-SUPERVISED VIDEO ANOMALY DETECTION

Jie Wen (Senior Member, IEEE) received the Ph.D.
degree in computer science and technology from the
Harbin Institute of Technology, Shenzhen, China, in
2019. He is currently an Associate Professor with
the School of Computer Science and Technology,
Harbin Institute of Technology, Shenzhen. His research interests include image and video enhancement, pattern recognition, and machine learning. He
has authored or coauthored more than 100 technical
papers at prestigious international journals and conferences, including IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, IEEE TRANSACTIONS ON IMAGE
PROCESSING, IEEE TRANSACTIONS ON CYBERNETICS, NeurIPS, ICML, CVPR,
AAAI, IJCAI, and ACM MM. He is also an Associate Editor for IEEE TRANSACTIONS ON IMAGE PROCESSING, IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, Pattern Recognition, and International Journal of Image
and Graphics, the Area Editor of Information Fusion. He was the Area Chair of
ACM MM and ICML. He was also selected for the ‘World’s Top 2% Scientists
List’ in 2021-2024. His one paper was the recipient of the Distinguished Paper
Award from AAAI’23. For more information, please refer to the homepage:
https://sites.google.com/view/jerry-wen-hit/home.

3143

Bob Zhang (Senior Member, IEEE) received the
Ph.D. degree in electrical and computer engineering from the University of Waterloo, Waterloo, ON,
Canada, in 2011. He was a Postdoctoral Researcher
with the Department of Electrical and Computer Engineering, Carnegie Mellon University, Pittsburgh,
PA, USA. He is currently an Associate Professor with
the Department of Computer and Information Science, University of Macau, Taipa, Macau. His research interests include biometrics, pattern recognition, and image processing. He is also a Technical Committee Member of the IEEE Systems, Man, and Cybernetics Society
and an Associate Editors for IEEE TRANSACTIONS ON IMAGE PROCESSING,
IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, IEEE
TRANSACTIONS ON SYSTEMS, MAN, AND CYBERNETICS, and Artificial Intelligence Review.
PAPER_TEXT
