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
# [385] CLIP-Based Multi-Modal Feature Learning for Cloth-Changing Person Re-Identification
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
编号：385
题名：CLIP-Based Multi-Modal Feature Learning for Cloth-Changing Person Re-Identification
年份：2025
DOI：10.1109/tip.2025.3602641
来源：IEEE Transactions on Image Processing
PDF：paper/10.1109_TIP.2025.3602641.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：无
相关性：弱相关，分数 1
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\385.txt
- 原始字符数：66651
- 本次发送字符数：66651
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
5570

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

CLIP-Based Multi-Modal Feature Learning for
Cloth-Changing Person Re-Identification
Guoqing Zhang , Member, IEEE, Jieqiong Zhou, Lu Jiang, Yuhui Zheng , Member, IEEE,
and Weisi Lin , Fellow, IEEE
Abstract—Contrastive Language-Image Pre-training (CLIP)
has achieved remarkable results in the field of person
re-identification (ReID) due to its excellent cross-modal understanding ability and high scalability. Since the text encoder of
CLIP mainly focuses on easy-to-describe attributes such as clothing, and clothing is the main interference factor that reduces the
recognition accuracy in cloth-changing person ReID (CC ReID).
Consequently, directly applying CLIP to cloth-changing scenario
may be difficult to adapt to such dynamic feature changes,
thereby affecting the precision of identification. To solve this
challenge, we propose a CLIP-based multi-modal feature learning
framework (CMFF) for CC ReID. Specifically, we first design
a pose-aware identity enhancement module (PIE) to enhance
the model’s perception of identity-intrinsic information. In this
branch, to weaken the interference of clothing information,
we apply a ranking loss to minimize the difference between
appearance and pose in the feature space. Secondly, we propose
a global-local hybrid attention module (GLHA), which fuses
head and global features through a cross-attention mechanism,
enhancing the global recognition ability of key head information.
Finally, considering that existing CLIP-based methods often
ignore the potential importance of shallow features, we propose a graph-based multi-layer interactive enhancement module
(GMIE), which groups and integrates multi-layer features of the
image encoder, aiming to enhance the contextual awareness of
multi-scale features. Extensive experiments on multiple popular
pedestrian datasets validate the outstanding performance of our
proposed CMFF.
Index Terms—CC ReID, contrastive language-image pretraining, graph attention network.

I. I NTRODUCTION

P

ERSON re-identification (ReID) aims to retrieve target
pedestrians across non-overlapping camera networks (as

Received 17 January 2025; revised 11 July 2025; accepted 21 August 2025.
Date of publication 1 September 2025; date of current version 5 September
2025. This work was supported in part by the National Natural Science
Foundation of China under Grant 62172231, Grant 92470202, and Grant
U22B2056; and in part by the Natural Science Foundation of Jiangsu Province
of China under Grant BK20220107. The associate editor coordinating the
review of this article and approving it for publication was Prof. Liqiang Nie.
(Corresponding author: Yuhui Zheng.)
Guoqing Zhang is with the College of Computer Science and Software
Engineering, Hohai University, Nanjing 210098, China, and also with the
School of Computer Science, Nanjing University of Information Science and
Technology, Nanjing 211544, China (e-mail: guoqingzhang@nuist.edu.cn).
Jieqiong Zhou and Lu Jiang are with the School of Computer Science,
Nanjing University of Information Science and Technology, Nanjing 211544,
China (e-mail: jieqiongz1999@163.com; jianglu2024@nuist.edu.cn).
Yuhui Zheng is with the Key Laboratory of Tibetan Information Processing,
Ministry of Education, Qinghai Normal University, Xining 810008, China
(e-mail: zhengyh@vip.126.com).
Weisi Lin is with the School of Computer Science and Engineering, Nanyang Technological University, Singapore 639798 (e-mail:
wslin@ntu.edu.sg).
Digital Object Identifier 10.1109/TIP.2025.3602641

Fig. 1. Retrieval examples for short-term (e.g., in a same day) person ReID.

illustrated in Fig. 1). During recent years, it has become
a crucial technique in various public safety and monitoring, including criminal suspect tracking, missing person
localization, and intelligent traffic management. However, in
real-world scenarios, recognition accuracy is affected by many
factors, such as illumination changes, object occlusion, cross
resolution, and modality differences. Therefore, researchers
have proposed a large number of methods to deal with the
above challenges [1], [2], [3], [4]. For example, Zhang et al.
[1] proposed a progressive difference elimination model that
reduces the impact of cross-modal and intra-class differences
between visible light and infrared modalities on recognition
by fusing visible and infrared stripes and generating highquality transitional modality images. Li et al. [2] achieved
resolution-invariant image representation through generative
adversarial networks, successfully recovering the lost details in
low-resolution input images. Lin et al. [3] proposed a temporal
camera contrast learning framework, aiming to reduce the
intra-ID discrepancy caused by background shift in unsupervised person re-identification and accurately extract invariant
semantic cues in pedestrian images.
While these methods demonstrate promising results under
controlled conditions, they fundamentally rely on the assumption of stable appearance features – an assumption frequently
violated in practical long-term surveillance scenarios. As
shown in Fig. 2, clothing changes over days or months
significantly alter pedestrian appearance, posing substantial
challenges for conventional appearance-based ReID systems.

1941-0042 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

ZHANG et al.: CLIP-BASED MULTI-MODAL FEATURE LEARNING FOR CLOTH-CHANGING PERSON ReID

5571

Fig. 3. Example of traditional image-text person ReID, where yellow box
represents correct matches and red boxes denote incorrect ones.

Fig. 2. An example of correct matches of a pedestrian in clothing-changing
scenarios.

This limitation underscores the urgent need to develop
clothing-invariant ReID methods that maintain robust performance during long-term real-world deployment.
To deal with the interference of clothing changes on identity
information, researchers have conducted in-depth studies in
the field of clothing-change ReID (CC ReID). Existing CC
ReID methods can be primarily classified into two groups:
one focuses on mining clothing-independent biomodal information, such as body contour, gait and posture [5], [6], [7].
To mitigate the influence of clothing information, the other
methods separate clothing from the non-clothing human parts
[8], [9], [10], [11] and focus on non-clothing parts to improve
recognition accuracy. However, methods that rely on auxiliary
biological modalities will greatly limit identity features in
the case of poor image quality (such as severe occlusion
or low-light environment). In addition, merely removing the
clothing part will not only damage the integrity of the nonclothing area, but also lead to the loss of crucial identity
information. Recently, contrastive language-image pre-training
[12] (CLIP) has attracted widespread attention due to its excellent zero-shot learning capabilities and has achieved superior
progress in multiple computer vision fields such as object
classification [13], anomaly detection [14], and semantic segmentation [15]. In the person ReID tasks, CLIP improves the
model’s capability to capture pedestrian identity features by
analyzing the intricate semantic connection between images
and textual descriptions, thus boosting both the precision and
textcolorbluerobustness of recognition. For instance, Yan et
al. [16] proposed a CLIP-driven framework CFine, which
aims to exploit the powerful multi-modal knowledge of CLIP
to mine fine-grained and discriminative details for effective
global alignment. In addition, to deal with the partial loss of
appearance details due to occlusion, Cui et al. [17] proposed a
prompt-guided feature disentanglement method (ProFD) that
generates robust local features through text prompt activation
and utilization of the rich knowledge pre-trained in the model.
Although the CLIP model demonstrates great potential in
multi-modal representation learning, it also encounters significant challenges that cannot be ignored when applying it

