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
# [537] Self-Calibrated CLIP for Training-Free Open-Vocabulary Segmentation
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
编号：537
题名：Self-Calibrated CLIP for Training-Free Open-Vocabulary Segmentation
年份：2025
DOI：10.1109/tip.2025.3639996
来源：IEEE Transactions on Image Processing
PDF：paper/10.1109_TIP.2025.3639996.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：无
相关性：弱相关，分数 
已有代码状态：候选不可访问；SCCLIP

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\537.txt
- 原始字符数：71415
- 本次发送字符数：71415
- 是否截断：False

代码包：
- 仓库：SCCLIP
  - URL：https://github.com/SuleBai/SCCLIP
  - 状态：failed
  - 本地目录：source\SCCLIP
  - 顶层结构：
  - 主要语言：
  - README 标题：
  - README 运行线索：
  - 关键文件：{}
  - 数据集线索：

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

8271

Self-Calibrated CLIP for Training-Free
Open-Vocabulary Segmentation
Sule Bai , Yong Liu , Yifei Han, Haoji Zhang , Yansong Tang , Member, IEEE, Jie Zhou , Fellow, IEEE,
and Jiwen Lu , Fellow, IEEE

Abstract—Recent advancements in pre-trained vision-language
models like CLIP, have enabled the task of open-vocabulary
segmentation. CLIP demonstrates impressive zero-shot capabilities in various downstream tasks that require holistic image
understanding. However, due to the image-level contrastive
learning and fully global feature interaction, ViT-based CLIP
struggles to capture local details, resulting in poor performance in
segmentation tasks. Our analysis of ViT-based CLIP reveals that
anomaly tokens emerge during the forward process, attracting
disproportionate attention from normal patch tokens and thereby
diminishing spatial awareness. To address this issue, we propose
Self-Calibrated CLIP (SC-CLIP), a training-free method that
calibrates CLIP to generate finer representations while preserving its original generalization ability—without introducing
new parameters or relying on additional backbones. Specifically, we mitigate the negative impact of anomaly tokens from
two complementary perspectives. First, we explicitly identify
the anomaly tokens and replace them based on local context.
Second, we reduce their influence on normal tokens by enhancing
feature discriminability and attention correlation, leveraging the
inherent semantic consistency within CLIP’s mid-level features.
In addition, we introduce a two-pass strategy that effectively
integrates multi-level features to enrich local details under the
training-free setting. Together, these strategies enhance CLIP’s
feature representations with improved granularity and semantic
coherence. Experimental results demonstrate the effectiveness of
SC-CLIP, achieving state-of-the-art results across all datasets
and surpassing previous methods by 9.5%. Notably, SC-CLIP
boosts the performance of vanilla CLIP ViT-L/14 by 6.8 times.
Furthermore, we discuss our method’s applicability to other
vision–language models and tasks for a comprehensive evaluation.
Our source code is available at https://github.com/SuleBai/SCCLIP
Index Terms—Open-vocabulary segmentation, training-free.

I. I NTRODUCTION

O

PEN-VOCABULARY Segmentation (OVS) is an emerging task in computer vision that aims to segment

Received 10 July 2025; revised 9 October 2025 and 20 November
2025; accepted 27 November 2025. Date of publication 10 December
2025; date of current version 16 December 2025. This work was supported in part by Shenzhen Science and Technology Program under Grant
CJGJZD20220517142402006 and in part by the National Natural Science
Foundation of China under Grant 62206153. The associate editor coordinating
the review of this article and approving it for publication was Dr. Deng-Ping
Fan. (Sule Bai and Yong Liu contributed equally to this work.) (Corresponding
author: Yansong Tang.)
Sule Bai, Yong Liu, Yifei Han, Haoji Zhang, and Yansong Tang are
with Shenzhen International Graduate School, Tsinghua University, Shenzhen 518055, China (e-mail: bsl23@mails.tsinghua.edu.cn; tang.yansong@sz.
tsinghua.edu.cn).
Jie Zhou and Jiwen Lu are with the Department of Automation, Tsinghua
University, Beijing 100084, China.
Digital Object Identifier 10.1109/TIP.2025.3639996

Fig. 1. Left: Vanilla CLIP produces a noisy segmentation map, while
our Self-Calibrated CLIP (SC-CLIP) generates a much clearer and finer
result. Right: Performance comparison of the open-vocabulary segmentation
methods, where our SC-CLIP achieves the best results across all benchmarks.

arbitrary categories based on the textual inputs, overcoming the
limitations of predefined category sets. To achieve this, models
must generalize beyond the training data. Vision-language
pretrained models such as CLIP [1], demonstrate remarkable
zero-shot capabilities by leveraging large-scale image-text
pairs, effectively fulfilling these requirements. However, the
image-level pre-training strategy and fully global feature interactions of ViT-based CLIP leads to an excessive emphasis
on global context, neglecting local and fine-grained details
essential for dense prediction tasks. Consequently, directly
applying ViT-based CLIP to segmentation tasks yields poor
performance. For example, as shown in Figure 1, the segmentation result generated by patch-text cosine similarity exhibits
considerable noise. CLIP ViT-B/16 achieves only 8.9% mIoU
on the COCO-Object dataset [2], significantly lagging behind
its ability on image-level recognition.
To address ViT-based CLIP’s limitations in capturing local
details, recent studies have proposed various modifications to
its last layer. One line of research [3], [4], [5], [6], [7], [8],
[9], [10] introduces correlative attention, replacing the original
QK> attention with alternatives like KK> , to enhance focus
on relevant regions. But these methods still operate on the
global and noisy inputs, hindering their effectiveness. Another
approach [11], [12] incorporates additional backbones [13],
[14], [15] like DINO [13] to provide richer spatial details.
Despite performance gains, they fail to fully exploit CLIP’s
semantic knowledge and impose extra computational costs. In

1941-0042 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

8272

Fig. 2. Anomaly tokens in CLIP. In (a), we visualize the attention maps of
various selected patches (marked by F), which all exhibit excessive focus
on the same regions (indicated by the orange dashed circle). And this region
aligns with the outliers identified in the PCA analysis shown in (b).

fact, both strategies overlook the underlying causes of CLIP’s
global focus, preventing them from fundamentally resolving
the issue of diminished spatial awareness in CLIP.
Motivated by these limitations, we begin with an in-depth
analysis of CLIP. As indicated by the orange dashed circles
in Figure 2 (a), we observe that different patch tokens consistently exhibit high activation regions within their attention
map. These regions attract excessive attention from other
normal patches, distracting their focus away from local and
relevant areas. To further investigate, we perform PCA [16]
on the patch-level features from CLIP’s last layer and project
them into a 2D space, as shown in Figure 2 (b), revealing
these over-attended tokens significantly differ from the normal
ones (including the [CLS] token). Thus, we refer to them as
anomaly tokens. We attribute CLIP’s disadvantage in dense
prediction tasks to the emergence of anomaly tokens, which
leads to uniform attention activations across locations. This
disrupts the attention’s ideal ability to extract relevant semantics, resulting in feature homogenization that diminishes local
awareness and further exacerbates noise in the feature maps.
Building on this analysis, we propose enhancing CLIP’s
feature representation by weakening the influence of anomaly
tokens. To this end, we introduce Self-Calibrated CLIP (SCCLIP), a training-free approach that leverages CLIP’s inherent
properties for effective calibration, strengthening its perception
on local and relevant regions.
Specifically, we address the negative impact of anomaly
tokens from two perspectives. On the one hand, we propose
directly resolving these anomaly tokens. To identify them, we
apply the Local Outlier Factor (LOF) algorithm [17], a method
for detecting outliers. Once located, we replace these anomaly
tokens with values interpolated from their spatial neighbors,
considering that spatially close regions often share similar
semantics. This not only serves as a regularization to prevent
inappropriate attention focus but also reassigns meaningful
semantic information to the anomaly tokens, aligning them
with the local context. On the other hand, to relieve the
feature homogenization problem caused by anomaly tokens,
we propose a self-adjusting strategy to enhance feature discriminability and attention correlation. We observe that the
mid-layers’ features of CLIP exhibit good semantic coherence,

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

