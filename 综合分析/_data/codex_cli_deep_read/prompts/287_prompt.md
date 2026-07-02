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
# [287] ReFLIP-VAD: Towards Weakly Supervised Video Anomaly Detection via Vision-Language Model
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
编号：287
题名：ReFLIP-VAD: Towards Weakly Supervised Video Anomaly Detection via Vision-Language Model
年份：2024
DOI：10.1109/tcsvt.2024.3482007
来源：IEEE Transactions on Circuits and Systems for Video Technology
PDF：paper/10.1109_TCSVT.2024.3482007.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：其他AI安全与跨域异常检测、入侵检测与网络异常检测
相关性：弱相关，分数 3
已有代码状态：已下载；ReFLIP-VAD -> source\ReFLIP-VAD

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\287.txt
- 原始字符数：84757
- 本次发送字符数：84757
- 是否截断：False

代码包：
- 仓库：ReFLIP-VAD
  - URL：https://github.com/prasaddev97/ReFLIP-VAD
  - 状态：downloaded
  - 本地目录：source\ReFLIP-VAD
  - 顶层结构：LICENSE、README.md、ReFLIP/、crop.py、data/、list/、model.py、ucf_option.py、ucf_test.py、ucf_train.py、utils/、xd_option.py、xd_test.py、xd_train.py
  - 主要语言：Python:24
  - README 标题：ReFLIP-VAD、Framework、Highlights、<a name="2"></a> Prerequisites、Dataset、UCF-Crime、XD-Violence、Train and Test、<a name="6"></a> Results、References
  - README 运行线索：sh Das</a>；python ucf_train.py；python ucf_test.py；python xd_train.py；python xd_test.py；sh Das</a>；python ucf_train.py；python ucf_test.py
  - 关键文件：{"数据处理入口": ["utils/dataset.py"], "模型定义": ["model.py", "ReFLIP/model.py", "utils/layers.py"]}
  - 数据集线索：Quic、Tor、dapt、ton、tor

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2024.3482007

1

ReFLIP-VAD: Towards Weakly Supervised Video
Anomaly Detection via Vision-Language Model
Prabhu Prasad Dev, Graduate Student Member, IEEE, Raju Hazari, Member, IEEE, Pranesh Das, Member, IEEE

Abstract—The vision-language model has recently achieved
notable success in image-related tasks, showcasing its ability to
learn deep and meaningful visual representations. Applying this
robust model to video analysis for detecting anomalies poses a significant challenge. This paper introduces Reparameterized Finegrained Language Image Pretraining-Video Anomaly Detection
(ReFLIP-VAD), a novel approach designed to leverage visionlanguage capabilities for video anomaly detection. ReFLIP-VAD
employs a prompt encoder to generate reparameterized learnable
prompt templates, enhancing interpretability and understanding
of anomaly-specific semantics. The framework adopts a dualblock architecture: a classification block that uses visual features
for binary classification and a video-text alignment block that
integrates textual and visual features for precise language-vision
alignment. This proposed approach is further strengthened by
the Glimpse-Emphasize network that effectively captures both
global and local temporal dependencies across time and the
MIL-Align mechanism that selects the most representative video
frames for each label, representing the entire video. ReFLIPVAD has demonstrated superior performance on two largescale benchmark datasets achieving an Average Precision (AP)
of 86.29% on XD-Violence and an Area Under the Curve
(AUC) of 89.14% on UCF-Crime, significantly surpassing existing state-of-the-art methods. Our source code is available at
https://github.com/prasaddev97/ReFLIP-VAD.
Index Terms—Video anomaly detection, Weakly supervised,
Vision-language pre-training, Prompt template

I. I NTRODUCTION

V

IDEO anomaly detection(VAD) task has recently gained
significant attention in real-world scenarios, including
but not limited to public surveillance, transportation management, traffic monitoring, and military settings. This task is
approached through three primary paradigms, namely, FullySupervised VAD (FSVAD) [1], Unsupervised VAD (USVAD)
[2], and Weakly-Supervised VAD (WSVAD) [3]. Traditional
FSVAD is deemed impractical due to the scattered and diverse
anomalies that require extensive manual frame-level annotations. Conversely, unsupervised VAD, which relies solely on
learning from normal videos to identify open-set anomalies,
often generates false alarms. However, it is inherently challenging to determine what is normal and abnormal without
prior knowledge when provided only with normal videos. In
Corresponding author: Prabhu Prasad Dev
Prabhu Prasad Dev is with the Department of Computer Science and
Engineering, National Institute of Technology, Calicut, Kerala, India and
the School of Computer Engineering, KIIT Deemed to be University,
Bhubaneswar, Odisha, India (e-mail: prasaddev97@gmail.com).
Raju Hazari and Pranesh Das are with Department of Computer Science and
Engineering, National Institute of Technology, Calicut, Kerala, India (e-mail:
rajuhazari@nitc.ac.in, praneshdas@nitc.ac.in)

contrast to both FSVAD and USVAD, our primary focus is on
the practical paradigm of WSVAD, which utilizes only videolevel annotations. This paradigm results in reduced costs for
manual and detailed annotations.
Current research in the VAD domain typically follows a systematic approach. It starts with extracting only visual features
using visual backbone models, e.g., C3D [4], [5], I3D [6], [7],
ViT [8], which are pre-trained on activity recognition tasks.
These extracted features are then fed into binary classifiers
based on multiple instance learning (MIL) framework [9].
The last step involves detecting abnormal events using the
predicted anomaly confidence. Although these straightforward
approaches have shown potential results, they do not fully
harness cross-modal connections between vision and language.
In recent years, significant advancements have been observed in the advancement of vision-language models such
as Contrastive Language-Image Pre-training (CLIP) [10],
A Large-scale ImaGe and Noisy-text embedding (ALIGN)
[11], Context Optimization (CoOp) [12] and Fine-grained
Language-Image Pre-training (FLIP) [13]. These models aim
to acquire generalized visual representations enriched with
semantic concepts. The key idea behind CLIP is to align
images and text in a shared embedding space using contrastive
learning, allowing it to associate images with their textual
descriptions and perform various tasks involving vision and
language. Given the remarkable success of VLMs in recent
times, there is a growing interest in exploring the development
of task-specific models built upon CLIP.
Despite the evident potential of VLMs in diverse visual
tasks, their primary emphasis lies within the realm of static
images. Hence, it is imperative to thoroughly investigate
how to effectively transform a model trained on image-text
pairs into a tool capable of addressing the more intricate
challenge of video anomaly detection with limited supervision.
To harness generalized knowledge effectively and enable FLIP
to realize its full potential in the WSVAD task, it is crucial
to address specific challenges aligned with the characteristics
of WSVAD. Firstly, exploring methods to capture contextual
dependencies across time is vital. Secondly, determining how
to utilize acquired knowledge and enhance visual-language
connections is essential. Thirdly, maintaining vision-language
model performance in video anomaly detection scenarios is of
critical importance.
To effectively address the above-mentioned issues, a novel
framework ReFLIP-VAD is developed:Reparameterized Finegrained Language Image Pre-training for Video Anomaly
Detection. A Glimpse-Emphasize network is introduced to
address the first challenge based on a global-to-local strat-

© 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2024.3482007

2

egy. It comprises two key components: the Glimpse module
and the Emphasize module. The Glimpse module primarily
captures the global context information and the Emphasize
module extracts the local features. Addressing the second
challenge divergently from existing approaches that only rely
on visual features, ReFLIP-VAD incorporates textual features
with visual features. This multi-modality strategy aims to
maximize the preservation of learned knowledge. ReFLIPVAD involves a classification block and a video-text alignment block. The former leverages visual features for binary
classification while the latter leverages both textual and visual
features for language-vision alignment. Furthermore, these
blocks effortlessly accomplish both coarse-grained and finegrained weakly supervised video anomaly detection [14]. In
addition to these blocks, two prompt mechanisms namely the
multi-modal prompts and reparameterized learnable prompts
are introduced to enhance text label representations. Contrary
to existing methods [10], [12], [15], [16], which depend
on either hand-crafted or learnable prompts, the proposed
approach utilizes a prompt encoder, specifically DistilBERT
[17], to generate reparameterized learnable prompt template.
These templates are contextually rich and provide a level of
interpretability, facilitating a more detailed understanding of
the specific semantics associated with anomalies. To address
the third challenge, a multiple instance learning (MIL)-align
mechanism is utilized for the visual and language alignment
block.
The main contributions of this paper are outlined as follows:
1) A novel framework i.e. ReFLIP-VAD is developed that
employs a prompt encoder to generate reparameterized
learnable prompt templates instead of hand-crafted templates. These templates are contextually rich, enhancing
interpretability and providing a deeper understanding of
the specific semantics associated with anomalies.
2) The proposed approach comprises a classification block
and a video-text alignment block. The former leverages
visual features for binary classification while the latter
leverages both textual and visual features for languagevision alignment. Consequently, this dual block based
proposed approach is able to detect video anomalies at
both coarse and fine-grained levels.
3) A Glimpse-Emphasize network is developed that effectively captures both the global and local temporal
dependencies across time. The MIL-Align mechanism
is also developed to optimize visual-language alignment
under weak supervision.
4) The effectiveness of ReFLIP-VAD is demonstrated
on two large-scale benchmarks. ReFLIP-VAD achieves
state-of-the-art performance, including 86.29% AP on
XD-Violence and 89.14% AUC on UCF-Crime, surpassing existing state-of-the-art methods by a large margin.
The rest of the paper is structured as follows: Section II
discusses the state-of-the-art approaches for the detection
of anomalies in videos and how to adapt vision-language
models in video anomaly detection. Section III describes the
proposed methodology that achieves both coarse-grained and
fine-grained video anomaly detection effectively. Section IV