directly to the CC ReID task; we use CLIP-ReID [18] as
our backbone network and evaluating on the clothing dataset
Celebreid [19]. The visual outcomes of some experiments are
presented in Fig. 3, and it is evident that although CLIP is
able to generate text cues that are closely related to pedestrian
clothing, its cross-modal capability does strengthen the connection between visual content and text descriptions. However,
the model shows obvious deficiencies in handling identity
information interference caused by clothing changes. This
limitation mainly stems from CLIP’s pre-training mechanism,
which tends to emphasize salient features of visual elements
such as clothing, while ignoring subtle features, such as facial
features or body posture that are critical to identity recognition.
To tackle the aforementioned challenges, we put forward a
CLIP-based multi-modal feature fusion network (CMFF) for
CC ReID, which combines image, text, and biological (head,
posture) modalities to enhance the model’s robustness. Firstly,
we propose a pose-aware identity enhancement module that
leverages the pose estimation model HRNet [20] to capture
the detailed pose information of pedestrians. By combining the
pose information with the global visual features obtained from
CLIP, the model’s ability to perceive the inherent characteristics of pedestrian identities can be enhanced. Among them,
to minimize the impact of clothing changes on recognition
accuracy, we use the ranking loss function to fine-tune the
model to effectively narrow the semantic distance between
posture and appearance features. Furthermore, given that the
head region contains richer identity information than other
body parts, we adopt an innovative global-local hybrid attention to promote the interaction between global features and
head features. This fusion strategy not only allows to guide
and strengthen the emphasis on head information from a global
perspective, but also enables head features to be contextually
enhanced based on global information, aiming to significantly
improving feature representation capability. Finally, to enhance
the information flow between features at each layer of the
image encoder, we employ a graph attention structure to
carefully group and integrate features from multiple layers,
thereby optimizing the semantic richness and discriminability
of the overall feature hierarchy.
Our primary contributions are outlined in the following
points.
• We propose a CLIP-based multi-modal feature fusion
network (CMFF) for CC ReID that combines image, text,
and biological modalities information to strengthen the
model’s robustness in identity recognition.

5572

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

• We propose a posture-aware identity enhancement module (PIE), designed to enhance the model’s capability
of perceiving inherent identity information of individuals
by fusing global appearance features with structural pose
features.
• We propose a global-local hybrid attention module
(GLHA) to contextually enhance head features by leveraging global information, aiming to guide and strengthen
the attention on head information from a global perspective.
• We propose a graph-based multi-layer interactive
enhancement module (GMIE) that applies a graph attention mechanism to finely group and fuse multi-layer
image encoder features, effectively enhancing the semantic richness and discriminability at the feature level,
significantly boosting the model’s overall performance.
II. R ELATED W ORKS
A. Cloth-Changing Person Re-Identification
Person ReID aims to retrieve images of the same pedestrian
from different camera perspectives and plays a vital role in
public safety applications. However, most existing methods
[21], [22] depend on clothing information as the primary
identifier, ignoring the fact that pedestrians clothing changes
in real scenes. Consequently, cloth-changing person ReID has
attracted a large number of scholars to study as an emerging
topic, with its primary objective being to identify and learn
stable identity features that are independent of clothing.
1) Auxiliary Biological Information Based Methods:
Thanks to the collection of multiple cloth-changing pedestrian
datasets [19], [23] [24], [25], CC ReID research has made
great progress. To reduce the visual interference caused by
clothing changes, mainstream methods use auxiliary information such as gait [5], [26], silhouette/shape [6], [27], face [28],
[29] and posture [7] to learn clothing independent identity
features. Feng et al. [27] proposed AGS-Net, an attentionguided two-stream framework that utilizes visual and contour
information from RGB images and silhouette sketches as
discriminative features. This two-branch structure focuses on
identity-related features while minimizing sensitivity to clothing changes using an attention module. Nguyen et al. [7]
proposed a contrastive clothing and pose generation framework
(CCPG) to jointly learn clothing-independent features through
appearance and shape, and generate cross-identity clothing
and pose transformation images to enrich training samples,
thereby supervising the learning of discriminative features.
Wu et al. [28] recovered the lost facial details from the
teacher network and propagate them to a smaller network,
aiming to mine sensitive identity cues in faces. Compared with
short-term ReID methods, these methods have significantly
improvements in clothing changing scenes, but they rely too
much on the acquisition of auxiliary information, which limits
the scalability and generalization of the model and also leads
to a significant increase in computational costs. In addition, the
high requirements for image quality of this method mean that
once pedestrians are blocked or in a dark light environment,
the generated auxiliary information will inevitably contain
noise, affecting the stability of training.

2) Clothing Decoupling Based Methods: Another mainstream methods is to decouple the clothing parts of the
human body from the non-clothing parts, enabling the model
to concentrate on learning clothing-independent features [8],
[9], [10], [11]. Eom et al. [8] proposed an identity shuffled
adversarial network that using only identity labels without
any auxiliary supervision signals to separate identity-related
and irrelevant features from portraits. Zheng et al. [10]
proposed a joint learning framework that separates the appearance and shape features of each image and exchanges them
within and between identities to achieve data augmentation.
SAVS [11] located the human body and clothing regions
through human semantic segmentation, masked clues related
to clothing appearance, and only focuses on visual semantic
knowledge that is insensitive to view/pose changes. However,
due to the lack of exact ground truth guidance, the entire
feature decoupling process is performed implicitly, which
makes the model inevitably disturbed by clothing features
when extracting clothing-independent features. In addition, the
high computational overhead incurred by these methods when
processing large-scale data remains a problem that needs to
be optimized.
B. CLIP in Person Re-Identification Task
Contrastive Language-Image Pre-training [12] has demonstrated remarkable zero-shot learning capabilities by adopting
a contrastive learning strategy on a large-scale multi-modal
dataset. Its core idea is to map images and descriptive text into
the same vector space through contrastive learning, optimize
the similarity between images and text and learn the representation of the association between visual content and language
descriptions. As a result, it is not limited to fixed datasets
and predefined categories when processing visual tasks, but
can also understand concepts or objects that have not been
seen during training. This training strategy gives CLIP strong
generalization capabilities, enabling it to effectively perform
zero-shot inference on a range of visual tasks, including finegrained object classification [13], anomaly detection [14], and
semantic segmentation [15].
Recently, researchers have explored the use of CLIP in
the domain of person ReID [18] and have made significant
progress in scenarios such as visible-infrared [30], occlusion
[31] and lifelong learning [31]. Acknowledging that highlevel semantics of pedestrian appearance are consistent across
modalities, Yu et al. [30] proposed a CLIP-driven semantic
discovery network, which seeks to bridge the gap between
visible and infrared modalities by combining visual features
with high-level semantics. To address the challenge of crossdomain knowledge mismatch in lifelong person ReID under
different clothing states, LReID-Hybrid [32] leveraged the
consistency and generalization of the text space and introduced
a framework that efficiently aligns, transfers, and accumulates
knowledge, creating an image-text-image closed loop. He et
al. [31] designed a multi-granularity contrastive consistency
alignment framework, aiming to semantically align occluded
visual effects and query text by leveraging intra-granular/intergranular visual text representations.

ZHANG et al.: CLIP-BASED MULTI-MODAL FEATURE LEARNING FOR CLOTH-CHANGING PERSON ReID

5573

Fig. 4. The CLIP-based multi-modal feature learning framework (CMFF) we proposed consists of two stages.The first training phase fixes the text encoder
and image encoder and optimizes a set of learnable text tags to generate text features. In the second stage, the visual encoder adopts a three-branch structure
to enhance the accuracy of identity recognition. Specifically, posture-aware identity enhancement module (PIE) improves the perception of identity features
by introducing posture information; global-local hybrid attention module (GLHA) targets crucial head information to boost global recognition; graph-based
multi-layer interactive enhancement (GMIE) module groups and integrates the image encoder’s multi-layer features to enhance the contextual awareness of
multi-scale features.