as shown in Figure 4. In order to retain the rich semantics
of deep features and the spatial consistency of mid-level
features, we utilize the latter to adaptively aggregate deep
features, while simultaneously enhancing attention correlation.
This self-adjusting approach improves the overall semantic
coherence. Furthermore, we explore how to effectively leverage multi-level feature fusion under the training-free setting
and propose a two-pass strategy to enhance the capture of
details at different scales. The key insights lie in ensuring
feature compatibility across layers through alignment with
CLIP’s final layer, and preserving the integrity of the lastlayer features to maintain strong cross-modal correspondence.
Experimental results demonstrate that SC-CLIP achieves
remarkable performance, establishing new state-of-the-art
results across eight datasets, as shown in Figure 1. Our
approach significantly outperforms previous methods by 9.5%
on CLIP ViT-B/16. Notably, SC-CLIP boosts the performance
of vanilla CLIP ViT-L/14 by 6.8 times, without the need for
additional parameters, data, or backbones.
Our contributions can be summarized as follows:
• We propose SC-CLIP, a training-free method designed to
enhance CLIP’s dense feature representation, effectively
addressing the uniform attention activations and feature
homogenization caused by the anomaly tokens.
• We mitigate the negative effects of anomaly tokens from
two perspectives. First, we explicitly address the anomaly
tokens based on local context. Second, we reduce their
impact on normal tokens by enhancing feature discriminability and attention correlation, leveraging the spatial
consistency inherent in CLIP’s mid-level features.
• Our approach sets new state-of-the-art results across popular benchmarks. And we conduct extensive experiments
to validate the effectiveness of our method.
II. R ELATED W ORK
This section focuses on two interrelated areas: visionlanguage pretrained models and open-vocabulary segmentation. We highlight significant advancements and ongoing
challenges, providing a critical overview that identifies gaps in
current research and proposes directions for future exploration.
A. Vision-Language Pretrained Models
Vision-language models [1], [18], [19], [20], [21], [22]
pretrained on large-scale web data, represented by CLIP [1],
employ contrastive learning to align images with associated
captions. These models have demonstrated remarkable zeroshot capabilities across various downstream tasks that require
comprehensive image understanding, such as visual question
answering and image-text retrival [23], [24], [25]. However,
CLIP’s image-level pre-training, which relies on the [CLS]
token to represent the whole image, causes the model to excessively focus on the global features at the expense of local and
fine-grained details. This limitation hinders its performance in
dense prediction tasks which require pixel-level understanding.
To address this, our work focuses on effectively adapting CLIP
for segmentation task while preserving its original knowledge
and cross-modal alignment capabilities.

BAI et al.: SELF-CALIBRATED CLIP FOR TRAINING-FREE OPEN-VOCABULARY SEGMENTATION

8273

Fig. 3. Resolving the Anomaly Tokens. (a) Illustration of the resolving process. We plot the feature map using the mean value of each token. After locating
the anomaly tokens (the center of red square), we replace them with the interpolated values obtained from their neighboring regions. (b) Effect on the attention
map. We highlight the changes on attention map for a normal token (F), and an anomaly token (N).

QK> attention with the combination of QQ> and KK> attention, to enhance correlation. GEM [5] proposes generalized
self-self attention and a set of regularizations. ClearCLIP
[7] identifies the primary source of noise stems from the
residual connections, and proposes to remove it. CLIPTrase
[10] notices the [CLS] token may disrupt the patch correlations
and proposes using self-self attention along with clustering and
denoising for post-processing. Other works leverage additional
vision models like DINO [13] and SAM [14] for providing
fine-grained spatial details. For example, CLIP-DINOiser [12]
refines feature maps using the affinity learned from DINO’s
feature correspondence, while ProxyCLIP [11] applies them to
adjust attention weights. In contrast, our approach improves
semantic coherence by exploiting CLIP’s internal properties
and explicitly resolving the negative impact of anomaly tokens.
III. M ETHOD
Fig. 4. Top: Visualization of patch similarities shows that CLIP’s last-layer
features perform poorly, but its mid-level features exhibit semantic consistency
comparable to DINO. Bottom Left: ROC curve analysis further supports this
observation, with our SC-CLIP showing superior semantic coherence. Bottom
Right: Detailed ROC analysis of our method.

B. Open-Vocabulary Segmentation
The open-vocabulary segmentation (OVS) task [26] focuses
on segmenting images with arbitrary text queries by leveraging
the zero-shot capabilities of vision-language models [1], [18].
This task has broad potential applications across many visionrelated tasks [27], [28], [29], [30], [31], [32], [33], [34], [35].
Existing works can be broadly classified into three categories:
fully-supervised, weakly-supervised and training-free. Fullysupervised methods [36], [37], [38], [39], [40], [41], [42],
[43], [44], [45], [46], [47], [48], [49], [50], [51] require finetuning on pixel-level annotated datasets. Weakly-supervised
approaches [52], [53], [54], [55], [56], [57], [58], [59] reduce
reliance on dense annotations by using image-text pair to guide
region grouping. Training-free methods [3], [4], [5], [6], [8],
[9], [10], [11], [12], [60], [61], [62], [63] directly use CLIP for
segmentation by making minimal adjustments to the model’s
architecture without additional training.
Our approach needs no training and falls into the third
category. Recent methods have discovered that CLIP’s finallayer exhibits poor spatial consistency and proposed various
modifications. For instance, SCLIP [4] replaces the original

In this section, we begin with an overview of CLIP and
its dense inference pipeline. We then present SC-CLIP, our
training-free approach designed to enhance CLIP’s dense representation. We address anomaly tokens from two perspectives.
First, we directly identify these tokens and replace them
based on local context. Next, to mitigate their influence on
normal tokens, we leverage mid-level features with stronger
spatial consistency to guide the adaptive aggregation of deep
features and enhance the attention correlation. Furthermore,
we propose a two-pass strategy to effectively integrate multilevel features and enrich spatial details.
A. Preliminaries
CLIP ViT model encodes an input image into a token
sequence X = [xcls , x1 , . . . , xN ], where xcls is the [CLS] token
and the others represent dense visual features, comprising N
patch tokens. The CLIP model includes multiple layers, with
each layer l processing the input X(l−1) as follows:
Zl = SA(LN(X(l−1) )) + X(l−1)

(1)

X = FFN(LN(Z )) + Z

(2)

l

l

l

where SA, FFN and LN denote self-attention module, feedforward network, and layer normalization, respectively.
For dense inference, the visual features are aligned with C
categories to produce the patch-text similarity map of dimensions N × C. And the final segmentation result is obtained by
applying argmax operation to this similarity map.

8274

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

Our method is training-free and modifies only the last
layer of the CLIP visual encoder while keeping the other
layers unchanged to prevent model collapse. For clarity and
consistency in notation, we denote X penul and Xlast as the
penultimate and last feature representations, respectively.

reducing attention on relevant local areas, and 2) anomaly
tokens focus on prominent objects and other anomaly tokens.
After resolving the anomaly tokens via interpolation, normal
tokens refocus on relevant local regions, while the updated
anomaly tokens also shift attention to appropriate areas.

B. Resolving the Anomaly Tokens

C. Self-Adjusting for Semantic Coherence