presents the experimental results and discussion on the UCF
Crime and XD-Violence dataset. Section V concludes with a
discussion of future research directions.
II. R ELATED W ORK
A. Video Anomaly Detection
1) Unsupervised VAD (USVAD): Video anomaly detection
has undergone a revolutionary transformation with the advent
of deep learning techniques. Methods utilizing convolutional
neural networks [18]–[20], recurrent neural networks [21],
[22], and transformers [23], [24] have progressively emerged
as the primary focus of research in this area. Peng et al.
[18] proposed a deep one-stage neural network by employing a stacked convolutional encoder to generate their lowdimensional high-level representations aiming for maximal
compactness. Furthermore, they incorporated a decoder to
reconstruct raw samples from these low-dimensional representations. By employing proxy task learning, Liu et al.
[19] introduced a spatial-temporal memory-augmented autoencoder. Following this structure, researchers [25], [26], [27]
developed the video prediction network that separately learns
appearance and motion normality to predict the anomalies.
Zhong et al. [28] utilized a cascade structure combining pixel
reconstruction and optical flow prediction to enhance anomaly
detection. Zeng et al. [29] used Graph Convolutional Neural
Network to detect human-related anomalies. Jin et al. [23]
utilized transformers that learn the discriminative temporal
features among all video frames. Zhong et al. [30] developed
an attention-based feature fusion module to integrate forward
and backward spatio-temporal features, and utilizes an error
pyramid and mean pooling for anomaly evaluation, effectively
detecting objects of varying sizes in complex scenes. Li et al.
[31] leveraged multi-branch generative adversarial network to
detect abnormal events.
2) Weakly Supervised VAD (WSVAD): Weakly supervised
video anomaly detection methods have garnered increased
attention, particularly following the introduction of the weakly
supervised Multiple Instance Learning(MIL) framework by
Sultani et al. [9]. They conceptualized each video as a bag,
with its segments representing instances within the bag. The
framework generates results based on the premise that the
anomaly score for instances within the positive bag (anomalous videos) should surpass that of the negative bag (normal
videos), utilizing ranking loss functions with video-level annotations. Therefore, several research works follow this direction
which has attracted the attention of the research community.
Zhong et al. [32] utilized a Graph Convolutional Neural
Network to correct label noise in the area of video anomaly
detection. Lv et al. [33] presented a localization framework
by employing a high-level context information module for
anomaly localization. Tian et al. [34] developed a robust
temporal feature magnitude learning framework by leveraging
a self-attention network and dilated convolutions to capture
short and long-range temporal dependencies. Huang et al. [35]
proposed a temporal feature aggregator for modeling the temporal relationships between segments of video. Moreover, they
also incorporated a discriminative feature encoder for feature

© 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2024.3482007

3

discrimination. Liu et al. [36] obtained deep discriminative
features by introducing a collaborative learning module. Chen
et al. [37] applied a magnitude contrastive loss to capture
feature separability between normal and abnormal videos
effectively. Fan et al. [38] proposed a snippet-level attention
mechanism to effectively localize the anomalous events in
survelliance videos.
B. Vision-Language Model (VLM)
Vision-language models have garnered significant attention
from the computer vision community due to their ability to
bridge the gap between visual data and natural language.
Earlier VLMs focused on image applications such as image classification [12], scene text detection [39], and image
captioning [40]. Recently, Xu et al. [41] extended the VLM
from image to video domains that aligns video and text by
contrasting temporally related video-text pairs showing robust
zero-shot capabilities in video tasks. Ju et al. [15] developed
a simple baseline for efficient action recognition task by
learning the task-specific prompt templates. Zanella et al.
[42] leveraged the latent CLIP feature space to identify the
normal events and establish text-driven vectors for detecting
abnormalities. Wu et al. [16] adapted the frozen CLIP model
to effectively transfer pre-trained language-visual knowledge
to WS-VAD. Yang et al. [43] proposed a novel framework by
utilizing the CLIP model to align video event description texts
with corresponding video frames, improving pseudo-label generation and self-training through fine-tuning, learnable text
prompts, and normality guidance. Wu et al. [44] introduced
a new paradigm for open-vocabulary video anomaly detection
using the CLIP model to improve detection and categorization
of seen and unseen anomalies.
The following shortcomings of video anomaly detection
methods based on the vision-language model are identified
from the related works:
• Despite the effectiveness of existing approaches, they do
not effectively capture the dynamic and temporal dependencies in videos. To address this challenge, we have
introduced a Glimpse and Emphasize Network (detailed
in Section III-C).
• Current state-of-the-art methods fail to fully exploit the
connection between visual and language features, resulting in suboptimal performance. This limitation is addressed through a dual-block structure, where one branch
focuses on visual features for coarse-grained binary classification, and the other integrates both visual and textual
features for fine-grained anomaly detection (discussed in
Section III-D and III-E).
• Existing methods rely on hand-crafted or learnable
prompts, which are inadequate for capturing the subtle
anomalies. To overcome this issue, we have incorporated
a reparameterized learnable prompt (explained in Section
III-F).
III. M ETHODOLOGY
This section provides a detailed description of the proposed
ReFLIP-VAD, which addresses the shortcomings discussed in

Section II-B. Section III-A defines the problem formulation
of weakly supervised anomaly detection in videos. Section
III-B outlines the process for extracting both visual and textual
features. Section III-C presents the glimpse and emphasize network of how global and local context information is captured
effectively. Section III-D and III-E describe the classification
and video-text alignment block respectively. Section III-F
introduces the novel reparameterized learnable prompt using
the DistilBERT encoder. Section III-G outlines how visual and
text embeddings are combined. Finally, the coarse-grained and
fine-grained alignment along with a novel feature magnitude
separability loss functions are described. The overall framework of the proposed method illustrated in Figure 1.
A. Problem Definition
uv
Consider a training set of untrimmed videos U = {uk }N
k=1 ,
where Nuv denotes the total number of untrimmed videos.
Each video uk is associated with a binary label lk ∈ {0, 1}
uv
from the set L = {lk }N
k=1 , where lk = 1 indicates that if
at least one frame of the video contains abnormal events and
lk = 0 otherwise. The WSVAD model aims to predict an
anomaly score vector svk ∈ RSk for each video, where Sk is
the number of segments in the k -th video, and each element of
svk represents a normalized anomaly score for each segment
in the range from 0 to 1.

B. Feature Extraction
Previous research studies typically employ pre-trained 3D
convolutional models like C3D and I3D to extract features
from videos. These features are then input into MIL-based
binary classifiers. Recently, FLIP [13] a large-scale languagevision pre-trained model, has significantly impacted various
computer vision fields, showcasing strong generalization capabilities across diverse tasks. Drawing inspiration from FLIP,
the proposed work not only utilizes the image encoder of FLIP
to extract video features but also explores leveraging text of
encoder of FLIP to fully utilize the rich associations between
visual content and textual concepts.
For the visual features, the image encoder is a Vision
Transformer that concatenates an additional [CLASS] token
embedding and projects image patches linearly as input [45].
For the textual features, following [10], a Byte-Pair Encoding
(BPE) [46] with a vocabulary size of 49,408 is used to tokenize
the text. Each text sequence starts with a Beginning of Sentence [BOS] token and ends with an End of Sentence [EOS]
token. The token embeddings are then fed into a modified
decoder-only Transformer model [47]. Textual tokens and
visual tokens are then projected into a multi-modal common
space and separately L2-normalized. This approach differs
from existing dual-stream models, which only model crossmodal interaction via global features. FLIP introduces a finegrained contrastive learning objective that accounts for the
interaction between image patches and textual tokens.
Initially, the FLIP image feature extractor processes a set
of Nuv raw untrimmed videos U. For each video uk ∈
RNf ×X ×Y×3 , the parameters Nf , X , and Y denote the number
of frames, height, and width of uk , respectively. Following

© 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2024.3482007

4

Input Video

CLS-Block
Coarse-grained
anomaly score

1

Visual
features
Glimpse &
Emphasize
Network

FLIP
Image
Encoder

2

Video-level binary
ground truth
Binary
Classifier

K

A

Reparamterized
Learnable Prompt

FLIP
Text
Encoder

[CLASS]

[riot][arrest]
DistilBERT

Multimodal
Prompt

D

[arson]

M

Visual-text
features

Fine-grained
alignment map

Prompt
Encoder

Video-level category
ground truth

VTA-Block

Learnable Prompt

ADD

Trainable

Frozen

A Aggregation

M MIL-Align

D Product K Top-K

Fig. 1. Proposed Framework

this, each video sequence is partitioned into S segments and
the resulting feature maps produced by the feature extractor
are denoted by G = {g k,j }, where k varies from 1 to Nuv ,
and j varies from 1 to S. These feature maps are quantified
as G ∈ RNuv ×S×C×D , with C indicating the number of crops
in each video segment and D representing the dimensionality
of features. Each g k,j ∈ RC×D corresponds to the feature set
of the j-th segment in the k-th video.
Furthermore, the Feature Intensify Module (FIM) module
initially processes a feature map G to compute a feature norm
F as will be discussed later. Subsequently, the Glimpse and
Emphasize module leverages this enhanced feature map to
extract global and local representation through a segmentlevel transformer (SLT) and self-attention mechanism (SAM),
respectively. Initially, FIM computes the feature norm F k,j of
g k,j as per Eq. (1):
F

k,j

=

D
X
d=1

g

k,j,d 2

! 21
∈R

1×1×C×1

Here, α signifies a hyperparameter governing the influence of
the norm term, and Conv1D is a 1-dimensional convolutional
layer that modulates the feature norm for every dimension.
C. Glimpse and Emphasize Network
1) Glimpse Module: The glimpse module comprises three
key components: channel squeezer (CS), segment level transformer (SLT), and feed-forward network (FFN). To streamline
computation, the channel squeezer reduces the dimensionality
of the feature map from D in the Feature Intensify Module (FIM) to D/32 that generates an output feature map
Gcs global ∈ RU ×C×S×D/32 . Furthermore, a video segment level
transformer (SLT) is implemented to learn the global feature
relationships across video segments. This is achieved by
formulating an attention map M ∈ R1×S×S×C that distinctly
associates the various temporal segments.
k,j1 ,j2

(1)

M

=

D
X


 

k,j1 ,d
k,j2 ,d
Q Gcs
global K Gcs global

(3)

d=1