Later, the CLIP model has also been explored for clothingchanging scenarios, but this attempt has encountered some
challenges that cannot be ignored: since the CLIP model tend
to emphasize visible and describable attributes during training,
which may lead to the model to over-focusing on clothing features in CC ReID scenarios, while ignoring intrinsic features
that are more closely related to personal identity, such as the
head and pedestrian profile.
To this end, we propose a CLIP-based multi-modal feature
learning framework (CMFF), which adopts a multi-branch
structure to mine biological modalities such as posture and
head to enhance the recognition of identity information.
Furthermore, we use the graph structure to fuse the multilayer features of the image encoder, enhancing the contextual
understanding ability of multi-scale features.
III. M ETHOD
A. Overview
In our framework, we adopt CLIP-ReID [18] as the backbone network, which enhances the missing text information
via a collection of pre-trained learnable text tags. The entire
method is split into two stages, as illustrated in Fig. 4.
In the initial training stage, we adopt learnable text tags
associated with each identity to handle ambiguous text descriptions and ensure that these descriptions are unique for each
ID. Specifically, the text description T (·) is formatted as a
photo of a [X]1 [X]2 [X]3 . . . [X] M person”, where each [X]m
(m ∈ {1, . . . , M}) is a learnable text tag, and M represents the total number of text tags. In this stage, we refine
model by image-to-text contrastive loss Li2t and text-to-image
contrastive loss Lt2i , aiming to enhance the consistency of
cross-modal representation:
!
exp(s(Vi , T i ))
,
(1)
Li2t = − log PB
a=1 exp(s(Vi , T a ))

and
exp(s(Vi , T i ))

Lt2i = − log PB

a=1 exp(s(Va , T i ))

!
,

(2)

where s(·, ·) denotes the cosine similarity, which is used to
calculate the similarity between image embedding Vi and text
embedding T i in the cross-modal space. In addition, it is
also used to compare the similarity of Vi with other text
embeddings T a in the same batch.
In the second stage, we first fuse the pose information
with global visual features extracted by CLIP to improve the
model’s capability to perceive the inherent characteristics of
pedestrian identity. Then, we propose a global-local hybrid
attention module that emphasizes head information based on
a global perspective and enhances head features in context
through global information. Finally, we apply a graph attention
mechanism to finely group and integrate multi-layer image
encoder features to enhance the model’s contextual awareness
and feature-level semantic richness.
B. Posture-Aware Identity Enhancement Module
Since CLIP’s text encoder primarily focuses on easily
describable attributes (e.g., clothing), it struggles to capture
subtle but crucial identity-specific features such as body structure and posture. To address this limitation and reduce the
model’s dependency on clothing-related features, we propose
a pose-aware identity enhancement module (PIE) that aims to
leverage the inherent body structure information of pedestrians to enhance the model’s perception of persistent identity
markers that remain stable across clothing variations.
Pedestrian posture plays a key role in embodying key
structural information about the human body, such as characteristics that remains invariant across changes in attire, lighting
conditions, and viewing perspectives. By combining it with
global visual features, we aim to mitigate the influence of

5574

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

ID should be smaller than the distance between the global
features and posture features (negative sample pairs) belonging
to different IDs. Meanwhile, the distance between posture
features of different IDs needs to be increased, which ensures
that the model can focus more on the inherent characteristics of
pedestrians rather than the changeable appearance information
during the recognition process. Therefore, we propose the
inter-class ranking loss Lcross and the intra-class ranking loss
Lintra :
Lcross
N

Fig. 5. Visualization of the ranking loss, where the same color borders
represent the same ID. The purpose of the loss is to make RGB-pose pairs of
the same identity closer and separate RGB-pose pairs of different identities.

=



1 X
a
a
−
max 0, δ1 + k fg,i
− f p,+j k2 − k fg,i
− f p,t
k2 ,
N

(6)

i=1

Lintra
N

clothing variations on global visual representations, thereby
enhancing the model’s stability and robustness under significant changes in pedestrian appearance. Specifically, for a given
pedestrian image xi , we employ the pose estimation model
HRNet [20] to locate the coordinates of K body key points.
Based on these coordinates, we generate individual heatmaps
Hk (k = 1, 2, . . . , K) as follows:


(x − xk )2 + (y − yk )2
,
(3)
Hk (x, y) = exp −
2σ2
where (x, y) represents the spatial coordinates of a point in
the heatmap, σ represents standard deviation of the Gaussian
kernel, controlling the spread of the distribution, and (xk , yk ) is
the location of the k-th key point in the image. Furthermore, we
aggregate all K individual heatmaps into a combined posture
heatmap Hm :
K
X
Hm =
Hk ,
(4)
k=1
W×H

where Hm ∈ R
, with W and H denoting the width and
height of the heatmap, respectively. To integrate local pose
information with global visual features, we first expand the
global image features fg ∈ RD to match the spatial dimensions
of the posture heatmap Hm , and then perform element-wise
multiplication to obtain the pose-enhanced features f p :
f p = Hm

Expand( fg , W, H),

(5)

where
denotes
element-wise
multiplication,
Expand(·, W, H) is a function that reshapes the dimension of
a feature to W ∗ H. The fusion process enriches the feature
details and improves contextual relevance by combining pose
and global visual information.
Inspired by the contrastive loss based on silhouette sketches
and RGB images in [6], we introduce a ranking loss Lrank ,
which aims to reduce the dependence of appearance features
on clothing information by minimizing the distance between
appearance features and pose features, thereby enhancing the
model’s attention to the core information of pedestrian identity.
The specific calculation process is shown in Fig. 5, and
in a batch, there are N images and their corresponding N
posture heat maps. The distance between the RGB features and
posture features (positive sample pairs) belonging to the same

=



1 X
a
a
−
max 0, δ2 + k f p,i
− f p,+j k2 − k f p,i
− f p,t
k2 ,
N

(7)

i=1

where k · k2 represents the Euclidean distance, δ1 and δ2
are preset interval thresholds, which are used to guarantee
that the distance between the positive sample feature and the
anchor point is significantly less than the distance between
the negative sample and the anchor point. Afterwards, we
optimize the model performance by integrating Lcross and Lintra
losses into the total ranking loss function and using weight
coefficients λ1 and λ2 to adjust their weights in the total loss.
The specific formula is as follows:
Lrank = λ1 Lcross + λ2 Lintra .

(8)

C. Global-Local Hybrid Attention Module
Although CLIP is good at capturing the global features of
an image, it often ignores the importance of local regions,
especially the head region, which usually contains more key
and rich identity recognition features than other parts of the
body. To overcome this limitation and enhance the model’s
ability to focus on key identity regions, we propose a globallocal hybrid attention module to enhance the model’s ability
to focus on head features by effectively fusing with global
information. For a given image xi , we first apply the pose
estimation model [20] to accurately locate the key points of the
human head and shoulders. Then, based on these key points,
we use the advanced image segmentation algorithm Mask RCNN to accurately extract the head and neck area from the
entire image. Next, we feed both full pedestrian image and
its corresponding head image into image encoder separately.
Considering the difference in dimensions between the two
inputs, we perform adaptive pooling operations on the global
and head images in the global and head branches respectively,
thereby obtaining the global feature fg and head feature fh .
The global-local hybrid attention is shown in Fig. 6. We first
perform different linear transformations on fg and fh to map
them into the form of query (Q), key (K) and value (V), respectively. Different from traditional self-attention mechanism, we
use the query vector of fg to pay attention to the key and value
(V) vectors of fh , and vice versa. Then, we combine these
two weighted features through the concatenation operation

ZHANG et al.: CLIP-BASED MULTI-MODAL FEATURE LEARNING FOR CLOTH-CHANGING PERSON ReID

5575