We attribute CLIP’s limitations in dense prediction tasks to
the presence of anomaly tokens within its features, which deviate significantly from normal tokens. These anomaly tokens
cause other tokens to disproportionately focus on them in deep
layers, leading to identical attention activation, which undermines attention’s capacity to extract semantically coherent
regions. Since attention mechanism [64], [65] manages spatial
arrangements, this pattern intensifies noise in the feature map,
ultimately degrading performance. Studies [66], [67] suggest
that pretrained models like CLIP may identify redundant
tokens and use them to gather global information, thereby
expediting processing. However, these tokens lack semantics,
conveying minimal information about their original positions.
Existing methods do not explicitly address the anomaly tokens
or the impact they cause to other normal tokens.
To address the negative impact of anomaly tokens, we
propose an intuitive approach to directly resolve them in X penul
before the last layer, as illustrated in Figure 3 (a). First, it
is essential to identify the anomaly tokens. As previously
analyzed in Figure 2, they exhibit a clear distinction from
other tokens. To detect these anomalies, we employ the Local
Outlier Factor (LOF) algorithm [17], a widely used method for
anomaly detection. LOF identifies outliers by measuring the
local density deviation of a data point relative to its neighbors.
Specifically, it computes the local reachability density and
assigns a high LOF score to points with significantly lower
density than their neighbors, indicating potential anomalies.
Besides, we implement the PyTorch-based LOF algorithm to
enhance the computational efficiency.
Once the anomalies are located, we replace them with the
values interpolated from their 3×3 neighboring regions, based
on the assumption that features in spatially adjacent regions are
generally similar. Specifically, we apply a 3 × 3 convolution
kernel with the center set to 0. And if neighboring regions
contain any other anomaly tokens, they are explicitly excluded
from the interpolation. The operation’s formula is provided
below, where X̃ penul denotes the feature after operation and A
is the set of anomaly tokens.
P1 P1
penul
i=−1
j=−1 wi, j · X(x+i,y+ j)
penul
, ∀(x, y) ∈ A
X̃(x,y) =
P1 P1
i=−1
j=−1 wi, j
(
0, if (x + i, y + j) ∈ A
wi, j =
(3)
1, otherwise

After resolving the anomaly tokens, the model reduces focus
on them in the last layer’s attention. However, a challenge
still remains: anomaly tokens have already caused substantial
disruption to other normal tokens in the previous layers,
diminishing their local awareness.
To alleviate this influence and further enhance feature discriminability and attention correlation, we seek to restore the
spatial structure among normal tokens. Some existing methods
[11], [12] address this by introducing backbones with strong
spatial coherence, such as DINO [13] and SAM [14], to
provide fine-grained details. While effective, these approaches
rely on additional backbones and incur extra computational
costs during training and inference.
This motivates us to explore whether such semantic coherence can be uncovered within CLIP itself. We begin by
visualizing patch similarities, as shown in Figure 4 (top),
where we observe the CLIP’s last layer performs poorly as
expected. However, its mid-layer exhibits stronger semantic
coherence, comparable to that of DINO. To further validate
this observation, we quantitatively evaluate all features of
CLIP using ROC curve analysis. Specifically, we use 2000
images from the ADE20K validation set [68]. For each
image, we extract patch-level features at each layer l and
compute their cosine similarity to construct the similarity map
l l
·X
Simil ∈ RN×N , defined as Simil = kXXl kkX
l k . This similarity
map serves as a binary classifier to indicate whether two
patches belong to the same category, with patches of the
same category labeled as 1 and otherwise 0. Each patch’s
category is determined by majority voting on pixel labels in
the segmentation map. A higher area under the curve (AUC) in
ROC analysis reflects better semantic consistency. As shown
in Figure 4 (bottom left), CLIP’s mid-layer features exhibit
strong spatial coherence (AUC=0.76), closely matching DINO
(AUC=0.77). However, CLIP’s last-layer features perform
much worse (AUC=0.66).
The OVS task requires spatially coherent cross-modal alignment. CLIP’s last feature Xlast offers rich semantics but lacks
coherence, while its mid-level features Xmid exhibit strong
spatial consistency but are semantically limited. Inspired by
[12], we propose feature aggregation to effectively combine
the strengths of both. As illustrated in Figure 5 (a), we
leverage Simimid to adaptively aggregate Xdeep , generating new
features X̂deep by combining semantically similar patches with
weighted contributions based on their similarity. This process
can be formulated as follows:

We believe that eliminating anomaly tokens offers two key
benefits. First, it acts as a form of regularization for the
attention. Second, it reassigns semantic information to these
anomaly tokens, aligning them with the local context. As
shown in the Figure 3 (b), the vanilla attention in CLIP has two
issues: 1) normal tokens excessively focus on anomaly tokens,

X̂deep
=
p

N
X

deep
Norm(Simimid
(p, q) ) · Xq

(4)

q=1

The Norm function normalizes the sum to 1. The aggregated
features X̂deep show better results than the original Xdeep .

BAI et al.: SELF-CALIBRATED CLIP FOR TRAINING-FREE OPEN-VOCABULARY SEGMENTATION

8275

Fig. 5. Illustration of the self-adjusting strategy. (a) We use the similarity map from CLIP’s mid layer to adaptively aggregate deep features by combining
semantically similar patches, producing clearer results. The second row provides a detailed process for the selected patch F. (b) We apply the similarity map
to enhance attention, broadening and refining the activation regions.

Moreover, we find that the self-self attention (e.g, KK>
attention) proposed in the previous works [4], [5], [6], [7]
exhibit insufficient attention activations. Therefore, we further
incorporate the similarity map Simimid to augment the attention
operation, as detailed in the following formula. As shown in
Figure 5 (b), the attention regions now display more extensive
and accurate activations.
attention score = softmax(KK> ) + softmax(Simimid )

(5)

Feature aggregation and attention enhancement constitute
the self-adjusting strategy, which significantly improves the
semantic coherence, increasing the AUC to 0.80, as shown in
Figure 4 (bottom right). This demonstrates that the inherent
consistency within CLIP’s mid-level features can be effectively
leveraged for adjustment.

D. Two-Pass Strategy
Motivated by the effectiveness of multi-level feature aggregation in enriching details for dense prediction tasks [6],
[69], [70], [71], [72], we explore the potential of leveraging CLIP’s multi-level features in a training-free manner. A
straightforwardP
way is to directly sum features from different
layers:Xlast + i∈M Xi , where M denotes a set of midlevel features (e.g., layers 4 to 9). However, CLIP exhibits
significant discrepancies across different
layers. Specifically,
P
i
the similarity between Xlast and
X
is merely 0.094,
i∈M
and directly summing them severely disrupts CLIP’s crossmodal alignment capability. To address this issue, we note
that different blocks of the ViT-based CLIP encoder capture
complementary visual patterns, from local and structural cues
in mid-level layers to more global and semantic information
in deeper layers. The final visual layer is the only component
whose output is directly contrasted with text embeddings during CLIP pre-training, and we therefore assume it effectively
acts as an alignment head that maps these visual representations into the joint image–text embedding space. Based on
these observations, we derive two key principles for training1
free P
feature fusion O.
Ensuring the compatibility between Xlast
i
and i∈M X is crucial. This can be achieved by leveraging the

parameter space of the last layer
Notably, the

Pfor alignment.
i
similarity between Xlast and L
X
increases
to 0.983,
i∈M
where L denotes the last layer. This indicates that the last
layer can effectively realign the aggregated multi-level features
to match the original last-layer representation, without any
2
fine-tuning.O.
Preserving the integrity of Xlast is critical for
maintaining cross-modal alignment, as it directly corresponds
to the text embeddings.
Based on these insights, we propose a two-pass strategy,
where CLIP’s final layer is explicitly employed for alignment.
This strategy involves two forward passes—one with the original X penul and another
with
 multi-level features, formulated as:
P
i
L(X penul ) + L
X
.Ablation experiments validate that
i∈M
this design enriches the representation with complementary
multi-level information while preserving CLIP’s cross-modal
alignment capability.
IV. E XPERIMENT
A. Experimental Setup
1) Datasets and Metric: We conduct comprehensive evaluations on eight commonly used benchmark datasets, which
are grouped into two categories: 1) with a background class,
including PASCAL VOC (VOC21) [73], PASCAL Context
(Context) [74], and COCO Object (COCO-Obj) [2]; 2) without
a background class, including PASCAL VOC20 (VOC20)
[73], Cityscapes (City) [75], PASCAL Context59 (Context59)
[74], ADE20K (ADE) [68], and COCOStuff (COCO-Stf) [2].
And we evaluate results with the standard mean-intersectionover-union (mIoU) as the metric.
2) Implementation Details: In our experiments, we utilize
the CLIP [1] with ViT-B/16 and ViT-L/14 architectures. And
our code implementation is built on the MMSegmentation.
After deriving the similarity map Simimid from mid-level
features, we apply thresholding following previous works [12],
[77]. Specifically, values below the threshold β are set to
zero to strengthen feature correlation. And we set β to 0.4.
For the evaluation protocol, we adopt the sliding window
inference strategy from SCLIP [4]: input images are resized
to have a short side of 336 (560 for Cityscapes [75] due to its
higher resolution), and the slide inference is conducted with a

8276

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

TABLE I
P ERFORMANCE C OMPARISON OF O UR A PPROACH W ITH OTHER M ETHODS ON E IGHT S EMANTIC S EGMENTATION B ENCHMARKS . F OR A FAIR
C OMPARISON , W E R EPRODUCE A LL M ETHODS F OLLOWING THE E VALUATION P ROTOCOL IN S ECTION IV-A, C ONSIDERING THE D IFFERENT
S ETTINGS U SED BY E ACH M ETHOD . CLIP-DINO ISER† D ENOTES O UR R EPRODUCED R ESULTS U SING O PENAI’ S P RETRAINED W EIGHTS .
W E R EPORT P ROXY CLIP * R ESULTS U SING I TS DINO-B/16 VARIANT

224 × 224 window and a 112 × 112 stride. No post-processing
strategies are applied. Across all datasets, we use the standard
ImageNet prompts [1] combined with their category names to
construct text descriptions. For all the hyper-parameters, we
keep consistent across all datasets without separate tuning.
For datasets with the background class (Pascal VOC and
COCO-Object), we adhere to the evaluation protocol outlined
in previous works [4], [8], [11], [63]. Since the “background”
class is overly broad for CLIP and thus challenging to classify,
it is represented by a set of stuff categories such as “sky, river,
sea, . . . ”, which do not overlap with other target classes. And
this pipeline is consistent with prior studies.

B. Main Results
To ensure a fair comparison, we strictly follow the evaluation protocol specified in the Section IV-A to reproduce
all methods. For CLIP-DINOiser [12], we retrain the model
using the OpenAI’s pretrained weights. Table I presents the
comparison of all methods, where our SC-CLIP achieves an
average mIoU of 43.9% on CLIP ViT-B/16, setting a new
state-of-the-art results across eight benchmarks with a notable
9.5% improvement over previous methods. Furthermore, our
method demonstrates robustness across different backbones,
achieving optimal performance on CLIP ViT-L/14, improving
the results by 3.5% average mIoU.
The vanilla CLIP achieves only a 14.4% and 6.6% mIoU on
ViT-B/16 and ViT-L/14 respectively, demonstrating its limitations in capturing fine-grained spatial details. Our training-free