where, j1 , j2 ∈ [1, S], Q, K represent 1D “query” and “key”
where d is the index of the feature dimension.
convolutions of the transformer. Then, softmax normalization
Subsequently, FIM enhances the features {g k,j }Frozen
F IM by
is appliedMtoMIL-Align
obtain mD∈ Product
R1×S×S×D
, where mk,j1 ,: indicates
A Aggregation
K Top-K
Residual Connection
Trainable
k,j
integrating the modulated feature norm, Conv1D(F ), with the association of other segments with the clip j1 .
g k,j acting as a residual component as illustrated in Eq. (2):
k,j1 ,j2
eM
k,j1 ,j2
m
=
(4)
PS
Mk,j1 ,j2
gFk,jIM = g k,j + αConv1D(F k,j ) ∈ R1×1×C×D
(2)
j2 =1 e
© 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2024.3482007

5

The feature map Gsam local is computed by the self-attentional

FFN

FFN

SLT
SAM

Conv 1d

Conv 1d

CS

Batch Normalization 1d

CS

Fig. 2. Glimpse Module introduced in III-C to capture the global features.

D

The output Gslt global of SLT is in R1×S×C× 32 , reflecting the
weighted average of all segment features in the long video.
k,j1 ,d
Gslt
global =

S
X



k,j2 ,d
mk,j1 ,j2 V Gcs
global



(5)

j2 =1

Here, the Glimpse module within the network structure as
shown in Figure 2 uses a 1D “value” convolution represented
by V from the transformer architecture. This module equips
the network with an understanding of typical, expected scenarios, which enhances its ability to pinpoint anomalies. Moreover, it leverages this insight to make better use of extensive
temporal contexts within the data. The Glimpse module also
incorporates a Feed-Forward Network (FFN), consisting of
a pair of fully connected layers alongside a Gaussian Error
Linear Unit (GeLU) non-linear function. This setup is designed
to enhance the ability of the model to represent and process
complex features. The resulting feature map from the Glimpse
module is then directed into the subsequent Emphasize module
for further analysis.
2) Emphasize Module: The emphasize module comprises
three key components: channel squeezer (CS), self-attention
mechanism (SAM), and the feed-forward network (FFN).
The channel squeezer effectively reduces the feature map
from its original channel dimension D to D/16. The selfattention mechanism (SAM) enhances the local features in
each video segment by learning channel-wise correlations.
It allows the model to focus on relevant information and
capture context. The feed-forward network contributes to the
generation of a refined feature map. This refined map serves
as an indicator of anomalies present in the video segments.

Fig. 3. Emphasize module introduced in III-C to capture the local features.

convolution on Gca local which is represented in Eq. (5) . The
operation is represented by a Hadamard product (denoted by
⊗) of Gca local with itself, resulting in a tensor of dimensions
D
U × S × C × 16
. The individual elements of Gsam local are
D
computed by summing over the 16
channels of the Hadamard
product of the corresponding elements of Gca local represented
in Eq. (6), without the use of learnable weights. This process
facilitates each channel in accessing adjacent channels to learn
channel-wise correlations. Following this operation, a twolayered feedforward network (FFN) processes the output to
produce the final feature map as shown in Figure 3.
D

Gsam local = Gca local ⊗ Gca local ∈ RU ×S×C× 16

(6)

where for each element of Gsam local , we have:
D

k,j,l1
Gsam
local =

16
X

k,j,l1
k,j,l2
1×1×C×1
Gca
local · Gca local ∈ R

(7)

l1 ,l2 =0

D. Classification Block (CLS Block)
Unlike previous WSVAD approaches, ReFLIP-VAD incorporates a two-pronged block architecture. Following temporal modeling, the local video features Gsam local are passed
through a fully connected (FC) layer to produce the final visual
features as Gvisual . Typically, in the CLS block, Gvisual is
fed into a binary classifier. This classifier includes a feedforward network layer (FFN), a fully connected layer (FN),

© 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2024.3482007

6

Output Prompt Embeddings

and a Sigmoid activation(σ) to calculate the coarse-grained
anomaly confidence score A, given in Eq. (8):
A = σ(FC(FFN(Gvisual ) + Gvisual ))

(8)

E. Video-Text Alignment Block (VTA-Block)
In addition to the conventional binary classification block, a
novel video-text alignment block is introduced. In this block,
textual labels such as ‘explosion’, ‘road accident’, ‘arson’,
‘abuse’ etc., are not encoded as one-hot vectors; rather, they
are converted into class embeddings using the text encoder
of FLIP. By leveraging the static pre-trained text encoder
of FLIP, we harness its linguistic knowledge for enhancing
video anomaly detection. Subsequently, the similarities between class embeddings and frame-level visual features are
assessed to generate the alignment map AM ∈ Rn×ℓ , where
ℓ is the number of textual labels. This arrangement mirrors
the setup in CLIP, where each input text label corresponds
to a distinct class of abnormal events, facilitating fine-grained
WS-VAD.

Layer Normalization

+

Transformer Layer 6

Feed Forward
Layer Normalization

Transformer Layer 2

+

Transformer Layer 1

Multi-Head
Attention
key

DistilBERT

value query

F. Reparameterized Learnable Prompt
The proposed method is built upon the CLIP [10], a visuallanguage model consisting of the visual encoder and text
encoder that transforms images and text into visual and textual
embeddings. CLIP generates the textual label embeddings
by leveraging manual prompts. However, such handcrafted
prompts pose a significant challenge because it is highly
time-consuming. To address this issue, a novel approach is
introduced: Reparameterized Fine-grained Language-Image
Pre-training (ReFLIP). Instead of directly optimizing prompts,
ReFLIP employs a reparameterized prompt encoder (DistilBERT) as depicted in Figure 4 to re-parameterize input prompt
embeddings. This reparameterization enhances the exploration
of task-specific knowledge from few-shot samples.
Given a set of original prompt embeddings P E consisting
of N prompt tokens P E = {pe1 , pe2 , ..., peN }, the prompt
g
encoder is applied to obtain a reparameterized sequence P
E
as follows:

Input Prompt Embeddings

Fig. 4. Reparameterized Learnable Prompt using DistilBERT Architecture

G. Multimodal Prompt
To enhance text label representations for abnormal events,
we introduce a method utilizing visual contexts to refine
class embeddings. This involves an anomaly-centric visual
prompt leveraging the visual embeddings from abnormal video
segments to improve text label accuracy. The anomaly confidence vector from the Classification block serves as anomaly
attention. The video-level prompt is calculated by the dot(.)
product of this anomaly attention with the video feature vector,
followed by normalization. The visual prompt is then integrated with the class embedding, and the final segment-specific
class embedding is generated using a Feedforward Neural
Network with an addition operation and a skip connection.

g
P
E = {pe
e 1 , pe
e 2 , ..., pe
e N } = {ϕ(pe1 ), ϕ(pe2 ), ..., ϕ(peN )}

V = Norm(AT · Gvisual )

where ϕ(·) denotes the reparameterization function of the
prompt encoder, which includes a network θ(·) with a residual
connection. The function ϕ is defined for each prompt token
pei as:
ϕ(pei ) = θ(pei ) + pei , i ∈ {1...N }

where V ∈ Rd is the anomaly-centric visual prompt. We
then add V to the class embedding T and obtain the final
instance-specific class embedding CE by a simple FFN layer
and a skip connection.

The network θ(·) is an adaptable approach that forms connections between the prompt embeddings. This facilitates the
creation of task-specific reparameterization within the prompt
embeddings. After applying reparameterization, the class token
embedding ci for the i-th class is integrated into the center
of the reparameterized learnable prompts ϕ(pei ) forming the
sequence as pi = {ϕ(pe1 ), ϕ(pe2 ), .ci .., ϕ(peN ), }. Following
their integration with positional embeddings to incorporate
positional information, these prompts are fed into the FLIP
textual encoder etext (·). This process generates the textual class
embeddings, represented as Ti = etext (pi ).

CE = FFN(ADD(V, T )) + T

(9)

(10)

where ADD denotes element-wise addition. The finegrained alignment map AM is then generated by calculating
the similarity scores across all instance-specific class embeddings and frame-level visual features.
H. Loss function
For the CLS block, the WSVAD task handles known anomalies using either MIL or Top- K due to the lack of precise
frame-level annotations. It utilizes the Top-K mechanism to

© 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2024.3482007

7

identify K highest anomaly confidences. It calculates the classification loss using binary cross entropy between the videolevel predictions and the actual ground truth. In contrast, the
Video-Text Alignment-block (VTA-block) addresses scenarios
where there are no anomaly confidences and the challenge of
dealing with multiple classes instead of binary classes. Taking
inspiration from Wu et al. [16], the MIL-Align mechanism
is utilized to address the above challenge. The MIL-Align
mechanism focuses on the alignment map AM, which captures the similarity between frame-level video features and
all class embeddings. By selecting the top K similarities and
averaging them, the degree of fine-grained alignment for a
given video with the current class is assessed such that it
exhibits the highest similarity score among all options. The
probability for multi-class classification is computed as the
softmax normalized similarity between visual embeddings V
and all text embeddings T for each category.
exp (sim(V, Ti )/τ )
pvt
i = PK+1
j=1 exp (sim(V, Tj )/τ )

(11)

where pvt
i denotes the predicted probability corresponding
to the i-th category, sim(.,.) is the cosine similarity and
K + 1 is the K number of anomaly categories and 1 normal
category. τ represents the temperature scaling parameter that
adjusts the softmax distribution. The fine-grained alignment
loss Lf ga is calculated using the Kullback-Leibler divergence.
This approach compels the network to discern between the
visual content of the video that depicts abnormal behavior
(foreground) and the content irrelevant to the abnormal behavior (background).
Lf ga = Ep∼p(v) [log pvt (v) − log q vt (v)]

(12)

where pvt (v) and q vt (v) denote the similarity score and
semantic consistency label of the visual-prompt pair, respectively. If it is a positive pair, q = 1; otherwise, q = 0.
The coarse-grained alignment loss is binary cross entropy loss
Lcga between pi and lk as given in Eq. (13).

U /2
X

Lf ms =