to the low to high levels of Transformer. We empirically set
the number of groups to t=3 as it provides an optimal balance
between feature diversity and information completeness, which
is further validated through ablation studies in Section IV. We
then establish the relationship between nodes based on the
features. The edge weight eit j is determined by the similarity
between nodes, reflecting the relative importance of node i in
relation to node j in t-th group, and the calculation formula
of eit j is as follows:
eit j = P

Fig. 6. Illustration of the global-local hybrid attention module (GLHA), which
aims to enhance the importance of head information from global perspective.

concat(·, ·) to form the final fused feature Fg−h . The detailed
expression is provided below:


Qg KhT
Ag-h = softmax
Vh ,
(9)
√
d !
Qh KgT
Vg ,
(10)
Ah-g = softmax
√
d
Fg−h = concat(Ag-h fg , Ah-g fh ).

(11)

In this way, our model can effectively capture the interdependence between head features and the global context of the
whole body image.

Most existing CLIP-based methods use the final layer
features of the image encoder (ViT) as the main visual
representation, which may ignore the valuable information
contained in the intermediate layers. To address this underutilization of multi-scale features and enhance the contextual
understanding ability of the model, we propose a graph-based
multi-layer interactive enhancement module (GMIE).
The detailed architecture of GMIE is shown in Fig. 7.
Firstly, we extract the output features of each layer from the
ViT model and denote X (l) ∈ RN×D as the output features of
the l th layer, where l ∈ {1, 2, . . . , 12}, N and D represents
the sequence length and feature dimension. Prior to inputting
these features into the graph attention module, we perform
layer normalization on the output features of each layer:
X (l) − µ(l)
,
(12)
 + σ(l)
where  is a small constant that prevents the denominator from
being zero, µ(l) which σ(l) represent the mean and standard
deviation of X (l) respectively, and are computed as follow:
X̂ (l) =

D

1 X (l)
X:,d ,
D
d=1
v
u
D
u1 X
(l)
(l)
σ = t
(X:,d
− µ(l) )2 .
D

(q)
(i)
k∈Ni exp(sim( X̂t , X̂t ))

,

(15)

where sim(·, ·) denotes cosine similarity between two nodes,
and Ni represents the set of neighbors of node i. Then, we
calculate the attention coefficient αit j between the two nodes,
which quantifies the influence of the neighboring node X̂t(i) on
node X̂t( j) during the feature update process:
αit j = P

eit j exp(LeakyReLU(aT [Wti kWtj ]))
q
j
ij
T
q∈Ni et exp(LeakyReLU(a [Wt kWt ]))

,

(16)

where W is a learnable linear transformation matrix, a is a
learnable vector for calculating attention and k represents the
concatenation of vectors. We then update the node features hit
with the adjusted attention coefficients:
0
1
X iq (i)
αt X̂t A ,
(17)
hit = ReLU @
q∈Ni

D. Graph-Based Multi-Layer Interactive Enhancement
Module

µ(l) =

exp(sim(X̂t(i) , X̂t( j) ))

(13)

(14)

d=1

Subsequently, we map the normalized features to graph
nodes and divide the nodes into three groups (t = 3) according

where ReLU(·) represents nonlinear activation function. Afterwards, we aggregate each group of node features through
maximum pooling to obtain the final feature ht of each group:
ht = maxpooling(h1t , h2t , h3t , h4t ), t ∈ {1, 2, 3}.

(18)

Finally, we concatenate the outputs of each group processed
by the graph attention network to construct the final feature
representation Fgraph of GMIE, aiming to leverage features
of each layer in the image encoder to improve the model’s
robustness in complex scenarios.
E. Adaptive Fusion and Model Optimization
1) Adaptive Feature Fusion: To maximize the utilization
of information from different branches and optimize the final
feature representation, we perform a adaptive fusion operations
on the output features of the three branches. Specifically, we
initialize the weights of each branch through fully connected
layer and normalize them with softmax function. According to
these generated weights, we perform weighted aggregation of
the three feature vectors, and adaptively adjusted the weights
during back propagation:
F f used = w pose f p + wg−h Fg−h + wgraph Fgraph .

(19)

2) Model Optimization: In the first stage, we employ the
image-to-text contrast loss Li2t and text-to-image contrast loss
Lt2i to reduce cross-modal discrepancy between images and
textual descriptions. The overall loss function is formulated as
follows:
L stage1 = Lt2i + Li2t .
(20)

5576

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

Fig. 7. Illustration of graph-based multi-layer interactive enhancement module.

In the second stage, we first apply a ranking loss Lrank in
the pose-aware identity enhancement moduleto minimize the
discrepancy between appearance and pose features. Furthermore, we adopt identity loss LID and triplet loss Ltri to achieve
further optimization of the model:

LID = −
Ltri =

C
X

1
N

yi log(pi ),

i=1
N
X


max 0, m + dap − dan ,

(21)

(22)

i=1

where C denotes number of categories, yi is the one-hot
encoding of the true label, pi is the predicted probability of the
corresponding category of the mode. N refers to the number
of samples in same batch, dap represents distance between the
anchor sample and the positive sample, and dan indicates the
distance from the anchor sample to the negative sample.
To fully exploit the potential of CLIP, we adopt an imageto-text cross-entropy loss to ensure that image features closely
correspond to the corresponding text descriptions while keeping distance from text features of other irrelevant identities:
!
N
X
e s(Vi ,Tyk )
Li2tce(i) = −
log PN
.
(23)
s(Vi ,T ya )
ya =1 e
k=1
where V represents the overall visual features fused in the
second stage, and S (·, ·) is used to calculate the similarity
score.
Thus, the overall loss function for the second stage is
expressed as follows:
L stage2 = Lrank + LID + Ltri + Li2tce .

(24)

IV. E XPERIMENTS
A. Datasets and Evaluation Metrics
1) Datasets: To assess the effectiveness of our proposed
CMFF method, we perform experiments on four publicly
available cloth-changing pedestrian datasets: VC-Clothes [23],
Celeb-reID [24], Celeb-reID-light [19], and NKUP [25]. In
particular, for the VC-clothes dataset, we set two scenarios:
one is “general”, which includes both clothing changes and
clothing consistency scenes; the other is “cloth-changing”,
which only includes clothing changes. The characteristics of
each dataset are summarized in Table I.
2) Evaluation Metrics: Following previous methods, we
adopt the first-rank hit rate (Rank-1) and mean average precision (mAP) as metrics to assess the efficacy of our proposed
CMFF.
B. Implementation Details
In this study, we use ViT-B-16 in the CLIP ReID framework
as the backbone network. The images are first resized to
256 × 128 resolution to accommodate the network input
requirements. To improve the generalization of the model,
we apply a series of data augmentation techniques, including
random horizontal flipping, random erasing, and edge padding.
During data loading, we use a hybrid sampler that combines
softmax and triplet loss, processes 4 instances per batch and
uses 8 worker threads for parallel data processing. The training
process of this study is optimized in two stages.
In the first stage, we use Adam optimizer with a batch size
of 128, a base learning rate of 3.5 ×10−4 , and a training
cycle of 60 epochs. In the second stage, the training cycle
is extended to 120 epochs, while the batch size remains
unchanged. The base learning rate is reduced to 0.5 ×10−5 ,
the number of iterations is set to 10, and both weight decay
and bias weight decay are configured at 0.1 ×10−3 .

ZHANG et al.: CLIP-BASED MULTI-MODAL FEATURE LEARNING FOR CLOTH-CHANGING PERSON ReID

5577

TABLE I
I NTRODUCTION TO THE DATASET U SED IN THE E XPERIMENT, W HERE ‘SC’ R EPRESENTS THE S AME C LOTHING AND ‘CC’ R EPRESENTS D IFFERENT
C LOTHING

TABLE II
C OMPARISON W ITH SOTA M ETHODS ON VC-C LOTHES (%)