TABLE II
E XPERIMENTS ON THE MESS B ENCHMARK [78]

method boosts its performance by threefold on the ViT-B/16
and by 6.8 times on the ViT-L/14.
In contrast to ProxyCLIP [11], which relies on the DINOB/16 [13] backbone to provide attention weights, our method
does not depend on any auxiliary backbone yet achieves
superior results. This highlights the inherent properties of
CLIP can be effectively leveraged to calibrate itself, thereby
enhancing its feature representation.
The MESS benchmark [78] includes a wide range of
domain-specific datasets spanning fields such as earth monitoring, medical sciences, engineering, agriculture, and biology. It
serves as a robust evaluation tool for assessing the generalization capability. We conduct experiments on datasets from each
domain within the MESS benchmark, and as shown in Table II,
our SC-CLIP consistently outperforms CLIP-DINOiser [12]
and ProxyCLIP [11], showing superior generalization ability.
C. Ablation Study
In this section, we conduct comprehensive ablation experiments to validate the effectiveness of our method. All ablations
are performed on the CLIP ViT-B/16 backbone. We use SCLIP

BAI et al.: SELF-CALIBRATED CLIP FOR TRAINING-FREE OPEN-VOCABULARY SEGMENTATION

TABLE III
A BLATION E XPERIMENTS ON THE P ROPOSED S TRATEGIES

[4] as our baseline, which modifies the attention mechanism
in the final layer by replacing the original QK> attention with
QQ> + KK> attention, to enhance correlations. Additionally,
we remove the residual connections and feed-forward network
(FFN) following [7], [11].
1) Analysis of Various Strategies: In Table III, we incrementally incorporate each strategy to highlight its contribution.
First, by resolving the anomaly tokens (denoted by AnomRes),
our method achieves a 1.2% mIoU improvement, effectively
addressing the issues brought by anomaly tokens, as discussed
in Section III-B. Next, we apply the self-adjusting strategy proposed in Section III-C, which leverages the spatial consistency
within CLIP’s mid-level features to enhance attention correlation (denoted by AttnEnh), leading to a 0.9% improvement.
By adaptively aggregating deep features (FeatAgg), we obtain
a further 0.8% gain in mIoU. Finally, the two-pass strategy
(TwoPass) in Section III-D provides a 1.6% boost in mIoU.
Collectively, these strategies contribute to a substantial 12.3%
improvement over the baseline. Besides, we conduct a detailed
ROC curve analysis as shown in Figure 4 (bottom right). SCCLIP achieves an AUC of 0.81, surpassing the baseline by
17.4% and significantly enhancing the semantic coherence.
2) Resolving the Anomaly Tokens: To thoroughly investigate the configurations for resolving anomaly tokens, we
conduct a series of ablation studies. These studies examine the
impact of varying the number of anomaly tokens, the choice
of different anomaly detection methods, various interpolation
strategies, and different neighborhood sizes. The results are
summarized in Table IV, where the first row reports the
baseline results for all four groups of experiments.
(a) The number of anomaly tokens: As we use the LOF
algorithm to identify the anomaly tokens, we need to adjust
the contamination hyperparameter to control the number of
detected anomalies. We explore the optimal number of tokens
to resolve, as shown in Table IV (a). As the number increases
from 1 to 10, performance gradually improves. However,
further increasing this number to 15 yields no additional gains.
Therefore, we adopt the removal of 10 tokens (about 5% of
the ViT-B/16 token sequence) in our method.
(b) Various anomaly detection methods: We investigate
alternative anomaly detection methods to the adopted LOF
algorithm, including Isolation Forest, DBSCAN, and OneClass SVM. As shown in Table IV (b), all methods lead to
improvements, with LOF algorithm achieving the best results.
(c) Various interpolation methods: We explore various
interpolation methods in Table IV (c). After identifying the
anomaly tokens, we first try replacing them with the CLS
token or the mean of the normal tokens, but these strategies do not lead to performance gains. We then conduct

8277

TABLE IV
A BLATION S TUDY ON R ESOLVING THE A NOMALY T OKENS

TABLE V
R EMOVING A NOMALIES F ROM D IFFERENT L AYERS

experiments based on the local neighborhood assumption,
employing bilinear, nearest-neighbor, median (using the
median value of neighboring pixels), weighted (assigning
weights based on distance), and mean interpolation. The
results show that mean interpolation achieves the best performance, and thus we adopt it as our final choice.
(d) Different neighborhood sizes: As shown in Table IV (d),
we compare different neighborhood sizes for mean interpolation. The results show that the 3 × 3 neighborhood performs
better than larger ones. We hypothesize that larger neighborhoods inevitably incorporate more irrelevant regions during
the interpolation process, which tends to over-smooth features
and blur semantics across object boundaries.
In addition, we also test the removal of anomaly tokens
starting from different layers on the VOC21 dataset in Table V.
The results show that the modification is only effective when
removing from the last layer; otherwise, performance drops
significantly. This is because the training-free setting relies on
the feature modeling of earlier CLIP layers, and improvements
stem from modifying only the final layer. To further support
this point, we apply self-self attention [3], [4], [7] (widely
validated) to different layers. Results show that it is effective
only when applied to the last layer; otherwise, it also drastically degrades performance due to feature space disruption.
This suggests that the observed degradation is not caused by
LOF’s inability to identify anomaly tokens in other layers.

8278

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

TABLE VI

TABLE VII

A BLATION S TUDY OF THE ATTENTION E NHANCEMENT

A BLATION S TUDY OF THE F EATURE AGGREGATION

TABLE VIII
A BLATION S TUDY OF THE β FOR F EATURE AGGREGATION

Fig. 6. Visualization of shallower and deeper mid-layer patch similarity. F
denotes the selected token.

3) Self-adjusting Strategy: To comprehensively evaluate the
effectiveness of the self-adjusting strategy, we conduct ablation
studies on both attention enhancement and feature aggregation.
Table VI presents the ablation study on attention enhancement, which can be regarded as a more detailed analysis
of the “+AttnEnh” entry in Table III. All experiments are
conducted with anomaly tokens resolved (i.e., under the
“+AnomRes” setting in Table III). We first evaluate different
1
4
forms of correlative attention (O
to O
in Table VI), and
find that these variants achieve comparable performance. We
5
then examine using only Simimid (O)
and its integration with
correlative attention. The results show that this integration (Eq.
(5)) consistently outperforms either component alone, demonstrating the effectiveness of attention enhancement. Among
4
5
them, enhancing KK> (O+
O)
achieves the best overall
performance.
And in Table VII, we conduct a comprehensive analysis of
the feature aggregation. We find that adjusting both X penul and
Xlast is essential, serving as the pre- and post-adjustment for
the last layer. Experiments indicate that using deeper midlayers (e.g, 9) for pre-adjustment and shallower mid-layer
(e.g, 4) for post-adjustment yields the optimal results, corresponding to (9, 4) in the table, achieving an average 39.8%
mIoU, a 6% improvement over the baseline. As illustrated
in Figure 6, the shallower mid-layers exhibit more localized
activations, while deeper mid-layers provide broader activations. Based on this, we hypothesize that deeper layers are
well-suited for pre-adjustment due to their broader activations,
which help aggregate more regions and enable the attention
mechanism capture more coherent semantics. On the other
side, shallower layers are ideal for post-adjustment, as their