p
q
(1 − I)(δ(Wnormal
, Wnormal
)

p,q=0
U
X

+

r
s
(1 − I)δ(Wabnormal
, Wabnormal
)

+

U /2
U
X
X

p
r
I (M argin − δ(Wnormal
, Wabnormal
))

p=0 r=U /2

Here, U/2 normal videos and U/2 abnormal videos are
sampled in each training batch U. p, q represent the normal
segments index, and r, s denote the abnormal segments index.
Wnormal and Wabnormal are the top-K feature magnitudes
for normal and abnormal segments respectively. δ(·, ·) is a
distance metric used to increase the feature magnitude distance
between the segments.
Here, I = 1 indicates that the two sampled video segments
(one normal and one abnormal) are of different categories.
The loss function is to increase the distance between the
feature magnitudes of these segments. The goal is to enhance
the model’s ability to distinguish clearly between normal and
abnormal segments, which aids in better anomaly detection.
I = 0 indicates that the paired segments sampled are both
from the same category, either both normal or both abnormal.
In this scenario, the Lf ms loss function aims to minimize
the distance between the feature magnitudes of the segments,
effectively grouping similar types of segments closer together
in the feature space. This reinforces the model’s capability to
recognize and maintain consistency within the same categories
of segments, thereby improving the overall model performance
in distinguishing between normal and abnormal segments.
p
q
The distance functions δ(Wnormal
, Wnormal
) and
p
q
δ(Wabnormal , Wabnormal ) are defined in Eq. (15) and
Eq. (16) respectively.
p
q
δ(Wnormal
, Wnormal
)=

Lcga = −

1
[lk log(pi ) + (1 − lk ) log(1 − pi )]
N i=1

(15)

min

u,v∈{0,...,S}
r,u
s,v
(O(∥fEM
∥2 ) − O(∥fEM
∥2 ))

(13)

where, N is the number of video segments, lk is the groundtruth label for the i-th video segment, where lk = 1 if the
segment is anomalous and lk = 0 if it is normal. pi is the
predicted probability that the i-th video segment is anomalous.
This model incorporates a feature magnitude separability
loss Lf ms given in Eq. (14) in addition to the coarse-grained
alignment loss Lcga and fine-grained alignment loss Lf ga .
This separability loss serves to incrementally separate the
normal class embeddings from the abnormal ones. The process
begins by computing the cosine similarity between the normal
and abnormal class embeddings. Subsequently, the contrastive
loss Lf ms is calculated as follows:

min

u,v∈{0,...,S}
p,u
q,v
(O(∥fEM ∥2 ) − O(∥fEM
∥2 ))

r
s
δ(Wabnormal
, Wabnormal
)=
N
X

(14)

r,s=U /2

(16)

where
r,u
O(∥fEM
∥2 ) is one of the top-K feature magnitudes among
r,{1,...,S}

fEM
.
p
r
Similarly, the distance δ(Wnormal
, Wabnormal
) for normal
feature p and abnormal features r is presented in Eq. (17) as:
p
r
δ(Wnormal
, Wabnormal
)=

max

u,v∈{0,...,S}
p,u
r,v
(O(∥fEM
∥2 ) − O(∥fEM
∥2 ))

(17)

Here, the max operation is taken over all temporal segments
u and v indicate the largest difference in feature magnitudes
between the normal and abnormal features.

© 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2024.3482007

8

To sum up, the overall loss for ReFLIP-VAD is expressed
in Eq. (18) as:
L = Lcga + λ1 Lf ga + λ2 Lf ms

(18)

where λ1 ,λ2 is the weighting factor that adjusts the influence of loss terms.

K as 1 for negative bags, where S denotes the length of input
feature. To make a fair comparison, the visual sample rate is
set to be 24 fps for UCF-Crime and 30 fps for XD-violence
as prior methods [14] and a sliding window with a size of 16
frames for visual feature extraction.
C. Comparison with State-of-the-art Methods

IV. E XPERIMENTS
A. Datasets and Evaluation Metrics
1) Datasets: Extensive experiments have been conducted
on two standard benchmark datasets, namely UCF-Crime [9]
and XD-Violence [48].
UCF-Crime is a large-scale weakly supervised video
anomaly detection dataset released in 2018. It comprises 1900
untrimmed real-world videos with a total duration of 128
hours. It includes 13 different classes of anomalous events.
It is split into a training set of 1610 videos and a testing set
of 290 videos.
XD-violence is a multi-modal large-scale diverse dataset
released in 2020. It is collected from movies, surveillance
cameras, and in-the-wild scenes for 217 hours. It includes
6 different classes of physically violent events. It comprises
4754 videos, with 2,349 categorized as normal and 2,405 as
abnormal. The training set comprises 3,954 videos, while the
test set contains 800 videos.
2) Evaluation Metrics: For evaluating coarse-grained
Weakly Supervised Video Anomaly Detection (WSVAD), this
study adopts the frame-level Average Precision (AP) metric,
which calculates the area under the precision-recall curve for
the XD-Violence dataset, and the frame-level Area Under the
Curve (AUC) for the UCF-Crime dataset. Additionally, the
AUC for only the anomalous videos (referred to as AnoAUC is
utilized to highlight the detection accuracy within anomalous
content, addressing the issue where high performance on
normal videos might obscure lower detection accuracy within
abnormal videos. For fine-grained WSVAD, the study follows
the established protocol in video action detection, employing
the mean Average Precision (mAP) across varying Intersection
over Union (IoU) thresholds. Specifically, IoU thresholds from
0.1 to 0.5, in increments of 0.1, are used to calculate mAP
values. The average of these mAP values (AVG) is also
reported. It is important to note that mAP calculations are
performed solely on the anomalous videos within the test set.
B. Implementation Details
The model is trained on NVIDIA RTX 4070 GPU using
the PyTorch framework. For the optimization of the network,
Adam is leveraged as the optimizer with a batch size of 128.
On the XD-Violence dataset, the learning rate and total epoch
are set as 5 × 10−4 and 50, respectively, and on the UCFCrime dataset, the learning rate and total epoch are set as
3 × 10−4 and 50, respectively. For hyper-parameters, τ in Eq.
(11) is set as 0.07. For the loss weight adjustment factor in
Eq. (18), the values of λ1 and λ2 are configured as 0.01 and
0.001 on the UCF-Crime dataset, respectively. On the XDViolence dataset, both λ1 and λ2 are set
 as 0.0001. For the
S
MIL-ranking, the value of K as 16
+ 1 for positive bags and

1) Coarse-grained WSVAD Results: The proposed method
is designed to handle both coarse-grained and fine-grained
WSVAD tasks effectively. To demonstrate its performance,
the method is compared with other state-of-the-art methods
in Tables I and II. This approach ensures that the comparisons
are equitable and highlights the capabilities of the proposed
method in anomaly detection.
TABLE I
P ERFORMANCE C OMPARISON (C OARSE - GRAINED ) ON UCF-C RIME
Supervision

Method

Features

AUC(%)

Ano-AUC(%)

Un

SVM baseline
OCSVM [49]
Hasan et al. [50]

-

50.10
63.20
51.20

50.00
51.06
39.43

Deep-MIL [9]
IBL [51]
Motion-Aware [52]
GCN [32]
HL-Net [14]
MS-BSAD [53]
Ju et al. [15]
CRFD [54]
LA-Net [55]
NG-MIL [56]
RTFM [34]
AnomalyCLIP [42]
DMU [57]
UB-MIL [58]
CLIP-TSA [59]
Vad-CLIP [16]

C3D
C3D
PWC Flow
TSN
I3D
I3D
CLIP
I3D
I3D
I3D
I3D
ViT-B/16
I3D
X-CLIP
CLIP
CLIP

75.42
78.66
79.01
82.12
82.45
83.54
84.72
84.89
85.12
85.63
85.66
86.36
86.75
86.97
87.58
88.02

54.25
62.18
59.03
60.27
62.60
63.86
66.8
68.94
69.31
70.23

ReFLIP-VAD (Ours)
ReFLIP-VAD (Ours)

CLIP
FLIP

88.57
89.14

72.35
74.72

Weak

Weak

Table I presents a performance comparison of existing
methods on the UCF-Crime dataset, emphasizing both coarsegrained AUC and anomaly-specific detection capabilities
(Ano-AUC). The proposed method achieves an impressive
AUC of 89.14% and an Ano-AUC of 74.72%, showing
substantial improvements over existing methods. Specifically,
when compared to the highest scores from previous methods,
VadCLIP [16] which scored 88.02% in AUC and 70.23% in
Ano-AUC, the proposed method demonstrates an improvement
of +1.12% in AUC and +4.49% in Ano-AUC. Additionally,
compared to the second highest-performing method, CLIPTSA [59], which scored an AUC of 87.58% and an AnoAUC of 69.31%, the proposed method exhibits improvements
of +1.56% in AUC and +5.41% in Ano-AUC. These enhancements significantly underscore the efficacy of the proposed method in distinguishing between normal and abnormal
events, setting a new benchmark for anomaly detection in the
UCF-Crime dataset.
Table II showcases a performance comparison of existing
anomaly detection methods on the XD-Violence dataset, categorized under unsupervised and weakly supervised techniques.

© 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2024.3482007

9

TABLE II
P ERFORMANCE C OMPARISON (C OARSE - GRAINED ) ON XD-V IOLENCE
Supervision

Method

Features

AP(%)

Un

Baseline
OCSVM [49]
Hasan et al. [50]

-

50.80
28.63
31.25

Deep-MIL [9]
CRFD [54]
Ju et al. [15]
RTFM [34]
HL-Net [14]
NG-MIL [56]
AnomalyCLIP [42]
MS-BSAD [53]
LA-Net [55]
CMRL [60]
DMU [57]
CLIP-TSA [59]
Vad-CLIP [16]

C3D
I3D
I3D
I3D
I3D
I3D
ViT-B/16
I3D
I3D
I3D
I3D
CLIP
CLIP

75.18
75.90
76.57
78.27
78.10
78.51
78.55
78.92
80.72
81.30
82.41
82.17
84.51

ReFLIP-VAD (Ours)
ReFLIP-VAD (Ours)

CLIP
FLIP

85.81
86.29

Weak

Weak

D. Qualitative Analysis

TABLE III
P ERFORMANCE C OMPARISONS (F INE - GRAINED ) ON UCF-C RIME
Method
Baseline
Deep-MIL [9]
HL-Net [14]
Vad-CLIP [16]
ReFLIP-VAD (Ours)

0.1
0.21
5.73
10.27
11.72
14.23

0.2
0.14
4.41
7.01
7.83
10.34

0.3
0.04
2.69
6.25
6.40
9.32

mAP@IoU(%)
0.4
0.5
0.02
0.01
1.93
1.44
3.42
3.29
4.53
2.93
7.54 6.81