C. Performance Evaluations and Comparison
In this experiment, we compare our method with the current
state-of-the-art (SOTA) methods on the VC-Clothes, NKUP,
Celeb-reID, and Celeb-reID-light datasets. In addition, we
further compare and analyze the performance differences of
these methods with or without auxiliary information.
1) Results on VC-Clothes: Consistent with previous studies, our comparative experiments on the VC-Clothes dataset
adopt the following two settings: 1) General setting, where
gallery sets include both samples with clothing changes and
samples with the same clothing; 2) Cloth-Changing setting,
where the gallery sets just contain samples that have undergone
clothing changes. As shown in Table II, our method achieves
the highest performance in both settings. Compared with the
second-best method DSIFLF [42], our method improves Rank1 and mAP by 0.5% and 0.2% in Cloth-Changing scenarios,
and improves mAP by 1.3% in the General scenarios. Among
the contrasting methods, GLH [41] utilizes a multi-branch
architecture to capture both global and local identity information, and trains local body parts by clustering the generated
pseudo labels for cross-image comparison. However, this
strategy that relies on automatically generated pseudo labels
may introduce errors due to inconsistent label quality, thus
affecting the accuracy and robustness of the model. FSAM [35]
enhances clothing-independent features by transferring finegrained body shape knowledge between two stream branches.
DSIFLF [42] uses a human body parsing model to erase

clothing parts, suppresses the fluctuations caused by clothing
texture in the identity feature space, and reduces the dependence on interference factors during discriminative learning by
generating adversarial interference factor decoupling networks.
GI-ReID [37] incorporates gait recognition as an auxiliary
task and utilizes unique gait information to guide model in
learning features that are independent of clothing. Although
these methods improve the accuracy of feature extraction
through single biomodal information, they also significantly
rely on the quality and consistency of the data, which limits
their generalization ability in new environments or changing
conditions. In contrast, our method combines pose estimation
and global features, fully leveraging the identity recognition
information of the head, which substantially enhances the
model’s capacity to capture inherent identity information.
2) Results on Celeb-reID and Celeb-reID-Light: We perform comparative experiments with state-of-the-art methods
on the Celeb-reID and Celeb-reID-light datasets, with detailed
results provided in Table III. Obviously, ours surpasses all
comparative methods on both datasets. MADE [50] extracts
personal attribute descriptions through attribute detection
model and masks out clothing and color information. However,
when clothing attributes are closely combined with other body
features, masking clothing attributes alone is not enough to
completely eliminate all clothing-related information. AFDNet [44] and SAFR [11] use generative adversarial networks
to separate identity-related and irrelevant features. Among
them, the decoupling and reconstruction of AFD-Net rely

5578

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

TABLE III
C OMPARISON W ITH SOTA M ETHODS ON C ELEB - RE ID AND C ELEB - RE ID-L IGHT DATASETS (%)

TABLE IV
C OMPARISON W ITH SOTA M ETHODS ON NKUP DATASET (%)

on complex self-supervision, which increases the difficulty of
training and is less efficient. Although SAFR learns disentangled features from random samples, the quality and diversity
of input samples limit its generalization ability. 3DInvarReID
[49] innovatively uses 3D body model to separate identity
and non-identity features, but extreme posture changes and
clothing diversity may reduce the accuracy and efficiency of its
decoupling. In contrast, our approach employs a multi-branch
architecture to extract critical identity cues from the head
and posture, while leveraging a graph attention mechanism to
aggregate multi-scale features, thereby significantly enhancing
the model’s performance in complex scenarios.
3) Results on NKUP: We conduct comparative experiments
with existing methods on the NKUP dataset, and the results
are shown in Table IV. In this experiment, our CMFF method
obtains the second highest performance, with rank-1 and mAP
0.9% and 8.5% lower than IGCL [54] respectively. The main
reason is that the images of the NKUP dataset are collected in
a dark environment, and the image clarity is low. IGCL introduces clothing attention activation maps to mask clues related
to the appearance of clothes, and enriches the expression

of different postures under the same identity through image
stitching technology, which can effectively extract human
semantic information independent of the background and adapt
to the posture changes of pedestrians. These strategies enable
IGCL to show a strong advantage in processing low-definition
images. CCUP [48] also demonstrated the effectiveness of
synthetic data pre-training in CC-ReID tasks, where the pretrain-fine-tune framework leverages large-scale synthetic data
to enhance the generalization ability of the model. However,
the performance gap compared to IGCL suggests that synthetic
pre-training may be of limited effectiveness for low-quality
surveillance scenarios like NKUP, where field-specific adaptation methods (such as the attention mechanism and pose
enhancement strategy of IGCL) show greater advantages when
handling low-resolution images under challenging lighting
conditions.
D. Ablation Study
1) Effectiveness of Graph Structure Grouping: We perform
an in-depth analysis on the impact of feature grouping in
GMIE module and set different grouping numbers n = {1,
2, 3, 4, 6} for experiments. The results presented in Fig. 8
demonstrate that mode’s performance fluctuates significantly
with change of the number of groups. In particular, when
n=1, the mAP of the model is always the lowest regardless
of the nature of the dataset; while when n = 3, it performs
optimally on all datasets. In addition, the number of groups
that is too low or too high will cause performance degradation.
The main reason is that when features are only divided into
one group, the model that relies on a single fusion output may
over-compress information, resulting in the loss of critical finegrained features such as edges and textures, which are essential
for identifying small differences in complex scenes. It is
evident that a moderate increase in the number of groups (such
as n = 3) can effectively retain and utilize features at different
scales, balance the diversity and completeness of information
through the complementarity of features within each group,

ZHANG et al.: CLIP-BASED MULTI-MODAL FEATURE LEARNING FOR CLOTH-CHANGING PERSON ReID

Fig. 8. Results with different numbers of groups on four cloth-changing
pedestrian datasets.
TABLE V
C OMPARISON W ITH SOTA M ETHODS ON VC-C LOTHES , NKUP AND
C ELEB - RE ID DATASETS (%)

and thus optimize the model performance. However, too many
groups (such as n = 4 or 6) will lead to over-dispersion of
features, resulting in insufficient information in each group,
which is not conducive to effective learning and recognition,
thereby reducing the overall performance. Therefore, choosing
the appropriate number of groups is extremely critical to
improving model accuracy and adaptability.
2) Effectiveness of Each Module: We assess the contribution of each branch in CMFF framework through experiments
conducted on three cloth-changing datasets: VC-Clothes,
NKUP and Celeb-reID. We set CLIP ReID with Vision Transformer as the backbone network as the baseline, and integrate
Pose-aware identity enhancement module (PIE), global-local
hybrid attention module (GLHA) and graph-based multi-layer
interactive enhancement module (GMIE) on this baseline, as
well as different combinations of these modules, to explore
their specific impact on performance. Table V lists all the
results, and its cumulative matching feature (CMC) curve is
shown in Fig. 9. First, we can find that the introduction of
a single module has achieved an improvement in accuracy
relative to the baseline model on the three datasets. Specifically, the improvements of the PIE module on mAP are 0.4%,
0.5% and 0.2% respectively; the improvements of the GLHA
module are 0.8%, 0.6% and 0.5%; and the improvements of the

5579