localized activations can preserve intricate spatial information.
And our method is robust to different combinations, with
(8, 3) also achieving an mIoU of 39.7. Furthermore, we
compare our approach with DINO, following prior studies
[12], [77], [79]. When applied to Xlast , DINO shows superior
performance, showing its fine-grained details; however, our
approach achieves comparable results when both pre- and
post-adjustments are applied, fully unlocking CLIP’s potential
without relying on additional backbones.
In addition, as mentioned in Section IV-A, we apply thresholding to Simimid , setting values below the threshold β to zero.
To analyze the effect of the β parameter, we experiment with
different β values using 4th-layer features to adjust Xlast (row 8
of Table VII). The results in Table VIII indicate that β should
not be too large, as this would cause Simi to activate only
for itself. Conversely, if β is too small, all tokens would be
activated in Simi, leading to feature homogenization. Overall,
β should be set to a moderate value like 0.4.
4) Two-pass Strategy: We conduct ablation study of
the multi-level fusion strategy in Table IX with following
penul 2
penul
1 baseline: L(X
approaches.
O
) OP
direct sum:
)+
 L(X
P
i 3
penul
i
4
X
O
one
pass:
L
X
+
X
O
two
pass:
i∈M
i∈M

P
i
L(X penul ) + L
i∈M X . Here, L is the last layer, and M
is the multi-level features. The results align with our analysis
in Section III-D, validating two key principles: (1) using the
2 and O
4 reveals
last layer for alignment: comparison between O
4 aligns the multi-level features using the parameter space
that O
of the last layer, which improves feature compatibility and
leads to a significant performance boost. (2) maintaining the
3
4
integrity of the last feature: comparison between O
and O
3 weakens the original last feature, resulting in
indicates that O
a performance drop. Additionally, we compare our approach
with the dual-path strategy proposed in CLIPSurgery [6],

BAI et al.: SELF-CALIBRATED CLIP FOR TRAINING-FREE OPEN-VOCABULARY SEGMENTATION

8279

TABLE IX
A BLATION S TUDY OF THE T WO -PASS S TRATEGY

TABLE X
S ELECTED L AYERS OF THE T WO -PASS S TRATEGY

TABLE XI
E FFICIENCY C OMPARISON OF T RAINING -F REE M ETHODS

Fig. 7. Detailed analysis of other ViT-based backbones.
TABLE XII
G ENERALIZATION TO OTHER V I T-BASED BACKBONES

where each layer of the image encoder in the new path is
modified to self-self attention, and the outputs of the new
path are directly aggregated.
This can be formulated as: dual
P
path: L(X penul ) + i∈M Xinew , where Xinew is the feature from
the new path. This strategy can be regarded as an enhanced
2
version of O.
However, in comparison, our method achieves
superior results while avoiding the additional computational
overhead introduced by the new path.
To analyze the impact of selected layers in multi-level
fusion, we report the average mIoU across eight datasets in
Table X, indicating that our method is robust to the choice of
selected layers, as different combinations yield similar results.
The notation 4–10 in the table denotes fusing all features from
layer 4 to 10, which achieves the best 43.9% mIoU, surpassing
the baseline (w/o) by 1.5% mIoU.
5) Efficiency Comparison: As shown in Table XI, we
compare the efficiency of different methods on the COCOObject dataset [2] using an NVIDIA V100 GPU. Compared
to the previous state-of-the-art method, ProxyCLIP [11], our
SC-CLIP eliminates the need for additional backbones, leading
to a significant improvement in efficiency. Specifically, the
FPS increases from 3.9 to 6.5, and the FLOPs are reduced
from 34.4G to 17.5G. We also provide a detailed breakdown
of the computational cost for each component. By default,
the LOF algorithm is implemented with NumPy, which is
computationally inefficient. As discussed in Section III-B, we
re-implement LOF using PyTorch, resulting in a substantial
inference speed-up. In particular, the FPS improves from 6.3
to 7.6, while maintaining functional consistency.

D. Discussion
In this section, we provide a broader discussion on
the applicability and generalization of our method. We
begin by evaluating its applicability to different ViT-based
vision–language models, assessing the consistency and robustness of our approach across models that vary in training data
and strategies. We then turn to ResNet-based CLIP models
to examine whether the anomaly token issue also arises in
non-ViT architectures. Finally, we explore the potential of
our approach in open-vocabulary 3D perception tasks, demonstrating its applicability to more complex scenarios. Together,
these analyses provide a more comprehensive validation for
our method.
1) Different ViT-based Vision–Language Models: To further
examine the generalization of our method, we evaluate it on
several ViT-based vision–language models, which all adopt
image–text contrastive pretraining but differ in certain aspects.
Specifically, MetaCLIP [22] and OpenCLIP (pretrained on
LAION) [80] vary in the pretraining data, while BLIP [20]
and SigLIP [21] introduce alternative training paradigms or
architectures. For each model, we adopt the same configurations as those used for CLIP in Section IV-A. As shown
in Table XII, our method consistently improves performance
across all cases, showing its generalization to diverse models.

8280

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

Fig. 8. Qualitative results of improvement analysis, where each strategy is progressively added to demonstrate its effect.
TABLE XIII
R ESOLVING A NOMALIES IN R ES N ET-BASED CLIP

Fig. 9. PCA analysis of the ResNet-based CLIP.
TABLE XIV

To further explain why our method generalizes well across
different models, we provide analyses in Figure 7 (better
viewed when zoomed in). In Figure 7 (a), using the image
from Figure 3 for illustration, the attention maps of four
different selected patch tokens (marked by F) show that different tokens all exhibit excessive focus on the same regions,
corresponding to anomaly tokens highlighted by the orange
dashed circles. In Figure 7 (b), PCA analysis of patch-level
features reveals these anomaly tokens as clear outliers, further
confirming their presence across all models. In Figure 7 (c),
ROC curves comparing mid-layer and last-layer features show
that mid-layer features consistently achieve higher AUC values
across all models, indicating stronger discriminative ability.
Building on this observation, our method explicitly addresses
anomaly tokens and leverages mid-layer spatial consistency,
leading to consistent relative AUC improvements, with gains
of 19.1% for MetaCLIP, 18.8% for OpenCLIP, 21.2% for
BLIP, and 12.5% for SigLIP. Overall, these results explain
the root of our method’s generalization ability: by tackling
the consistently observed anomaly token issue and enhancing
local correspondence, it achieves robust improvements across
diverse ViT-based vision–language models.
2) ResNet-based CLIP Models: We further examine
ResNet-based CLIP variants (ResNet-50, ResNet-101, and
ResNet-50×4) to investigate whether the anomaly token issue
also exists beyond ViT architectures. As shown in the PCA
visualizations in Figure 9, the feature distributions of ResNet
variants are tightly clustered within a narrow range (e.g.,
[−3, 3]). In contrast, ViT-based models (Figure 7 (b)) exhibit
clear outliers, with x-axis values reaching as high as 100–1000.
Quantitative results in Table XIII further confirm this observation: resolving anomaly tokens (denoted as “+AnomRes”)
leads to negligible changes in average performance. These
findings indicate that ResNet-based CLIP does not suffer from
the anomaly token issue. We hypothesize that this is due to
the strong local inductive bias of convolutional architectures,
which prevents the extreme outliers that often arise in ViTbased models.

P ERFORMANCE C OMPARISON OF D IFFERENT M ETHODS ON O PEN VOCABULARY 3D S EMANTIC S EGMENTATION

3) Open-vocabulary 3D perception tasks: Open-vocabulary
3D perception has recently gained increasing attention, aiming to extend vision–language models to tasks such as 3D
instance segmentation and object detection, with representative approaches including OpenMask3D [81], OpenIns3D
[82], Coda [83], and INHA [84]. To further validate the
applicability of SC-CLIP in 3D scenarios, we investigate
the open-vocabulary 3D semantic segmentation task using
OpenScene [85]. In this setting, the model is required to
perform per-point classification, which strongly relies on dense
feature representations and naturally aligns with the design of
SC-CLIP. Specifically, we employ the image feature fusion
method (corresponding to the “2D fusion” setting in their
paper), which enables a direct evaluation of the visual encoder
without additional training. Experiments on the ScanNet [86]
validation set and the Matterport3D [87] test set, as reported in
Table XIV, show that SC-CLIP achieves the best performance
among all training-free methods. The remaining performance
gap compared with training-based methods such as LSeg
[46] and OpenSeg [37] can be largely attributed to their
additional supervised training of both the image encoder and
decoder. Overall, these results demonstrate that SC-CLIP not
only advances open-vocabulary 2D segmentation, but also

BAI et al.: SELF-CALIBRATED CLIP FOR TRAINING-FREE OPEN-VOCABULARY SEGMENTATION

8281

Fig. 10. Qualitative Results of Open-Vocabulary Segmentation. We compare our method with CLIP [1], MaskCLIP [3], SCLIP [4] and ClearCLIP [7], all
without post-processing. Our SC-CLIP produces much clearer and more accurate results.

generalizes effectively to 3D scenarios, thereby further validating its versatility and applicability.
E. Visualization
In Figure 8, we present a qualitative improvement analysis
which clearly illustrates the progressive improvements introduced by each strategy and highlights the overall contributions
of our method. Compared to the baseline result, resolving the
anomaly token effectively removes the noise in the lower part
of the image (d vs. c). Further applying the self-adjusting
strategy enhances local correspondence and leads to better
overall coherence, as can be observed in the upper region of
the result (e vs. d). Finally, incorporating the two-pass strategy
provides richer details, such as a more complete structure of
the bicycle frame and the seat (f vs. e).
Beyond the improvement analysis, we further provide a
qualitative comparison across different representative methods in Figure 10, including CLIP [1], MaskCLIP [3],
SCLIP [4], ClearCLIP [7], and our SC-CLIP. The results