AVG
0.08
3.24
6.05
6.68
9.62

TABLE IV
P ERFORMANCE C OMPARISONS (F INE - GRAINED ) ON XD-V IOLENCE
Method
Baseline
Deep-MIL [9]
HL-Net [14]
Vad-CLIP [16]
ReFLIP-VAD (Ours)

0.1
1.82
22.72
30.51
37.03
39.24

0.2
0.92
15.57
25.75
30.84
33.45

0.3
0.48
9.98
20.18
23.38
27.71

mAP@IOU(%)
0.4
0.5
0.23
0.09
6.20
3.78
14.83
9.79
17.90 14.31
20.86
17.22

re-implemented using visual features from CLIP, followed by
the setup in HL-Net to fine-tune Deep-MIL [9] for adapting to
fine-grained WSVAD. Fine-grained WSVAD presents a more
challenging task relative to coarse-fined WSVAD as it requires
attention to both multi-category classification accuracy and
detection segment continuity. In this task, the proposed method
is also clearly superior to these excellent comparison methods
on both XD-Violence and UCF-Crime datasets. For example,
on XD-Violence, the ReFLIP-VAD achieves performance improvements of 15.71% , 7.15% and 2.66% in terms of AVG
compared to Deep-MIL [9], HL-Net [14] and VadCLIP [16],
respectively.

AVG
0.71
11.65
20.21
24.70
27.36

Figures 5 and 6 illustrate the qualitative visualization results
for the UCF Crime and XD Violence datasets, respectively.
The frame-wise anomaly detection scores are depicted by
the blue solid line, and the ground-truth abnormal temporal
locations are depicted by the light orange shaded regions.
The proposed method has demonstrated effectiveness across
various categories within both the UCF-Crime and XDViolence datasets, effectively identifying anomalies within the
designated ground truth regions. This confirms the model’s
precision in temporal and situational anomaly detection.
Figure 7 presents t-SNE visualizations of feature distributions on these datasets, both with and without the proposed
loss function L . The visualizations highlight that incorporating L significantly enhances the separation between normal
(green dots) and abnormal (magenta dots) features, thereby
improving the proposed model’s discriminative capability. This
improved distinction is crucial for effective anomaly detection,
demonstrating the model’s vital role in enhancing surveillance
and safety systems by efficiently distinguishing between normal and anomalous activities.
E. Ablation Studies

The Proposed Method achieves a notable Average Precision
(AP) of 86.29%, which is substantially higher compared to
both categories of existing methods. Among unsupervised
methods, the Baseline method scores 50.80%, OCSVM [49]
achieves 28.63%, and Hasan et al. [50] achieve 31.25%.
Compared to these, the proposed method shows improvements
of 35.49%, 57.66%, and 54.04% respectively. In the realm
of weakly supervised methods, the highest previous AP was
achieved by VadCLIP [16] at 84.51% and the lowest by DeepMIL [9] at 75.18%. The proposed method surpasses UBMIL [58] the second best-performing existing method in this
category, by 4.12%. This significant outperformance of the
proposed method over both unsupervised and weakly supervised methods underscores its superior efficacy in accurately
identifying anomalies in the XD-Violence dataset.
2) Fine-grained WSVAD Results: For the fine-grained performance on two benchmark dataset, ReFLIP-VAD is compared with previous works [9], [14], [16] in Tables III and IV.
HL-Net [14], the first work to propose fine-grained WSVAD, is

Comprehensive ablation studies have been conducted to
verify the effectiveness of the proposed model. For these
studies, the similarity map is utilized to calculate the framelevel anomaly degree for coarse-grained WSVAD.
1) Effectiveness of Temporal Modeling module: To evaluate
the efficacy of the temporal modeling module in the proposed framework, experiments are conducted on XD-Violence
dataset in various settings.
TABLE V
E FFECTIVENESS OF T EMPORAL M ODELING MODULE IN P ROPOSED
F RAMEWORK
Configuration
I
II
III
IV
V
VI
VII
VIII
IX
X
XI

Method
Baseline (w/o temporal modeling)
Global TF-Encoder
Emphasize-Glimpse (EG)
Local TF-Encoder
Emphasize-Emphasize (EE)
Graph Convolutional Network (GCN)
Local TF-Encoder + Global TF-Encoder
Global TF-Encoder + GCN
Local TF-Encoder + GCN
Glimpse-Emphasize-Fusion (GE-Fusion)
Glimpse-Emphasize (GE) (Proposed Method)

AP(%)
73.31
82.69
82.89
81.34
81.59
82.65
80.12
85.15
85.57
85.89
86.29

AVG(%)
16.27
16.98
17.43
18.67
19.27
24.19
20.93
21.76
25.42
26.58
27.36

© 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2024.3482007

10

(a) Arrest

(b) Vandalism

(a) Explosion

(b) Riot

(c) Explosion

(d) Assault

(c) Car Accident

(d) Abuse

(e) Shooting

(e) Road Accident

(f) Normal Video

(f) Normal Video

Fig. 5. Visualization Results of ground-truth and anomaly detection score
of the proposed method on UCF-Crime dataset. The blue solid line depicts
the frame-wise anomaly detection score and the light orange shaded regions
indicate the ground-truth abnormal temporal locations. Green arrow represents
the location of normal frame and red arrow represents the location of abnormal
frame.

Fig. 6. Visualization Results of ground-truth and anomaly detection score
of the proposed method on XD-Violence dataset. The blue solid line depicts
the frame-wise anomaly detection score and the light orange shaded regions
indicate the ground-truth abnormal temporal locations. Green arrow represents
the location of normal frame and red arrow represents the location of abnormal
frame.

Table V illustrates the effectiveness of the Temporal Modeling module in the proposed framework across various configurations. Configuration I serves as the baseline without
the temporal modeling capabilities of the proposed method,
achieving an AP of 73.31% and an AVG of 16.27%. In Configuration II, the inclusion of the Global TF-Encoder enhances
the AP and AVG scores to 82.69% and 16.98%, respectively.
The Emphasize-Glimpse (EG) sequence in Configuration III
further improves the scores slightly to 82.89% for AP and
17.43% for AVG. Compared to the baseline (Setting I), this
configuration improves AP by +9.58% and AVG by +1.16%.
In Configurations IV and V, the Local TF-Encoder and
the Emphasize-Emphasize (EE) arrangements show further
improvements, with Configuration V (EE) achieving 81.59%
AP and 19.27% AVG. This setting shows a decrease of -

1.35% in AP and -2.15% in AVG compared to Setting III.
The integration of Graph Convolutional Network (GCN) in
Configuration VI leads to an improvement, reaching 82.65%
AP and 24.19% AVG. Configuration X shows an increase of
+5.77% in AP and +5.65% in AVG compared to Configuration
VII, an increase of +0.74% in AP and +4.82% in AVG
compared to Configuration VIII, and an increase of +0.32%
in AP and +1.16% in AVG compared to Configuration IX.
However, it shows a notable decrease of -0.40% in AP and
-0.78% in AVG compared to the proposed method in Setting
XI. Configuration XI, representing the Glimpse-Emphasize
(GE) method proposed in this paper, outperforms all other
configurations, achieving the highest AP of 86.29% and an
AVG of 27.36%. This emphasizes the efficacy of the GE
approach, which leverages a sequential arrangement of the

© 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2024.3482007

11

w/o

w/

w/o

w/

(b) XD-Violence

(a) UCF-Crime

Fig. 7. Visualizations of the distributions of the normal and abnormal embeddings learned without and with the proposed loss (L ) using t-Distributed
Stochastic Neighbor Embedding (t-SNE) [61], on (a) UCF-Crime dataset. and (b) XD-Violence dataset.

Glimpse and Emphasize modules, highlighting its advantage
in handling temporal dependencies in video anomaly detection
tasks.
2) Effectiveness of dual block: ReFLIP-VAD can simultaneously realize coarse-grained and fine-grained WSVAD tasks
through a dual-block approach. To evaluate the effectiveness of
each block and the prompt mechanisms in the video-text alignment (VTA-Block), extensive experiments were conducted,
with detailed results presented in Table VI. The method
utilizing only the Classification block (CLS-Block) falls under
the classification-based paradigm and competes with current
state-of-the-art methods on XD-Violence. However, using only
the VTA block results in unsatisfactory performance in terms
of AP, as it primarily focuses on fine-grained WSVAD. With
the integration of coarse-grained classification for feature
optimization in the CLS block, the VTA block experiences
a significant improvement, approximately a 12% increase in
AP. Furthermore, the dual block that integrates the Reparameterized Learnable Prompt (RL-prompt) and the Visual
Prompt (V-prompt) to form a multimodal prompt achieves
substantial improvements of +2.42% and +6.23%, respectively. Additionally, the incorporation of learnable prompts
and visual prompts, which are specific designs in the VTA
block, consistently enhances performance, establishing a new
state-of-the-art. These results demonstrate that the dual-block
configuration, which combines a coarse-grained classification
paradigm with a fine-grained alignment paradigm, effectively
increases the performance.
TABLE VI
E FFECTIVENESS OF D UAL B LOCK ON XD-V IOLENCE DATASET
CLS-Block
✓
✗
✓
✓
✓
✓

VTA-Block
✗
✓
✓
✓
✓
✓

RL-Prompt
✗
✗
✗
✓
✗
✓

V-Prompt
✗
✗
✗
✗
✓
✓

AP(%)
81.28
69.24
77.33
79.75
83.56
86.29

3) Effectiveness of Context Length, Window Length, and
Video Input Length: As shown in Table VII, the performance metrics, AP(%) and AVG(%), tend to improve as the
context length in the learnable prompt increases from 8 to
24. Specifically, the AP(%) reaches its peak at a context
length of 24, yielding 86.29%, and an AVG(%) of 27.36%,