GMIE module are 1.4%, 0.3% and 1.4%. Secondly, PIE and
GLHA, as biometric learning branches, focus on extracting
pedestrian posture and head information respectively. The
combination of the two achieves 1.3%, 2.0% and 2.7% Rank1 improvement on the three datasets respectively compared
with the baseline, proving complementarity of the two modules
and their effectiveness in extracting discriminative features.
On this basis, the GMIE module was introduced, and the
Rank-1 accuracy was further improved by 1.3%, 0.6%, and
1.4%, verifying the effect of enhancing multi-scale context
perception.
To highlight the individual contribution of each module more clearly, we further conduct ablation experiments
by removing each component from the full model. The
results demonstrate substantial performance degradation when
excluding any single module: (1) removing the PIE module
leads to Rank-1 accuracy drops of 1.5%, 0.6%, and 0.7%
on the three datasets; (2) eliminating GLHA resulting in a
more significant drop of 2.1%, 1.1%, and 1.5%; (3) removing
GMIE causes a drop of 1.3%, 0.6%, and 1.2%. The findings
reveal that GLHA contributes most significantly to overall
performance, followed by GMIE and PIE, which is consistent
with the intuition that head features maintain the highest
reliability in clothing-changing scenarios. In addition, the
consistent performance drops across all modules confirm their
complementary nature and collective necessity for achieving
optimal results.
We also visualize each branch and combination on CelebreID dataset, as illustrated in Fig. 10. It can be seen that the
PIE, GLHA and GMIE modules alone outperform the baseline
model, with the combination of PIE and GLHA significantly
improving the matching rate for Ranks 1-10. Especially after
the introduction of the GMIE module, the model accuracy is
further improved, which is consistent with the results of our
ablation experiments.
3) Effectiveness of λ1 and λ2 : To comprehensively evaluate
the robustness of the model, we conduct ablation experiments
on the hyperparameters in the ranking loss function on the
dataset NKUP, where both parameters varied between 0.1 and
1.0, as shown in Table VI. The experimental results show
that the performance is optimal when λ1 = 0.5 and λ2 =
0.5, which indicates that balancing the weights of inter-class
and intra-class ranking loss is crucial for effective feature
learning. The model performs relatively stably in the range of
λ1 , λ2 ∈ [0.3,0.7], with performance fluctuations of less than
1%. However, when any parameter takes an extreme value (0.1
or 1.0), the performance will further degrade due to insufficient
inter-class distinction or over-constrained intra-class variation.
Therefore, the balanced parameter configuration ensures that
the model can effectively coordinate inter-class separation and
intra-class aggregation to achieve the optimal feature learning
effect.
4) Effectiveness of Ranking Loss in PIE Module: To verify
the effectiveness of our proposed ranking loss in the poseaware identity enhancement (PIE) module, we conducted
comparative experiments on two cloth-changing datasets:
NKUP, and Celeb-reID. As demonstrated in Table VII, we systematically three variants: (1) using our proposed ranking loss

5580

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

Fig. 9. Advantages of each module using CMC curves on NKUP, Celeb-reID and VC-Clothes datasets.

Fig. 10. Visualization of retrieval results on Celebreid dataset. The left side presents the results of our method (including various modules), and the right side
shows the results of CLIP-ReID. Rank-1 to Rank-10 are reported. Positive matches are indicated by green rectangles, and negative matches are highlighted
with red rectangles.

Lrank , (2) PIE using the standard L2 loss, and (3) the baseline.
Experimental results show that our ranking loss consistently
outperforms the other two alternatives on all datasets. It is

worth noting that the L2 loss method only slightly improves
over the baseline, and sometimes even performs worse, which
indicates that simple distance minimization is not sufficient for

ZHANG et al.: CLIP-BASED MULTI-MODAL FEATURE LEARNING FOR CLOTH-CHANGING PERSON ReID

5581

TABLE VI
P ERFORMANCE OF D IFFERENT λ1 AND λ2 C OMBINATIONS ON NKUP DATASET

TABLE VII
E FFECTIVENESS OF D IFFERENT L OSS F UNCTIONS IN PIE M ODULE (%)

TABLE IX
P ERFORMANCE C OMPARISON OF D IFFERENT ATTENTION M ECHANISMS IN
GLHA M ODULE

TABLE VIII
P ERFORMANCE C OMPARISON OF D IFFERENT F EATURE F USION IN GMIE
M ODULE

effective pose-appearance alignment. Therefore, our ranking
loss design effectively minimizes the intra-class distance while
maximizing the inter-class separation, which is crucial for
cloth-changing person ReID.
5) Effectiveness of Graph Structure in GMIE Module:
To verify the effectiveness of the graph structure in the
multi-layer interaction enhancement (GMIE) module, we conducted comparative experiments on two clothing-changing
datasets, NKUP and Celeb-reID, and the results are shown
in Table VIII. We designed three variants for comparison: (1)
GMIE using simple concatenation followed by linear projection, (2) GMIE using weighted average of multi-layer features,
and (3) GMIE using our proposed graph-structure-based
fusion method. Experimental results show that our method
significantly outperforms other alternatives on both datasets.
Although the simple concatenation method can integrate multilayer information, it is constrained by feature redundancy and
increased computational overhead, resulting in limited performance improvement. The weighted average method alleviates
the dimensionality explosion problem to a certain extent, but
it still cannot fully utilize cross-layer information due to the
lack of ability to model complex spatial relationships between
multi-scale features. In contrast, our graph structure effectively
captures the spatial correlation of cross-layer features by
adaptively learning the dependencies between features, thereby
achieving more robust multi-scale context understanding in the
cloth-changing person re-identification task.
6) Effectiveness of Bidirectional Attention in GLHA Module: To verify the superiority of the bidirectional attention

mechanism we designed in the GLHA module, we conducted
ablation experiments on the NKUP and Celeb-reID datasets,
comparing three attention mechanisms: unidirectional fg → fh
(global to head), unidirectional fh → fg (head to global),
and our proposed bidirectional method. The experimental
results in Table IX show that bidirectional attention can
consistently achieve the best performance on both datasets,
indicating that the mutual guidance between global features
and head features is crucial for effective identity representation
learning. Specifically, on the NKUP dataset, our bidirectional
method outperforms the best unidirectional variant ( fg → fh )
by 0.3% and 0.6% in Rank-1 and mAP, respectively. On
the Celeb-reID dataset, bidirectional attention outperforms
the unidirectional alternative by 0.2% and 0.7% in Rank-1
and mAP, respectively. This is sufficient to prove that the
bidirectional design effectively combines the advantages of
both directions, realizes comprehensive feature interaction and
achieves superior recognition accuracy.

V. C ONCLUSION
In this work, we have proposed a multi-modal feature learning method (CMFF) to tackle the challenges of cloth-changing
person Re-ID. First, we designed a pose-aware identity
enhancement module (PIE) that combines pose estimation with
global feature analysis to strengthen the model’s capacity of
discriminating essential identity features and narrow the gap
between appearance and pose-driven features through ranking
loss. Next, we introduced a global-local hybrid attention module (GLHA) to highlight key head information in the global
scope through head branch fusion with cross attention. Finally,
we adopt a graph-based multi-layer interactive enhancement
module (GMIE) to update and integrate multi-layer features of
the image encoder to enhance the context-awareness of multiscale features. Extensive experiments on several mainstream
cloth-changing pedestrian datasets demonstrates the superior
performance of our proposed CMFF.

5582

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

Despite our approach achieving promising results, it still
suffers from some limitations including computational complexity from the multi-branch architecture and dependency
on pose estimation accuracy. For future work, we plan to
integrate infrared modality to enhance performance in lowlight conditions, develop lightweight variants for practical
deployment, and explore video-based extensions with temporal
consistency, which may provide additional discriminative cues
for clothing-invariant ReID.
R EFERENCES
[1]