demonstrate that SC-CLIP (last column) consistently produces
more precise and higher-quality outcomes compared to the
other methods, showing robustness across different visual
contexts. In contrast, CLIP’s results are considerably noisy
and suffer from a homogeneity effect (e.g, in the second row,
the entire image is labeled as “dog”). Previous approaches
such as SCLIP and ClearCLIP focused only on modifying the
attention computation, without explicitly resolving anomaly
tokens or enhancing local correspondence, which makes their
results still suboptimal. By directly addressing these issues,
our method achieves more semantically consistent outputs with
sharper boundaries and finer structural details.
F. Failure Case Analysis
We further analyze the failure cases of our method, as
illustrated in Figure 11. Our motivation is to enhance CLIP’s
local correspondence in a training-free manner; however, the
approach is inherently bounded by CLIP’s representational
capacity. Specifically, the limitations manifest in two aspects:

8282

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

[2]

Fig. 11. Failure case analysis in textual and visual aspects.

(1) Textual aspect. As shown in Figure 11 (a), when using
generic input prompts such as “Tree” or “Person”, the segmentation results are suboptimal, producing vague or incomplete
masks. In contrast, more specific and descriptive inputs like
“Tree With Snow” or “Skiing Person” lead to significantly
improved results. This phenomenon suggests that for CLIPbased models, using more specific and descriptive inputs leads
to better results; (2) Visual aspect. The limited resolution and
training paradigm of the CLIP image encoder make it difficult
to accurately represent small objects or boundary regions in
complex scenes. As shown in Figure 11 (b), such limitations
result in coarse boundaries (e.g., the contour of the car on the
left) and recognition errors (e.g., failing to detect the distant
traffic sign). These failure cases provide a more comprehensive
perspective on the applicability and limitations of our method.
V. C ONCLUSION
In this paper, we present Self-Calibrated CLIP (SC-CLIP),
a training-free approach designed to enhance the openvocabulary segmentation performance of CLIP. We observe
that anomaly tokens induce uniform attention patterns and
feature homogenization, which compromise spatial representation. To address this, we mitigate their adverse effects from
two complementary perspectives. First, we explicitly identify
anomaly tokens and replace them based on local context. Second, we reduce their influence on normal tokens by enhancing
feature discriminability and attention correlation, leveraging
the intrinsic semantic consistency embedded in CLIP’s midlevel features. Together with a two-pass strategy, SC-CLIP
achieves state-of-the-art performance without requiring additional data, parameters, or backbones. These results demonstrate that the inherent capabilities of CLIP can be effectively
leveraged to calibrate itself and produce semantically coherent
representations.
The motivation of this work is to enhance the dense feature
representation of CLIP while preserving its original capabilities in a training-free manner. For future work, we believe
that to fundamentally improve the model, modifications to the
architecture and training strategy are necessary. Naturally, this
would necessitate retraining the model from scratch, along
with substantial computational resources and large-scale data.
R EFERENCES
[1]

A. Radford et al., “Learning transferable visual models from natural language supervision,” in Proc. Int. Conf. Mach. Learn., 2021,
pp. 8748–8763.

H. Caesar, J. Uijlings, and V. Ferrari, “COCO-stuff: Thing and stuff
classes in context,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.,
Jun. 2024, pp. 1209–1218.
[3] C. Zhou, C. C. Loy, and B. Dai, “Extract free dense labels from CLIP,”
in Proc. Eur. Conf. Comput. Vis., 2021, pp. 696–712.
[4] F. Wang, J. Mei, and A. Yuille, “SCLIP: Rethinking self-attention for
dense vision-language inference,” in Proc. Eur. Conf. Comput. Vis.,
2023, pp. 315–332.
[5] W. Bousselham, F. Petersen, V. Ferrari, and H. Kuehne, “Grounding
everything: Emerging localization properties in vision-language
transformers,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2024, pp. 3828–3837.
[6] Y. Li, H. Wang, Y. Duan, J. Zhang, and X. Li, “A closer look at
the explainability of contrastive language-image pre-training,” 2023,
arXiv:2304.05653.
[7] M. Lan, Z. Chen, Y. Ke, X. Wang, L. Feng, and W. Zhang,
“ClearCLIP: Decomposing CLIP representations for dense visionlanguage inference,” in Proc. Eur. Conf. Comput. Vis., 2024,
pp. 143–160.
[8] S. Hajimiri, I. B. Ayed, and J. Dolz, “Pay attention to your neighbours:
Training-free open-vocabulary semantic segmentation,” in Proc. IEEE
Winter Conf. Appl. Comput. Vis., Feb. 2025, pp. 5061–5071.
[9] D. Kang and M. Cho, “In defense of lazy visual grounding for openvocabulary semantic segmentation,” in Proc. Eur. Conf. Comput. Vis.,
2024, pp. 143–164.
[10] T. Shao, Z. Tian, H. Zhao, and J. Su, “Explore the potential of CLIP
for training-free open vocabulary semantic segmentation,” in Proc. Eur.
Conf. Comput. Vis., 2024, pp. 139–156.
[11] M. Lan, C. Chen, Y. Ke, X. Wang, L. Feng, and W. Zhang, “Proxyclip:
Proxy attention improves clip for open-vocabulary segmentation,” in
Proc. Eur. Conf. Comput. Vis., 2024, pp. 70–88.
[12] M. Wysoczańska, O. Siméoni, M. Ramamonjisoa, A. Bursuc,
T. P. Trzcinski, and P. Pérez, “CLIP-DINOiser: Teaching CLIP a few
DINO tricks for open-vocabulary semantic segmentation,” in Proc. Eur.
Conf. Comput. Vis., 2023, pp. 320–337.
[13] M. Caron et al., “Emerging properties in self-supervised vision
transformers,” in Proc. IEEE Int. Conf. Comput. Vis., Oct. 2021,
pp. 9630–9640.
[14] A. Kirillov et al., “Segment anything,” in Proc. IEEE/CVF Int. Conf.
Comput. Vis., Oct. 2023, pp. 4015–4026.
[15] R. Rombach, A. Blattmann, D. Lorenz, P. Esser, and B. Ommer,
“High-resolution image synthesis with latent diffusion models,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022,
pp. 10674–10685.
[16] S. Wold, K. H. Esbensen, and P. Geladi, “Principal component analysis,”
Wiley Interdiscipl. Reviews, Comput. Statist., vol. 2, no. 4, pp. 433–459,
2010.
[17] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “LOF: Identifying density-based local outliers,” ACM SIGMOD Rec., vol. 29, no. 2,
pp. 93–104, Jun. 2000.
[18] C. Jia et al., “Scaling up visual and vision-language representation
learning with noisy text supervision,” in Proc. Int. Conf. Mach. Learn.,
2021, pp. 4904–4916.
[19] J. Yu, Z. Wang, V. K. Vasudevan, L. Yeung, M. Seyedhosseini,
and Y. Wu, “CoCa: Contrastive captioners are image-text foundation
models,” Trans. Mach. Learn. Res., vol. 2022, 2022. [Online]. Available:
https://openreview.net/forum?id=Ee277P3AYC
[20] J. Li, D. Li, C. Xiong, and S. C. H. Hoi, “BLIP: Bootstrapping languageimage pre-training for unified vision-language understanding and
generation,” in Proc. Int. Conf. Mach. Learn., 2022, pp. 12888–12900.
[21] X. Zhai, B. Mustafa, A. Kolesnikov, and L. Beyer, “Sigmoid loss for
language image pre-training,” in Proc. IEEE/CVF Int. Conf. Comput.
Vis. (ICCV), Oct. 2023, pp. 11975–11986.
[22] X. Hu et al., “Demystifying CLIP data,” in Proc. Int. Conf. Learn.
Represent., 2023.
[23] A. U. Khan, H. Kuehne, C. Gan, N. D. V. Lobo, and M. Shah, “Weakly
supervised grounding for VQA in vision-language transformers,” in
Proc. Eur. Conf. Comput. Vis., 2022, pp. 652–670.
[24] A. Mishra, K. Alahari, and C. V. Jawahar, “Image retrieval using textual
cues,” in Proc. IEEE Int. Conf. Comput. Vis., Dec. 2013, pp. 3040–3047.
[25] S. Antol et al., “VQA: Visual question answering,” in Proc. IEEE Int.
Conf. Comput. Vis., Dec. 2015, pp. 2425–2433.
[26] J. Wu et al., “Towards open vocabulary learning: A survey,” IEEE Trans.
Pattern Anal. Mach. Intell., vol. 46, no. 7, pp. 5092–5113, Jul. 2024.
[27] C. Zhang et al., “OccNeRF: Advancing 3D occupancy prediction
in LiDAR-free environments,” IEEE Trans. Image Process., vol. 34,
pp. 3096–3107, 2025.

BAI et al.: SELF-CALIBRATED CLIP FOR TRAINING-FREE OPEN-VOCABULARY SEGMENTATION