representing a substantial improvement of approximately 5%
in AP and 4.62% in AVG compared to a context length of
8. However, further increasing the context length to 32 leads
to a slight decrease in performance, with AP(%) dropping
by 2.16% and AVG(%) by 4.47%, indicating that while a
larger context length generally enhances the model’s ability
to capture relevant features, there is a threshold beyond which
the benefits diminish.
The performance of the model is then analyzed by varying
the window length of the Glimpse and Emphasize network.
The optimal window length is identified between 32 and 64,
where the AP(%) and AVG(%) reach their maximum values
of 86.29% and 27.36%, respectively, showing an improvement
of 2.11% in AP and 2.19% in AVG over the shortest window
length of 16. However, extending the window length to 256
results in a notable decline in performance, with AP(%)
decreasing by 2.75% and AVG(%) by 3.82%, indicating that
excessively long window lengths might introduce unnecessary
noise or irrelevant information, thereby affecting the model’s
robustness.
The input length directly influences the amount of video
data processed by the model. As input length increases from
64 to 512, both AP(%) and AVG(%) improve, peaking at an
input length of 512 with a substantial improvement of 4.69% in
AP and 4.49% in AVG compared to the shortest input length.
This demonstrates that the method is capable of effectively
handling larger input sizes, leading to enhanced performance.
4) Scale of Vision-Language Models (VL-Models) and Their
Impact on Fine-Grained WSVAD: Table VIII illustrates the
performance impact of different Vision-Language Model (VLModel) variants on fine-grained WSVAD task. The DistilBERT
+ FLIP model achieves the highest mAP@IoU=0.3 of 27.71%
and an AUC of 86.29%, representing a significant improvement over the base CLIP model, which records an mAP of
22.38% and an AUC of 81.19%. Specifically, the DistilBERT
+ FLIP variant outperforms the CLIP model by 23.82% in
mAP and 6.27% in AUC. Compared to ALIGN, which has
the largest model size at 307M parameters, DistilBERT + FLIP
still shows a 9.37% increase in mAP and a 1.77% improvement
in AUC, despite having a considerably smaller model size of
165M parameters. This highlights the effectiveness and efficiency of integrating DistilBERT with FLIP for fine-grained
WSVAD tasks, offering a better trade-off between model size

© 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2024.3482007

12

TABLE VII
I MPACT OF C ONTEXT L ENGTH , W INDOW L ENGTH , AND V IDEO I NPUT L ENGTH
Context Length

AP(%)

AVG(%)

Window Length

AP(%)

AVG(%)

Input Length

AP(%)

AVG(%)

8
16
20
24
32

81.26
82.78
84.91
86.29
84.13

22.74
23.34
25.61
27.36
22.89

16
32
64
128
256

84.19
84.68
86.29
84.87
83.54

27.26
25.17
27.36
23.26
26.54

64
128
256
512
1024

82.54
82.19
85.41
86.29
84.54

26.87
26.38
25.08
27.36
24.45

TABLE VIII
S CALE OF V ISION -L ANGUAGE M ODELS (VL-M ODELS ) AND T HEIR
I MPACT ON F INE -G RAINED WSVAD
VL-Model Variant

Model Size (Parameters)

mAP@IoU=0.3(%)

AP(%)

CLIP [10]
DistilBERT + CLIP
ALIGN [11]
FLIP [13]
DistilBERT + FLIP

144M
126M
307M
238M
165M

22.38
24.54
25.42
25.89
27.71

81.19
83.76
84.52
84.95
86.29

and performance.
5) Analysis of Computational Complexity and Model Size:
The comparison of model size and computational complexity
between the Glimpse-Emphasize Network and other methods
[53], [34], [55] and [14] is presented in Table IX. The results
for all methods were obtained by executing their official codes
on NVIDIA RTX 4070 GPU. For an equitable comparison,
open-source codes were utilized to replicate existing modules,
which were then integrated into the baseline. The GlimpseEmphasize Network demonstrates a significant reduction in
model size, with only 1.14 million parameters compared to the
13.27 million of MS-BSAD [53] and 24.7 million of RTFM
[34], the highest among the compared methods. Additionally,
the computational complexity, measured in FLOPs, for the
Glimpse-Emphasize Network stands at only 0.36 GigaFLOPs.
This is much lower than the 2.63 GigaFLOPs of MS-BSAD
[53] and only slightly higher than the 0.29 GigaFLOPs from
HL-Net [14], indicating a balance between efficiency and
complexity. Despite its smaller size and lower computational
cost, the Glimpse-Emphasize Network outperforms all others
in terms of effectiveness on challenging benchmarks. The
findings in Table IX confirm that the Glimpse-Emphasize
Network is both lightweight and efficient.
TABLE IX
C OMPARISON OF M ODEL S IZE (M) AND C OMPUTATIONAL
COMPLEXITY (G) OF DIFFERENT METHODS
Method
MS-BSAD [53]
RTFM [34]
LA-Net [55]
HL-Net [14]
Glimpse-Emphasize Network

Parameters
(M)

FLOPs
(G)

UCF-Crime
AUC(%)

XD-Violence
AP(%)

13.27
24.7
2.69
5.66
1.14

2.63
0.79
0.53
0.29
0.36

83.15
84.30
83.67
83.12
85.76

78.92
77.81
79.18
79.58
82.44

6) Performance comparison on different prompt templates:
The performance comparison across different prompt templates as shown in Table X highlights the effectiveness of the
proposed method, particularly the ‘Reparameterized Learnable
Prompt (RL-Prompt) + [CLASS]’ template, which achieves

TABLE X
P ERFORMANCE C OMPARISON OF D IFFERENT P ROMPT T EMPLATE

Prompt Template
[CLASS]
‘a video of’ + [CLASS]
‘a long video of’ + [CLASS]
L-Prompt + [CLASS]
RL- Prompt + [CLASS]

UCF-Crime
AUC(%)

XD-Violence
AP(%)

83.95
85.55
85.63
86.48
89.14

80.69
81.06
82.59
84.48
86.29

the highest performance metrics. This template significantly
outperforms other methods in the UCF-Crime dataset with an
AUC of 89.14% and in the XD-Violence dataset with an AP
of 86.29%. Compared to the next best performing template,
the ‘Learnable Prompt (L-Prompt) + [CLASS],’ the proposed
prompt template shows a substantial improvement of approximately 4.66% in AUC for UCF-Crime and a remarkable 1.81%
increase in AP for XD-Violence. This marked enhancement
underscores the method’s ability to fine-tune and optimize the
feature extraction process, leading to more accurate and robust
anomaly detection across varying video contexts.
7) Effectiveness of different hyper-parameter settings: The
impact of varying temperature coefficients (τ ) is presented in
Table XI.
TABLE XI
P ERFORMANCE C OMPARISON OF D IFFERENT T EMPERATURE
C OEFFICIENTS τ
τ

0.01

0.03

0.05

0.07

0.09

0.1

UCF@AUC (%)
XD@AP (%)

87.34
85.33

88.78
84.45

88.56
85.13

89.14
86.29

88.12
85.20

87.64
85.36

The optimal performance is achieved with (τ ) of 0.07,
yielding an AUC of 89.14% on UCF-Crime and AP of 86.29%
on XD-Violence. This configuration notably outperforms other
tested settings, showing a remarkable increase in model efficacy. Specifically, the (τ ) value of 0.07 shows an increase of up
to 2.06% in AUC and 2.18% in AP over the lowest-performing
configurations.
Figures 8 and 9 demonstrate the impact of the loss weight
adjustment factors, λ1 and λ2 , by 1×e−x , on the performance
of the proposed method across the UCF-Crime and XDViolence datasets. The evaluation reveals that the optimal
performance for λ1 on the UCF-Crime dataset is achieved
at x = 2, where the AUC reaches approximately 88%, and
on the XD-Violence dataset at x = 4, achieving an AP of
about 86%. Similarly, λ2 exhibits peak performance on the

© 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2024.3482007

13

90

AUC(%) on UCF-Crime

AP(%) on XD-Violence

89

86

83

85

2

3
x

4

5

90

AUC(%) on UCF-Crime

AP(%) on XD-Violence

0

Fig. 10. Class-wise Ano-AUC results of top three methods on UCF-Crime
dataset

90

87

AP (%)

ReFLIP-VAD

60

85

84

AP (%)

50
40
30
20
10

1

2

3
x

4

5

82

Fig. 9. Model performance under different loss weight adjustment factor λ2 .
It shows the AUC results on UCF-Crime and AP results on XD-Violence of
the proposed method for different values of λ2 (1 × e−x ) where, different
values of x are represented as x-axis.

UCF-Crime dataset at x = 3 with an AUC of 89%, and
the AP peaks at x = 4 for the XD-Violence dataset. Both
figures indicate a subsequent decline in model performance as
x exceeds these optimal values. This behavior highlights the
sensitivity of the model to the tuning of λ values, emphasizing
the necessity of precise modulation of these parameters to
enhance the overall effectiveness of the anomaly detection
capabilities across varied scenarios.
8) Effectiveness of class-wise AUC and AP results : To
showcase the detailed performance on specific anomalous
events, the class-wise Anomaly-Area Under Curve (Ano-AUC)
results on the UCF-Crime dataset for top three performing
methods: DMU, UB-MIL, and ReFLIP-VAD is illustrated in
Figure 10. While ReFLIP-VAD demonstrates superior performance across most categories in the UCF-Crime dataset,
there are certain failure cases where its effectiveness is rerag
e
Av
e

t

tin
g
oo
Sh

Rio

tin
Fig
h

Ab

83

g

0

us

83

e
rA
cci
de
nt
Ex
plo
sio
n

84

Ca

AUC (%)

85

86

82

CLIP-TSA [53]

70
86

87

DMU [52]

80

89
88

30
10

80

Fig. 8. Model performance under different loss weight adjustment factor λ1 .
It shows the AUC results on UCF-Crime and AP results on XD-Violence of
the proposed method for different values of λ1 (1 × e−x ) where, different
values of x are represented as x-axis.

40

Ab
us
e
Arr
est
Ars
o
As n
sau
Bu lt
rg
Ex lary
plo
sio
n
Ro Fight
ad ing
Ac
cid
e
Ro nt
bb
Sh ery
oo
Va ting
nd
Sh alism
op
lift
i
Ste ng
ali
Av ng
era
ge

1

50

20

81

83

ReFLIP-VAD

60

82

84

UB-MIL [57]

70
Ano-AUC (%)

AP (%)

84

DMU [52]

80

85

87
AUC (%)

90

86

88

82

87

Fig. 11. Class-wise AP results of top three methods on XD-Violence dataset