G. Zhang, Z. Wang, H. Wang, J. Zhou, and Y. Zheng, “Progressive
discrepancy elimination for visible–infrared person re-identification,”
Neurocomputing, vol. 607, Nov. 2024, Art. no. 128387.
[2] Y.-J. Li, Y.-C. Chen, Y.-Y. Lin, and Y.-C. F. Wang, “Cross-resolution
adversarial dual network for person re-identification and beyond,” 2020,
arXiv:2002.09274.
[3] G. Zhang, H. Zhang, W. Lin, A. K. Chandran, and X. Jing, “Camera
contrast learning for unsupervised person re-identification,” IEEE Trans.
Circuits Syst. Video Technol., vol. 33, no. 8, pp. 4096–4107, Aug. 2023.
[4] Y. Chen, G. Zhang, Y. Lu, Z. Wang, and Y. Zheng, “TIPCB: A simple but
effective part-based convolutional baseline for text-based person search,”
Neurocomputing, vol. 494, pp. 171–181, Jul. 2022.
[5] Y. Dong et al., “HybridGait: A benchmark for spatial–temporal clothchanging gait recognition with hybrid explorations,” in Proc. AAAI Conf.
Artif. Intell., 2024, vol. 38, no. 2, pp. 1600–1608.
[6] J. Zheng, X. Hu, T. Xiang, and P. P. K. Chan, “Dual-path model for
person re-identification under cloth changing,” in Proc. Int. Conf. Mach.
Learn. Cybern. (ICMLC), Dec. 2020, pp. 291–297.
[7] V. D. Nguyen, P. Mantini, and S. K. Shah, “Contrastive clothing and
pose generation for cloth-changing person re-identification,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. Workshops (CVPRW),
Jun. 2024, pp. 7541–7549.
[8] C. Eom, W. Lee, G. Lee, and B. Ham, “Disentangled representations for
short-term and long-term person re-identification,” IEEE Trans. Pattern
Anal. Mach. Intell., vol. 44, no. 12, pp. 8975–8991, Dec. 2022.
[9] P. P. K. Chan, X. Hu, H. Song, P. Peng, and K. Chen, “Learning disentangled features for person re-identification under clothes changing,” ACM
Trans. Multimedia Comput., Commun., Appl., vol. 19, no. 6, pp. 1–21,
Nov. 2023.
[10] Z. Zheng, X. Yang, Z. Yu, L. Zheng, Y. Yang, and J. Kautz, “Joint
discriminative and generative learning for person re-identification,” in
Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2019, pp. 2138–2147.
[11] Z. Gao, H. Wei, W. Guan, J. Nie, M. Wang, and S. Chen, “A semanticaware attention and visual shielding network for cloth-changing person
re-identification,” IEEE Trans. Neural Netw. Learn. Syst., vol. 36, no. 1,
pp. 1243–1257, Jan. 2025.
[12] A. Radford et al., “Learning transferable visual models from natural
language supervision,” in Proc. Int. Conf. Mach. Learn., vol. 139, 2021,
pp. 8748–8763.
[13] J. Xin, H. Tang, J. Gao, X. Du, S. He, and Z. Li, “Delving into
multimodal prompting for fine-grained visual classification,” in Proc.
AAAI Conf. Artif. Intell., 2023, pp. 2570–2578.
[14] Z. Zuo, J. Dong, Y. Wu, Y. Qu, and Z. Wu, “CLIP3D-AD: Extending
CLIP for 3D few-shot anomaly detection with multi-view images
generation,” 2024, arXiv:2406.18941.
[15] J. Chen et al., “Exploring open-vocabulary semantic segmentation from
CLIP vision encoder distillation only,” in Proc. IEEE/CVF Int. Conf.
Comput. Vis. (ICCV), Oct. 2023, pp. 699–710.
[16] S. Yan, N. Dong, L. Zhang, and J. Tang, “CLIP-driven fine-grained textimage person re-identification,” IEEE Trans. Image Process., vol. 32,
pp. 6032–6046, 2023.
[17] C. Cui, S. Huang, W. Song, P. Ding, M. Zhang, and D. Wang,
“ProFD: Prompt-guided feature disentangling for occluded person reidentification,” in Proc. 32nd ACM Int. Conf. Multimedia, Oct. 2024,
pp. 1583–1592.
[18] S. Li, S. Li, and Q. Li, “CLIP-ReID: Exploiting vision-language model
for image re-identification without concrete text labels,” in Proc. AAAI
Conf. Artif. Intell., vol. 37, 2023, pp. 1405–1413.
[19] Y. Huang, Q. Wu, J. Xu, and Y. Zhong, “Celebrities-ReID: A benchmark
for clothes variation in long-term person re-identification,” in Proc. Int.
Joint Conf. Neural Netw. (IJCNN), Jul. 2019, pp. 1–8.

[20] K. Sun, B. Xiao, D. Liu, and J. Wang, “Deep high-resolution representation learning for human pose estimation,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2019, pp. 5686–5696.
[21] G. Zhang, Y. Chen, Y. Zheng, G. Martin, and R. Wang, “Local-enhanced
representation for text-based person search,” Pattern Recognit., vol. 161,
May 2025, Art. no. 111247.
[22] G. Zhang, J. Li, Y. Zheng, and R. Wang, “InfinitePerson: Innovating
synthetic data creation for generalization person re-identification,” IEEE
Trans. Circuits Syst. Video Technol., vol. 35, no. 4, pp. 3160–3171, Apr.
2025.
[23] F. Wan, Y. Wu, X. Qian, Y. Chen, and Y. Fu, “When person
re-identification meets changing clothes,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. Workshops (CVPRW), Jun. 2020,
pp. 830–831.
[24] Y. Huang, J. Xu, Q. Wu, Y. Zhong, P. Zhang, and Z. Zhang, “Beyond
scalar neuron: Adopting vector-neuron capsules for long-term person
re-identification,” IEEE Trans. Circuits Syst. Video Technol., vol. 30,
no. 10, pp. 3459–3471, Oct. 2020.
[25] K. Wang, Z. Ma, S. Chen, J. Yang, K. Zhou, and T. Li, “A benchmark for
clothes variation in person re-identification,” Int. J. Intell. Syst., vol. 35,
no. 12, pp. 1881–1898, 2020.
[26] W. Li et al., “An in-depth exploration of person re-identification and
gait recognition in cloth-changing conditions,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2023, pp. 13824–13833.
[27] Z. Feng, S. Huang, and J. Lai, “Attention-guided Siamese network for
clothes-changing person re-identification,” in Proc. Int. Conf. Image
Graph., 2021, pp. 314–325.
[28] J. Wu, H. Liu, W. Shi, H. Tang, and J. Guo, “Identity-sensitive
knowledge propagation for cloth-changing person re-identification,” in
Proc. IEEE Int. Conf. Image Process. (ICIP), Oct. 2022, pp. 1016–1020.
[29] D. Arkushin, B. Cohen, S. Peleg, and O. Fried, “GEFF: Improving
any clothes-changing person ReID model using gallery enrichment with
face features,” in Proc. IEEE/CVF Winter Conf. Appl. Comput. Vis.
Workshops (WACVW), Jan. 2024, pp. 143–153.
[30] X. Yu, N. Dong, L. Zhu, H. Peng, and D. Tao, “CLIP-driven semantic
discovery network for visible-infrared person re-identification,” 2024,
arXiv:2401.05806.
[31] S. He et al., “Region generation and assessment network for occluded
person re-identification,” IEEE Trans. Inf. Forensics Security, vol. 19,
pp. 120–132, 2024.
[32] Q. Wang, X. Qian, B. Li, Y. Fu, and X. Xue, “Image-text-image
knowledge transferring for lifelong person re-identification with hybrid
clothing states,” 2024, arXiv:2405.16600.
[33] Y. Sun, L. Zheng, Y. Yang, Q. Tian, and S. Wang, “Beyond part models:
Person retrieval with refined part pooling (and a strong convolutional
baseline),” in Proc. Eur. Conf. Comput. Vis. (ECCV), 2018, pp. 480–496.
[34] K. Zhu, H. Guo, Z. Liu, M. Tang, and J. Wang, “Identity-guided
human semantic parsing for person re-identification,” in Proc. Eur. Conf.
Comput. Vis., 2020, pp. 346–363.
[35] P. Hong, T. Wu, A. Wu, X. Han, and W.-S. Zheng, “Fine-grained shapeappearance mutual learning for cloth-changing person re-identification,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun.
2021, pp. 10513–10522.
[36] X. Gu, H. Chang, B. Ma, S. Bai, S. Shan, and X. Chen,
“Clothes-changing person re-identification with RGB modality only,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun. 2022,
pp. 1060–1069.
[37] X. Jin et al., “Cloth-changing person re-identification from a single
image with gait prediction and regularization,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., Jun. 2022, pp. 14278–14287.
[38] Z. Yang, X. Zhong, Z. Zhong, H. Liu, Z. Wang, and S. Satoh, “Win-win
by competition: Auxiliary-free cloth-changing person re-identification,”
IEEE Trans. Image Process., vol. 32, pp. 2985–2999, 2023.
[39] Z. Zhao, B. Liu, Y. Lu, Q. Chu, N. Yu, and C. W. Chen, “Joint
identity-aware mixstyle and graph-enhanced prototype for clotheschanging person re-identification,” IEEE Trans. Multimedia, vol. 26,
pp. 3457–3468, 2024.
[40] Y. Ding, A. Wang, and L. Zhang, “Multidimensional semantic disentanglement network for clothes-changing person re-identification,” in Proc.
Int. Conf. Multimedia Retr., May 2024, pp. 1025–1033.
[41] D. T. Thanh, Y. Lee, and B. Kang, “Enhancing long-term person
re-identification using global, local body part, and head streams,”
Neurocomputing, vol. 580, May 2024, Art. no. 127480.
[42] Y. Li, D. Cheng, C. Fang, C. Jiao, N. Wang, and X. Gao, “Disentangling
identity features from interference factors for cloth-changing person reidentification,” in Proc. 32nd ACM Int. Conf. Multimedia, Oct. 2024,
pp. 2252–2261.