[28] Y. Xu, M. Zhang, X. Yang, and C. Xu, “Exploring multi-modal contextual knowledge for open-vocabulary object detection,” IEEE Trans.
Image Process., vol. 33, pp. 6253–6267, 2024.
[29] J. Wu, X. Li, X. Li, H. Ding, Y. Tong, and D. Tao, “Towards robust
referring image segmentation,” IEEE Trans. Image Process., vol. 33,
pp. 1782–1794, 2022.
[30] Y. He, W. Chen, S. Wang, T. Liu, and M. Wang, “Recalling unknowns
without losing precision: An effective solution to large model-guided
open world object detection,” IEEE Trans. Image Process., vol. 34,
pp. 729–742, 2025.
[31] H. Yuan, X. Li, C. Zhou, Y. Li, K. Chen, and C. C. Loy, “Openvocabulary SAM: Segment and recognize twenty-thousand classes
interactively,” in Proc. Eur. Conf. Comput. Vis., 2024, pp. 419–437.
[32] Y. Liu, C. Zhang, Y. Wang, J. Wang, Y. Yang, and Y. Tang, “Universal
segmentation at arbitrary granularity with language instruction,” in Proc.
IEEE Conf. Comput. Vis. Pattern Recognit., Jun. 2024, pp. 3459–3469.
[33] Y. Sun, Q. Chen, J. Wang, J. Wang, and Z. Li, “Exploring effective
factors for improving visual in-context learning,” IEEE Trans. Image
Process., vol. 34, pp. 2147–2160, 2025.
[34] X. Li et al., “Transformer-based visual segmentation: A survey,” IEEE
Trans. Pattern Anal. Mach. Intell., vol. 46, no. 12, pp. 10138–10163,
Dec. 2024.
[35] W. Zhao, Y. Rao, Y. Tang, J. Zhou, and J. Lu, “VideoABC: A realworld video dataset for abductive visual reasoning,” IEEE Trans. Image
Process., vol. 31, pp. 6048–6061, 2022.
[36] J. Wang et al., “Diffusion model is secretly a training-free open
vocabulary semantic segmenter,” IEEE Trans. Image Process., vol. 34,
pp. 1895–1907, 2025.
[37] G. Ghiasi, X. Gu, Y. Cui, and T.-Y. Lin, “Scaling open-vocabulary image
segmentation with image-level labels,” in Proc. Eur. Conf. Comput. Vis.,
2021, pp. 540–557.
[38] M. Xu et al., “A simple baseline for open-vocabulary semantic segmentation with pre-trained vision-language model,” in Proc. Eur. Conf.
Comput. Vis., 2021, pp. 736–753.
[39] J. Ding, N. Xue, G.-S. Xia, and D. Dai, “Decoupling zero-shot semantic
segmentation,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., Jun.
2022, pp. 11573–11582.
[40] F. Liang et al., “Open-vocabulary semantic segmentation with maskadapted CLIP,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2023, pp. 7061–7070.
[41] Y. Liu, S. Bai, G. Li, Y. Wang, and Y. Tang, “Open-vocabulary segmentation with semantic-assisted calibration,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2024, pp. 3491–3500.
[42] M. Xu, Z. Zhang, F. Wei, H. Hu, and X. Bai, “Side adapter network
for open-vocabulary semantic segmentation,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2023, pp. 2945–2954.
[43] K. Han et al., “Global knowledge calibration for fast open-vocabulary
segmentation,” in Proc. IEEE Int. Conf. Comput. Vis., Oct. 2023,
pp. 797–807.
[44] Q. Yu, J. He, X. Deng, X. Shen, and L.-C. Chen, “Convolutions die hard:
Open-vocabulary segmentation with single frozen convolutional CLIP,”
in Proc. Adv. Neural Inform. Process. Syst., 2023, pp. 32215–32234.
[45] B. Xie, J. Cao, J. Xie, F. S. Khan, and Y. Pang, “SED: A simple encoder–decoder for open-vocabulary semantic segmentation,”
in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., Jun. 2024,
pp. 3426–3436.
[46] B. Li, K. Q. Weinberger, S. Belongie, V. Koltun, and R. Ranftl,
“Language-driven semantic segmentation,” in Proc. Int. Conf. Learn.
Represent., 2022.
[47] S. Cho, H. Shin, S. Hong, A. Arnab, P. H. Seo, and S. Kim, “CAT-SEG:
Cost aggregation for open-vocabulary semantic segmentation,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2024,
pp. 4113–4123.
[48] X. Xu, T. Xiong, Z. Ding, and Z. Tu, “MasQCLIP for open-vocabulary
universal image segmentation,” in Proc. IEEE/CVF Int. Conf. Comput.
Vis. (ICCV), Oct. 2023, pp. 887–898.
[49] J. Oin et al., “FreeSeg: Unified, universal and open-vocabulary image
segmentation,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., Jun.
2023, pp. 19446–19455.
[50] H. Zhou et al., “Rethinking evaluation metrics of open-vocabulary
segmentation,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 47, no. 8,
pp. 6780–6796, Aug. 2025.
[51] X. Li et al., “OMG-seg: Is one model good enough for all
segmentation?,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2024, pp. 27948–27959.

8283

[52] J. Mukhoti et al., “Open vocabulary semantic segmentation with patch
aligned contrastive learning,” in Proc. IEEE Conf. Comput. Vis. Pattern
Recognit., Jun. 2023, pp. 19413–19423.
[53] P. Ren et al., “ViewCo: Discovering text-supervised segmentation masks
via multi-view semantic consistency,” in Proc. Int. Conf. Learn. Represent., 2023.
[54] J. Cha, J. Mun, and B. Roh, “Learning to generate text-grounded mask
for open-world semantic segmentation from only image-text pairs,” in
Proc. IEEE Conf. Comput. Vis. Pattern Recognit., Jun. 2022.
[55] J. Xu et al., “GroupViT: Semantic segmentation emerges from text
supervision,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., Jun.
2022, pp. 18113–18123.
[56] H. Luo, J. L. Bao, Y. Wu, X. He, and T. Li, “SegCLIP: Patch aggregation
with learnable centers for open-vocabulary semantic segmentation,” in
Proc. Int. Conf. Mach. Learn., 2022, pp. 23033–23044.
[57] J. Xu et al., “Learning open-vocabulary semantic segmentation models
from natural language supervision,” in Proc. IEEE Conf. Comput. Vis.
Pattern Recognit., Jun. 2023.
[58] W. He, S. Jamonnak, L. Gou, and L. Ren, “CLIP-s4: Language-guided
self-supervised semantic segmentation,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2023, pp. 11207–11216.
[59] T. Chen, Y. Yao, X. Huang, Z. Li, L. Nie, and J. Tang, “Spatial structure
constraints for weakly supervised semantic segmentation,” IEEE Trans.
Image Process., vol. 33, pp. 1136–1148, 2024.
[60] L. Barsellotti, R. Amoroso, M. Cornia, L. Baraldi, and R. Cucchiara,
“Training-free open-vocabulary segmentation with offline diffusionaugmented prototype generation,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit. (CVPR), Jun. 2024, pp. 3689–3698.
[61] M. Wysoczańska, M. Ramamonjisoa, T. Trzciński, and O. Siméoni,
“CLIP-DIY: CLIP dense inference yields open-vocabulary semantic
segmentation for-free,” in Proc. IEEE/CVF Winter Conf. Appl. Comput.
Vis. (WACV), Jan. 2024, pp. 1392–1402.
[62] Y. Lin et al., “TagCLIP: A local-to-global framework to enhance openvocabulary multi-label classification of CLIP without training,” in Proc.
AAAI, vol. 38, 2024, pp. 3513–3521.
[63] S. Sun, R. Li, P. Torr, X. Gu, and S. Li, “CLIP as RNN: Segment countless visual concepts without training endeavor,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2024,
pp. 13171–13182.
[64] A. Vaswani et al., “Attention is all you need,” in Proc. Adv. Neural
Inform. Process. Syst., vol. 30, 2025, pp. 5998–6008.
[65] A. Dosovitskiy et al., “An image is worth 16×16 words: Transformers
for image recognition at scale,” in Proc. Int. Conf. Learn. Represent.,
2020.
[66] T. Darcet, M. Oquab, J. Mairal, and P. Bojanowski, “Vision transformers
need registers,” in Proc. Int. Conf. Learn. Represent., 2023.
[67] G. Xiao, Y. Tian, B. Chen, S. Han, and M. Lewis, “Efficient streaming
language models with attention sinks,” in Proc. Int. Conf. Learn.
Represent., 2023.
[68] B. Zhou, H. Zhao, X. Puig, S. Fidler, A. Barriuso, and A. Torralba,
“Scene parsing through ADE20K dataset,” in Proc. IEEE Conf. Comput.
Vis. Pattern Recognit. (CVPR), Jul. 2017, pp. 5122–5130.
[69] T.-Y. Lin, P. Dollár, R. Girshick, K. He, B. Hariharan, and S. Belongie,
“Feature pyramid networks for object detection,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jul. 2017, pp. 936–944.
[70] Y. Li, Z. Li, Q. Zeng, Q. Hou, and M. Cheng, “CascadeCLIP: Cascaded vision-language embeddings alignment for zero-shot
semantic segmentation,” in Proc. Int. Conf. Mach. Learn., 2024,
pp. 28243–28258.
[71] E. Xie, W. Wang, Z. Yu, A. Anandkumar, J. M. Alvarez, and P. Luo,
“SegFormer: Simple and efficient design for semantic segmentation
with transformers,” in Proc. Adv. Neural Inform. Process. Syst., 2021,
pp. 12077–12090.
[72] M.-H. Guo, C.-Z. Lu, Q. Hou, Z. Liu, M. Cheng, and S. Hu, “SegNeXt:
Rethinking convolutional attention design for semantic segmentation,”
in Proc. Adv. Neural Inform. Process. Syst., 2022, pp. 1140–1156.
[73] M. Everingham and J. Winn, “The Pascal visual object classes challenge
2012 (voc2012) development kit,” Pattern Anal. Stat. Model. Comput.
Learn., Tech. Rep, vol. 2007, nos. 1–45, p. 5, 2012.
[74] R. Mottaghi et al., “The role of context for object detection and semantic
segmentation in the wild,” in Proc. IEEE Conf. Comput. Vis. Pattern
Recognit., Jun. 2014, pp. 891–898.
[75] M. Cordts et al., “The cityscapes dataset for semantic urban scene
understanding,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2016, pp. 3213–3223.