duced. These shortcomings are evident in categories where the
anomalies are more subtle or difficult to describe with simple
textual prompts. For example, in the ‘Shoplifting’ category,
ReFLIP-VAD achieves an Ano-AUC of 62.2%, which is comparable to the performance of UB-MIL at 62.3% and slightly
higher than the performance of DMU at 62.2%. Similarly, in
the ‘Fighting’ category, ReFLIP-VAD scores 73.5%, which,
although higher than the performance of UB-MIL at 65.9%
and DMU at 65.4%, is not as significantly superior as in other
categories. These cases highlight the challenges ReFLIP-VAD
faces in scenarios where the anomalous actions are subtle,
less visually distinctive, or not easily captured by the prompt
dictionary used to describe anomalies.
The class-wise Average Precision (AP) results on the XDViolence dataset for top three performing methods: DMU,
CLIP-TSA, and ReFLIP-VAD is presented in Figure 11.
ReFLIP-VAD consistently demonstrates superior performance
across various violence categories. For instance, in the ‘Abuse
category, ReFLIP-VAD achieves an AP of 70.9%, outperforming CLIP-TSA and DMU, which attain 65.9% and 57.8%, respectively. Similarly, in the ‘Car Accident’ category, ReFLIP-

© 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2024.3482007

14

VAD leads with an AP of 77.1%, followed by CLIP-TSA
at 75.2% and DMU at 73.4%. These results highlight the
effectiveness of ReFLIP-VAD in accurately identifying and
classifying different types of violent events, which is crucial
for applications in surveillance and security.
V. C ONCLUSION
This paper introduces ReFLIP-VAD, an innovative framework for video anomaly detection that leverages the strengths
of vision-language models. By employing a reparameterized
prompt encoder, ReFLIP-VAD generates contextually rich and
interpretable prompt templates, enhancing the detection of
specific semantics associated with anomalies. The proposed
approach incorporates a dual-block architecture, consisting
of a classification block and a video-text alignment block,
enabling effective anomaly detection at both coarse and finegrained levels. This approach is further strengthened by the
Glimpse-Emphasize network, which captures both global and
local temporal dependencies, and the MIL-Align mechanism,
optimizing visual-language alignment under weak supervision.
Extensive evaluations on benchmark datasets demonstrate that
ReFLIP-VAD outperforms existing methods, achieving stateof-the-art performance. As a future research direction, the
proposed approach can be adapted to handle situations where
anomalies are not predefined, improving its effectiveness in
real-world settings where unexpected events frequently occur.
This will enable the model to identify and categorize new
unseen types of anomalies that were not part of its initial
training.
R EFERENCES
[1] A. Acsintoae, A. Florescu, M.-I. Georgescu, T. Mare, P. Sumedrea, R. T.
Ionescu, F. S. Khan, and M. Shah, “Ubnormal: New benchmark for
supervised open-set video anomaly detection,” in Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern Recognition,
2022, pp. 20 143–20 153.
[2] Y. Liang, J. Zhang, S. Zhao, R. Wu, Y. Liu, and S. Pan, “Omni-frequency
channel-selection representations for unsupervised anomaly detection,”
IEEE Transactions on Image Processing, 2023.
[3] Z. Yang, Y. Guo, J. Wang, D. Huang, X. Bao, and Y. Wang, “Towards
video anomaly detection in the real world: A binarization embedded
weakly-supervised network,” IEEE Transactions on Circuits and Systems
for Video Technology, 2023.
[4] D. Tran, L. Bourdev, R. Fergus, L. Torresani, and M. Paluri, “Learning
spatiotemporal features with 3d convolutional networks,” in Proceedings
of the IEEE international conference on computer vision, 2015, pp.
4489–4497.
[5] B. Zhang and J. Xue, “Weakly-supervised anomaly detection with a
sub-max strategy,” Neurocomputing, p. 126770, 2023.
[6] J. Carreira and A. Zisserman, “Quo vadis, action recognition? a new
model and the kinetics dataset,” in 2017 IEEE Conference on Computer
Vision and Pattern Recognition (CVPR), 2017, pp. 4724–4733.
[7] P. P. Dev, P. Das, and R. Hazari, “Msdeepnet: A novel multi-stream deep
neural network for real-world anomaly detection in surveillance videos,”
in International Conference on Deep Learning Theory and Applications.
Springer, 2023, pp. 157–172.
[8] H. Yuan, Z. Cai, H. Zhou, Y. Wang, and X. Chen, “Transanomaly: Video
anomaly detection using video vision transformer,” IEEE Access, vol. 9,
pp. 123 977–123 986, 2021.
[9] W. Sultani, C. Chen, and M. Shah, “Real-world anomaly detection in
surveillance videos,” in Proceedings of the IEEE conference on computer
vision and pattern recognition, 2018, pp. 6479–6488.
[10] A. Radford, J. W. Kim, C. Hallacy, A. Ramesh, G. Goh, S. Agarwal,
G. Sastry, A. Askell, P. Mishkin, J. Clark et al., “Learning transferable
visual models from natural language supervision,” in International
conference on machine learning. PMLR, 2021, pp. 8748–8763.

[11] C. Jia, Y. Yang, Y. Xia, Y.-T. Chen, Z. Parekh, H. Pham, Q. Le, Y.-H.
Sung, Z. Li, and T. Duerig, “Scaling up visual and vision-language
representation learning with noisy text supervision,” in International
conference on machine learning. PMLR, 2021, pp. 4904–4916.
[12] K. Zhou, J. Yang, C. C. Loy, and Z. Liu, “Learning to prompt for visionlanguage models,” International Journal of Computer Vision, vol. 130,
no. 9, pp. 2337–2348, 2022.
[13] L. Yao, R. Huang, L. Hou, G. Lu, M. Niu, H. Xu, X. Liang, Z. Li,
X. Jiang, and C. Xu, “Filip: Fine-grained interactive language-image
pre-training,” arXiv preprint arXiv:2111.07783, 2021.
[14] P. Wu, X. Liu, and J. Liu, “Weakly supervised audio-visual violence
detection,” IEEE Transactions on Multimedia, 2022.
[15] C. Ju, T. Han, K. Zheng, Y. Zhang, and W. Xie, “Prompting visuallanguage models for efficient video understanding,” in European Conference on Computer Vision. Springer, 2022, pp. 105–124.
[16] P. Wu, X. Zhou, G. Pang, L. Zhou, Q. Yan, P. Wang, and Y. Zhang,
“Vadclip: Adapting vision-language models for weakly supervised video
anomaly detection,” in Proceedings of the AAAI Conference on Artificial
Intelligence, vol. 38, no. 6, 2024, pp. 6074–6082.
[17] V. Sanh, L. Debut, J. Chaumond, and T. Wolf, “Distilbert, a distilled
version of bert: smaller, faster, cheaper and lighter,” arXiv preprint
arXiv:1910.01108, 2019.
[18] P. Wu, J. Liu, and F. Shen, “A deep one-class neural network for
anomalous event detection in complex scenes,” IEEE transactions on
neural networks and learning systems, vol. 31, no. 7, pp. 2609–2622,
2019.
[19] Y. Liu, J. Liu, J. Lin, M. Zhao, and L. Song, “Appearance-motion
united auto-encoder framework for video anomaly detection,” IEEE
Transactions on Circuits and Systems II: Express Briefs, vol. 69, no. 5,
pp. 2498–2502, 2022.
[20] Y. Liu, Z. Xia, M. Zhao, D. Wei, Y. Wang, S. Liu, B. Ju, G. Fang, J. Liu,
and L. Song, “Learning causality-inspired representation consistency for
video anomaly detection,” in Proceedings of the 31st ACM International
Conference on Multimedia, 2023, pp. 203–212.
[21] H. Song, C. Sun, X. Wu, M. Chen, and Y. Jia, “Learning normal patterns
via adversarial attention-based autoencoder for abnormal event detection
in videos,” IEEE Transactions on Multimedia, vol. 22, no. 8, pp. 2138–
2148, 2019.
[22] X. Wang, Z. Che, B. Jiang, N. Xiao, K. Yang, J. Tang, J. Ye, J. Wang,
and Q. Qi, “Robust unsupervised video anomaly detection by multipath
frame prediction,” IEEE transactions on neural networks and learning
systems, vol. 33, no. 6, pp. 2301–2312, 2021.
[23] P. Jin, L. Mou, G.-S. Xia, and X. X. Zhu, “Anomaly detection in
aerial videos with transformers,” IEEE Transactions on Geoscience and
Remote Sensing, vol. 60, pp. 1–13, 2022.
[24] Z. Yang, J. Liu, Z. Wu, P. Wu, and X. Liu, “Video event restoration
based on keyframes for video anomaly detection,” in Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern Recognition,
2023, pp. 14 592–14 601.
[25] Y. Chang, Z. Tu, W. Xie, B. Luo, S. Zhang, H. Sui, and J. Yuan,
“Video anomaly detection with spatio-temporal dissociation,” Pattern
Recognition, vol. 122, p. 108213, 2022.
[26] C. Guo, H. Wang, Y. Xia, and G. Feng, “Learning appearance-motion
synergy via memory-guided event prediction for video anomaly detection,” IEEE Transactions on Circuits and Systems for Video Technology,
2023.
[27] G. Wang, Y. Wang, J. Qin, D. Zhang, X. Bao, and D. Huang, “Video
anomaly detection by solving decoupled spatio-temporal jigsaw puzzles,” in European Conference on Computer Vision. Springer, 2022,
pp. 494–511.
[28] Y. Zhong, X. Chen, J. Jiang, and F. Ren, “A cascade reconstruction
model with generalization ability evaluation for anomaly detection in
videos,” Pattern Recognition, vol. 122, p. 108336, 2022.
[29] X. Zeng, Y. Jiang, W. Ding, H. Li, Y. Hao, and Z. Qiu, “A hierarchical
spatio-temporal graph convolutional neural network for anomaly detection in videos,” IEEE Transactions on Circuits and Systems for Video
Technology, vol. 33, no. 1, pp. 200–212, 2021.
[30] Y. Zhong, X. Chen, Y. Hu, P. Tang, and F. Ren, “Bidirectional spatiotemporal feature learning with multiscale evaluation for video anomaly
detection,” IEEE Transactions on Circuits and Systems for Video Technology, vol. 32, no. 12, pp. 8285–8296, 2022.
[31] D. Li, X. Nie, R. Gong, X. Lin, and H. Yu, “Multi-branch gan-based
abnormal events detection via context learning in surveillance videos,”
IEEE Transactions on Circuits and Systems for Video Technology, 2023.
[32] J.-X. Zhong, N. Li, W. Kong, S. Liu, T. H. Li, and G. Li, “Graph
convolutional label noise cleaner: Train a plug-and-play action classifier