ZHANG et al.: CLIP-BASED MULTI-MODAL FEATURE LEARNING FOR CLOTH-CHANGING PERSON ReID

[43] G. Wang, Y. Yuan, X. Chen, J. Li, and X. Zhou, “Learning discriminative
features with multiple granularities for person re-identification,” in Proc.
26th ACM Int. Conf. Multimedia, Oct. 2018, pp. 274–282.
[44] W. Xu, H. Liu, W. Shi, Z. Miao, Z. Lu, and F. Chen, “Adversarial
feature disentanglement for long-term person re-identification,” in Proc.
30th Int. Joint Conf. Artif. Intell., Aug. 2021, pp. 1201–1207.
[45] G. Zhang, J. Liu, Y. Chen, Y. Zheng, and H. Zhang, “Multi-biometric
unified network for cloth-changing person re-identification,” IEEE
Trans. Image Process., vol. 32, pp. 4555–4566, 2023.
[46] Y. Huang et al., “Meta clothing status calibration for long-term person
re-identification,” IEEE Trans. Image Process., vol. 33, pp. 2334–2346,
2024.
[47] S. Yang, B. Kang, and Y. Lee, “Sampling agnostic feature representation
for long-term person re-identification,” IEEE Trans. Image Process.,
vol. 31, pp. 6412–6423, 2022.
[48] Q. Wang, X. Qian, B. Li, X. Xue, and Y. Fu, “Exploring finegrained representation and recomposition for cloth-changing person re-identification,” IEEE Trans. Inf. Forensics Security, vol. 19,
pp. 6280–6292, 2024.
[49] F. Liu, M. Kim, Z. Gu, A. Jain, and X. Liu, “Learning clothing
and pose invariant 3D shape representation for long-term person reidentification,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct.
2023, pp. 19617–19626.
[50] C. Peng, B. Wang, D. Liu, N. Wang, R. Hu, and X. Gao,
“Masked attribute description embedding for cloth-changing person reidentification,” 2024, arXiv:2401.05646.
[51] Z. Gao, H. Wei, W. Guan, W. Nie, M. Liu, and M. Wang, “Multigranular
visual-semantic embedding for cloth-changing person re-identification,”
in Proc. 30th ACM Int. Conf. Multimedia, Oct. 2022, pp. 3703–3711.
[52] Y. Yan et al., “Weakening the influence of clothing: Universal clothing
attribute disentanglement for person re-identification,” in Proc. 31st Int.
Joint Conf. Artif. Intell., Jul. 2022, pp. 1523–1529.
[53] Y. Zhao, C. Wu, Y. Xu, X. Du, R. Li, and G. Niu, “CCUP: A controllable
synthetic data generation pipeline for pretraining cloth-changing person
re-identification models,” 2024, arXiv:2410.13567.
[54] Z. Gao, S. Wei, W. Guan, L. Zhu, M. Wang, and S. Chen, “Identityguided collaborative learning for cloth-changing person reidentification,”
IEEE Trans. Pattern Anal. Mach. Intell., vol. 46, no. 5, pp. 2819–2837,
May 2024.

Guoqing Zhang (Member, IEEE) received the B.S.
and master’s degrees in information engineering
from Yangzhou University, Yangzhou, China, in
2009 and 2012, respectively, and the Ph.D. degree
in pattern recognition and intelligent systems from
Nanjing University of Science and Technology, Nanjing, China, in 2017. He is currently a Professor
with the School of Computer Science, Nanjing
University of Information Science and Technology
(NUIST), Nanjing. His current research interests
include computer vision, pattern recognition, and
machine learning.

5583

Jieqiong Zhou received the B.E. degree in software
engineering from Nanjing Xiaozhuang University in
2021. She is currently pursuing the master’s degree
with the School of Computer and Cyberspace Security, Nanjing University of Information Science and
Technology. Her research interests include pedestrian re-identification in clothing-changing scenarios
and related applications.

Lu Jiang received the master’s degree from Peking
University. She is currently pursuing the Ph.D.
degree with the School of Computer Science,
Nanjing University of Information Science and
Technology, Nanjing, China. Her research interests
include deep learning and computer vision.

Yuhui Zheng (Member, IEEE) was born in Shanxi,
China, in 1982. He received the B.Sc. degree in pharmacy engineering and the Ph.D. degree in pattern
recognition and intelligent systems from Nanjing
University of Science and Technology, Nanjing,
China, in 2004 and 2009, respectively. From 2014
to 2015, he was a Visiting Professor with the Digital Media Laboratory, School of Electronic and
Electrical Engineering, Sungkyunkwan University,
South Korea. He is currently a Full Professor at the
Key Laboratory of Tibetan Information Processing,
Ministry of Education, Qinghai Normal University. His main research areas
include image and video analysis, scene understanding, visual tracking, and
pattern recognition.

Weisi Lin (Fellow, IEEE) received the Ph.D. degree
from King’s College London, U.K. He is currently
a Professor with the School of Computer Science
and Engineering, Nanyang Technological University.
His research interests include image processing,
perceptual signal modeling, video compression, and
multimedia communication, in which he has published more than 200 journal articles, more than
230 conference papers, filed seven patents, and
authored two books. He is a fellow of the IET
and an Honorary Fellow of Singapore Institute of
Engineering Technologists. He was the Technical Program Chair of the IEEE
ICME 2013, PCM 2012, QoMEX 2014, and IEEE VCIP 2017. He has
been an invited/panelist/keynote/tutorial speaker at more than 20 international
conferences. He was a Distinguished Lecturer of the IEEE Circuits and
Systems Society from 2016 to 2017 and Asia–Pacific Signal and Information
Processing Association (APSIPA) from 2012 to 2013. He has been an
Associate Editor of IEEE T RANSACTIONS ON I MAGE P ROCESSING, IEEE
T RANSACTIONS ON C IRCUITS AND S YSTEMS FOR V IDEO T ECHNOLOGY,
IEEE T RANSACTIONS ON M ULTIMEDIA, and IEEE S IGNAL P ROCESSING
L ETTERS.
PAPER_TEXT