8284

IEEE TRANSACTIONS ON IMAGE PROCESSING, VOL. 34, 2025

[76] G. Shin, W. Xie, and S. Albanie, “ReCo: Retrieve and co-segment for
zero-shot transfer,” in Proc. Adv. Neural Inform. Process. Syst., 2022,
pp. 33754–33767.
[77] Y. Wang, X. Shen, S. X. Hu, Y. Yuan, J. L. Crowley, and D. Vaufreydaz,
“Self-supervised transformers for unsupervised object discovery using
normalized cut,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.,
Jun. 2022, pp. 14543–14553.
[78] B. Blumenstiel, J. Jakubik, H. Kühne, and M. Vössing, “What a MESS:
Multi-domain evaluation of zero-shot semantic segmentation,” in Proc.
Adv. Neural Inform. Process. Syst., 2023, pp. 73299–73311.
[79] O. Siméoni et al., “Localizing objects with self-supervised transformers
and no labels,” in Proc. Brit. Mach. Vis. Conf., 2021, p. 310.
[80] M. Cherti et al., “Reproducible scaling laws for contrastive languageimage learning,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.,
Jun. 2022, pp. 2818–2829.
[81] A. Takmaz, E. Fedele, R. W. Sumner, M. Pollefeys, F. Tombari,
and F. Engelmann, “OpenMask3D: Open-vocabulary 3D instance
segmentation,” in Proc. Adv. Neural Inform. Process. Syst., 2023,
pp. 68367–68390.
[82] Z. Huang, X. Wu, X. Chen, H. Zhao, L. Zhu, and J. Lasenby,
“OpenIns3D: Snap and lookup for 3D open-vocabulary instance
segmentation,” in Proc. Eur. Conf. Comput. Vis., 2023, pp. 169–185.
[83] Y. Cao, Y. Zeng, H. Xu, and D. Xu, “CoDA: Collaborative novel
box discovery and cross-modal alignment for open-vocabulary 3D
object detection,” in Proc. Adv. Neural Inform. Process. Syst., 2023,
pp. 71862–71873.
[84] P. Jiao, N. Zhao, J. Chen, and Y.-G. Jiang, “Unlocking textual and
visual wisdom: Open-vocabulary 3D object detection enhanced by
comprehensive guidance from text and image,” in Proc. Eur. Conf.
Comput. Vis., 2024, pp. 376–392.
[85] S. Peng, K. Genova, C. Jiang, A. Tagliasacchi, M. Pollefeys, and
T. Funkhouser, “OpenScene: 3D scene understanding with open
vocabularies,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2023, pp. 815–824.
[86] A. Dai, A. X. Chang, M. Savva, M. Halber, T. Funkhouser, and
M. Nießner, “ScanNet: Richly-annotated 3D reconstructions of indoor
scenes,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR),
Jul. 2017, pp. 5828–5839.
[87] A. L. S. Chang et al., “Matterport3D: Learning from RGB-D data in
indoor environments,” in Proc. 3DV, 2017, pp. 667–676.

Sule Bai received the B.Eng. degree from Beijing University of Posts and Telecommunications,
China, in 2023. He is currently pursuing the
master’s degree with Shenzhen International Graduate School, Tsinghua University. His research
interests include computer vision and fine-grained
visual understanding.

Yong Liu received the B.Eng. degree from Shandong University in 2020. He is currently pursuing
the Ph.D. degree with Tsinghua Shenzhen International Graduate School, Tsinghua University. His
current research interests include fine-grained video
understanding and multimodal understanding.

Yifei Han received the B.Sc. degree from the
Department of Mathematical Sciences, Tsinghua
University, in 2023, where he is currently pursuing the master’s degree with Tsinghua Shenzhen
International Graduate School. His research interests
include embodied intelligence, 3D reconstruction,
and 3D perception.

Haoji Zhang received the B.S. degree in mathematics and physics from Tsinghua University, Beijing,
China, where he is currently pursuing the M.S.
degree in data science and information technology with Tsinghua Shenzhen International Graduate
School. His research interests include computer
vision and deep learning.

Yansong Tang (Member, IEEE) received the B.S.
and Ph.D. degrees from the Department of Automation, Tsinghua University, in 2015 and 2020,
respectively. From 2020 to 2022, he was a Postdoctoral Fellow with the Department of Engineering
Science, University of Oxford. He is currently
a tenure-track Associate Professor with Shenzhen
International Graduate School, Tsinghua University.
In recent years, he has authored more than 40 papers
in top peer-reviewed journals and conferences, such
as T RANSACTIONS ON PATTERN A NALYSIS AND
M ACHINE I NTELLIGENCE, T RANSACTIONS ON I MAGE P ROCESSING, and
CVPR. His research interests include computer vision, pattern recognition,
and video processing.

Jie Zhou (Fellow, IEEE) received the B.S. and
M.S. degrees from the Department of Mathematics,
Nankai University, Tianjin, China, in 1990 and 1992,
respectively, and the Ph.D. degree from the Institute
of Pattern Recognition and Artificial Intelligence,
Huazhong University of Science and Technology,
Wuhan, China, in 1995. From 1995 to 1997, he
was a Postdoctoral Fellow with the Department of
Automation, Tsinghua University, Beijing, China,
where he has been a Full Professor since 2003. In
recent years, he has authored more than 300 papers
in peer-reviewed journals and conferences. Among them, more than 100
papers have been published in top journals and conferences, such as IEEE
T RANSACTIONS ON PATTERN A NALYSIS AND M ACHINE I NTELLIGENCE,
IEEE T RANSACTIONS ON I MAGE P ROCESSING, and CVPR. His research
interests include computer vision, pattern recognition, and image processing.
He is an IAPR Fellow. He was a recipient of the National Outstanding
Youth Foundation of China Award. He is also an Associate Editor of IEEE
T RANSACTIONS ON PATTERN A NALYSIS AND M ACHINE I NTELLIGENCE
and two other journals.

Jiwen Lu (Fellow, IEEE) received the B.Eng.
degree in mechanical engineering and the M.Eng.
degree in electrical engineering from Xi’an University of Technology, Xi’an, China, in 2003 and
2006, respectively, and the Ph.D. degree in electrical
engineering from Nanyang Technological University,
Singapore, in 2012. From 2011 to 2015, he was
with the Advanced Digital Sciences Center, Singapore. In November 2015, he joined the Department
of Automation, Tsinghua University, where he is
currently a Full Professor and the Deputy Chair.
His current research interests include computer vision, pattern recognition,
multimedia computing, and intelligent robotics. He is an IAPR Fellow. He was
a recipient of the National Natural Science Funds for Distinguished Young
Scholar. He serves as the Co-Editor-in-Chief for Pattern Recognition Letters
and an Associate Editor for IEEE T RANSACTIONS ON I MAGE P ROCESSING,
IEEE T RANSACTIONS ON C IRCUITS AND S YSTEMS FOR V IDEO T ECHNOL OGY , IEEE T RANSACTIONS ON B IOMETRICS , B EHAVIOR , AND I DENTITY
S CIENCE, and Pattern Recognition.
PAPER_TEXT