© 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Circuits and Systems for Video Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCSVT.2024.3482007

15

for anomaly detection,” in Proceedings of the IEEE/CVF conference on
computer vision and pattern recognition, 2019, pp. 1237–1246.
[33] H. Lv, C. Zhou, Z. Cui, C. Xu, Y. Li, and J. Yang, “Localizing anomalies
from weakly-labeled videos,” IEEE transactions on image processing,
vol. 30, pp. 4505–4515, 2021.
[34] Y. Tian, G. Pang, Y. Chen, R. Singh, J. W. Verjans, and G. Carneiro,
“Weakly-supervised video anomaly detection with robust temporal feature magnitude learning,” in Proceedings of the IEEE/CVF international
conference on computer vision, 2021, pp. 4975–4986.
[35] C. Huang, C. Liu, J. Wen, L. Wu, Y. Xu, Q. Jiang, and Y. Wang,
“Weakly supervised video anomaly detection via self-guided temporal
discriminative transformer,” IEEE Transactions on Cybernetics, 2022.
[36] Y. Liu, J. Liu, M. Zhao, S. Li, and L. Song, “Collaborative normality
learning framework for weakly supervised video anomaly detection,”
IEEE Transactions on Circuits and Systems II: Express Briefs, vol. 69,
no. 5, pp. 2508–2512, 2022.
[37] Y. Chen, Z. Liu, B. Zhang, W. Fok, X. Qi, and Y.-C. Wu, “Mgfn:
Magnitude-contrastive glance-and-focus network for weakly-supervised
video anomaly detection,” in Proceedings of the AAAI Conference on
Artificial Intelligence, vol. 37, no. 1, 2023, pp. 387–395.
[38] Y. Fan, Y. Yu, W. Lu, and Y. Han, “Weakly-supervised video anomaly
detection with snippet anomalous attention,” IEEE Transactions on
Circuits and Systems for Video Technology, 2024.
[39] W. Yu, Y. Liu, W. Hua, D. Jiang, B. Ren, and X. Bai, “Turning a clip
model into a scene text detector,” in Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition, 2023, pp.
6978–6988.
[40] J. Lee, J. Kim, H. Shon, B. Kim, S. H. Kim, H. Lee, and J. Kim, “Uniclip: Unified framework for contrastive language-image pre-training,”
Advances in Neural Information Processing Systems, vol. 35, pp. 1008–
1019, 2022.
[41] H. Xu, G. Ghosh, P.-Y. Huang, D. Okhonko, A. Aghajanyan,
F. Metze, L. Zettlemoyer, and C. Feichtenhofer, “Videoclip: Contrastive
pre-training for zero-shot video-text understanding,” arXiv preprint
arXiv:2109.14084, 2021.
[42] L. Zanella, B. Liberatori, W. Menapace, F. Poiesi, Y. Wang, and E. Ricci,
“Delving into clip latent space for video anomaly recognition,” arXiv
preprint arXiv:2310.02835, 2023.
[43] Z. Yang, J. Liu, and P. Wu, “Text prompt with normality guidance
for weakly supervised video anomaly detection,” in Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern Recognition,
2024, pp. 18 899–18 908.
[44] P. Wu, X. Zhou, G. Pang, Y. Sun, J. Liu, P. Wang, and Y. Zhang, “Openvocabulary video anomaly detection,” in Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition, 2024, pp.
18 297–18 307.
[45] A. Dosovitskiy, L. Beyer, A. Kolesnikov, D. Weissenborn, X. Zhai,
T. Unterthiner, M. Dehghani, M. Minderer, G. Heigold, S. Gelly et al.,
“An image is worth 16x16 words: Transformers for image recognition
at scale,” arXiv preprint arXiv:2010.11929, 2020.
[46] R. Sennrich, B. Haddow, and A. Birch, “Neural machine translation of
rare words with subword units,” arXiv preprint arXiv:1508.07909, 2015.
[47] A. Radford, J. Wu, R. Child, D. Luan, D. Amodei, I. Sutskever et al.,
“Language models are unsupervised multitask learners,” OpenAI blog,
vol. 1, no. 8, p. 9, 2019.
[48] P. Wu, J. Liu, Y. Shi, Y. Sun, F. Shao, Z. Wu, and Z. Yang, “Not
only look, but also listen: Learning multimodal violence detection under
weak supervision,” in Computer Vision–ECCV 2020: 16th European
Conference, Glasgow, UK, August 23–28, 2020, Proceedings, Part XXX
16. Springer, 2020, pp. 322–339.
[49] K.-L. Li, H.-K. Huang, S.-F. Tian, and W. Xu, “Improving one-class svm
for anomaly detection,” in Proceedings of the 2003 international conference on machine learning and cybernetics (IEEE Cat. No. 03EX693),
vol. 5. IEEE, 2003, pp. 3077–3081.
[50] M. Hasan, J. Choi, J. Neumann, A. K. Roy-Chowdhury, and L. S. Davis,
“Learning temporal regularity in video sequences,” in Proceedings of the
IEEE conference on computer vision and pattern recognition, 2016, pp.
733–742.
[51] J. Zhang, L. Qing, and J. Miao, “Temporal convolutional network with
complementary inner bag loss for weakly supervised anomaly detection,”
in 2019 IEEE International Conference on Image Processing (ICIP).
IEEE, 2019, pp. 4030–4034.
[52] Y. Zhu and S. Newsam, “Motion-aware feature for improved video
anomaly detection,” arXiv preprint arXiv:1907.10211, 2019.
[53] Y. Zhen, Y. Guo, J. Wei, X. Bao, and D. Huang, “Multi-scale background
suppression anomaly detection in surveillance videos,” in 2021 IEEE

International Conference on Image Processing (ICIP). IEEE, 2021,
pp. 1114–1118.
[54] P. Wu and J. Liu, “Learning causal temporal relation and feature
discrimination for anomaly detection,” IEEE Transactions on Image
Processing, vol. 30, pp. 3513–3527, 2021.
[55] Y. Pu and X. Wu, “Locality-aware attention network with discriminative
dynamics learning for weakly supervised anomaly detection,” in 2022
IEEE International Conference on Multimedia and Expo (ICME). IEEE,
2022, pp. 1–6.
[56] S. Park, H. Kim, M. Kim, D. Kim, and K. Sohn, “Normality guided multiple instance learning for weakly supervised video anomaly detection,”
in Proceedings of the IEEE/CVF Winter Conference on Applications of
Computer Vision, 2023, pp. 2665–2674.
[57] H. Zhou, J. Yu, and W. Yang, “Dual memory units with uncertainty regulation for weakly supervised video anomaly detection,” in Proceedings
of the AAAI Conference on Artificial Intelligence, vol. 37, no. 3, 2023,
pp. 3769–3777.
[58] H. Lv, Z. Yue, Q. Sun, B. Luo, Z. Cui, and H. Zhang, “Unbiased multiple
instance learning for weakly supervised video anomaly detection,” in
Proceedings of the IEEE/CVF conference on computer vision and
pattern recognition, 2023, pp. 8022–8031.
[59] H. K. Joo, K. Vo, K. Yamazaki, and N. Le, “Clip-tsa: Clip-assisted
temporal self-attention for weakly-supervised video anomaly detection,”
in 2023 IEEE International Conference on Image Processing (ICIP).
IEEE, 2023, pp. 3230–3234.
[60] M. Cho, M. Kim, S. Hwang, C. Park, K. Lee, and S. Lee, “Look around
for anomalies: weakly-supervised anomaly detection via context-motion
relational learning,” in Proceedings of the IEEE/CVF conference on
computer vision and pattern recognition, 2023, pp. 12 137–12 146.
[61] L. Van der Maaten and G. Hinton, “Visualizing data using t-sne.” Journal
of machine learning research, vol. 9, no. 11, 2008.
Prabhu Prasad Dev (Graduate Student Member,
IEEE) received his B.Tech and M.Tech degree
from KIIT Deemed to be University, Bhubaneswar,
Odisha, India in 2019 and 2021 respectively. He is
currently pursuing the PhD degree in the Department of Computer Science and Engineering, National Institute of Technology, Calicut, Kerala, India.
Also, he is currently working as Assistant Professor
at KIIT Deemed to be University, Bhubaneswar,
Odisha, India. He has more than 5 years of teaching
experience. His research interests include computer
vision, anomaly detection, video analysis, and deep learning.
Raju Hazari (Member, IEEE) received his B.E and
M.E degree in Information Technology from Indian
Institute of Engineering Science and Technology,
Shibpur, West Bengal, India, in 2009 and 2013 respectively. He received a PhD degree in Engineering
from the Department of Information Technology in
Indian Institute of Engineering Science and Technology, Shibpur, West Bengal, India, in 2019. He
has more than 4 years of teaching experience. He
has authored and co-authored over 15 journals and
conference papers. Currently, he is working as an
assistant professor in the Department of Computer Science and Engineering at
National Institute of Technology Calicut, Kerala, India. His research interests
include Machine learning, Cellular automata, and Computational Biology.
Pranesh Das (Member, IEEE) received his B.Tech
degree in information technology from Maulana
Abul Kalam Azad University of Technology, West
Bengal, India, in 2007, M.Tech degree in computer
science and engineering from the National Institute of Technology Rourkela, India, in 2013 and
Ph.D from the Department of Computer Science
and Engineering in National Institute of Technology
Nagaland, India in 2019.
He has more than 10 years of teaching experience. He has publications in reputed journals and
conferences including IEEE Transactions on Emerging Topics in Computing,
IEEE Sensors journal and Applied soft computing, Elsevier. Currently, he
is working as an assistant professor at the National Institute of Technology
Calicut, Kerala, India. His research interests include computer vision, machine
learning, data mining, soft computing, and optimization algorithms.

© 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.See https://www.ieee.org/publications/rights/index.html for more information.
PAPER_TEXT
